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
        min_length=50,
        max_length=50,
        description="Exactly 50 distinct questions.",
    )


QUESTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 50,
            "maxItems": 50,
        }
    },
    "required": ["questions"],
    "additionalProperties": False,
}


def _style_for_coupleyness(coupleyness: int) -> tuple[str, list[str]]:
    """Map 0–200 coupley-ness to prompt guidance and example questions."""
    value = max(0, min(200, int(coupleyness)))

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
        # 141–200: strongly coupley / intensified
        examples = COUPLE
        intensity = "warm and specific" if value <= 170 else "deeply intimate, playful, and emotionally rich"
        style = (
            f"Generate strongly couple-focused questions that feel {intensity}. "
            "Use 'you/me/us/we' where it fits. Push beyond surface romance into "
            "shared life, desire, support, future, and quirky togetherness. "
            "Do not make them clinical or therapy-worksheet bland."
        )

    return style, examples


def build_prompt(coupleyness: int, vibe: str = "") -> str:
    style, examples = _style_for_coupleyness(coupleyness)
    example_block = "\n".join(f"- {q}" for q in examples[:18])
    vibe_line = f"\nExtra vibe / tone guidance from the players: {vibe.strip()}" if vibe.strip() else ""

    return f"""You write banks of conversation questions for two people who take turns answering out loud.

Generate exactly 50 questions.
Coupley-ness setting: {coupleyness}% (0 = purely personal get-to-know-you, 100 = balanced coupley, 200 = intensely couple-focused).

Style target:
{style}
{vibe_line}

Quality bar:
- Curious, specific, and interesting to answer out loud
- Not yes/no; invite a real answer
- Distinct from each other — no near-duplicates
- Avoid clichés like "what's your favorite color"
- Do not number the questions in the text itself

Example questions that match the desired feel (inspire, do not copy verbatim):
{example_block}
"""


def generate_questions(
    *,
    api_key: str,
    coupleyness: int = 100,
    vibe: str = "",
    model: str = "gpt-5.6",
) -> list[str]:
    client = OpenAI(api_key=api_key)
    prompt = build_prompt(coupleyness, vibe)

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
    if len(cleaned) != 50:
        raise ValueError("Model did not return exactly 50 questions")
    if len(set(cleaned)) < 45:
        raise ValueError("Too many duplicate questions returned")
    return cleaned


def _clean_question(text: str) -> str:
    q = " ".join(text.strip().split())
    # Strip leading numbering like "12." or "12)"
    if len(q) > 3 and q[0].isdigit():
        parts = q.split(maxsplit=1)
        if len(parts) == 2 and parts[0].rstrip(".)").isdigit():
            q = parts[1]
    return q
