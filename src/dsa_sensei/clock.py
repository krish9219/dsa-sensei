"""The scheduler's notion of today.

``DSA_SENSEI_TODAY=YYYY-MM-DD`` freezes the clock for tests and demos.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone

from dsa_sensei.errors import SenseiError


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SenseiError(f"Invalid date {value!r}. Use YYYY-MM-DD.") from exc


def today() -> date:
    raw = os.environ.get("DSA_SENSEI_TODAY", "").strip()
    if not raw:
        return date.today()
    return parse_iso_date(raw)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
