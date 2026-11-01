from __future__ import annotations

import pytest

from dsa_sensei.catalog import get_catalog
from dsa_sensei.errors import ProblemNotFound, SenseiError


def test_alias_resolves_to_the_canonical_problem() -> None:
    problem = get_catalog().get("two-sum")
    assert problem.id == "pair-with-target"
    assert get_catalog().get("  STAIR-WAYS ").id == "stair-ways"


def test_unknown_problem_suggests_a_near_id() -> None:
    with pytest.raises(ProblemNotFound, match="stair-ways") as caught:
        get_catalog().get("stair-way")
    assert "stair-ways" in caught.value.suggestions


def test_filters_and_unknown_topic() -> None:
    hard_graphs = get_catalog().list_problems(topic="graphs", difficulty="hard")
    assert hard_graphs == []
    graphs = get_catalog().list_problems(topic="Graphs")
    assert graphs
    assert {problem.topic for problem in graphs} == {"graphs"}
    with pytest.raises(SenseiError, match="Unknown topic"):
        get_catalog().list_problems(topic="sorting")
    with pytest.raises(SenseiError, match="Difficulty"):
        get_catalog().list_problems(difficulty="trivial")
