from __future__ import annotations

import pytest

from dsa_sensei.errors import InvalidQuality
from dsa_sensei.srs import apply_sm2, parse_quality, starting_state


def test_successful_reviews_follow_sm2_intervals() -> None:
    first = apply_sm2(starting_state(), 5)
    assert first.interval_days == 1
    assert first.repetitions == 1
    assert first.ease == pytest.approx(2.6)

    second = apply_sm2(first, 5)
    assert second.interval_days == 6
    assert second.repetitions == 2
    assert second.ease == pytest.approx(2.7)

    third = apply_sm2(second, 5)
    assert third.interval_days == 16
    assert third.repetitions == 3
    assert third.ease == pytest.approx(2.8)


def test_failure_resets_the_ladder_and_ease_has_a_floor() -> None:
    failed = apply_sm2(starting_state(), 0)
    assert failed.repetitions == 0
    assert failed.interval_days == 1
    assert failed.ease == pytest.approx(1.7)

    floored = apply_sm2(failed, 0)
    assert floored.ease == pytest.approx(1.3)
    assert apply_sm2(floored, 0).ease == pytest.approx(1.3)

    learned = apply_sm2(apply_sm2(starting_state(), 5), 5)
    lapsed = apply_sm2(learned, 2)
    assert lapsed.repetitions == 0
    assert lapsed.interval_days == 1
    assert lapsed.ease < learned.ease


def test_quality_four_does_not_change_ease() -> None:
    updated = apply_sm2(starting_state(), 4)
    assert updated.ease == pytest.approx(2.5)
    assert updated.interval_days == 1


def test_quality_words_and_rejection() -> None:
    assert parse_quality("good") == 4
    assert parse_quality("easy") == 5
    assert parse_quality(" hard ") == 3
    assert parse_quality("2") == 2
    assert parse_quality(0) == 0
    for bad in (True, False, 6, -1, "nope", 1.5, None):
        with pytest.raises(InvalidQuality):
            parse_quality(bad)
    with pytest.raises(InvalidQuality):
        apply_sm2(starting_state(), 9)
