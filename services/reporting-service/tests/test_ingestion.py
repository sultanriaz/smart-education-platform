from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.schemas.events import InternalEventIn


def ev(event_type, payload, event_id=None, source="test-service"):
    return InternalEventIn(
        event_id=event_id or uuid.uuid4(),
        source_service=source,
        event_type=event_type,
        payload=payload,
        occurred_at=datetime.now(UTC),
    )


def test_event_is_idempotent(service):
    event_id = uuid.uuid4()
    item = ev(
        "academic.enrollment_created",
        {"student_user_id": str(uuid.uuid4()), "section_id": str(uuid.uuid4())},
        event_id,
    )
    assert service.ingest_event(item) == "processed"
    assert service.ingest_event(item) == "duplicate"


def test_attendance_projection_updates_in_place(service):
    session_id = uuid.uuid4()
    student_id = uuid.uuid4()
    section_id = uuid.uuid4()

    service.ingest_event(
        ev(
            "attendance.recorded",
            {
                "attendance_session_id": str(session_id),
                "student_user_id": str(student_id),
                "section_id": str(section_id),
                "status": "ABSENT",
                "session_date": "2026-10-07",
            },
        )
    )
    service.ingest_event(
        ev(
            "attendance.updated",
            {
                "attendance_session_id": str(session_id),
                "student_user_id": str(student_id),
                "section_id": str(section_id),
                "status": "PRESENT",
                "session_date": "2026-10-07",
            },
        )
    )

    rows = service._attendance_dicts()
    assert len(rows) == 1
    assert rows[0]["status"] == "PRESENT"


def test_assessment_projection_upsert(service):
    attempt_id = uuid.uuid4()
    student_id = uuid.uuid4()

    service.ingest_event(
        ev(
            "assessment.attempt_graded",
            {
                "attempt_id": str(attempt_id),
                "student_user_id": str(student_id),
                "percent": 80,
                "passed": True,
            },
        )
    )
    service.ingest_event(
        ev(
            "assessment.attempt_graded",
            {
                "attempt_id": str(attempt_id),
                "student_user_id": str(student_id),
                "percent": 90,
                "passed": True,
            },
        )
    )

    rows = service._assessment_dicts()
    assert len(rows) == 1
    assert rows[0]["percent"] == 90


def test_facility_booking_status_progression(service):
    booking = uuid.uuid4()
    facility = uuid.uuid4()

    service.ingest_event(
        ev(
            "facility.booking_requested",
            {"booking_id": str(booking), "facility_id": str(facility)},
        )
    )
    service.ingest_event(
        ev(
            "facility.booking_approved",
            {"booking_id": str(booking), "facility_id": str(facility)},
        )
    )

    rows = service._facility_dicts()
    assert len(rows) == 1
    assert rows[0]["status"] == "APPROVED"


def test_notification_projection(service):
    service.ingest_event(
        ev(
            "notification.delivered",
            {
                "delivery_id": "delivery-1",
                "notification_id": str(uuid.uuid4()),
                "channel": "EMAIL",
                "status": "DELIVERED",
            },
        )
    )
    rows = service._notification_dicts()
    assert len(rows) == 1
    assert rows[0]["status"] == "DELIVERED"


def test_schedule_projection(service):
    section = uuid.uuid4()
    event = ev(
        "schedule.updated",
        {"section_id": str(section)},
        source="scheduling-service",
    )
    service.ingest_event(event)
    rows = service._schedule_dicts()
    assert len(rows) == 1
    assert rows[0]["activity_type"] == "schedule.updated"


def test_enrollment_projection_status(service):
    student = uuid.uuid4()
    section = uuid.uuid4()

    service.ingest_event(
        ev(
            "academic.enrollment_created",
            {"student_user_id": str(student), "section_id": str(section)},
        )
    )
    service.ingest_event(
        ev(
            "academic.enrollment_dropped",
            {"student_user_id": str(student), "section_id": str(section)},
        )
    )

    rows = service._enrollment_dicts()
    assert len(rows) == 1
    assert rows[0]["status"] == "DROPPED"
