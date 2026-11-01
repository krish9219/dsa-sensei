from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from dsa_sensei import __version__
from dsa_sensei.cli import app

runner = CliRunner()


def test_version_list_show_and_hint(tmp_path: Path) -> None:
    db = tmp_path / "cli.db"
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert __version__ in version.stdout

    listed = runner.invoke(app, ["--db", str(db), "list", "--topic", "stacks"])
    assert listed.exit_code == 0
    assert "balanced-brackets" in listed.stdout
    assert "histogram-largest" in listed.stdout
    assert not db.exists()

    shown = runner.invoke(app, ["show", "kadane"])
    assert shown.exit_code == 0
    assert "Best Contiguous Sum" in shown.stdout
    assert "seen[x]" not in shown.stdout

    hinted = runner.invoke(app, ["--db", str(db), "hint", "kadane"])
    assert hinted.exit_code == 0
    assert "nudge" in hinted.stdout
    assert db.exists()
    missing = runner.invoke(app, ["show", "nope"])
    assert missing.exit_code == 2
    assert "Unknown problem" in missing.stdout


def test_analyze_attempt_review_and_progress(tmp_path: Path) -> None:
    db = tmp_path / "cli.db"
    source = tmp_path / "solution.py"
    source.write_text(
        "def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n",
        encoding="utf-8",
    )
    analyzed = runner.invoke(
        app,
        ["analyze", str(source), "--problem", "stair-ways"],
    )
    assert analyzed.exit_code == 0
    assert "O(2^n)" in analyzed.stdout
    assert "slower" in analyzed.stdout

    stdin = runner.invoke(app, ["analyze", "-"], input="def f(nums):\n    return sorted(nums)\n")
    assert stdin.exit_code == 0
    assert "O(n log n)" in stdin.stdout

    broken = runner.invoke(app, ["analyze", "-"], input="def (\n")
    assert broken.exit_code == 2
    assert "parse" in broken.stdout

    logged = runner.invoke(
        app,
        ["--db", str(db), "attempt", "climbing-stairs", "--quality", "good", "--hints", "1"],
    )
    assert logged.exit_code == 0
    assert "2026-04-02" in logged.stdout

    quiet = runner.invoke(app, ["--db", str(db), "review"])
    assert quiet.exit_code == 0
    assert "Nothing is due" in quiet.stdout
    due = runner.invoke(app, ["--db", str(db), "review", "--on", "2026-04-02"])
    assert due.exit_code == 0
    assert "stair-ways" in due.stdout

    stats = runner.invoke(app, ["--db", str(db), "progress"])
    assert stats.exit_code == 0
    assert "dynamic-programming" in stats.stdout
    assert "streak 1" in stats.stdout


def test_schedule_status_edges_and_entrypoint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "cli.db"
    runner.invoke(app, ["--db", str(db), "attempt", "stair-ways", "--quality", "5"])
    listed = runner.invoke(app, ["--db", str(db), "list", "--topic", "dynamic-programming"])
    assert listed.exit_code == 0
    assert "due 2026-04-02" in listed.stdout
    monkeypatch.setenv("DSA_SENSEI_TODAY", "2026-04-03")
    overdue = runner.invoke(app, ["--db", str(db), "practice", "--topic", "dynamic-programming"])
    assert overdue.exit_code == 0
    assert "overdue" in overdue.stdout
    runner.invoke(app, ["--db", str(db), "attempt", "count-islands", "--quality", "good"])
    runner.invoke(app, ["--db", str(db), "attempt", "course-schedule-ii", "--quality", "good"])
    runner.invoke(app, ["--db", str(db), "attempt", "clone-graph", "--quality", "good"])
    finished = runner.invoke(app, ["--db", str(db), "practice", "--topic", "graphs"])
    assert finished.exit_code == 0
    assert "already seen" in finished.stdout

    missing = runner.invoke(app, ["analyze", str(tmp_path / "nope.py")])
    assert missing.exit_code == 2
    fresh = runner.invoke(app, ["--db", str(tmp_path / "empty.db"), "reset", "--yes"])
    assert fresh.exit_code == 0
    assert "no study log" in fresh.stdout
    monkeypatch.setenv("DSA_SENSEI_LLM_MODEL", "only-model")
    configured = runner.invoke(app, ["--db", str(db), "config"])
    assert configured.exit_code == 0
    assert "both" in configured.stdout

    from dsa_sensei import mcp_server

    monkeypatch.setattr(mcp_server, "run", lambda: None)
    served = runner.invoke(app, ["mcp"])
    assert served.exit_code == 0

    from dsa_sensei.cli import main

    monkeypatch.setattr("sys.argv", ["dsa-sensei", "--version"])
    with pytest.raises(SystemExit):
        main()


def test_show_hides_patterns_until_the_approach(tmp_path: Path) -> None:
    shown = runner.invoke(app, ["show", "kadane"])
    assert shown.exit_code == 0
    assert "best sum ending here" not in shown.stdout
    hinted = runner.invoke(app, ["--db", str(tmp_path / "h.db"), "hint", "kadane", "--level", "2"])
    assert hinted.exit_code == 0
    assert "best sum ending here" in hinted.stdout
    source = tmp_path / "latin1.py"
    source.write_bytes(b"def f():\n    return '\xff'\n")
    rejected = runner.invoke(app, ["analyze", str(source)])
    assert rejected.exit_code == 2
    assert "UTF-8" in rejected.stdout


def test_practice_config_reset_and_topics(tmp_path: Path) -> None:
    db = tmp_path / "cli.db"
    started = runner.invoke(app, ["--db", str(db), "practice", "--difficulty", "easy"])
    assert started.exit_code == 0
    assert "dominating-value" in started.stdout
    topics = runner.invoke(app, ["topics"])
    assert topics.exit_code == 0
    assert "binary-search" in topics.stdout
    configured = runner.invoke(app, ["--db", str(db), "config"])
    assert configured.exit_code == 0
    assert "Custom hints: off" in configured.stdout
    assert str(db) in configured.stdout
    refused = runner.invoke(app, ["--db", str(db), "reset"])
    assert refused.exit_code == 2
    wiped = runner.invoke(app, ["--db", str(db), "reset", "--yes"])
    assert wiped.exit_code == 0
    empty = runner.invoke(app, ["practice", "--topic", "not-a-topic"])
    assert empty.exit_code == 2
