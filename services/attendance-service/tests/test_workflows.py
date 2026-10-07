from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.core.exceptions import DependencyUnavailable
from app.domain.models import AttendanceCorrection, AttendanceRecord, OutboxEvent, SessionHistory
from tests.conftest import bulk_payload


def records_url(session_data):
    return f"/api/v1/sessions/{session_data['id']}/records"


def test_create_session_validates_external_ids_and_outbox(session_data, academic, db):
    assert session_data["course_id"] == str(academic.section.course_id)
    assert session_data["semester_id"] == str(academic.section.semester_id)
    assert session_data["status"] == "OPEN"
    event = db.scalar(select(OutboxEvent))
    assert event.event_type == "attendance.session_created"
    assert event.payload["session_id"] == session_data["id"]
    assert event.published_at is None


def test_duplicate_session_and_scheduled_occurrences(client, session_data, academic):
    payload = {"section_id": str(academic.section.id), "session_date": "2026-10-07"}
    assert client.post("/api/v1/sessions", json=payload).status_code == 409
    payload["schedule_occurrence_id"] = str(uuid4())
    assert client.post("/api/v1/sessions", json=payload).status_code == 201
    assert client.post("/api/v1/sessions", json=payload).status_code == 409
    payload["schedule_occurrence_id"] = str(uuid4())
    assert client.post("/api/v1/sessions", json=payload).status_code == 201


def test_bulk_mark_is_atomic_and_identical_retry_is_idempotent(client, session_data, academic, db):
    url = records_url(session_data)
    payload = bulk_payload(academic)
    response = client.put(url, json=payload)
    assert response.status_code == 200, response.text
    assert len(response.json()) == 3
    first_events = db.scalar(select(func.count()).select_from(OutboxEvent))
    assert client.put(url, json=payload).json() == response.json()
    assert db.scalar(select(func.count()).select_from(OutboxEvent)) == first_events
    assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 3
    assert len(client.get(url + "?limit=1&offset=1").json()) == 1


def test_bulk_invalid_roster_member_commits_nothing(client, session_data, academic, db):
    payload = bulk_payload(academic)
    payload["records"][-1]["student_user_id"] = str(uuid4())
    assert client.put(records_url(session_data), json=payload).status_code == 403
    assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 0
    assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 1


def test_duplicate_students_rejected(client, session_data, academic):
    mark = {"student_user_id": str(academic.students[0]), "status": "PRESENT"}
    response = client.put(records_url(session_data), json={"records": [mark, mark]})
    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


def test_conflicting_retry_rolls_back_other_records(client, session_data, academic, db):
    url = records_url(session_data)
    assert (
        client.put(
            url,
            json={"records": [{"student_user_id": str(academic.students[0]), "status": "PRESENT"}]},
        ).status_code
        == 200
    )
    payload = {
        "records": [
            {"student_user_id": str(academic.students[1]), "status": "ABSENT"},
            {"student_user_id": str(academic.students[0]), "status": "ABSENT"},
        ]
    }
    assert client.put(url, json=payload).status_code == 409
    assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 1
    assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 2


def test_correction_audits_status_notes_reason_and_actor(client, session_data, academic, db):
    url = records_url(session_data)
    assert client.put(url, json=bulk_payload(academic)).status_code == 200
    record = client.get(url).json()[0]
    student_id = record["student_user_id"]
    response = client.patch(
        f"{url}/{student_id}",
        json={
            "status": "EXCUSED",
            "notes": "Approved absence",
            "reason": "Medical documentation",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["marked_at"] == record["marked_at"]
    history = client.get(f"{url}/{student_id}/history").json()
    assert len(history) == 1
    assert history[0]["previous_status"] == record["status"]
    assert history[0]["new_status"] == "EXCUSED"
    assert history[0]["new_notes"] == "Approved absence"
    assert history[0]["reason"] == "Medical documentation"
    assert history[0]["changed_by_user_id"] == response.json()["marked_by_user_id"]
    assert (
        client.patch(
            f"{url}/{student_id}", json={"status": "EXCUSED", "reason": "Retry"}
        ).status_code
        == 200
    )
    assert db.scalar(select(func.count()).select_from(AttendanceCorrection)) == 1
    assert (
        client.patch(
            f"{url}/{student_id}",
            json={"status": "EXCUSED", "notes": "Changed note", "reason": "Clarification"},
        ).status_code
        == 200
    )
    assert db.scalar(select(func.count()).select_from(AttendanceCorrection)) == 2


def test_finalize_reopen_and_cancel_keep_audit(client, session_data, academic, db):
    base = f"/api/v1/sessions/{session_data['id']}"
    url = base + "/records"
    assert client.post(base + "/finalize").status_code == 409
    assert client.put(url, json=bulk_payload(academic)).status_code == 200
    response = client.post(base + "/finalize")
    assert response.status_code == 200, response.text
    assert response.json()["finalized_at"] is not None
    assert client.put(url, json=bulk_payload(academic)).status_code == 409
    assert client.patch(base, json={"starts_at": "08:00", "reason": "Change"}).status_code == 409
    assert (
        client.post(base + "/reopen", json={"reason": "Fix attendance"}).json()["status"] == "OPEN"
    )
    assert client.get(base).json()["finalized_at"] is None
    assert client.post(base + "/finalize").status_code == 200
    assert (
        client.post(base + "/cancel", json={"reason": "Class did not occur"}).json()["status"]
        == "CANCELLED"
    )
    assert len(client.get(url).json()) == 3
    assert client.put(url, json=bulk_payload(academic)).status_code == 409
    assert client.post(base + "/reopen", json={"reason": "Revive"}).status_code == 409
    assert (
        client.patch(
            url + f"/{academic.students[0]}", json={"status": "ABSENT", "reason": "Fix"}
        ).status_code
        == 409
    )
    actions = [row["action"] for row in client.get(base + "/history").json()]
    assert actions == ["FINALIZED", "REOPENED", "FINALIZED", "CANCELLED"]
    assert db.scalar(select(func.count()).select_from(SessionHistory)) == 4


def test_admin_can_correct_finalized_historical_record(client, session_data, academic):
    url = records_url(session_data)
    client.put(url, json=bulk_payload(academic))
    client.post(f"/api/v1/sessions/{session_data['id']}/finalize")
    student = academic.students.pop()
    response = client.patch(
        f"{url}/{student}", json={"status": "EXCUSED", "reason": "Historical correction"}
    )
    assert response.status_code == 200
    assert client.get(f"{url}/{student}/history").json()[0]["reason"] == "Historical correction"


def test_session_time_changes_are_validated_and_audited(client, session_data):
    base = f"/api/v1/sessions/{session_data['id']}"
    assert (
        client.patch(base, json={"starts_at": "11:00", "reason": "Invalid range"}).status_code
        == 409
    )
    assert (
        client.patch(base, json={"starts_at": "08:30", "reason": "Early class"}).status_code == 200
    )
    assert client.get(base + "/history").json()[0]["action"] == "TIMES_UPDATED"
    assert (
        client.patch(
            base, json={"starts_at": None, "ends_at": None, "reason": "Remove time"}
        ).status_code
        == 200
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"starts_at": "10:00", "ends_at": "09:00"},
        {"starts_at": "09:00"},
        {"starts_at": "09:00+05:00", "ends_at": "10:00+05:00"},
    ],
)
def test_invalid_session_times(client, academic, payload):
    assert (
        client.post(
            "/api/v1/sessions",
            json={"section_id": str(academic.section.id), "session_date": "2026-10-07", **payload},
        ).status_code
        == 422
    )


def test_immutable_academic_references(client, session_data):
    assert (
        client.patch(
            f"/api/v1/sessions/{session_data['id']}",
            json={
                "section_id": str(uuid4()),
                "reason": "Wrong course",
            },
        ).status_code
        == 422
    )


def test_academic_outage_blocks_changes(client, session_data, academic, db):
    academic.failure = DependencyUnavailable()
    assert (
        client.post(
            "/api/v1/sessions",
            json={"section_id": str(academic.section.id), "session_date": "2026-10-08"},
        ).status_code
        == 503
    )
    assert client.put(records_url(session_data), json=bulk_payload(academic)).status_code == 503
    assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 0
    assert client.get("/health").status_code == 200


def test_bulk_outbox_failure_rolls_back_records(client, session_data, academic, db, monkeypatch):
    from app.repositories.attendance import AttendanceRepository

    original = AttendanceRepository.add

    def fail_event(self, row):
        if isinstance(row, OutboxEvent):
            raise RuntimeError("outbox storage failed")
        return original(self, row)

    monkeypatch.setattr(AttendanceRepository, "add", fail_event)
    with pytest.raises(RuntimeError, match="outbox storage failed"):
        client.put(records_url(session_data), json=bulk_payload(academic))
    assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 0


def test_correction_failure_rolls_back_history_and_current_value(
    client, session_data, academic, db, monkeypatch
):
    url = records_url(session_data)
    client.put(url, json=bulk_payload(academic))
    old_status = client.get(url).json()[0]["status"]
    student_id = client.get(url).json()[0]["student_user_id"]

    def fail_commit():
        raise RuntimeError("commit failure")

    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(RuntimeError):
        client.patch(f"{url}/{student_id}", json={"status": "EXCUSED", "reason": "Approved"})
    assert db.scalar(select(func.count()).select_from(AttendanceCorrection)) == 0
    assert (
        next(row for row in client.get(url).json() if row["student_user_id"] == student_id)[
            "status"
        ]
        == old_status
    )
