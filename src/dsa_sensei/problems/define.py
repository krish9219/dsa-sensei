"""Authoring helper for built-in problems. Records are still schema-checked."""

from __future__ import annotations

from typing import Any


def problem(
    *,
    id: str,
    title: str,
    topic: str,
    tags: list[str],
    difficulty: str,
    prompt: str,
    examples: list[dict[str, str]],
    constraints: list[str],
    nudge: str,
    approach: str,
    pseudocode: str,
    patterns: list[str],
    target_time: str,
    target_space: str,
    aliases: list[str] | None = None,
    acceptable_time: list[str] | None = None,
    complexity_note: str = "",
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": id,
        "title": title,
        "topic": topic,
        "tags": tags,
        "difficulty": difficulty,
        "prompt": prompt,
        "examples": examples,
        "constraints": constraints,
        "hints": [
            {"level": "nudge", "text": nudge},
            {"level": "approach", "text": approach},
            {"level": "pseudocode", "text": pseudocode},
        ],
        "patterns": patterns,
        "target_time": target_time,
        "target_space": target_space,
    }
    if aliases:
        record["aliases"] = aliases
    if acceptable_time:
        record["acceptable_time"] = acceptable_time
    if complexity_note:
        record["complexity_note"] = complexity_note
    return record
