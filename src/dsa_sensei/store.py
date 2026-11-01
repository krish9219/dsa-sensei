"""SQLite study log: attempts, SM-2 cards, and hint progress."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

from dsa_sensei.clock import utc_now_iso
from dsa_sensei.errors import SenseiError
from dsa_sensei.models import Attempt, Card
from dsa_sensei.srs import ReviewState, apply_sm2, starting_state

_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id TEXT NOT NULL,
    reviewed_on TEXT NOT NULL,
    reviewed_at TEXT NOT NULL,
    quality INTEGER NOT NULL CHECK(quality BETWEEN 0 AND 5),
    hints_used INTEGER NOT NULL CHECK(hints_used BETWEEN 0 AND 3),
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS cards (
    problem_id TEXT PRIMARY KEY,
    ease REAL NOT NULL,
    interval_days INTEGER NOT NULL,
    repetitions INTEGER NOT NULL,
    due_on TEXT NOT NULL,
    last_quality INTEGER,
    last_reviewed_on TEXT
);
CREATE TABLE IF NOT EXISTS hint_state (
    problem_id TEXT PRIMARY KEY,
    revealed INTEGER NOT NULL CHECK(revealed BETWEEN 0 AND 3)
);
CREATE TABLE IF NOT EXISTS custom_hints (
    prompt_hash TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    nudge TEXT NOT NULL,
    approach TEXT NOT NULL,
    pseudocode TEXT NOT NULL,
    revealed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_problem ON attempts(problem_id);
CREATE INDEX IF NOT EXISTS idx_attempts_day ON attempts(reviewed_on);
CREATE INDEX IF NOT EXISTS idx_cards_due ON cards(due_on);
"""


class Store:
    """One connection per operation. Safe to construct before the file exists."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(_SCHEMA)
            connection.execute(
                "INSERT INTO schema_meta(key, value) VALUES('version', '1') ON CONFLICT(key) DO NOTHING"
            )
            yield connection
            connection.commit()
        except sqlite3.Error as exc:
            connection.rollback()
            raise SenseiError(f"Could not use the study log at {self.path}: {exc}") from exc
        finally:
            connection.close()

    def revealed_level(self, problem_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT revealed FROM hint_state WHERE problem_id = ?",
                (problem_id,),
            ).fetchone()
        if row is None:
            return 0
        return int(row["revealed"])

    def reveal(self, problem_id: str, level: int) -> int:
        if not 1 <= level <= 3:
            raise SenseiError("Hint progress only stores levels 1, 2, or 3.")
        with self._connect() as connection:
            current = connection.execute(
                "SELECT revealed FROM hint_state WHERE problem_id = ?",
                (problem_id,),
            ).fetchone()
            revealed = level if current is None else max(int(current["revealed"]), level)
            connection.execute(
                "INSERT INTO hint_state(problem_id, revealed) VALUES(?, ?) "
                "ON CONFLICT(problem_id) DO UPDATE SET revealed = excluded.revealed",
                (problem_id, revealed),
            )
        return revealed

    def record_attempt(
        self,
        problem_id: str,
        quality: int,
        *,
        hints_used: int,
        notes: str,
        on: date,
    ) -> Card:
        if not 0 <= hints_used <= 3:
            raise SenseiError("hints_used must be between 0 and 3.")
        if len(notes) > 2000:
            raise SenseiError("Notes are limited to 2000 characters.")
        with self._connect() as connection:
            row = connection.execute(
                "SELECT ease, interval_days, repetitions FROM cards WHERE problem_id = ?",
                (problem_id,),
            ).fetchone()
            state = (
                starting_state()
                if row is None
                else ReviewState(
                    ease=float(row["ease"]),
                    interval_days=int(row["interval_days"]),
                    repetitions=int(row["repetitions"]),
                )
            )
            updated = apply_sm2(state, quality)
            due = on + timedelta(days=updated.interval_days)
            connection.execute(
                "INSERT INTO attempts(problem_id, reviewed_on, reviewed_at, quality, hints_used, notes) "
                "VALUES(?, ?, ?, ?, ?, ?)",
                (problem_id, on.isoformat(), utc_now_iso(), quality, hints_used, notes),
            )
            connection.execute(
                """
                INSERT INTO cards(
                    problem_id, ease, interval_days, repetitions, due_on, last_quality, last_reviewed_on
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(problem_id) DO UPDATE SET
                    ease = excluded.ease,
                    interval_days = excluded.interval_days,
                    repetitions = excluded.repetitions,
                    due_on = excluded.due_on,
                    last_quality = excluded.last_quality,
                    last_reviewed_on = excluded.last_reviewed_on
                """,
                (
                    problem_id,
                    updated.ease,
                    updated.interval_days,
                    updated.repetitions,
                    due.isoformat(),
                    quality,
                    on.isoformat(),
                ),
            )
        card = self.get_card(problem_id)
        if card is None:
            raise SenseiError(f"The attempt for '{problem_id}' did not persist.")
        return card

    def get_card(self, problem_id: str) -> Card | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM cards WHERE problem_id = ?",
                (problem_id,),
            ).fetchone()
        return None if row is None else _card(row)

    def due_cards(self, on: date) -> list[Card]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM cards WHERE due_on <= ? ORDER BY due_on, problem_id",
                (on.isoformat(),),
            ).fetchall()
        return [_card(row) for row in rows]

    def all_cards(self) -> list[Card]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM cards ORDER BY problem_id").fetchall()
        return [_card(row) for row in rows]

    def attempts(self) -> list[Attempt]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM attempts ORDER BY reviewed_on, id").fetchall()
        return [_attempt(row) for row in rows]

    def get_custom_hint(self, prompt_hash: str) -> tuple[str, str, str, int] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT nudge, approach, pseudocode, revealed FROM custom_hints WHERE prompt_hash = ?",
                (prompt_hash,),
            ).fetchone()
        if row is None:
            return None
        return (str(row["nudge"]), str(row["approach"]), str(row["pseudocode"]), int(row["revealed"]))

    def save_custom_hint(
        self,
        prompt_hash: str,
        prompt: str,
        ladder: tuple[str, str, str],
        revealed: int,
    ) -> None:
        nudge, approach, pseudocode = ladder
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO custom_hints(
                    prompt_hash, prompt, nudge, approach, pseudocode, revealed, created_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(prompt_hash) DO UPDATE SET
                    nudge = excluded.nudge,
                    approach = excluded.approach,
                    pseudocode = excluded.pseudocode,
                    revealed = MAX(custom_hints.revealed, excluded.revealed)
                """,
                (prompt_hash, prompt, nudge, approach, pseudocode, revealed, utc_now_iso()),
            )

    def reset(self) -> bool:
        """Delete the study log. Returns whether a file was removed."""
        if not self.path.exists():
            return False
        self.path.unlink()
        return True


def _card(row: sqlite3.Row) -> Card:
    last_quality = row["last_quality"]
    last_reviewed = row["last_reviewed_on"]
    return Card(
        problem_id=str(row["problem_id"]),
        ease=float(row["ease"]),
        interval_days=int(row["interval_days"]),
        repetitions=int(row["repetitions"]),
        due_on=date.fromisoformat(str(row["due_on"])),
        last_quality=None if last_quality is None else int(last_quality),
        last_reviewed_on=None if last_reviewed is None else date.fromisoformat(str(last_reviewed)),
    )


def _attempt(row: sqlite3.Row) -> Attempt:
    return Attempt(
        id=int(row["id"]),
        problem_id=str(row["problem_id"]),
        reviewed_on=date.fromisoformat(str(row["reviewed_on"])),
        reviewed_at=str(row["reviewed_at"]),
        quality=int(row["quality"]),
        hints_used=int(row["hints_used"]),
        notes=str(row["notes"]),
    )
