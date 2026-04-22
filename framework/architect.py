"""Translates a natural language request into a structured AppBlueprint."""

from __future__ import annotations
import json
import os
import anthropic
from .models import AppBlueprint
from .prompts import ARCHITECT_SYSTEM


async def design_app(request: str) -> AppBlueprint:
    """Call Claude to interpret `request` and return an AppBlueprint."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=ARCHITECT_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Design a Yggdrasil app for the following request:\n\n{request}\n\n"
                    "Return only the JSON blueprint."
                ),
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return AppBlueprint.model_validate(data)
