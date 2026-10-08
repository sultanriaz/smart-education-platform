from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.core.errors import DomainError
from app.schemas.events import InternalEventIn


def test_csv_export(service):
    service.ingest_event(
        InternalEventIn(
            event_id=uuid.uuid4(),
            source_service="assessment-service",
            event_type="assessment.attempt_graded",
            payload={
                "attempt_id": str(uuid.uuid4()),
                "student_user_id": str(uuid.uuid4()),
                "percent": 75,
                "passed": True,
            },
            occurred_at=datetime.now(UTC),
        )
    )
    content, count = service.export_csv("assessment", uuid.uuid4())
    assert count == 1
    assert "attempt_id" in content
    assert "75" in content


def test_snapshot_creation(service):
    snap = service.create_snapshot("overview", {}, uuid.uuid4())
    assert snap.report_type == "overview"
    assert "active_enrollments" in snap.payload


def test_snapshot_applies_filters_and_rejects_silent_unsupported_filters(service):
    students = [uuid.uuid4(), uuid.uuid4()]
    for student in students:
        service.ingest_event(
            InternalEventIn(
                event_id=uuid.uuid4(),
                source_service="assessment-service",
                event_type="assessment.attempt_graded",
                payload={
                    "attempt_id": str(uuid.uuid4()),
                    "student_user_id": str(student),
                    "percent": 75,
                    "passed": True,
                },
                occurred_at=datetime.now(UTC),
            )
        )
    snapshot = service.create_snapshot(
        "assessment", {"student_user_id": str(students[0])}, uuid.uuid4()
    )
    assert len(snapshot.payload["rows"]) == 1
    assert snapshot.payload["rows"][0]["student_user_id"] == str(students[0])
    with pytest.raises(DomainError):
        service.create_snapshot("assessment", {"unknown_filter": "ignored"}, uuid.uuid4())
    with pytest.raises(DomainError):
        service.export_csv("unsupported", uuid.uuid4())
