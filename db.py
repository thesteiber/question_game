"""SQLite persistence for shared game rooms."""

from __future__ import annotations

import json
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "question_game.db"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class GameDB:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else DEFAULT_DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS rooms (
                    room_name TEXT PRIMARY KEY,
                    players TEXT NOT NULL DEFAULT '[]',
                    settings TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS questions (
                    room_name TEXT NOT NULL,
                    number INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    answered INTEGER NOT NULL DEFAULT 0,
                    answered_by TEXT,
                    PRIMARY KEY (room_name, number),
                    FOREIGN KEY (room_name) REFERENCES rooms(room_name) ON DELETE CASCADE
                );
                """
            )

    def get_room(self, room_name: str) -> dict[str, Any] | None:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT room_name, players, settings, updated_at FROM rooms WHERE room_name = ?",
                (key,),
            ).fetchone()
            if not row:
                return None
            return _room_from_row(row)

    def ensure_room(self, room_name: str) -> dict[str, Any]:
        existing = self.get_room(room_name)
        if existing:
            return existing
        key = _normalize_room(room_name)
        settings = {
            "coupleyness": 100,
            "vibe": "",
            "current_player_index": 0,
            "current_question_number": None,
            "phase": "setup",
        }
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO rooms (room_name, players, settings, updated_at) VALUES (?, ?, ?, ?)",
                (key, json.dumps([]), json.dumps(settings), _utc_now()),
            )
        return self.get_room(room_name)  # type: ignore[return-value]

    def save_room(
        self,
        room_name: str,
        *,
        players: list[str] | None = None,
        settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        room = self.ensure_room(room_name)
        key = room["room_name"]
        next_players = players if players is not None else room["players"]
        next_settings = settings if settings is not None else room["settings"]
        with self._connect() as conn:
            conn.execute(
                "UPDATE rooms SET players = ?, settings = ?, updated_at = ? WHERE room_name = ?",
                (json.dumps(next_players), json.dumps(next_settings), _utc_now(), key),
            )
        return self.get_room(key)  # type: ignore[return-value]

    def replace_questions(self, room_name: str, questions: list[str]) -> None:
        room = self.ensure_room(room_name)
        key = room["room_name"]
        if len(questions) != 50:
            raise ValueError("Expected exactly 50 questions")
        with self._connect() as conn:
            conn.execute("DELETE FROM questions WHERE room_name = ?", (key,))
            conn.executemany(
                "INSERT INTO questions (room_name, number, text, answered, answered_by) VALUES (?, ?, ?, 0, NULL)",
                [(key, i + 1, text) for i, text in enumerate(questions)],
            )
        settings = dict(room["settings"])
        settings["current_player_index"] = 0
        settings["current_question_number"] = None
        settings["phase"] = "play"
        self.save_room(key, settings=settings)

    def list_questions(self, room_name: str) -> list[dict[str, Any]]:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT number, text, answered, answered_by
                FROM questions
                WHERE room_name = ?
                ORDER BY number
                """,
                (key,),
            ).fetchall()
        return [
            {
                "number": row["number"],
                "text": row["text"],
                "answered": bool(row["answered"]),
                "answered_by": row["answered_by"],
            }
            for row in rows
        ]

    def question_count(self, room_name: str) -> int:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM questions WHERE room_name = ?",
                (key,),
            ).fetchone()
        return int(row["n"]) if row else 0

    def remaining_questions(self, room_name: str) -> list[dict[str, Any]]:
        return [q for q in self.list_questions(room_name) if not q["answered"]]

    def get_question(self, room_name: str, number: int) -> dict[str, Any] | None:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT number, text, answered, answered_by
                FROM questions
                WHERE room_name = ? AND number = ?
                """,
                (key, number),
            ).fetchone()
        if not row:
            return None
        return {
            "number": row["number"],
            "text": row["text"],
            "answered": bool(row["answered"]),
            "answered_by": row["answered_by"],
        }

    def set_current_question(self, room_name: str, number: int | None) -> dict[str, Any]:
        room = self.ensure_room(room_name)
        settings = dict(room["settings"])
        settings["current_question_number"] = number
        return self.save_room(room_name, settings=settings)

    def claim_random_question(self, room_name: str) -> dict[str, Any] | None:
        """Atomically draw a remaining question if none is already active."""
        key = _normalize_room(room_name)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT settings FROM rooms WHERE room_name = ?",
                (key,),
            ).fetchone()
            if not row:
                return None
            settings = json.loads(row["settings"])
            current = settings.get("current_question_number")
            if current is not None:
                qrow = conn.execute(
                    """
                    SELECT number, text, answered, answered_by
                    FROM questions
                    WHERE room_name = ? AND number = ? AND answered = 0
                    """,
                    (key, int(current)),
                ).fetchone()
                if qrow:
                    return {
                        "number": qrow["number"],
                        "text": qrow["text"],
                        "answered": bool(qrow["answered"]),
                        "answered_by": qrow["answered_by"],
                    }

            remaining = conn.execute(
                """
                SELECT number, text, answered, answered_by
                FROM questions
                WHERE room_name = ? AND answered = 0
                """,
                (key,),
            ).fetchall()
            if not remaining:
                settings["current_question_number"] = None
                if settings.get("phase") != "setup":
                    settings["phase"] = "done"
                conn.execute(
                    "UPDATE rooms SET settings = ?, updated_at = ? WHERE room_name = ?",
                    (json.dumps(settings), _utc_now(), key),
                )
                return None

            chosen = random.choice(remaining)
            settings["current_question_number"] = chosen["number"]
            settings["phase"] = "play"
            conn.execute(
                "UPDATE rooms SET settings = ?, updated_at = ? WHERE room_name = ?",
                (json.dumps(settings), _utc_now(), key),
            )
            return {
                "number": chosen["number"],
                "text": chosen["text"],
                "answered": bool(chosen["answered"]),
                "answered_by": chosen["answered_by"],
            }

    def mark_answered(self, room_name: str, number: int, answered_by: str) -> None:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE questions
                SET answered = 1, answered_by = ?
                WHERE room_name = ? AND number = ?
                """,
                (answered_by, key, number),
            )
        room = self.ensure_room(key)
        settings = dict(room["settings"])
        players = room["players"]
        if players:
            settings["current_player_index"] = (int(settings.get("current_player_index", 0)) + 1) % len(
                players
            )
        settings["current_question_number"] = None
        if not self.remaining_questions(key):
            settings["phase"] = "done"
        self.save_room(key, settings=settings)

    def reset_progress(self, room_name: str) -> dict[str, Any]:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE questions
                SET answered = 0, answered_by = NULL
                WHERE room_name = ?
                """,
                (key,),
            )
        room = self.ensure_room(key)
        settings = dict(room["settings"])
        settings["current_player_index"] = 0
        settings["current_question_number"] = None
        settings["phase"] = "play" if self.question_count(key) else "setup"
        return self.save_room(key, settings=settings)

    def clear_questions(self, room_name: str) -> dict[str, Any]:
        key = _normalize_room(room_name)
        with self._connect() as conn:
            conn.execute("DELETE FROM questions WHERE room_name = ?", (key,))
        room = self.ensure_room(key)
        settings = dict(room["settings"])
        settings["current_player_index"] = 0
        settings["current_question_number"] = None
        settings["phase"] = "setup"
        return self.save_room(key, settings=settings)


def _normalize_room(room_name: str) -> str:
    return " ".join(room_name.strip().lower().split())


def _room_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "room_name": row["room_name"],
        "players": json.loads(row["players"]),
        "settings": json.loads(row["settings"]),
        "updated_at": row["updated_at"],
    }
