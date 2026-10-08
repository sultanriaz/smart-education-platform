from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    not os.getenv("PLATFORM_TEST_DATABASE_URL"),
    reason="PLATFORM_TEST_DATABASE_URL not configured",
)
def test_postgres_duplicate_event_race_placeholder():
    # Repository integration should extend this with two concurrent transactions
    # inserting the same event_id into internal_events.
    assert os.getenv("PLATFORM_TEST_DATABASE_URL").startswith("postgres")
