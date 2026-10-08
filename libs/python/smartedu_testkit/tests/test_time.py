import pytest

from smartedu_testkit import FrozenClock, utc_datetime


def test_frozen_clock_advances_deterministically():
    clock = FrozenClock(utc_datetime(2026, 10, 7, 12, 0))
    assert clock.advance(minutes=15).isoformat() == "2026-10-07T12:15:00+00:00"


def test_frozen_clock_rejects_naive_datetime():
    from datetime import datetime

    with pytest.raises(ValueError):
        FrozenClock(datetime(2026, 10, 7))
