"""Load and query the built-in problem catalog."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from dsa_sensei.errors import ProblemNotFound, SenseiError
from dsa_sensei.models import Problem
from dsa_sensei.schema import DIFFICULTIES, TOPICS, SchemaError, parse_problem

_DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


@dataclass(frozen=True, slots=True)
class Catalog:
    problems: tuple[Problem, ...]
    by_id: dict[str, Problem]
    aliases: dict[str, str]

    def get(self, problem_id: str) -> Problem:
        key = problem_id.strip().lower()
        if key in self.by_id:
            return self.by_id[key]
        canonical = self.aliases.get(key)
        if canonical is not None:
            return self.by_id[canonical]
        pool = list(self.by_id) + list(self.aliases)
        matches = difflib.get_close_matches(key, pool, n=5, cutoff=0.55)
        suggestions: list[str] = []
        for match in matches:
            canonical_id = match if match in self.by_id else self.aliases[match]
            if canonical_id not in suggestions:
                suggestions.append(canonical_id)
            if len(suggestions) == 3:
                break
        raise ProblemNotFound(problem_id, suggestions)

    def list_problems(self, *, topic: str | None = None, difficulty: str | None = None) -> list[Problem]:
        chosen_topic = _normalize_topic(topic)
        chosen_difficulty = _normalize_difficulty(difficulty)
        selected = [
            problem
            for problem in self.problems
            if (chosen_topic is None or problem.topic == chosen_topic)
            and (chosen_difficulty is None or problem.difficulty == chosen_difficulty)
        ]
        return sorted(
            selected,
            key=lambda problem: (
                TOPICS.index(problem.topic),
                _DIFFICULTY_ORDER[problem.difficulty],
                problem.id,
            ),
        )


def build_catalog(raw_problems: list[dict[str, Any]]) -> Catalog:
    problems: list[Problem] = []
    by_id: dict[str, Problem] = {}
    aliases: dict[str, str] = {}
    for raw in raw_problems:
        problem = parse_problem(raw)
        if problem.id in by_id or problem.id in aliases:
            raise SchemaError(f"Duplicate problem id '{problem.id}'.")
        for alias in problem.aliases:
            if alias in by_id or alias in aliases:
                owner = by_id[alias].id if alias in by_id else aliases[alias]
                raise SchemaError(f"Alias '{alias}' on {problem.id} collides with {owner}.")
            aliases[alias] = problem.id
        by_id[problem.id] = problem
        problems.append(problem)
    return Catalog(problems=tuple(problems), by_id=by_id, aliases=aliases)


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    from dsa_sensei.problems import RAW_PROBLEMS

    return build_catalog(RAW_PROBLEMS)


def _normalize_topic(topic: str | None) -> str | None:
    if topic is None or not topic.strip():
        return None
    key = topic.strip().lower()
    if key not in TOPICS:
        known = ", ".join(TOPICS)
        raise SenseiError(f"Unknown topic {topic!r}. Known topics: {known}.")
    return key


def _normalize_difficulty(difficulty: str | None) -> str | None:
    if difficulty is None or not difficulty.strip():
        return None
    key = difficulty.strip().lower()
    if key not in DIFFICULTIES:
        raise SenseiError("Difficulty must be easy, medium, or hard.")
    return key
