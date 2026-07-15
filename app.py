"""Question Game — Streamlit UI."""

from __future__ import annotations

import html
from datetime import timedelta

import streamlit as st

from db import GameDB
from openai_questions import generate_questions

st.set_page_config(
    page_title="Question Game",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Mobile-friendly CSS
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 40rem; }
    h1 { font-size: 1.9rem !important; letter-spacing: -0.02em; margin-bottom: 0.25rem !important; }
    .qg-meta { color: #5c564c; font-size: 0.95rem; margin-bottom: 1rem; }
    .qg-turn {
        background: #2c5f4f;
        color: #f7f3ec;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 0.75rem 0 1rem 0;
    }
    .qg-number {
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #5c564c;
        margin-bottom: 0.35rem;
    }
    .qg-question {
        font-size: 1.45rem;
        line-height: 1.35;
        font-weight: 560;
        color: #1c1a16;
        margin-bottom: 1.25rem;
    }
    .qg-progress { color: #5c564c; margin: 0.5rem 0 1rem 0; }
    div.stButton > button {
        width: 100%;
        min-height: 3rem;
        font-size: 1.05rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_db() -> GameDB:
    if "db" not in st.session_state:
        st.session_state.db = GameDB()
    return st.session_state.db


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


def render_room_gate() -> None:
    st.title("Question Game")
    st.markdown(
        '<p class="qg-meta">Enter a shared room name to play. Same name = same game '
        "(handy on one phone or two).</p>",
        unsafe_allow_html=True,
    )
    with st.form("room_form"):
        room = st.text_input("Room name", placeholder="sydniko")
        submitted = st.form_submit_button("Enter room", type="primary")
    if submitted:
        if not room.strip():
            st.error("Enter a room name.")
            return
        db = get_db()
        db.ensure_room(room)
        st.session_state.room_name = room.strip()
        st.rerun()


def render_setup(db: GameDB, room_name: str, room: dict) -> None:
    st.title("Question Game")
    st.markdown(
        f'<p class="qg-meta">Room: <strong>{html.escape(room_name)}</strong></p>',
        unsafe_allow_html=True,
    )

    st.subheader("Players")
    existing = room.get("players") or ["", ""]
    while len(existing) < 2:
        existing.append("")
    p1 = st.text_input("Player 1", value=existing[0], placeholder="Name")
    p2 = st.text_input("Player 2", value=existing[1], placeholder="Name")
    extra = st.text_input(
        "More players (optional, comma-separated)",
        value=", ".join(existing[2:]) if len(existing) > 2 else "",
    )

    st.subheader("Question vibe")
    coupleyness = st.slider(
        "Coupley-ness",
        min_value=0,
        max_value=200,
        value=int(room["settings"].get("coupleyness", 100)),
        help="0 = personal get-to-know-you · 100 = coupley · 200 = intensely us",
    )
    vibe = st.text_area(
        "Optional notes for generation",
        value=room["settings"].get("vibe", ""),
        placeholder="e.g. playful, late-night, less about the future…",
        height=80,
    )

    api_key = get_api_key()
    if not api_key:
        st.warning("Add OPENAI_API_KEY in Streamlit secrets before generating.")

    if st.button("Generate 50 questions", type="primary", disabled=not api_key):
        players = [p1.strip(), p2.strip()]
        if extra.strip():
            players.extend([p.strip() for p in extra.split(",") if p.strip()])
        players = [p for p in players if p]
        if len(players) < 2:
            st.error("Enter at least two player names.")
            return

        settings = dict(room["settings"])
        settings["coupleyness"] = coupleyness
        settings["vibe"] = vibe
        db.save_room(room_name, players=players, settings=settings)

        with st.spinner("Generating questions…"):
            try:
                questions = generate_questions(
                    api_key=api_key,
                    coupleyness=coupleyness,
                    vibe=vibe,
                    model=get_model(),
                )
                db.replace_questions(room_name, questions)
                st.success("Ready to play.")
                st.rerun()
            except Exception:
                st.error("Could not generate questions. Check the API key / model and try again.")

    if st.button("Leave room"):
        st.session_state.pop("room_name", None)
        st.rerun()


def render_play(db: GameDB, room_name: str, room: dict) -> None:
    players = room.get("players") or []
    remaining = db.remaining_questions(room_name)
    answered = [q for q in db.list_questions(room_name) if q["answered"]]
    total = db.question_count(room_name)
    player = current_player(room)

    st.title("Question Game")
    st.markdown(
        f'<p class="qg-meta">Room: <strong>{html.escape(room_name)}</strong> · '
        f"{len(remaining)} of {total} left</p>",
        unsafe_allow_html=True,
    )

    if not remaining and room["settings"].get("phase") == "done":
        st.markdown('<div class="qg-turn">All questions answered</div>', unsafe_allow_html=True)
        st.write("Nice work. Generate a new bank or reset this one.")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Reset same questions"):
                db.reset_progress(room_name)
                st.rerun()
        with col_b:
            if st.button("New question bank", type="primary"):
                db.clear_questions(room_name)
                st.rerun()
        _answered_expander(answered)
        return

    question = db.claim_random_question(room_name)
    room = db.get_room(room_name) or room
    player = current_player(room)
    remaining = db.remaining_questions(room_name)

    if player:
        st.markdown(
            f'<div class="qg-turn">{html.escape(player)}\'s turn</div>',
            unsafe_allow_html=True,
        )

    if question:
        st.markdown(
            f'<div class="qg-number">Question {question["number"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="qg-question">{html.escape(question["text"])}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="qg-progress">{len(remaining)} remaining · next up after this turn</p>',
            unsafe_allow_html=True,
        )

        if st.button("Next turn", type="primary"):
            db.mark_answered(room_name, question["number"], player or "unknown")
            st.rerun()
    else:
        st.info("No questions left.")

    with st.expander("Game options"):
        if st.button("New question bank"):
            db.clear_questions(room_name)
            st.rerun()
        if st.button("Reset progress (reuse questions)"):
            db.reset_progress(room_name)
            st.rerun()
        if st.button("Leave room"):
            st.session_state.pop("room_name", None)
            st.rerun()

    _answered_expander(answered)


def _answered_expander(answered: list[dict]) -> None:
    with st.expander(f"Answered ({len(answered)})"):
        if not answered:
            st.caption("Nothing crossed off yet.")
            return
        for q in answered:
            who = f" — {html.escape(q['answered_by'])}" if q.get("answered_by") else ""
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

    # Auto-refresh so a second phone picks up Next turn without manual reload.
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
