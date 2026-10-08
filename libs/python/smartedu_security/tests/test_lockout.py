import pytest

from smartedu_security import MemoryLockoutStore


@pytest.mark.asyncio
async def test_account_locks_after_threshold_and_clears_on_success():
    current = {"value": 1000.0}

    def clock():
        return current["value"]

    store = MemoryLockoutStore(
        max_failures=3,
        failure_window_seconds=60,
        lock_seconds=120,
        clock=clock,
    )

    assert (await store.check("User@Example.edu")).allowed
    assert (await store.failure("User@Example.edu")).allowed
    assert (await store.failure("user@example.edu")).allowed

    third = await store.failure("user@example.edu")
    assert not third.allowed
    assert third.retry_after_seconds == 120

    locked = await store.check("USER@example.edu")
    assert not locked.allowed

    current["value"] += 121
    assert (await store.check("user@example.edu")).allowed

    await store.failure("user@example.edu")
    await store.success("user@example.edu")
    assert (await store.check("user@example.edu")).failure_count == 0
