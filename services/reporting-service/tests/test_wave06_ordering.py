from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from app.schemas.events import InternalEventIn


def make(name, payload, when):
    return InternalEventIn(event_id=uuid.uuid4(), source_service="test-service", event_type=name,
                           payload=payload, occurred_at=when)


def test_late_attendance_event_does_not_regress_projection(service):
    sid, uid, section = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    base = {"session_id": str(sid), "attendance_session_id": str(sid), "student_user_id": str(uid),
            "section_id": str(section), "session_date": "2026-10-10"}
    t = datetime.now(UTC)
    assert service.ingest_event(make("attendance.updated", {**base, "status": "PRESENT"}, t)) == "processed"
    assert service.ingest_event(make("attendance.recorded", {**base, "status": "ABSENT"}, t - timedelta(minutes=1))) == "processed"
    assert service._attendance_dicts()[0]["status"] == "PRESENT"


def test_attendance_cancelled_reopened_and_refinalized_not_counted_while_open(service):
    sid, uid, section = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    t = datetime.now(UTC)
    base = {"session_id": str(sid), "attendance_session_id": str(sid), "student_user_id": str(uid),
            "section_id": str(section), "session_date": "2026-10-10", "status": "PRESENT"}
    service.ingest_event(make("attendance.recorded", base, t))
    assert len(service._attendance_dicts()) == 1
    service.ingest_event(make("attendance.session_reopened", {"session_id": str(sid)}, t + timedelta(seconds=1)))
    assert len(service._attendance_dicts()) == 0
    service.ingest_event(make("attendance.session_finalized", {"session_id": str(sid)}, t + timedelta(seconds=2)))
    assert len(service._attendance_dicts()) == 1
    service.ingest_event(make("attendance.session_cancelled", {"session_id": str(sid)}, t + timedelta(seconds=3)))
    assert len(service._attendance_dicts()) == 0
    service.ingest_event(make("attendance.session_finalized", {"session_id": str(sid)}, t + timedelta(seconds=2)))
    assert len(service._attendance_dicts()) == 0


def test_assessment_out_of_order_does_not_downgrade_and_preserves_dimensions(service):
    attempt, user, course, section, quiz = (uuid.uuid4() for _ in range(5))
    t = datetime.now(UTC)
    base = {"attempt_id": str(attempt), "student_user_id": str(user), "quiz_id": str(quiz),
            "course_id": str(course), "section_id": str(section), "passed": True}
    service.ingest_event(make("assessment.attempt_graded", {**base, "percent": 95}, t))
    service.ingest_event(make("assessment.attempt_graded", {**base, "percent": 30}, t - timedelta(minutes=1)))
    row = service._assessment_dicts()[0]
    assert row["percent"] == 95
    assert row["course_id"] == str(course)
    assert row["section_id"] == str(section)
    assert row["quiz_id"] == str(quiz)
