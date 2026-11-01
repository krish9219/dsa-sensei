from __future__ import annotations

import pytest

from dsa_sensei.catalog import build_catalog, get_catalog
from dsa_sensei.problems import RAW_PROBLEMS
from dsa_sensei.schema import DIFFICULTIES, HINT_LEVELS, TOPICS, SchemaError, parse_problem


def test_catalog_matches_the_schema() -> None:
    catalog = get_catalog()
    assert 45 <= len(catalog.problems) <= 60
    topics = {problem.topic for problem in catalog.problems}
    assert topics == set(TOPICS)
    for topic in TOPICS:
        assert sum(problem.topic == topic for problem in catalog.problems) >= 3
    difficulties = {problem.difficulty for problem in catalog.problems}
    assert difficulties == set(DIFFICULTIES)
    assert sum(problem.difficulty == "hard" for problem in catalog.problems) >= 5
    assert sum(problem.difficulty == "easy" for problem in catalog.problems) >= 10
    ids = [problem.id for problem in catalog.problems]
    assert len(ids) == len(set(ids))
    for problem in catalog.problems:
        assert [hint.level for hint in problem.hints] == list(HINT_LEVELS)
        assert "leetcode" not in problem.prompt.casefold()
        assert "```" not in problem.prompt
        for hint in problem.hints:
            assert "```" not in hint.text
            assert "class Solution" not in hint.text
        assert problem.target_time in problem.acceptable_time
        public = problem.public_dict()
        assert "hints" not in public
        assert "target_time" not in public
        assert "target_space" not in public


def test_duplicate_ids_are_rejected() -> None:
    with pytest.raises(SchemaError, match="Duplicate"):
        build_catalog([RAW_PROBLEMS[0], RAW_PROBLEMS[0]])


def _valid() -> dict[str, object]:
    return {
        "id": "sample-problem",
        "title": "A Sample Problem",
        "topic": "arrays",
        "tags": ["array"],
        "difficulty": "easy",
        "prompt": "x" * 80,
        "examples": [{"input": "n = 1", "output": "1"}],
        "constraints": ["n >= 1"],
        "hints": [
            {"level": "nudge", "text": "n" * 40},
            {"level": "approach", "text": "a" * 40},
            {"level": "pseudocode", "text": "p" * 40},
        ],
        "patterns": ["scan"],
        "target_time": "O(n)",
        "target_space": "O(1)",
    }


def test_schema_rejects_malformed_records() -> None:
    missing = _valid()
    del missing["prompt"]
    with pytest.raises(SchemaError, match="missing"):
        parse_problem(missing)

    unknown = _valid()
    unknown["solution"] = "nope"
    with pytest.raises(SchemaError, match="unknown"):
        parse_problem(unknown)

    bad_level = _valid()
    hints = bad_level["hints"]
    assert isinstance(hints, list)
    hints[0] = {"level": "approach", "text": "n" * 40}
    with pytest.raises(SchemaError, match="nudge"):
        parse_problem(bad_level)

    short = _valid()
    short["prompt"] = "too short"
    with pytest.raises(SchemaError, match="prompt"):
        parse_problem(short)

    named = _valid()
    named["prompt"] = "This prompt mentions leetcode which is not allowed. " * 2
    with pytest.raises(SchemaError, match="original"):
        parse_problem(named)

    difficulty = _valid()
    difficulty["difficulty"] = "boss"
    with pytest.raises(SchemaError, match="difficulty"):
        parse_problem(difficulty)


def test_schema_rejects_more_bad_shapes() -> None:
    bad_id = _valid()
    bad_id["id"] = "Not A Slug"
    with pytest.raises(SchemaError, match="slug"):
        parse_problem(bad_id)

    dup_tags = _valid()
    dup_tags["tags"] = ["array", "array"]
    with pytest.raises(SchemaError, match="duplicates"):
        parse_problem(dup_tags)

    short_hint = _valid()
    hints = short_hint["hints"]
    assert isinstance(hints, list)
    hints[2] = {"level": "pseudocode", "text": "too short"}
    with pytest.raises(SchemaError, match="too short"):
        parse_problem(short_hint)

    bad_bound = _valid()
    bad_bound["target_time"] = "O(lots)"
    with pytest.raises(SchemaError, match="target_time"):
        parse_problem(bad_bound)

    bad_example = _valid()
    bad_example["examples"] = [{"input": "only input"}]
    with pytest.raises(SchemaError, match="input and output"):
        parse_problem(bad_example)

    echoed = _valid()
    echoed["aliases"] = ["sample-problem"]
    with pytest.raises(SchemaError, match="alias cannot"):
        parse_problem(echoed)

    colliding = _valid()
    first = RAW_PROBLEMS[0]
    aliases = first["aliases"]
    assert isinstance(aliases, list)
    colliding["aliases"] = [str(aliases[0])]
    with pytest.raises(SchemaError, match="collides"):
        build_catalog([first, colliding])


def test_schema_accepts_a_minimal_record() -> None:
    problem = parse_problem(_valid())
    assert problem.id == "sample-problem"
    assert problem.acceptable_time == ("O(n)",)
    assert problem.examples[0].explanation == ""
