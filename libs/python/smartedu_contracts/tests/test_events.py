from __future__ import annotations

from datetime import UTC

from smartedu_contracts.context import reset_request_context, set_request_context
from smartedu_contracts.events import EventEnvelope, new_event


def test_event_envelope_uses_context_correlation_id():
    tokens = set_request_context("request-1", "correlation-1")
    try:
        event = new_event(
            event_type="attendance.session.finalized",
            source="attendance-service",
            subject="attendance-session:abc",
            data={"session_id": "abc"},
        )
    finally:
        reset_request_context(tokens)

    assert event.correlation_id == "correlation-1"
    assert event.event_version == 1
    assert event.occurred_at.tzinfo == UTC


def test_event_rejects_naive_time():
    from datetime import datetime

    import pytest

    with pytest.raises(ValueError):
        EventEnvelope(
            event_type="schedule.changed",
            source="scheduling-service",
            correlation_id="cid",
            occurred_at=datetime(2026, 1, 1),
        )
