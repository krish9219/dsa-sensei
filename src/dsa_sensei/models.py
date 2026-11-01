"""Catalog and scheduling records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Example:
    input: str
    output: str
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class Hint:
    level: str
    text: str


@dataclass(frozen=True, slots=True)
class Problem:
    id: str
    title: str
    topic: str
    tags: tuple[str, ...]
    difficulty: str
    prompt: str
    examples: tuple[Example, ...]
    constraints: tuple[str, ...]
    hints: tuple[Hint, ...]
    patterns: tuple[str, ...]
    target_time: str
    target_space: str
    aliases: tuple[str, ...] = ()
    acceptable_time: tuple[str, ...] = ()
    complexity_note: str = ""

    def public_dict(self) -> dict[str, object]:
        """Statement and metadata. Hints, patterns, aliases, and targets stay off this payload."""
        return {
            "id": self.id,
            "title": self.title,
            "topic": self.topic,
            "tags": list(self.tags),
            "difficulty": self.difficulty,
            "prompt": self.prompt,
            "examples": [
                {"input": item.input, "output": item.output, "explanation": item.explanation}
                for item in self.examples
            ],
            "constraints": list(self.constraints),
        }


@dataclass(frozen=True, slots=True)
class HintResult:
    problem_id: str
    title: str
    level: int
    level_name: str
    text: str
    levels_remaining: int
    source: str
    exhausted: bool = False
    patterns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "problem_id": self.problem_id,
            "title": self.title,
            "level": self.level,
            "level_name": self.level_name,
            "text": self.text,
            "levels_remaining": self.levels_remaining,
            "source": self.source,
            "exhausted": self.exhausted,
        }
        if self.patterns:
            payload["patterns"] = list(self.patterns)
        return payload


@dataclass(frozen=True, slots=True)
class Card:
    problem_id: str
    ease: float
    interval_days: int
    repetitions: int
    due_on: date
    last_quality: int | None
    last_reviewed_on: date | None

    def to_dict(self) -> dict[str, object]:
        return {
            "problem_id": self.problem_id,
            "ease": self.ease,
            "interval_days": self.interval_days,
            "repetitions": self.repetitions,
            "due_on": self.due_on.isoformat(),
            "last_quality": self.last_quality,
            "last_reviewed_on": (self.last_reviewed_on.isoformat() if self.last_reviewed_on else None),
        }


@dataclass(frozen=True, slots=True)
class Attempt:
    id: int
    problem_id: str
    reviewed_on: date
    reviewed_at: str
    quality: int
    hints_used: int
    notes: str


@dataclass(frozen=True, slots=True)
class AttemptResult:
    problem_id: str
    quality: int
    quality_label: str
    ease: float
    interval_days: int
    repetitions: int
    due_on: str
    hints_used: int
    lapsed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "problem_id": self.problem_id,
            "quality": self.quality,
            "quality_label": self.quality_label,
            "ease": self.ease,
            "interval_days": self.interval_days,
            "repetitions": self.repetitions,
            "due_on": self.due_on,
            "hints_used": self.hints_used,
            "lapsed": self.lapsed,
        }


@dataclass(frozen=True, slots=True)
class TopicProgress:
    topic: str
    total: int
    seen: int
    mastered: int
    due: int
    attempts: int
    average_quality: float | None

    def to_dict(self) -> dict[str, object]:
        return {
            "topic": self.topic,
            "total": self.total,
            "seen": self.seen,
            "mastered": self.mastered,
            "due": self.due,
            "attempts": self.attempts,
            "average_quality": self.average_quality,
        }


@dataclass(frozen=True, slots=True)
class ProgressReport:
    topics: tuple[TopicProgress, ...]
    total_problems: int
    seen: int
    mastered: int
    due: int
    attempts: int
    streak_days: int

    def to_dict(self) -> dict[str, object]:
        return {
            "topics": [topic.to_dict() for topic in self.topics],
            "total_problems": self.total_problems,
            "seen": self.seen,
            "mastered": self.mastered,
            "due": self.due,
            "attempts": self.attempts,
            "streak_days": self.streak_days,
        }


@dataclass(frozen=True, slots=True)
class PracticePick:
    reason: str
    problem: Problem | None
    due_on: str | None = None
    overdue_days: int = 0

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "reason": self.reason,
            "due_on": self.due_on,
            "overdue_days": self.overdue_days,
            "problem": None if self.problem is None else self.problem.public_dict(),
        }
        return payload
