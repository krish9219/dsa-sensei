"""SM-2 scheduling.

This follows the published SuperMemo SM-2 steps: the current ease factor sizes
the next interval, then the ease factor moves based on the 0-5 grade. A grade
below 3 restarts the interval ladder and does not reset ease to 2.5. Ease is
floored at 1.3. Intervals use half-up rounding.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from dsa_sensei.errors import InvalidQuality

INITIAL_EASE = 2.5
MIN_EASE = 1.3

QUALITY_LABELS: dict[int, str] = {
    0: "blackout",
    1: "again",
    2: "fuzzy",
    3: "hard",
    4: "good",
    5: "perfect",
}

_QUALITY_WORDS: dict[str, int] = {
    "blackout": 0,
    "again": 1,
    "fuzzy": 2,
    "hard": 3,
    "good": 4,
    "easy": 5,
    "perfect": 5,
}


@dataclass(frozen=True, slots=True)
class ReviewState:
    ease: float
    interval_days: int
    repetitions: int


def starting_state() -> ReviewState:
    return ReviewState(ease=INITIAL_EASE, interval_days=0, repetitions=0)


def parse_quality(value: object) -> int:
    if isinstance(value, bool):
        raise InvalidQuality(value)
    if isinstance(value, int):
        if 0 <= value <= 5:
            return value
        raise InvalidQuality(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text.isdigit():
            grade = int(text)
            if 0 <= grade <= 5:
                return grade
        if text in _QUALITY_WORDS:
            return _QUALITY_WORDS[text]
    raise InvalidQuality(value)


def apply_sm2(state: ReviewState, quality: int) -> ReviewState:
    """Return the next SM-2 state. ``quality`` must already be an int in 0..5."""
    if not isinstance(quality, int) or isinstance(quality, bool) or not 0 <= quality <= 5:
        raise InvalidQuality(quality)
    ease = state.ease
    interval = state.interval_days
    repetitions = state.repetitions
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = max(1, _round_half_up(interval * ease))
        repetitions += 1
    delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    ease = max(MIN_EASE, ease + delta)
    return ReviewState(ease=round(ease, 4), interval_days=interval, repetitions=repetitions)


def _round_half_up(value: float) -> int:
    return math.floor(value + 0.5)
