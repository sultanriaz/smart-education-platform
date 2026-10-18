import uuid
from app.schemas.events import InternalEventIn
from app.core.errors import DomainError
import pytest


def test_report_screen_and_csv_filter_parity(service):
    students = [uuid.uuid4(), uuid.uuid4()]
    for student in students:
        service.ingest_event(InternalEventIn(event_id=uuid.uuid4(), source_service="assessment-service", event_type="assessment.attempt_graded", payload={"attempt_id": str(uuid.uuid4()), "student_user_id": str(student), "percent": 83.0, "passed": True}))
    scope = {"student_user_id": str(students[0])}
    page = service.report_page("assessment", scope, limit=1, offset=0)
    csv, count = service.export_csv("assessment", uuid.uuid4(), scope)
    snapshot = service.create_snapshot("assessment", scope, uuid.uuid4())
    assert page["total"] == count == len(snapshot.payload["rows"]) == 1
    assert str(students[1]) not in csv
    with pytest.raises(DomainError):
        service.report_page("assessment", {"unknown_filter": "malicious"})


def test_csv_injection_cells_are_escaped(service):
    for content in ("=SUM(A1)", "+1+2", "-1", "@evil", "\t=evil", "  =evil"):
        assert service.csv_cell(content).startswith("'")
    assert service.csv_cell("safe") == "safe"
