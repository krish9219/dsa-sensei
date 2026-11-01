"""MCP server so coding agents can use dsa-sensei as a tutor.

The official Python SDK exposes this style of server as ``MCPServer``
(the successor of FastMCP). Tools never return a full solution.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from dsa_sensei import __version__, service
from dsa_sensei.errors import SenseiError

T = TypeVar("T")

INSTRUCTIONS = (
    "dsa-sensei is a Socratic DSA tutor. Use get_problem and get_hint. "
    "Reveal one hint rung at a time and do not write a full solution while "
    "tutoring with this server. After the student tries, call analyze_complexity "
    "on their Python and record_attempt with a 0-5 recall grade. "
    "due_reviews and progress read the local spaced-repetition log."
)

server = MCPServer(
    name="dsa-sensei",
    instructions=INSTRUCTIONS,
    version=__version__,
    log_level="WARNING",
)


def _guard(func: Callable[[], T]) -> T:
    try:
        return func()
    except SenseiError as exc:
        raise ToolError(str(exc)) from exc


@server.tool()
def get_problem(problem_id: str) -> dict[str, object]:
    """Return one built-in problem statement, examples, and tags. Does not include hints or a solution."""
    return _guard(lambda: service.get_problem(problem_id).public_dict())


@server.tool()
def list_problems(topic: str = "", difficulty: str = "") -> dict[str, object]:
    """List built-in problems. Filter with a topic and/or difficulty (easy, medium, hard)."""

    def _run() -> dict[str, object]:
        problems = service.list_problems(topic=topic or None, difficulty=difficulty or None)
        return {"problems": [problem.public_dict() for problem in problems]}

    return _guard(_run)


@server.tool()
def get_hint(problem_id: str = "", level: int = 0, custom_prompt: str = "") -> dict[str, object]:
    """Return one hint rung: 1 nudge, 2 approach, 3 pseudocode.

    Pass level 0 for the next unrevealed rung. This never returns a full solution.
    """

    def _run() -> dict[str, object]:
        result = service.get_hint(
            problem_id or None,
            None if level == 0 else level,
            custom_prompt=custom_prompt or None,
        )
        return result.to_dict()

    return _guard(_run)


@server.tool()
def analyze_complexity(code: str, problem_id: str = "") -> dict[str, object]:
    """Estimate time and space of Python with AST heuristics.

    Pass a catalog id to compare the estimate with that problem's known bound.
    """
    return _guard(lambda: service.analyze_code(code, problem_id or None))


@server.tool()
def record_attempt(
    problem_id: str,
    quality: int,
    hints_used: int = 0,
    notes: str = "",
) -> dict[str, object]:
    """Log a recall grade from 0 (blackout) to 5 (perfect) and update the SM-2 review schedule."""
    return _guard(
        lambda: service.record_attempt(
            problem_id,
            quality,
            hints_used=hints_used,
            notes=notes,
        ).to_dict()
    )


@server.tool()
def due_reviews(on: str = "") -> dict[str, object]:
    """List catalog problems due on an ISO date (YYYY-MM-DD). Omit the date to use today."""
    return _guard(lambda: {"reviews": service.due_reviews(on=on or None)})


@server.tool()
def progress() -> dict[str, object]:
    """Return spaced-repetition progress grouped by topic, including streak and mastery counts."""
    return _guard(lambda: service.progress_report().to_dict())


def run() -> None:
    """Serve the tutor over stdin and stdout."""
    server.run(transport="stdio")
