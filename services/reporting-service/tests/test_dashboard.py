from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.schemas.events import InternalEventIn


def ingest(service, event_type, payload):
    service.ingest_event(
        InternalEventIn(
            event_id=uuid.uuid4(),
            source_service="test",
            event_type=event_type,
            payload=payload,
            occurred_at=datetime.now(UTC),
        )
    )


def test_dashboard_aggregates(service):
    student = uuid.uuid4()
    section = uuid.uuid4()

    ingest(
        service,
        "academic.enrollment_created",
        {"student_user_id": str(student), "section_id": str(section)},
    )

    for status in ["PRESENT", "PRESENT", "ABSENT"]:
        ingest(
            service,
            "attendance.recorded",
            {
                "attendance_session_id": str(uuid.uuid4()),
                "student_user_id": str(student),
                "section_id": str(section),
                "status": status,
            },
        )

    ingest(
        service,
        "assessment.attempt_graded",
        {
            "attempt_id": str(uuid.uuid4()),
            "student_user_id": str(student),
            "percent": 80,
            "passed": True,
        },
    )

    booking = uuid.uuid4()
    facility = uuid.uuid4()
    ingest(
        service,
        "facility.booking_approved",
        {"booking_id": str(booking), "facility_id": str(facility)},
    )

    ingest(
        service,
        "notification.delivered",
        {"delivery_id": "d1", "channel": "EMAIL", "status": "DELIVERED"},
    )
    ingest(service, "schedule.updated", {"section_id": str(section)})

    data = service.overview()
    assert data["active_enrollments"] == 1
    assert data["attendance_records"] == 3
    assert data["attendance_percentage"] == 66.67
    assert data["graded_attempts"] == 1
    assert data["assessment_average_percent"] == 80.0
    assert data["assessment_pass_rate"] == 100.0
    assert data["approved_facility_bookings"] == 1
    assert data["notification_success_rate"] == 100.0
    assert data["schedule_changes"] == 1
