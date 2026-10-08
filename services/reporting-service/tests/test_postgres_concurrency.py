from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    not os.getenv("REPORTING_TEST_DATABASE_URL"),
    reason="REPORTING_TEST_DATABASE_URL not configured",
)
def test_postgres_duplicate_event_race_placeholder():
    # Repository integration should replace/extend this with two concurrent
    # transactions inserting the same external event_id against PostgreSQL.
    assert os.getenv("REPORTING_TEST_DATABASE_URL").startswith("postgres")
