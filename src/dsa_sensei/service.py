"""Operations shared by the CLI and the MCP server."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path

from dsa_sensei.catalog import get_catalog
from dsa_sensei.clock import parse_iso_date, today
from dsa_sensei.complexity import analyze_python, describe_comparison
from dsa_sensei.errors import InvalidHintLevel, SenseiError
from dsa_sensei.llm import generate_ladder, require_settings
from dsa_sensei.models import (
    Attempt,
    AttemptResult,
    HintResult,
    PracticePick,
    Problem,
    ProgressReport,
    TopicProgress,
)
from dsa_sensei.paths import default_db_path
from dsa_sensei.schema import TOPICS
from dsa_sensei.srs import QUALITY_LABELS, parse_quality
from dsa_sensei.store import Store

_LEVEL_NAMES = ("nudge", "approach", "pseudocode")
_EXHAUSTED = (
    "You already opened every rung. Write the solution yourself and check its "
    "complexity; a full solution is not part of this tutor."
)


def resolve_db(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser()
    return default_db_path()


def open_store(explicit: Path | None = None, *, write: bool) -> Store | None:
    path = resolve_db(explicit)
    if not write and not path.exists():
        return None
    return Store(path)


def list_problems(
    *,
    topic: str | None = None,
    difficulty: str | None = None,
) -> list[Problem]:
    return get_catalog().list_problems(topic=topic, difficulty=difficulty)


def get_problem(problem_id: str) -> Problem:
    return get_catalog().get(problem_id)


def get_hint(
    problem_id: str | None = None,
    level: int | None = None,
    *,
    custom_prompt: str | None = None,
    db: Path | None = None,
) -> HintResult:
    if custom_prompt and custom_prompt.strip():
        if problem_id and problem_id.strip():
            raise SenseiError("Pass either a catalog id or a custom prompt, not both.")
        return _custom_hint(custom_prompt.strip(), level, db)
    if not problem_id or not problem_id.strip():
        raise SenseiError("Provide a problem id, or a custom prompt.")
    problem = get_catalog().get(problem_id)
    store = open_store(db, write=True)
    assert store is not None
    revealed = store.revealed_level(problem.id)
    exhausted = False
    if level is None or level == 0:
        if revealed >= 3:
            chosen = 3
            exhausted = True
        else:
            chosen = revealed + 1
    else:
        if level not in (1, 2, 3):
            raise InvalidHintLevel(level)
        chosen = level
    store.reveal(problem.id, chosen)
    hint = problem.hints[chosen - 1]
    text = f"{hint.text}\n\n{_EXHAUSTED}" if exhausted else hint.text
    return HintResult(
        problem_id=problem.id,
        title=problem.title,
        level=chosen,
        level_name=hint.level,
        text=text,
        levels_remaining=3 - chosen,
        source="builtin",
        exhausted=exhausted,
    )


def analyze_code(code: str, problem_id: str | None = None) -> dict[str, object]:
    report = analyze_python(code)
    payload = report.to_dict()
    payload["comparison"] = None
    payload["target_time"] = None
    payload["target_space"] = None
    payload["problem_id"] = None
    if problem_id and problem_id.strip():
        problem = get_catalog().get(problem_id)
        payload["problem_id"] = problem.id
        payload["target_time"] = problem.target_time
        payload["target_space"] = problem.target_space
        payload["comparison"] = describe_comparison(
            report.time,
            problem.target_time,
            problem.acceptable_time,
            estimate_space=report.space,
            target_space=problem.target_space,
            note=problem.complexity_note,
        )
    return payload


def record_attempt(
    problem_id: str,
    quality: object,
    *,
    hints_used: int = 0,
    notes: str = "",
    db: Path | None = None,
    on: date | None = None,
) -> AttemptResult:
    problem = get_catalog().get(problem_id)
    grade = parse_quality(quality)
    if not isinstance(hints_used, int) or isinstance(hints_used, bool) or not 0 <= hints_used <= 3:
        raise SenseiError("hints_used must be an integer from 0 to 3.")
    store = open_store(db, write=True)
    assert store is not None
    day = on or today()
    card = store.record_attempt(
        problem.id,
        grade,
        hints_used=hints_used,
        notes=notes.strip(),
        on=day,
    )
    return AttemptResult(
        problem_id=problem.id,
        quality=grade,
        quality_label=QUALITY_LABELS[grade],
        ease=card.ease,
        interval_days=card.interval_days,
        repetitions=card.repetitions,
        due_on=card.due_on.isoformat(),
        hints_used=hints_used,
        lapsed=grade < 3,
    )


def due_reviews(
    *,
    on: date | str | None = None,
    db: Path | None = None,
) -> list[dict[str, object]]:
    day = _coerce_day(on)
    store = open_store(db, write=False)
    if store is None:
        return []
    catalog = get_catalog()
    reviews: list[dict[str, object]] = []
    for card in store.due_cards(day):
        problem = catalog.by_id.get(card.problem_id)
        reviews.append(
            {
                "problem_id": card.problem_id,
                "title": None if problem is None else problem.title,
                "topic": None if problem is None else problem.topic,
                "difficulty": None if problem is None else problem.difficulty,
                "due_on": card.due_on.isoformat(),
                "overdue_days": (day - card.due_on).days,
                "ease": card.ease,
                "interval_days": card.interval_days,
                "repetitions": card.repetitions,
                "last_quality": card.last_quality,
            }
        )
    return reviews


def progress_report(*, db: Path | None = None, on: date | None = None) -> ProgressReport:
    day = on or today()
    catalog = get_catalog()
    store = open_store(db, write=False)
    cards = [] if store is None else store.all_cards()
    attempts = [] if store is None else store.attempts()
    by_id = {card.problem_id: card for card in cards}
    attempt_counts: dict[str, int] = {}
    quality_sums: dict[str, int] = {}
    for attempt in attempts:
        problem = catalog.by_id.get(attempt.problem_id)
        if problem is None:
            continue
        attempt_counts[problem.topic] = attempt_counts.get(problem.topic, 0) + 1
        quality_sums[problem.topic] = quality_sums.get(problem.topic, 0) + attempt.quality
    topics: list[TopicProgress] = []
    seen = mastered = due = 0
    for topic in TOPICS:
        members = [problem for problem in catalog.problems if problem.topic == topic]
        topic_seen = 0
        topic_mastered = 0
        topic_due = 0
        for problem in members:
            card = by_id.get(problem.id)
            if card is None:
                continue
            topic_seen += 1
            if card.due_on <= day:
                topic_due += 1
            if _mastered(card.repetitions, card.interval_days, card.last_quality):
                topic_mastered += 1
        count = attempt_counts.get(topic, 0)
        average = None if count == 0 else round(quality_sums[topic] / count, 2)
        topics.append(
            TopicProgress(
                topic=topic,
                total=len(members),
                seen=topic_seen,
                mastered=topic_mastered,
                due=topic_due,
                attempts=count,
                average_quality=average,
            )
        )
        seen += topic_seen
        mastered += topic_mastered
        due += topic_due
    return ProgressReport(
        topics=tuple(topics),
        total_problems=len(catalog.problems),
        seen=seen,
        mastered=mastered,
        due=due,
        attempts=len(attempts),
        streak_days=_streak(attempts, day),
    )


def practice(
    *,
    topic: str | None = None,
    difficulty: str | None = None,
    db: Path | None = None,
    on: date | None = None,
) -> PracticePick:
    day = on or today()
    pool = list_problems(topic=topic, difficulty=difficulty)
    if not pool:
        return PracticePick(reason="empty", problem=None)
    store = open_store(db, write=False)
    cards = [] if store is None else store.all_cards()
    by_id = {card.problem_id: card for card in cards}
    due = [by_id[problem.id] for problem in pool if problem.id in by_id and by_id[problem.id].due_on <= day]
    due.sort(key=lambda card: (card.due_on, card.problem_id))
    if due:
        card = due[0]
        return PracticePick(
            reason="due",
            problem=get_catalog().by_id[card.problem_id],
            due_on=card.due_on.isoformat(),
            overdue_days=(day - card.due_on).days,
        )
    unseen = [problem for problem in pool if problem.id not in by_id]
    if unseen:
        return PracticePick(reason="new", problem=unseen[0])
    return PracticePick(reason="done", problem=None)


def reset_progress(db: Path | None = None) -> bool:
    return Store(resolve_db(db)).reset()


def _custom_hint(prompt: str, level: int | None, db: Path | None) -> HintResult:
    if len(prompt) > 4000:
        raise SenseiError("Custom prompts are limited to 4000 characters.")
    digest = hashlib.sha256(" ".join(prompt.split()).encode("utf-8")).hexdigest()
    store = open_store(db, write=True)
    assert store is not None
    cached = store.get_custom_hint(digest)
    if cached is None:
        ladder = generate_ladder(prompt, require_settings())
        revealed = 0
    else:
        ladder = cached[0], cached[1], cached[2]
        revealed = cached[3]
    exhausted = False
    if level is None or level == 0:
        if revealed >= 3:
            chosen = 3
            exhausted = True
        else:
            chosen = revealed + 1
    else:
        if level not in (1, 2, 3):
            raise InvalidHintLevel(level)
        chosen = level
    store.save_custom_hint(digest, prompt, ladder, chosen)
    text = ladder[chosen - 1]
    if exhausted:
        text = f"{text}\n\n{_EXHAUSTED}"
    return HintResult(
        problem_id=f"custom-{digest[:12]}",
        title="Custom problem",
        level=chosen,
        level_name=_LEVEL_NAMES[chosen - 1],
        text=text,
        levels_remaining=3 - chosen,
        source="llm",
        exhausted=exhausted,
    )


def _coerce_day(value: date | str | None) -> date:
    if value is None or value == "":
        return today()
    if isinstance(value, date):
        return value
    return parse_iso_date(value)


def _mastered(repetitions: int, interval_days: int, last_quality: int | None) -> bool:
    return repetitions >= 2 and interval_days >= 6 and (last_quality or 0) >= 3


def _streak(attempts: list[Attempt], day: date) -> int:
    reviewed = {attempt.reviewed_on for attempt in attempts}
    if not reviewed:
        return 0
    cursor = day if day in reviewed else day - timedelta(days=1)
    streak = 0
    while cursor in reviewed:
        streak += 1
        cursor -= timedelta(days=1)
    return streak
