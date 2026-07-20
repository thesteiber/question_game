"""Dice-based question picking for Question Game.

Two dice show digits 0–5. Concatenated they form 00–55.
We keep rolling until we land on a remaining question number (1–50).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import streamlit.components.v1 as components


@dataclass(frozen=True)
class DiceResult:
    tens: int
    ones: int
    number: int
    attempts: int  # how many rolls it took (for UI flavor)


def roll_until_valid(remaining_numbers: set[int], *, max_attempts: int = 200) -> DiceResult:
    """Roll two 0–5 dice until the two-digit result is in remaining_numbers."""
    if not remaining_numbers:
        raise ValueError("No remaining questions to roll for")

    for attempt in range(1, max_attempts + 1):
        tens = random.randint(0, 5)
        ones = random.randint(0, 5)
        number = tens * 10 + ones
        if number in remaining_numbers:
            return DiceResult(tens=tens, ones=ones, number=number, attempts=attempt)

    # Extremely unlikely with 1–50 pool; fall back so the game never stalls.
    number = random.choice(sorted(remaining_numbers))
    return DiceResult(tens=number // 10, ones=number % 10, number=number, attempts=max_attempts)


def render_dice_roll(result: DiceResult) -> None:
    """Show tumbling 0–5 dice that land on the chosen question number."""
    components.html(
        f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700&family=Nunito:wght@700;800&display=swap');
  body {{
    margin: 0;
    background: transparent;
    font-family: 'Nunito', sans-serif;
    overflow: hidden;
  }}
  .stage {{
    display: flex;
    justify-content: center;
    gap: 1rem;
    padding: 0.4rem 0 0.2rem;
  }}
  .die {{
    width: 4.7rem;
    height: 4.7rem;
    border-radius: 1rem;
    background: linear-gradient(145deg, #fffdf9, #f0e4d6);
    border: 2px solid #1a2e2a;
    box-shadow: 0 8px 0 #1a2e2a, 0 14px 22px rgba(26,46,42,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: tumble 1.25s cubic-bezier(.2,.8,.2,1) both;
  }}
  .die:nth-child(2) {{ animation-delay: 0.1s; }}
  .face {{
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #1a2e2a;
    line-height: 1;
  }}
  .result {{
    text-align: center;
    font-size: 1.15rem;
    font-weight: 800;
    color: #1a2e2a;
    margin: 0.65rem 0 0;
    opacity: 0;
    animation: pop 0.35s ease-out 1.35s forwards;
  }}
  .spacer {{
    height: 0.5rem;
  }}
  @keyframes tumble {{
    0%   {{ transform: translateY(-30px) rotate(-20deg) scale(0.85); }}
    20%  {{ transform: translateY(6px) rotate(14deg) scale(1.06); }}
    40%  {{ transform: translateY(-12px) rotate(-10deg); }}
    60%  {{ transform: translateY(3px) rotate(7deg); }}
    80%  {{ transform: translateY(-3px) rotate(-3deg); }}
    100% {{ transform: translateY(0) rotate(0) scale(1); }}
  }}
  @keyframes pop {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
</style>
</head>
<body>
  <div class="stage">
    <div class="die"><span class="face" id="d0">?</span></div>
    <div class="die"><span class="face" id="d1">?</span></div>
  </div>
  <p class="result"><strong>{result.tens}{result.ones:d}</strong></p>
  <div class="spacer"></div>
<script>
  const finals = [{result.tens}, {result.ones}];
  const faces = [document.getElementById('d0'), document.getElementById('d1')];
  const duration = 1300;
  const start = performance.now();

  function tick(now) {{
    const t = now - start;
    if (t < duration) {{
      faces[0].textContent = Math.floor(Math.random() * 6);
      faces[1].textContent = Math.floor(Math.random() * 6);
      requestAnimationFrame(tick);
    }} else {{
      faces[0].textContent = finals[0];
      faces[1].textContent = finals[1];
    }}
  }}
  requestAnimationFrame(tick);
</script>
</body>
</html>
        """,
        height=160,
        scrolling=False,
    )


def idle_dice_html() -> str:
    return """
<div class="qg-idle-dice">
  <div class="qg-die"><span class="qg-die-face">?</span></div>
  <div class="qg-die"><span class="qg-die-face">?</span></div>
</div>
"""
