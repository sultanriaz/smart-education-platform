import uuid
from datetime import UTC, datetime
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.schemas.events import InternalEventIn
from app.services.reporting_service import ReportingService
from app.api.v1.endpoints.reports import my_academic_report, section_academic_report
from app.security.auth import Principal


def ingest(service, event_type, payload):
    service.ingest_event(InternalEventIn(event_id=uuid.uuid4(), source_service="fixture",
        event_type=event_type, payload=payload, occurred_at=datetime.now(UTC)))


def test_student_report_scopes_all_three_datasets(service):
    sid, other, section, course, quiz, attempt = [uuid.uuid4() for _ in range(6)]
    for user in (sid, other):
        ingest(service, "academic.enrollment_created", {"student_user_id": str(user), "section_id": str(section)})
        ingest(service, "attendance.recorded", {"student_user_id": str(user), "session_id": str(uuid.uuid4()),
            "attendance_session_id": str(uuid.uuid4()), "section_id": str(section), "course_id": str(course), "status": "PRESENT"})
        ingest(service, "assessment.attempt_graded", {"attempt_id": str(uuid.uuid4()), "student_user_id": str(user),
            "quiz_id": str(quiz), "section_id": str(section), "course_id": str(course), "percent": 80, "passed": True})
    result = my_academic_report(Principal(sid, {"student"}, "dummy"), service)
    assert result["active_enrollments"] == 1
    assert result["graded_attempts"] == 1
    assert all(row["student_user_id"] == str(sid) for row in result["assessment"])
    assert all(row["student_user_id"] == str(sid) for row in result["attendance"])
    assert all(row["student_user_id"] == str(sid) for row in result["enrollments"])


def test_teacher_section_report_is_denied_by_academic_owner(service):
    principal = Principal(uuid.uuid4(), {"teacher"}, "dummy")
    with patch("app.api.v1.endpoints.reports.require_teacher_section",
               side_effect=HTTPException(status_code=403, detail="not assigned")) as authorize:
        with pytest.raises(HTTPException) as exc:
            section_academic_report(uuid.uuid4(), principal, service)
    assert exc.value.status_code == 403
    authorize.assert_called_once()


def test_unscoped_academic_aggregation_denied(service):
    from app.core.errors import DomainError
    with pytest.raises(DomainError):
        service.academic_report()
