import pytest

from smartedu_security import MemoryFixedWindowLimiter


@pytest.mark.asyncio
async def test_fixed_window_limiter_blocks_after_limit():
    current = {"value": 100.0}

    def clock():
        return current["value"]

    limiter = MemoryFixedWindowLimiter(
        limit=2,
        window_seconds=60,
        clock=clock,
    )

    assert (await limiter.hit("a")).allowed
    assert (await limiter.hit("a")).allowed
    blocked = await limiter.hit("a")
    assert not blocked.allowed
    assert blocked.retry_after_seconds > 0

    current["value"] += 61
    assert (await limiter.hit("a")).allowed
