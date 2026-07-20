# Question Game

Mobile-friendly conversation game: generate a bank of 55 questions with OpenAI, take turns, and auto-cross off what’s already been answered.

## How it works

1. Enter a **shared room name** (example: `sydniko`).
2. Add player names, set **coupley-ness** (0–200), generate questions.
3. On a turn the app picks a random remaining question. Answer out loud — nothing is typed.
4. Tap **Next turn** to cross it off and advance to the next player.
5. One phone handed back and forth works; two phones work too (play screen auto-refreshes every ~2s).

The OpenAI API key stays on the server (`st.secrets`). It is never sent to the browser.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), create an app pointing at `app.py`.
3. In **Settings → Secrets**, paste:

```toml
OPENAI_API_KEY = "sk-..."
# optional
# OPENAI_MODEL = "gpt-5.6"
```

4. Open the app URL on your phones.

Room state is stored in SQLite on the app server. Streamlit Cloud can wipe the filesystem on rare rebuilds; if that happens, just generate a new bank.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit secrets.toml with your key
streamlit run app.py
```

On a phone on the same Wi‑Fi: `http://<your-computer-lan-ip>:8501`.
