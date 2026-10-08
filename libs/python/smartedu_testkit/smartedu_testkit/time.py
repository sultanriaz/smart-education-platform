from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass
class FrozenClock:
    current: datetime

    def __post_init__(self) -> None:
        if self.current.tzinfo is None:
            raise ValueError("FrozenClock requires a timezone-aware datetime")

    def now(self) -> datetime:
        return self.current

    def advance(self, **delta) -> datetime:
        self.current = self.current + timedelta(**delta)
        return self.current

    def set(self, value: datetime) -> None:
        if value.tzinfo is None:
            raise ValueError("FrozenClock requires a timezone-aware datetime")
        self.current = value


def utc_datetime(
    year: int = 2026,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    return datetime(year, month, day, hour, minute, second, tzinfo=UTC)
