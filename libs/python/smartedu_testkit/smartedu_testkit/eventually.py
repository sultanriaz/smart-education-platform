from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def eventually(
    probe: Callable[[], Awaitable[T]],
    predicate: Callable[[T], bool],
    *,
    timeout_seconds: float = 5.0,
    interval_seconds: float = 0.1,
) -> T:
    deadline = time.monotonic() + timeout_seconds
    last: T | None = None
    while time.monotonic() < deadline:
        last = await probe()
        if predicate(last):
            return last
        await asyncio.sleep(interval_seconds)
    raise AssertionError(f"Condition not met within {timeout_seconds}s; last value={last!r}")
