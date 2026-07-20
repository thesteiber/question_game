"""Question Game — Streamlit UI."""

from __future__ import annotations

import html
import time
from datetime import timedelta

import streamlit as st

from db import GameDB
from dice import DiceResult, idle_dice_html, render_dice_roll, roll_until_valid
from openai_questions import generate_questions
from styles import APP_CSS

st.set_page_config(
    page_title="Question Game",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)

DICE_REVEAL_SECONDS = 1.7


def get_db() -> GameDB:
    # Always construct fresh so redeploys pick up new GameDB methods
    # (session_state would otherwise keep a stale class instance).
    return GameDB()


def get_api_key() -> str | None:
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None


def get_model() -> str:
    try:
        return st.secrets.get("OPENAI_MODEL", "gpt-5.6")
    except Exception:
        return "gpt-5.6"


def current_player(room: dict) -> str | None:
    players = room.get("players") or []
    if not players:
        return None
    idx = int(room["settings"].get("current_player_index", 0)) % len(players)
    return players[idx]


def enter_room(room_name: str) -> None:
    db = get_db()
    db.ensure_room(room_name)
    st.session_state.room_name = room_name.strip()
    st.session_state.pop("just_rolled", None)
    st.rerun()


def progress_bar(remaining: int, total: int) -> None:
    if total <= 0:
        return
    done = total - remaining
    pct = max(0, min(100, round(100 * done / total)))
    st.markdown(
        f"""
        <div class="qg-progress-wrap">
          <div class="qg-progress-bar">
            <div class="qg-progress-fill" style="width:{pct}%"></div>
          </div>
          <div class="qg-progress-label">{remaining} left</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def brand_header(subtitle: str | None = None) -> None:
    st.markdown('<p class="qg-brand">Question Game</p>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="qg-meta">{subtitle}</p>', unsafe_allow_html=True)


def render_room_gate() -> None:
    db = get_db()
    st.markdown('<p class="qg-brand">Question Game</p>', unsafe_allow_html=True)
    st.markdown('<p class="qg-subtitle">a game by Sydney &amp; Niko</p>', unsafe_allow_html=True)
    st.markdown('<div class="qg-landing-mark">🎲</div>', unsafe_allow_html=True)

    with st.form("room_form"):
        room = st.text_input(
            "Room name",
            placeholder="enter room name…",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Enter", type="primary")
    if submitted:
        if not room.strip():
            st.error("Enter a room name.")
        else:
            enter_room(room)

    rooms = db.list_rooms()
    if rooms:
        st.markdown('<div class="qg-landing-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="qg-section-label">Rooms</p>', unsafe_allow_html=True)
        for room in rooms:
            name = room["room_name"]
            players = ", ".join(room["players"]) if room["players"] else "—"
            if room["total"]:
                progress = f"{room['remaining']} left"
            else:
                progress = "setup"
            st.markdown('<div class="qg-room-row">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="qg-room-card"><strong>{html.escape(name)}</strong>'
                f'<div class="qg-room-meta">{html.escape(players)} · {html.escape(progress)}</div></div>',
                unsafe_allow_html=True,
            )
            join_col, delete_col = st.columns(2, gap="small")
            with join_col:
                if st.button("Join", key=f"join_{name}", use_container_width=True, type="primary"):
                    enter_room(name)
            with delete_col:
                confirm_key = f"confirm_del_{name}"
                if st.session_state.get(confirm_key):
                    if st.button("Confirm", key=f"del_yes_{name}", use_container_width=True):
                        db.delete_room(name)
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                else:
                    if st.button("Delete", key=f"del_{name}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    favorites = db.list_favorites()
    if favorites:
        st.markdown('<div class="qg-landing-divider"></div>', unsafe_allow_html=True)
        with st.expander(f"Favorites ({len(favorites)})"):
            for fav in favorites:
                st.markdown(f"• {html.escape(fav['question_text'])}")
                if st.button("Remove", key=f"unfav_{fav['id']}"):
                    db.remove_favorite(fav["id"])
                    st.rerun()


def render_setup(db: GameDB, room_name: str, room: dict) -> None:
    brand_header(f'<strong>{html.escape(room_name)}</strong>')

    st.markdown("##### Players")
    existing = room.get("players") or ["", ""]
    while len(existing) < 2:
        existing.append("")
    p1 = st.text_input("Player 1", value=existing[0], placeholder="Name")
    p2 = st.text_input("Player 2", value=existing[1], placeholder="Name")
    extra = st.text_input(
        "More players",
        value=", ".join(existing[2:]) if len(existing) > 2 else "",
        placeholder="comma-separated",
    )

    st.markdown("##### Vibe")
    coupleyness = st.slider(
        "Coupley-ness",
        min_value=0,
        max_value=200,
        value=int(room["settings"].get("coupleyness", 100)),
    )
    vibe = st.text_area(
        "Notes",
        value=room["settings"].get("vibe", ""),
        placeholder="optional",
        height=80,
        label_visibility="collapsed",
    )

    api_key = get_api_key()
    if not api_key:
        st.warning("Missing OPENAI_API_KEY in secrets.")

    if st.button("Generate 50 questions", type="primary", disabled=not api_key):
        players = [p1.strip(), p2.strip()]
        if extra.strip():
            players.extend([p.strip() for p in extra.split(",") if p.strip()])
        players = [p for p in players if p]
        if len(players) < 2:
            st.error("Need at least two players.")
            return

        settings = dict(room["settings"])
        settings["coupleyness"] = coupleyness
        settings["vibe"] = vibe
        db.save_room(room_name, players=players, settings=settings)

        with st.spinner("Generating…"):
            try:
                questions = generate_questions(
                    api_key=api_key,
                    coupleyness=coupleyness,
                    vibe=vibe,
                    model=get_model(),
                )
                db.replace_questions(room_name, questions)
                st.rerun()
            except Exception:
                st.error("Could not generate questions.")

    if st.button("Leave room"):
        st.session_state.pop("room_name", None)
        st.rerun()


def _render_roll_screen(db: GameDB, room_name: str, room: dict, remaining: list[dict]) -> None:
    player = current_player(room)
    if player:
        st.markdown(
            f'<div class="qg-turn">{html.escape(player)}\'s turn</div>',
            unsafe_allow_html=True,
        )

    st.markdown(idle_dice_html(), unsafe_allow_html=True)

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        if st.button("Roll", type="primary", use_container_width=True):
            result = roll_until_valid({q["number"] for q in remaining})
            claimed = db.claim_question_number(
                room_name,
                result.number,
                dice={"tens": result.tens, "ones": result.ones, "attempts": result.attempts},
            )
            if claimed:
                st.session_state["just_rolled"] = {
                    "room": room_name,
                    "tens": result.tens,
                    "ones": result.ones,
                    "attempts": result.attempts,
                    "number": result.number,
                    "started_at": time.time(),
                }
            st.rerun()


def _render_question_card(
    db: GameDB,
    room_name: str,
    room: dict,
    question: dict,
    remaining: list[dict],
    total: int,
) -> None:
    player = current_player(room)
    just = st.session_state.get("just_rolled")
    rolling = (
        isinstance(just, dict)
        and just.get("room") == room_name
        and just.get("number") == question["number"]
        and not just.get("revealed")
    )
    finishing = (
        isinstance(just, dict)
        and just.get("room") == room_name
        and just.get("number") == question["number"]
        and just.get("revealed")
    )

    if player:
        st.markdown(
            f'<div class="qg-turn">{html.escape(player)}\'s turn</div>',
            unsafe_allow_html=True,
        )

    # Phase 1: dice only — question waits until the tumble finishes.
    if rolling:
        render_dice_roll(
            DiceResult(
                tens=int(just["tens"]),
                ones=int(just["ones"]),
                number=int(just["number"]),
                attempts=int(just.get("attempts", 1)),
            )
        )

        @st.fragment(run_every=timedelta(milliseconds=250))
        def _reveal_after_roll() -> None:
            jr = st.session_state.get("just_rolled")
            if not (
                isinstance(jr, dict)
                and jr.get("room") == room_name
                and jr.get("number") == question["number"]
                and not jr.get("revealed")
            ):
                return
            started = float(jr.get("started_at") or 0)
            if time.time() - started < DICE_REVEAL_SECONDS:
                return
            st.session_state["just_rolled"] = {**jr, "revealed": True}
            st.rerun()

        _reveal_after_roll()
        return

    if finishing:
        st.session_state.pop("just_rolled", None)

    last = room["settings"].get("last_dice") or {}
    tens = last.get("tens", question["number"] // 10)
    ones = last.get("ones", question["number"] % 10)
    st.markdown(
        f"""
        <div class="qg-dice-stage">
          <div class="qg-die qg-dice-static"><span class="qg-die-face">{int(tens)}</span></div>
          <div class="qg-die qg-dice-static"><span class="qg-die-face">{int(ones)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="qg-number">Question {question["number"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="qg-question">{html.escape(question["text"])}</div>',
        unsafe_allow_html=True,
    )
    progress_bar(len(remaining), total)

    favorited = db.is_favorited(question["text"])
    fav_label = "★" if favorited else "☆"

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        if st.button("Next turn", type="primary", use_container_width=True):
            db.mark_answered(room_name, question["number"], player or "unknown")
            st.session_state.pop("just_rolled", None)
            st.rerun()

    col_skip, col_fav = st.columns(2)
    with col_skip:
        if st.button("Skip", use_container_width=True):
            db.skip_question(room_name, question["number"])
            st.session_state.pop("just_rolled", None)
            st.rerun()
    with col_fav:
        if st.button(fav_label, disabled=favorited, use_container_width=True):
            db.add_favorite(
                question["text"],
                room_name=room_name,
                source_number=question["number"],
            )
            st.rerun()


def render_play(db: GameDB, room_name: str, room: dict) -> None:
    remaining = db.remaining_questions(room_name)
    answered = [q for q in db.list_questions(room_name) if q["answered"]]
    total = db.question_count(room_name)
    player_names = room.get("players") or []

    brand_header(f'<strong>{html.escape(room_name)}</strong>')
    chips = '<div class="qg-chip-row">'
    for name in player_names[:4]:
        chips += f'<span class="qg-chip">{html.escape(name)}</span>'
    if len(player_names) > 4:
        chips += f'<span class="qg-chip">+{len(player_names) - 4}</span>'
    chips += "</div>"
    st.markdown(chips, unsafe_allow_html=True)

    if not remaining and room["settings"].get("phase") == "done":
        st.markdown(
            """
            <div class="qg-done">
              <div class="qg-done-title">That’s a wrap</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        progress_bar(0, total)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Reset", use_container_width=True):
                db.reset_progress(room_name)
                st.rerun()
        with col_b:
            if st.button("New bank", type="primary", use_container_width=True):
                db.clear_questions(room_name)
                st.rerun()
        _answered_expander(answered)
        return

    question = db.get_active_question(room_name)

    if question is None:
        if not remaining:
            st.info("No questions left.")
        else:
            _render_roll_screen(db, room_name, room, remaining)
    else:
        _render_question_card(db, room_name, room, question, remaining, total)

    with st.expander("Options"):
        with st.form("add_player_form", clear_on_submit=True):
            new_player = st.text_input("Add player", placeholder="Name", label_visibility="collapsed")
            if st.form_submit_button("Add player"):
                if db.add_player(room_name, new_player):
                    st.rerun()
        if st.button("New question bank"):
            db.clear_questions(room_name)
            st.session_state.pop("just_rolled", None)
            st.rerun()
        if st.button("Reset progress"):
            db.reset_progress(room_name)
            st.session_state.pop("just_rolled", None)
            st.rerun()
        if st.button("Leave room"):
            st.session_state.pop("room_name", None)
            st.session_state.pop("just_rolled", None)
            st.rerun()

    _answered_expander(answered)


def _answered_expander(answered: list[dict]) -> None:
    if not answered:
        return
    with st.expander(f"Done ({len(answered)})"):
        for q in answered:
            if q.get("answered_by") == "skipped":
                who = " — skipped"
            elif q.get("answered_by"):
                who = f" — {html.escape(q['answered_by'])}"
            else:
                who = ""
            st.markdown(f"~~{q['number']}. {html.escape(q['text'])}~~{who}")


def main() -> None:
    db = get_db()
    room_name = st.session_state.get("room_name")

    if not room_name:
        render_room_gate()
        return

    room = db.ensure_room(room_name)
    has_questions = db.question_count(room_name) > 0
    phase = room["settings"].get("phase", "setup")

    if not has_questions or phase == "setup":
        render_setup(db, room_name, room)
        return

    # During a local dice roll, skip the 2s poll so it doesn't interrupt the animation.
    just = st.session_state.get("just_rolled")
    rolling = (
        isinstance(just, dict)
        and just.get("room") == room_name
        and not just.get("revealed")
    )
    if rolling:
        render_play(db, room_name, room)
        return

    # Auto-refresh so a second phone picks up rolls / next turn.
    @st.fragment(run_every=timedelta(seconds=2))
    def play_fragment() -> None:
        latest = db.get_room(room_name)
        if not latest:
            st.warning("Room missing.")
            return
        render_play(db, room_name, latest)

    play_fragment()


if __name__ == "__main__":
    main()
