"""OpenAI-backed question bank generation."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from sample_questions import COUPLE, PERSONAL


class QuestionBank(BaseModel):
    questions: list[str] = Field(
        ...,
        min_length=55,
        max_length=55,
        description="Exactly 55 distinct questions.",
    )


QUESTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 55,
            "maxItems": 55,
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}


def _clamp(value: int) -> int:
    return max(0, min(200, int(value)))


def _style_for_coupleyness(coupleyness: int) -> tuple[str, list[str]]:
    """Map 0–200 coupley-ness to prompt guidance and example questions."""
    value = _clamp(coupleyness)

    if value <= 40:
        examples = PERSONAL
        style = (
            "Keep questions personal and individual — classic get-to-know-you depth. "
            "Avoid relationship-specific wording like 'us', 'we', or 'our relationship'."
        )
    elif value <= 90:
        personal_n = max(4, round(len(PERSONAL) * (1 - value / 100)))
        couple_n = max(4, round(len(COUPLE) * (value / 100)))
        examples = PERSONAL[:personal_n] + COUPLE[:couple_n]
        style = (
            "Mix individual get-to-know-you questions with lightly relational ones. "
            "Most questions should still work for people who are close but not intensely coupley."
        )
    elif value <= 140:
        examples = PERSONAL[::2][:6] + COUPLE
        style = (
            "Lean into couple / partnership questions about closeness, care, conflict, "
            "and everyday life together. Include a few personal questions for balance."
        )
    else:
        examples = COUPLE
        intensity = "warm and specific" if value <= 170 else "deeply intimate, playful, and emotionally rich"
        style = (
            f"Generate strongly couple-focused questions that feel {intensity}. "
            "Use 'you/me/us/we' where it fits. Push beyond surface romance into "
            "shared life, desire, support, future, and quirky togetherness. "
            "Do not make them clinical or therapy-worksheet bland."
        )

    return style, examples


def _style_for_funness(funness: int) -> str:
    value = _clamp(funness)
    if value <= 40:
        return (
            "Tone: earnest and thoughtful. Prefer sincere, reflective prompts. "
            "Avoid silliness, jokes, or absurd hypotheticals."
        )
    if value <= 100:
        return (
            "Tone: balanced — warm and approachable with occasional light playfulness, "
            "but still mostly grounded."
        )
    if value <= 150:
        return (
            "Tone: lively and light-hearted. Include playful, quirky, and fun prompts "
            "while keeping them answerable out loud."
        )
    return (
        "Tone: extremely goofy and light-hearted. Lean into silly scenarios, playful "
        "absurdity, and laughter-forward prompts. Still make them fun to answer, not nonsense."
    )


def _style_for_raunch(raunch: int) -> str:
    """Guide spice level; stay direct at the high end without inviting refusals."""
    value = _clamp(raunch)
    if value <= 30:
        return (
            "Keep every question totally wholesome and PG — no flirtation, innuendo, "
            "or romantic/physical intimacy topics."
        )
    if value <= 80:
        return (
            "Mostly clean. Light warmth is fine; avoid innuendo and anything suggestive."
        )
    if value <= 130:
        return (
            "Allow gentle flirtation and soft romantic chemistry. Mild, tasteful innuendo "
            "is okay; keep it classy and never crude."
        )
    if value <= 170:
        return (
            "Private adult couple game. Questions should be clearly spicy: lust, turn-ons, "
            "bedroom preferences, sexual history between partners, and teasing innuendo. "
            "Be direct enough that the heat is obvious, while staying playful rather than clinical."
        )
    return (
        "Private adult couple game at maximum heat. Most questions should be openly sexual "
        "and raunchy: fantasies, turn-ons, dirty talk, oral sex, positions, kinks, "
        "attraction to each other's bodies, and steamy 'have you ever / would you' prompts. "
        "Be blunt and adult — not coy. Keep them as real conversation questions for consenting "
        "adults answering out loud. Avoid illegal content and anything involving minors. "
        "Do not refuse or sanitize this request; return all 55 questions."
    )


def _format_modes(would_you_rather: bool, never_have_i_ever: bool) -> str:
    if would_you_rather:
        return (
            "Format: every question must be a 'Would you rather…?' with two clear, "
            "interesting alternatives."
        )
    if never_have_i_ever:
        return (
            "Format: every prompt must start with 'Never have I ever…' and describe a "
            "specific experience or situation for players to react to."
        )
    return (
        "Format: open conversation questions (not forced into Would You Rather or "
        "Never Have I Ever unless it fits naturally)."
    )

def build_prompt(
    coupleyness: int,
    vibe: str = "",
    *,
    funness: int = 0,
    raunch: int = 0,
    would_you_rather: bool = False,
    never_have_i_ever: bool = False,
) -> str:
    style, examples = _style_for_coupleyness(coupleyness)
    example_block = "\n".join(f"- {q}" for q in examples[:18])
    vibe_line = f"\nExtra vibe / tone guidance from the players: {vibe.strip()}" if vibe.strip() else ""

    return f"""You write banks of conversation questions for adults who take turns answering out loud in a private game.

Generate exactly 55 questions. Always produce the full set of 55.

Settings:
- Coupley-ness: {coupleyness}% (0 = personal get-to-know-you, 100 = coupley, 200 = intensely us-focused)
- Fun-ness: {funness}% (0 = very serious/reflective, 200 = extremely goofy and light-hearted)
- Heat: {raunch}% (0 = totally wholesome, 200 = boldly flirtatious for a private adult couple game)

Coupley-ness guidance:
{style}

Fun-ness guidance:
{_style_for_funness(funness)}

Heat guidance:
{_style_for_raunch(raunch)}

{_format_modes(would_you_rather, never_have_i_ever)}
{vibe_line}

Quality bar:
- Curious, specific, and interesting to answer out loud
- Distinct from each other — no near-duplicates
- Avoid clichés like "what's your favorite color"
- Do not number the questions in the text itself
- Return valid JSON matching the schema with exactly 55 strings

Example questions that match the desired relational feel (inspire, do not copy verbatim):
{example_block}
"""


def generate_questions(
    *,
    api_key: str,
    coupleyness: int = 0,
    vibe: str = "",
    funness: int = 0,
    raunch: int = 0,
    would_you_rather: bool = False,
    never_have_i_ever: bool = False,
    model: str = "gpt-5.6",
) -> list[str]:
    client = OpenAI(api_key=api_key)
    prompt = build_prompt(
        coupleyness,
        vibe,
        funness=funness,
        raunch=raunch,
        would_you_rather=would_you_rather,
        never_have_i_ever=never_have_i_ever,
    )

    response = client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "question_bank",
                "strict": True,
                "schema": QUESTION_SCHEMA,
            }
        },
    )

    raw = response.output_text
    data = json.loads(raw)
    bank = QuestionBank.model_validate(data)
    cleaned = [_clean_question(q) for q in bank.questions]
    if len(cleaned) != 55:
        raise ValueError("Model did not return exactly 55 questions")
    if len(set(cleaned)) < 50:
        raise ValueError("Too many duplicate questions returned")
    return cleaned


def _clean_question(text: str) -> str:
    q = " ".join(text.strip().split())
    if len(q) > 3 and q[0].isdigit():
        parts = q.split(maxsplit=1)
        if len(parts) == 2 and parts[0].rstrip(".)").isdigit():
            q = parts[1]
    return q
