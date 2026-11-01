"""Terminal interface for dsa-sensei."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import TypeVar

import typer
from rich import box
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dsa_sensei import __version__, service
from dsa_sensei.clock import today
from dsa_sensei.errors import SenseiError
from dsa_sensei.llm import load_settings
from dsa_sensei.models import Problem
from dsa_sensei.schema import TOPICS

console = Console(highlight=False)
app = typer.Typer(
    name="dsa-sensei",
    help=(
        "Socratic DSA tutor for interview prep. Ask for a hint rung, check the "
        "complexity of your Python, and come back when a problem is due."
    ),
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode="rich",
)
F = TypeVar("F", bound=Callable[..., None])

_DIFFICULTY_STYLE = {"easy": "green", "medium": "yellow", "hard": "red"}


class Settings:
    def __init__(self, db: Path | None) -> None:
        self.db = db


def _guard(func: F) -> F:
    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> None:
        try:
            func(*args, **kwargs)
        except SenseiError as exc:
            console.print(Panel(escape(str(exc)), title="dsa-sensei", border_style="red"))
            raise typer.Exit(code=2) from exc

    wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


def _state(ctx: typer.Context) -> Settings:
    state = ctx.obj
    if isinstance(state, Settings):
        return state
    return Settings(db=None)


def _version(value: bool) -> None:
    if value:
        console.print(__version__, highlight=False)
        raise typer.Exit()


@app.callback()
def root(
    ctx: typer.Context,
    db: Path | None = typer.Option(
        None,
        "--db",
        help="SQLite study log. Overrides DSA_SENSEI_DB.",
    ),
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=_version,
        is_eager=True,
        help="Print the version and exit.",
    ),
) -> None:
    """Study with hints instead of solutions."""
    ctx.obj = Settings(db=db)


@app.command("list")
@_guard
def list_problems(
    ctx: typer.Context,
    topic: str | None = typer.Option(None, "--topic", "-t", help="Filter by topic."),
    difficulty: str | None = typer.Option(None, "--difficulty", "-d", help="easy, medium, or hard."),
) -> None:
    """List the built-in catalog."""
    problems = service.list_problems(topic=topic, difficulty=difficulty)
    store = service.open_store(_state(ctx).db, write=False)
    cards = {} if store is None else {card.problem_id: card for card in store.all_cards()}
    table = Table(title=f"{len(problems)} problems", box=box.SIMPLE_HEAVY, header_style="bold")
    table.add_column("Id")
    table.add_column("Title")
    table.add_column("Topic")
    table.add_column("Level")
    table.add_column("Status")
    day = today()
    for problem in problems:
        card = cards.get(problem.id)
        if card is None:
            status = "new"
        elif card.due_on <= day:
            status = "due"
        else:
            status = f"due {card.due_on.isoformat()}"
        table.add_row(
            problem.id,
            problem.title,
            problem.topic,
            Text(problem.difficulty, style=_DIFFICULTY_STYLE[problem.difficulty]),
            status,
        )
    console.print(table)


@app.command("topics")
@_guard
def topics() -> None:
    """List catalog topics."""
    for topic in TOPICS:
        console.print(topic, markup=False)


@app.command("show")
@_guard
def show(problem_id: str = typer.Argument(..., help="Problem id or alias.")) -> None:
    """Show a problem statement. Hints stay behind the hint command."""
    _print_problem(service.get_problem(problem_id))
    console.print("[dim]Next: dsa-sensei hint " + escape(problem_id) + "[/dim]")


@app.command("hint")
@_guard
def hint(
    ctx: typer.Context,
    problem_id: str | None = typer.Argument(None, help="Problem id or alias."),
    level: int | None = typer.Option(
        None,
        "--level",
        "-l",
        min=1,
        max=3,
        help="1 nudge, 2 approach, 3 pseudocode. Omit to reveal the next rung.",
    ),
    custom: str | None = typer.Option(
        None,
        "--custom",
        help="Ask about a problem that is not in the catalog. Requires the LLM env vars.",
    ),
) -> None:
    """Reveal a single hint rung. A full solution is not available."""
    result = service.get_hint(
        problem_id,
        level,
        custom_prompt=custom,
        db=_state(ctx).db,
    )
    title = f"{result.level_name}  {result.level}/3"
    if result.source == "llm":
        title += "  · custom"
    console.print(Panel(escape(result.text), title=title, border_style="cyan"))
    if result.levels_remaining:
        console.print(
            f"[dim]{result.levels_remaining} rung(s) left. "
            "The next one is more specific, and still not a solution.[/dim]"
        )


@app.command("analyze")
@_guard
def analyze(
    source: str = typer.Argument(..., help="Path to a Python file, or '-' for stdin."),
    problem: str | None = typer.Option(
        None,
        "--problem",
        "-p",
        help="Compare the estimate with this catalog problem.",
    ),
) -> None:
    """Estimate the complexity of Python code. These are heuristics."""
    code = _read_source(source)
    report = service.analyze_code(code, problem)
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_row("Time", str(report["time"]))
    table.add_row("Space", str(report["space"]))
    table.add_row("Confidence", str(report["confidence"]))
    table.add_row("Function", str(report["primary_function"]))
    console.print(Panel(table, title="Complexity estimate", border_style="magenta"))
    warnings = report["warnings"]
    notes = report["notes"]
    if isinstance(warnings, list) and warnings:
        console.print("[bold]Watch-outs[/bold]")
        for item in warnings:
            console.print(f"  • {escape(str(item))}")
    if isinstance(notes, list) and notes:
        console.print("[bold]Notes[/bold]")
        for item in notes:
            console.print(f"  • {escape(str(item))}")
    comparison = report["comparison"]
    if isinstance(comparison, str):
        console.print(Panel(escape(comparison), title="Compared with the catalog", border_style="blue"))
    console.print(f"[dim]{escape(str(report['disclaimer']))}[/dim]")


@app.command("attempt")
@_guard
def attempt(
    ctx: typer.Context,
    problem_id: str = typer.Argument(..., help="Problem id or alias."),
    quality: str = typer.Option(
        ...,
        "--quality",
        "-q",
        help="0-5, or blackout, again, fuzzy, hard, good, easy, perfect.",
    ),
    hints: int = typer.Option(0, "--hints", min=0, max=3, help="How many hint rungs you used."),
    notes: str = typer.Option("", "--notes", "-n", help="Optional note stored with the attempt."),
) -> None:
    """Log how the recall felt and schedule the next review."""
    result = service.record_attempt(
        problem_id,
        quality,
        hints_used=hints,
        notes=notes,
        db=_state(ctx).db,
    )
    tone = "green" if not result.lapsed else "yellow"
    body = (
        f"Grade {result.quality} ({result.quality_label}).\n"
        f"Next review: {result.due_on}  ·  interval {result.interval_days} day(s)\n"
        f"Ease {result.ease}  ·  repetitions {result.repetitions}"
    )
    console.print(Panel(body, title=result.problem_id, border_style=tone))


@app.command("review")
@_guard
def review(
    ctx: typer.Context,
    on: str | None = typer.Option(None, "--on", help="ISO date to treat as today."),
) -> None:
    """Show problems due on a given day."""
    reviews = service.due_reviews(on=on, db=_state(ctx).db)
    if not reviews:
        console.print(
            "Nothing is due. Study something new with [bold]dsa-sensei practice[/bold], "
            "then log it with [bold]dsa-sensei attempt[/bold]."
        )
        return
    table = Table(title=f"{len(reviews)} due", box=box.SIMPLE_HEAVY)
    table.add_column("Id")
    table.add_column("Title")
    table.add_column("Topic")
    table.add_column("Due")
    table.add_column("Overdue")
    for item in reviews:
        table.add_row(
            str(item["problem_id"]),
            str(item["title"] or ""),
            str(item["topic"] or ""),
            str(item["due_on"]),
            str(item["overdue_days"]),
        )
    console.print(table)


@app.command("progress")
@_guard
def progress(ctx: typer.Context) -> None:
    """Show attempts, mastery, and streak by topic."""
    report = service.progress_report(db=_state(ctx).db)
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold")
    for column in ("Topic", "Seen", "Mastered", "Due", "Attempts", "Avg grade"):
        table.add_column(column)
    for topic in report.topics:
        average = "—" if topic.average_quality is None else f"{topic.average_quality:.2f}"
        table.add_row(
            topic.topic,
            f"{topic.seen}/{topic.total}",
            str(topic.mastered),
            str(topic.due),
            str(topic.attempts),
            average,
        )
    console.print(table)
    console.print(
        f"Seen {report.seen}/{report.total_problems}  ·  "
        f"mastered {report.mastered}  ·  due {report.due}  ·  "
        f"attempts {report.attempts}  ·  streak {report.streak_days} day(s)"
    )
    console.print("[dim]Mastered means at least two successful reviews and an interval of 6 days.[/dim]")


@app.command("practice")
@_guard
def practice(
    ctx: typer.Context,
    topic: str | None = typer.Option(None, "--topic", "-t"),
    difficulty: str | None = typer.Option(None, "--difficulty", "-d"),
) -> None:
    """Pick a due review, or a new problem if nothing is due."""
    pick = service.practice(topic=topic, difficulty=difficulty, db=_state(ctx).db)
    problem = pick.problem
    if problem is None:
        if pick.reason == "done":
            console.print("Nothing in this slice is due, and you have already seen all of it.")
            return
        console.print("No problems match that filter.")
        raise typer.Exit(code=2)
    label = "Due for review" if pick.reason == "due" else "New problem"
    if pick.overdue_days:
        label += f" · {pick.overdue_days} day(s) overdue"
    console.print(f"[bold]{label}[/bold]")
    _print_problem(problem)
    console.print(
        f"[dim]Hint: dsa-sensei hint {problem.id}\n"
        f"Log it: dsa-sensei attempt {problem.id} --quality good[/dim]"
    )


@app.command("reset")
@_guard
def reset(
    ctx: typer.Context,
    yes: bool = typer.Option(False, "--yes", help="Confirm deleting the local study log."),
) -> None:
    """Delete local attempts, schedules, and hint progress."""
    if not yes:
        raise SenseiError("Refusing to delete the study log without --yes.")
    removed = service.reset_progress(_state(ctx).db)
    if removed:
        console.print("Study log deleted.")
    else:
        console.print("There was no study log to delete.")


@app.command("config")
@_guard
def config(ctx: typer.Context) -> None:
    """Show the study-log path, catalog size, and whether custom hints are enabled."""
    path = service.resolve_db(_state(ctx).db)
    try:
        llm = load_settings()
    except SenseiError as exc:
        llm_line = str(exc)
    else:
        llm_line = "off" if llm is None else f"on · model {llm.model}"
    console.print(f"Database: {path}")
    console.print(f"Catalog:  {len(service.list_problems())} problems")
    console.print(f"Custom hints: {llm_line}", markup=False)


@app.command("mcp")
def mcp() -> None:
    """Run the MCP server on stdin/stdout for Claude Code, Cursor, and other agents."""
    from dsa_sensei.mcp_server import run

    run()


def _print_problem(problem: Problem) -> None:
    header = Text()
    header.append(problem.title, style="bold")
    header.append(f"  {problem.id}", style="dim")
    console.print(
        Panel(
            header,
            subtitle=f"{problem.topic} · {problem.difficulty}",
            border_style=_DIFFICULTY_STYLE[problem.difficulty],
        )
    )
    console.print(escape(problem.prompt))
    console.print()
    for index, example in enumerate(problem.examples, start=1):
        block = f"Input: {example.input}\nOutput: {example.output}"
        if example.explanation:
            block += f"\n{example.explanation}"
        console.print(Panel(escape(block), title=f"Example {index}", border_style="dim"))
    if problem.constraints:
        console.print("[bold]Constraints[/bold]")
        for item in problem.constraints:
            console.print(f"  • {escape(item)}")
    if problem.patterns:
        console.print("[bold]Patterns:[/bold] " + escape(", ".join(problem.patterns)))


def _read_source(source: str) -> str:
    if source == "-":
        return _stdin()
    path = Path(source)
    if not path.is_file():
        raise SenseiError(f"No Python file at {source}.")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SenseiError(f"Could not read {source}: {exc}") from exc


def _stdin() -> str:
    import sys

    return sys.stdin.read()


def main_entry() -> None:
    app()


# The console script calls this name.
def main() -> None:
    main_entry()
