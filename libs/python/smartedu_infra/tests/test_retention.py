from datetime import UTC, datetime

import pytest

from smartedu_infra.retention import RetentionRule


def test_retention_cutoff_is_timezone_aware():
    rule = RetentionRule(
        table_name="outbox_events",
        timestamp_column="published_at",
        retention_days=14,
    )
    now = datetime(2026, 10, 7, tzinfo=UTC)
    assert rule.cutoff(now).isoformat() == "2026-09-23T00:00:00+00:00"


def test_retention_rejects_naive_clock():
    rule = RetentionRule(
        table_name="outbox_events",
        timestamp_column="published_at",
        retention_days=14,
    )
    with pytest.raises(ValueError):
        rule.cutoff(datetime(2026, 10, 7))
