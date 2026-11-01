"""Validate built-in problem records.

The catalog is authored as Python data. Every record still has to pass this
schema before it can be served, and the test suite runs the same check.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, cast

from dsa_sensei.errors import SenseiError
from dsa_sensei.models import Example, Hint, Problem

TOPICS: tuple[str, ...] = (
    "arrays",
    "two-pointers",
    "sliding-window",
    "hashing",
    "binary-search",
    "linked-lists",
    "stacks",
    "trees",
    "graphs",
    "dynamic-programming",
)
DIFFICULTIES: frozenset[str] = frozenset({"easy", "medium", "hard"})
HINT_LEVELS: tuple[str, ...] = ("nudge", "approach", "pseudocode")
ALLOWED_COMPLEXITY: frozenset[str] = frozenset(
    {
        "O(1)",
        "O(log n)",
        "O(n)",
        "O(n + e)",
        "O(n log n)",
        "O(n^2)",
        "O(n^3)",
        "O(2^n)",
    }
)
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_REQUIRED = (
    "id",
    "title",
    "topic",
    "tags",
    "difficulty",
    "prompt",
    "examples",
    "constraints",
    "hints",
    "patterns",
    "target_time",
    "target_space",
)
_OPTIONAL = frozenset({"aliases", "acceptable_time", "complexity_note"})


class SchemaError(SenseiError):
    """A built-in problem record does not match the catalog schema."""


def parse_problem(data: Mapping[str, Any]) -> Problem:
    if not isinstance(data, Mapping):
        raise SchemaError("A problem must be an object.")
    raw = cast(dict[str, Any], dict(data))
    missing = [key for key in _REQUIRED if key not in raw]
    if missing:
        raise SchemaError(f"Problem is missing fields: {', '.join(missing)}.")
    unknown = sorted(set(raw) - set(_REQUIRED) - _OPTIONAL)
    if unknown:
        raise SchemaError(f"Problem has unknown fields: {', '.join(unknown)}.")

    problem_id = _slug(raw["id"], "id")
    title = _text(raw["title"], "title", minimum=8, maximum=80)
    topic = _text(raw["topic"], "topic", minimum=1, maximum=40)
    if topic not in TOPICS:
        raise SchemaError(f"{problem_id}: unknown topic {topic!r}.")
    difficulty = _text(raw["difficulty"], "difficulty", minimum=1, maximum=20)
    if difficulty not in DIFFICULTIES:
        raise SchemaError(f"{problem_id}: difficulty must be easy, medium, or hard.")
    prompt = _text(raw["prompt"], "prompt", minimum=80, maximum=2000)
    if "leetcode" in prompt.casefold() or "leetcode" in title.casefold():
        raise SchemaError(f"{problem_id}: write an original prompt; do not name other platforms.")

    tags = _str_list(raw["tags"], "tags", problem_id, minimum=1)
    for tag in tags:
        if not _SLUG.fullmatch(tag):
            raise SchemaError(f"{problem_id}: tag {tag!r} is not a slug.")
    patterns = _str_list(raw["patterns"], "patterns", problem_id, minimum=1)
    constraints = _str_list(raw["constraints"], "constraints", problem_id, minimum=1)
    aliases = _str_list(raw.get("aliases", []), "aliases", problem_id, minimum=0)
    for alias in aliases:
        if not _SLUG.fullmatch(alias):
            raise SchemaError(f"{problem_id}: alias {alias!r} is not a slug.")
        if alias == problem_id:
            raise SchemaError(f"{problem_id}: an alias cannot repeat the id.")

    examples = _examples(raw["examples"], problem_id)
    hints = _hints(raw["hints"], problem_id)
    target_time = _complexity(raw["target_time"], problem_id, "target_time")
    target_space = _complexity(raw["target_space"], problem_id, "target_space")
    acceptable = _acceptable(raw.get("acceptable_time"), target_time, problem_id)
    note = raw.get("complexity_note", "")
    if not isinstance(note, str):
        raise SchemaError(f"{problem_id}: complexity_note must be a string.")
    if len(note) > 300:
        raise SchemaError(f"{problem_id}: complexity_note is too long.")

    return Problem(
        id=problem_id,
        title=title,
        topic=topic,
        tags=tuple(tags),
        difficulty=difficulty,
        prompt=prompt,
        examples=tuple(examples),
        constraints=tuple(constraints),
        hints=tuple(hints),
        patterns=tuple(patterns),
        target_time=target_time,
        target_space=target_space,
        aliases=tuple(aliases),
        acceptable_time=tuple(acceptable),
        complexity_note=note.strip(),
    )


def _slug(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise SchemaError(f"{field} must be a lowercase slug, got {value!r}.")
    return value


def _text(value: object, field: str, *, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        raise SchemaError(f"{field} must be a string.")
    text = value.strip()
    if not minimum <= len(text) <= maximum:
        raise SchemaError(f"{field} must be between {minimum} and {maximum} characters.")
    return text


def _str_list(value: object, field: str, problem_id: str, *, minimum: int) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise SchemaError(f"{problem_id}: {field} must be a list of non-empty strings.")
    items = [item.strip() for item in value]
    if len(items) < minimum:
        raise SchemaError(f"{problem_id}: {field} needs at least {minimum} entries.")
    if len(items) != len(set(items)):
        raise SchemaError(f"{problem_id}: {field} contains duplicates.")
    return items


def _examples(value: object, problem_id: str) -> list[Example]:
    if not isinstance(value, list) or not 1 <= len(value) <= 4:
        raise SchemaError(f"{problem_id}: provide 1 to 4 examples.")
    examples: list[Example] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise SchemaError(f"{problem_id}: each example must be an object.")
        allowed = {"input", "output", "explanation"}
        unknown = set(item) - allowed
        if unknown or "input" not in item or "output" not in item:
            raise SchemaError(f"{problem_id}: examples need input and output only.")
        source = _text(item["input"], "example.input", minimum=1, maximum=500)
        output = _text(item["output"], "example.output", minimum=1, maximum=500)
        explanation = item.get("explanation", "")
        if not isinstance(explanation, str) or len(explanation) > 400:
            raise SchemaError(f"{problem_id}: example explanation must be a short string.")
        examples.append(Example(input=source, output=output, explanation=explanation.strip()))
    return examples


def _hints(value: object, problem_id: str) -> list[Hint]:
    if not isinstance(value, list) or len(value) != 3:
        raise SchemaError(f"{problem_id}: hints must be exactly three rungs.")
    hints: list[Hint] = []
    for expected, item in zip(HINT_LEVELS, value, strict=True):
        if not isinstance(item, Mapping):
            raise SchemaError(f"{problem_id}: each hint must be an object.")
        if set(item) != {"level", "text"}:
            raise SchemaError(f"{problem_id}: a hint has level and text, nothing else.")
        level = item["level"]
        text = item["text"]
        if level != expected:
            raise SchemaError(
                f"{problem_id}: hint rung {len(hints) + 1} must be {expected!r}, got {level!r}."
            )
        if not isinstance(text, str) or len(text.strip()) < 40:
            raise SchemaError(f"{problem_id}: the {expected} hint is too short.")
        if "```" in text or "class Solution" in text:
            raise SchemaError(f"{problem_id}: hints stay prose and pseudocode, not fenced code.")
        hints.append(Hint(level=expected, text=text.strip()))
    texts = [hint.text for hint in hints]
    if len(set(texts)) != 3:
        raise SchemaError(f"{problem_id}: hint rungs must not repeat each other.")
    return hints


def _complexity(value: object, problem_id: str, field: str) -> str:
    if not isinstance(value, str) or value not in ALLOWED_COMPLEXITY:
        raise SchemaError(f"{problem_id}: {field} must be one of {', '.join(sorted(ALLOWED_COMPLEXITY))}.")
    return value


def _acceptable(value: object, target_time: str, problem_id: str) -> list[str]:
    if value is None:
        return [target_time]
    if not isinstance(value, list) or not value:
        raise SchemaError(f"{problem_id}: acceptable_time must be a non-empty list.")
    bounds: list[str] = []
    for item in value:
        bounds.append(_complexity(item, problem_id, "acceptable_time"))
    if target_time not in bounds:
        bounds.insert(0, target_time)
    if len(bounds) != len(set(bounds)):
        raise SchemaError(f"{problem_id}: acceptable_time contains duplicates.")
    return bounds
