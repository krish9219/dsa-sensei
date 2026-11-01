from __future__ import annotations

import sys
from pathlib import Path

import anyio
import pytest
from mcp import Client
from mcp.client.stdio import StdioServerParameters

from dsa_sensei.mcp_server import run, server


def _run(async_fn: object) -> None:
    anyio.run(async_fn)  # type: ignore[arg-type]


def test_registered_tools_cover_the_tutor_surface() -> None:
    names = {tool.name for tool in server._tool_manager.list_tools()}
    assert names == {
        "get_problem",
        "list_problems",
        "get_hint",
        "analyze_complexity",
        "record_attempt",
        "due_reviews",
        "progress",
    }


def test_tools_hide_solutions_and_record_reviews(tmp_path: Path) -> None:
    db = tmp_path / "agent.db"

    async def _scenario() -> None:
        async with Client(server) as client:
            problem = await client.call_tool("get_problem", {"problem_id": "two-sum"})
            assert problem.is_error is False
            text = problem.content[0].text
            assert "Pair With a Target Sum" in text
            assert "nudge" not in text
            assert "pseudocode" not in text

            listed = await client.call_tool("list_problems", {"topic": "graphs", "difficulty": "medium"})
            assert "count-islands" in listed.content[0].text

            hint = await client.call_tool("get_hint", {"problem_id": "stair-ways", "level": 1})
            assert hint.is_error is False
            assert "nudge" in hint.content[0].text

            estimate = await client.call_tool(
                "analyze_complexity",
                {
                    "code": "def f(n):\n    if n < 2:\n        return n\n    return f(n - 1) + f(n - 2)\n",
                    "problem_id": "climbing-stairs",
                },
            )
            assert "O(2^n)" in estimate.content[0].text

            broken = await client.call_tool("analyze_complexity", {"code": "def ("})
            assert broken.is_error is True
            assert "parse" in broken.content[0].text

            missing = await client.call_tool("get_problem", {"problem_id": "missing"})
            assert missing.is_error is True
            assert "Unknown problem" in missing.content[0].text

            logged = await client.call_tool(
                "record_attempt",
                {"problem_id": "stair-ways", "quality": 5, "hints_used": 1},
            )
            assert logged.is_error is False
            assert "2026-04-02" in logged.content[0].text
            reviews = await client.call_tool("due_reviews", {"on": "2026-04-02"})
            assert "stair-ways" in reviews.content[0].text
            stats = await client.call_tool("progress", {})
            assert stats.is_error is False
            assert "streak_days" in stats.content[0].text

    # The tools read the study log from the environment, which the autouse fixture set.
    # Point that log at this test's directory before the calls.
    import os

    os.environ["DSA_SENSEI_DB"] = str(db)
    _run(_scenario)


def test_run_uses_stdio(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    def fake_run(transport: str = "stdio") -> None:
        seen["transport"] = transport

    monkeypatch.setattr(server, "run", fake_run)
    run()
    assert seen["transport"] == "stdio"


def test_stdio_entrypoint_answers_a_tool_call(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "dsa_sensei", "mcp"],
        env={
            "PYTHONPATH": str(root / "src"),
            "DSA_SENSEI_DB": str(tmp_path / "stdio.db"),
            "DSA_SENSEI_TODAY": "2026-04-01",
        },
        cwd=root,
    )

    async def _scenario() -> None:
        async with Client(params) as client:
            result = await client.call_tool("get_hint", {"problem_id": "sorted-lookup", "level": 2})
            assert result.is_error is False
            assert "approach" in result.content[0].text
            assert "class Solution" not in result.content[0].text

    _run(_scenario)
