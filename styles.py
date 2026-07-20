"""Shared CSS for Question Game — mobile-first, playful."""

APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
  font-family: 'Nunito', sans-serif !important;
}

.stApp {
  background:
    radial-gradient(120% 80% at 10% -10%, #e4efe8 0%, transparent 55%),
    radial-gradient(90% 60% at 100% 0%, #d5e6db 0%, transparent 50%),
    linear-gradient(180deg, #fff8f1 0%, #eef4f0 100%);
}

.block-container {
  padding-top: 1rem !important;
  padding-bottom: 3.5rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
  max-width: 28rem;
}

/* Hide Streamlit chrome for a game-like feel */
#MainMenu, header, footer { visibility: hidden; }
header[data-testid="stHeader"] { display: none; }
div[data-testid="stToolbar"] { display: none; }
div[data-testid="stDecoration"] { display: none; }
section[data-testid="stSidebar"] { display: none; }

.qg-brand {
  font-family: 'Fraunces', Georgia, serif !important;
  font-size: 2.15rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em;
  color: #2c3a34 !important;
  margin-bottom: 0.15rem !important;
  line-height: 1.15 !important;
  text-align: center;
}

h1 {
  font-family: 'Fraunces', Georgia, serif !important;
  font-size: 2.15rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em;
  color: #2c3a34 !important;
  margin-bottom: 0.15rem !important;
  line-height: 1.15 !important;
  text-align: center !important;
}

.qg-subtitle {
  color: #7d9b8a;
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 1.1rem 0;
  text-align: center;
}

.qg-meta {
  color: #6b6258;
  font-size: 0.92rem;
  margin-bottom: 0.85rem;
  text-align: center;
}

.qg-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin: 0.4rem 0 0.9rem 0;
  justify-content: center;
}

.qg-chip {
  background: rgba(26, 46, 42, 0.08);
  color: #2c3a34;
  border-radius: 999px;
  padding: 0.28rem 0.7rem;
  font-size: 0.8rem;
  font-weight: 700;
}

.qg-chip-accent {
  background: #2c3a34;
  color: #fff8f1;
}

.qg-turn {
  background: linear-gradient(135deg, #2c3a34 0%, #7d9b8a 100%);
  color: #fff8f1;
  border-radius: 18px;
  padding: 0.95rem 1.1rem;
  font-size: 1.2rem;
  font-weight: 800;
  margin: 0.5rem 0 1rem 0;
  box-shadow: 0 10px 24px rgba(26, 46, 42, 0.18);
  text-align: center;
}

.qg-number {
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #7d9b8a;
  font-weight: 800;
  margin: 0.15rem 0 0 !important;
  text-align: center;
  line-height: 1.2;
}

.qg-fav-mark {
  display: none;
}

/* Compact star between question number and question text */
div[data-testid="element-container"]:has(.qg-fav-mark)
  + div[data-testid="element-container"]
  button,
div[data-testid="stElementContainer"]:has(.qg-fav-mark)
  + div[data-testid="stElementContainer"]
  button {
  min-height: 1.55rem !important;
  height: 1.55rem !important;
  padding: 0 !important;
  margin: 0 !important;
  font-size: 1.2rem !important;
  font-weight: 500 !important;
  line-height: 1 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: #9bb5a6 !important;
}

div[data-testid="element-container"]:has(.qg-fav-mark.qg-fav-on)
  + div[data-testid="element-container"]
  button,
div[data-testid="stElementContainer"]:has(.qg-fav-mark.qg-fav-on)
  + div[data-testid="stElementContainer"]
  button {
  color: #c4a4a8 !important;
}

/* Tighten vertical gaps around number → star → question */
div[data-testid="element-container"]:has(.qg-number),
div[data-testid="stElementContainer"]:has(.qg-number) {
  margin-bottom: -0.65rem !important;
}

div[data-testid="element-container"]:has(.qg-question),
div[data-testid="stElementContainer"]:has(.qg-question) {
  margin-top: -0.45rem !important;
}

.qg-question {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.55rem;
  line-height: 1.3;
  font-weight: 600;
  color: #2c3a34;
  margin: 0.15rem 0 1rem 0;
  text-align: center;
  padding: 1rem 0.85rem;
  background: rgba(255,255,255,0.72);
  border-radius: 18px;
  border: 1px solid rgba(26, 46, 42, 0.08);
  animation: qg-pop 0.45s ease-out;
}

.qg-progress-wrap {
  margin: 0.2rem 0 1rem 0;
}

.qg-progress-bar {
  height: 10px;
  background: rgba(26, 46, 42, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

.qg-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7d9b8a, #e8a05a);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.qg-progress-label {
  color: #6b6258;
  font-size: 0.82rem;
  font-weight: 700;
  margin-top: 0.35rem;
  text-align: center;
}

.qg-room-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(26, 46, 42, 0.08);
  border-radius: 16px;
  padding: 0.95rem 1rem 0.85rem;
  margin-bottom: 0.45rem;
  box-shadow: 0 4px 14px rgba(26, 46, 42, 0.05);
  text-align: center;
}

.qg-room-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.45rem;
  font-weight: 800;
  color: #2c3a34;
  text-align: center;
  margin: 0 0 0.15rem 0;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.qg-room-meta {
  color: #8a938c !important;
  font-size: 0.7rem !important;
  font-weight: 400 !important;
  text-align: center;
  margin: 0.35rem 0 0.15rem 0;
  line-height: 1.35;
  letter-spacing: 0.01em;
}

.qg-room-row {
  margin: 0 0 1rem 0;
}

.qg-options {
  padding: 0.35rem 0 0.15rem;
}

.qg-options-title {
  text-align: center;
  font-weight: 800;
  color: #2c3a34;
  margin: 0.15rem 0 0.65rem 0;
}

.qg-landing-mark {
  text-align: center;
  font-size: 2rem;
  margin: 0.15rem 0 0.55rem 0;
  opacity: 0.9;
}

.qg-landing-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(26,46,42,0.18), transparent);
  margin: 0.35rem 0 0.2rem 0;
}

.qg-done {
  text-align: center;
  padding: 1.25rem 0.75rem 0.5rem;
}

.qg-done-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3a34;
  margin-bottom: 0.35rem;
}

.qg-done-sub {
  color: #6b6258;
  margin-bottom: 1rem;
}

/* Dice */
.qg-dice-stage {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 1rem 0 0.6rem 0;
  min-height: 5.5rem;
  align-items: center;
}

.qg-die {
  width: 4.6rem;
  height: 4.6rem;
  border-radius: 1rem;
  background: linear-gradient(145deg, #fffdf9, #f0e4d6);
  border: 2px solid #2c3a34;
  box-shadow:
    0 8px 0 #2c3a34,
    0 14px 22px rgba(26, 46, 42, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.qg-die-face {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 2.35rem;
  font-weight: 700;
  color: #2c3a34;
  line-height: 1;
}

.qg-dice-roll {
  animation: qg-tumble 1.35s cubic-bezier(.2,.8,.2,1) both;
  animation-delay: var(--delay, 0s);
}

.qg-dice-static .qg-die-face {
  animation: none;
}

.qg-dice-result {
  text-align: center;
  font-size: 1.15rem;
  font-weight: 800;
  color: #2c3a34;
  margin: 0.25rem 0 0.15rem 0;
  animation: qg-pop 0.4s ease-out 1.2s both;
}

.qg-roll-prompt {
  text-align: center;
  padding: 0.25rem 0 0;
}

div.stButton > button,
div.stFormSubmitButton > button {
  width: 100%;
  min-height: 3.15rem;
  font-size: 1.05rem !important;
  font-weight: 800 !important;
  border-radius: 14px !important;
  border: 1px solid rgba(44, 58, 52, 0.1) !important;
  background: linear-gradient(145deg, #f7efe4, #eadfcf) !important;
  color: #7a6550 !important;
  box-shadow: 0 5px 0 #c4b5a0 !important;
}

.qg-idle-dice {
  display: flex;
  justify-content: center;
  gap: 0.85rem;
  margin: 0.75rem 0 1rem 0;
  opacity: 0.55;
}

.qg-idle-dice .qg-die {
  width: 3.4rem;
  height: 3.4rem;
  box-shadow: 0 5px 0 #2c3a34;
}

.qg-idle-dice .qg-die-face {
  font-size: 1.6rem;
  color: #6b6258;
}

@keyframes qg-tumble {
  0%   { transform: translateY(-28px) rotate(-18deg) scale(0.85); }
  18%  { transform: translateY(4px) rotate(12deg) scale(1.05); }
  32%  { transform: translateY(-10px) rotate(-10deg); }
  48%  { transform: translateY(2px) rotate(8deg); }
  65%  { transform: translateY(-4px) rotate(-4deg); }
  80%  { transform: translateY(0) rotate(2deg); }
  100% { transform: translateY(0) rotate(0) scale(1); }
}

@keyframes qg-pop {
  from { opacity: 0; transform: translateY(8px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* During tumble, rapidly cycle face numbers for drama */
.qg-dice-roll .qg-die-face {
  animation: qg-faces 1.15s steps(1) both;
  animation-delay: var(--delay, 0s);
}

@keyframes qg-faces {
  0%   { content: none; }
  0%, 12%  { opacity: 1; }
}

/* Primary actions stay sage, with darker sage text */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"],
div.stFormSubmitButton > button[kind="primary"],
div.stFormSubmitButton > button[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #7d9b8a, #9bb5a6) !important;
  color: #2c4a3c !important;
  border: none !important;
  box-shadow: 0 6px 0 #5c7a6a !important;
}

div.stButton > button:active {
  transform: translateY(2px);
}

/* Dusty-rose danger buttons (Delete / Remove / Reset / Skip) */
div[data-testid="element-container"]:has(.qg-btn-danger-mark)
  + div[data-testid="element-container"]
  button,
div[data-testid="stElementContainer"]:has(.qg-btn-danger-mark)
  + div[data-testid="stElementContainer"]
  button {
  background: linear-gradient(135deg, #c4a4a8, #d4b8bb) !important;
  color: #5c3d42 !important;
  border: 1px solid rgba(140, 100, 108, 0.28) !important;
  box-shadow: 0 5px 0 #9e7f84 !important;
}

/* Landing form: center the enter button */
div[data-testid="stForm"] {
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
}

div[data-testid="stForm"] div.stFormSubmitButton {
  display: flex;
  justify-content: center;
  margin-top: 0.55rem;
}

div[data-testid="stForm"] div.stFormSubmitButton > button {
  max-width: 14rem;
}

/* Room action row: keep Join / Delete side by side */
.qg-room-row div[data-testid="stHorizontalBlock"] {
  gap: 0.5rem;
}

.qg-room-row div.stButton > button {
  min-height: 2.65rem !important;
  font-size: 0.95rem !important;
}

.stTextInput input, .stTextArea textarea {
  border-radius: 12px !important;
  min-height: 2.85rem;
  text-align: center;
}

.stTextInput input::placeholder {
  text-align: center;
}

.stSlider { padding-top: 0.25rem; padding-bottom: 0.5rem; }

.qg-setup-header {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: #2c3a34;
  text-align: center;
  margin: 1.25rem 0 0.75rem 0;
  letter-spacing: -0.02em;
}

.qg-player-row {
  background: linear-gradient(135deg, #e7efe9 0%, #d8e6dc 100%);
  border: 1px solid rgba(125, 155, 138, 0.45);
  border-radius: 14px;
  padding: 0.72rem 0.95rem;
  text-align: center;
  font-weight: 700;
  color: #2c3a34;
  box-shadow: 0 2px 8px rgba(44, 58, 52, 0.06);
  margin-bottom: 0.35rem;
}

.qg-player-block {
  margin-bottom: 0.85rem;
}

.qg-room-block {
  display: none;
}

.qg-mode-toggles {
  margin: 0.35rem 0 0.85rem 0;
  padding-left: 1.15rem;
  padding-right: 1.15rem;
}

div[data-testid="stToggle"] {
  display: flex;
  justify-content: center;
  padding: 0.35rem 0;
}

div[data-testid="stSlider"] {
  padding-left: 1.15rem !important;
  padding-right: 1.15rem !important;
}

/* Bigger, softer slider thumb */
div[data-baseweb="slider"] [role="slider"] {
  width: 1.55rem !important;
  height: 1.55rem !important;
  background-color: #7d9b8a !important;
  border: 3px solid #fff8f1 !important;
  box-shadow: 0 2px 8px rgba(44, 58, 52, 0.22) !important;
}

div[data-baseweb="slider"] div[data-testid="stThumbValue"] {
  font-weight: 700;
}

/* Track polish */
div[data-baseweb="slider"] > div > div {
  height: 8px !important;
  border-radius: 999px !important;
}

.qg-rooms-block {
  text-align: center;
  max-width: 22rem;
  margin: 0 auto;
}

.qg-rooms-block .qg-room-row {
  text-align: left;
}

/* Expanders */
details {
  background: rgba(255,255,255,0.55) !important;
  border-radius: 14px !important;
  border: 1px solid rgba(26, 46, 42, 0.08) !important;
}
"""
