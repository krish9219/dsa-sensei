from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from dsa_sensei.errors import SenseiError
from dsa_sensei.paths import default_db_path
from dsa_sensei.service import (
    due_reviews,
    get_hint,
    practice,
    progress_report,
    record_attempt,
    reset_progress,
)
from dsa_sensei.store import Store


def test_empty_log_has_nothing_due(tmp_path: Path) -> None:
    assert due_reviews(db=tmp_path / "missing.db") == []
    report = progress_report(db=tmp_path / "missing.db")
    assert report.attempts == 0
    assert report.seen == 0
    assert report.streak_days == 0
    assert all(topic.seen == 0 for topic in report.topics)


def test_attempt_schedules_the_next_day_and_not_today(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    day = date(2026, 4, 1)
    result = record_attempt("two-sum", "good", db=db, on=day)
    assert result.problem_id == "pair-with-target"
    assert result.due_on == "2026-04-02"
    assert result.lapsed is False
    assert due_reviews(db=db, on=day) == []
    due = due_reviews(db=db, on="2026-04-02")
    assert [item["problem_id"] for item in due] == ["pair-with-target"]
    overdue = due_reviews(db=db, on="2026-04-05")
    assert overdue[0]["overdue_days"] == 3


def test_lapse_and_mastery_and_streak(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    record_attempt("stair-ways", 5, db=db, on=date(2026, 4, 1))
    second = record_attempt("stair-ways", "good", hints_used=1, notes="ok", db=db, on=date(2026, 4, 2))
    assert second.repetitions == 2
    assert second.interval_days == 6
    report = progress_report(db=db, on=date(2026, 4, 2))
    assert report.mastered == 1
    assert report.streak_days == 2
    dynamic = next(topic for topic in report.topics if topic.topic == "dynamic-programming")
    assert dynamic.seen == 1
    assert dynamic.average_quality == pytest.approx(4.5)

    record_attempt("stair-ways", "again", db=db, on=date(2026, 4, 3))
    lapsed = progress_report(db=db, on=date(2026, 4, 3))
    assert lapsed.mastered == 0
    assert lapsed.streak_days == 3


def test_streak_survives_until_yesterday(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    record_attempt("stair-ways", 4, db=db, on=date(2026, 4, 1))
    assert progress_report(db=db, on=date(2026, 4, 2)).streak_days == 1
    assert progress_report(db=db, on=date(2026, 4, 3)).streak_days == 0


def test_hint_ladder_does_not_leak_and_remembers_progress(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    first = get_hint("pair-with-target", db=db)
    assert first.level == 1
    assert first.level_name == "nudge"
    assert "seen[x]" not in first.text
    second = get_hint("pair-with-target", 2, db=db)
    assert second.level == 2
    assert second.text != first.text
    third = get_hint("pair-with-target", db=db)
    assert third.level == 3
    assert "seen[x]" in third.text
    again = get_hint("pair-with-target", db=db)
    assert again.exhausted is True
    assert "full solution is not" in again.text
    with pytest.raises(SenseiError):
        get_hint("pair-with-target", 4, db=db)


def test_unknown_attempt_does_not_create_a_card(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    with pytest.raises(SenseiError, match="Unknown problem"):
        record_attempt("not-a-problem", 5, db=db)
    assert not db.exists()
    with pytest.raises(SenseiError, match="2000"):
        record_attempt("stair-ways", 5, notes="n" * 2001, db=db)


def test_practice_prefers_due_then_new(tmp_path: Path) -> None:
    db = tmp_path / "study.db"
    first = practice(db=db, on=date(2026, 4, 1))
    assert first.reason == "new"
    assert first.problem is not None
    assert first.problem.id == "dominating-value"
    record_attempt(first.problem.id, 3, db=db, on=date(2026, 4, 1))
    still_new = practice(db=db, on=date(2026, 4, 1))
    assert still_new.reason == "new"
    assert still_new.problem is not None
    assert still_new.problem.id != first.problem.id
    due = practice(db=db, on=date(2026, 4, 2))
    assert due.reason == "due"
    assert due.problem is not None
    assert due.problem.id == first.problem.id


def test_reset_and_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "nested" / "sensei.db"
    record_attempt("stair-ways", 5, db=db, on=date(2026, 4, 1))
    assert db.exists()
    assert reset_progress(db) is True
    assert not db.exists()
    assert reset_progress(db) is False

    monkeypatch.setenv("DSA_SENSEI_DB", str(tmp_path / "override.db"))
    assert default_db_path() == tmp_path / "override.db"
    monkeypatch.delenv("DSA_SENSEI_DB")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    assert default_db_path() == tmp_path / "xdg" / "dsa-sensei" / "sensei.db"


def test_store_rejects_bad_hint_level(tmp_path: Path) -> None:
    with pytest.raises(SenseiError):
        Store(tmp_path / "s.db").reveal("stair-ways", 0)


def test_service_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import date

    from dsa_sensei.clock import today
    from dsa_sensei.service import get_hint, practice, record_attempt

    monkeypatch.delenv("DSA_SENSEI_TODAY")
    assert today() == date.today()
    with pytest.raises(SenseiError, match="problem id"):
        get_hint(db=tmp_path / "s.db")
    with pytest.raises(SenseiError, match="hints_used"):
        record_attempt("stair-ways", 4, hints_used=True, db=tmp_path / "s.db")  # type: ignore[arg-type]
    empty = practice(topic="graphs", difficulty="hard", db=tmp_path / "s.db")
    assert empty.reason == "empty"
    assert empty.to_dict()["problem"] is None
    db = tmp_path / "orphan.db"
    store = Store(db)
    store.record_attempt("retired-problem", 4, hints_used=0, notes="", on=date(2026, 4, 1))
    report = progress_report(db=db, on=date(2026, 4, 1))
    assert report.seen == 0
    card = store.get_card("retired-problem")
    assert card is not None
    assert card.to_dict()["last_reviewed_on"] == "2026-04-01"


def test_attempt_restarts_the_hint_ladder(tmp_path: Path) -> None:
    db = tmp_path / "hints.db"
    assert get_hint("stair-ways", 3, db=db).level == 3
    record_attempt("stair-ways", 4, db=db, on=date(2026, 4, 1))
    assert get_hint("stair-ways", db=db).level == 1


def test_unknown_attempt_does_not_suggest_a_custom_prompt(tmp_path: Path) -> None:
    with pytest.raises(SenseiError, match="dsa-sensei list") as caught:
        record_attempt("zzzz-not-a-problem", 4, db=tmp_path / "s.db")
    assert "custom prompt" not in str(caught.value)
    with pytest.raises(SenseiError, match="custom prompt"):
        get_hint("zzzz-not-a-problem", db=tmp_path / "s.db")


def test_progress_ignores_unknown_problem_ids(tmp_path: Path) -> None:
    db = tmp_path / "orphan.db"
    Store(db).record_attempt("retired-problem", 5, hints_used=0, notes="", on=date(2026, 4, 1))
    report = progress_report(db=db, on=date(2026, 4, 1))
    assert report.attempts == 0
    assert report.seen == 0
    assert report.streak_days == 0


def test_schema_version_is_recorded(tmp_path: Path) -> None:
    import sqlite3

    db = tmp_path / "versioned.db"
    record_attempt("stair-ways", 5, db=db, on=date(2026, 4, 1))
    connection = sqlite3.connect(db)
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
    assert connection.execute("SELECT value FROM schema_meta WHERE key = 'version'").fetchone()[0] == "1"
    connection.close()


def test_parallel_reviews_do_not_lose_an_update(tmp_path: Path) -> None:
    import threading

    db = tmp_path / "race.db"
    record_attempt("stair-ways", 5, db=db, on=date(2026, 4, 1))
    barrier = threading.Barrier(2)

    def worker() -> None:
        barrier.wait()
        record_attempt("stair-ways", 5, db=db, on=date(2026, 4, 2))

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    card = Store(db).get_card("stair-ways")
    assert card is not None
    assert card.repetitions == 3


def test_bad_review_date(tmp_path: Path) -> None:
    with pytest.raises(SenseiError, match="YYYY-MM-DD"):
        due_reviews(on="April 1", db=tmp_path / "s.db")
