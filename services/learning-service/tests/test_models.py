from __future__ import annotations

from app.db.base import Base


def test_expected_tables_registered():
    assert {
        "resource_categories",
        "learning_resources",
        "resource_targets",
        "resource_versions",
        "resource_access_logs",
        "outbox_events",
    }.issubset(Base.metadata.tables.keys())
