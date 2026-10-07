from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.domain.models import OutboxEvent
from app.services.statistics import calculate_counts
from tests.conftest import bulk_payload


def test_teacher_assignment_boundaries(client, token, session_data, academic):
    client.headers["Authorization"] = (
        f"Bearer {token(subject=academic.teacher_id, roles=['teacher'])}"
    )
    base = f"/api/v1/sessions/{session_data['id']}"
    assert client.get(base).status_code == 200
    assert len(client.get("/api/v1/sessions").json()) == 1
    assert (
        client.post(
            "/api/v1/sessions",
            json={"section_id": str(academic.other_section.id), "session_date": "2026-10-07"},
        ).status_code
        == 403
    )
    assert client.get(f"/api/v1/sections/{academic.other_section.id}/summary").status_code == 403
    assert client.put(base + "/records", json=bulk_payload(academic)).status_code == 200
    assert (
        client.patch(
            base + f"/records/{academic.students[0]}",
            json={
                "status": "LATE",
                "reason": "Arrived later",
            },
        ).status_code
        == 200
    )
    assert client.post(base + "/finalize").status_code == 200
    assert (
        client.patch(
            base + f"/records/{academic.students[0]}",
            json={
                "status": "ABSENT",
                "reason": "Change",
            },
        ).status_code
        == 409
    )
    assert client.post(base + "/reopen", json={"reason": "Override"}).status_code == 403
    assert client.post(base + "/cancel", json={"reason": "Override"}).status_code == 403
    assert client.get(base + "/history").status_code == 200
    academic.teacher_id = uuid4()
    assert client.get(base).status_code == 403
    assert client.get(base + "/records").status_code == 403
    assert client.get("/api/v1/sessions").json() == []
    assert client.get("/api/v1/reports/low-attendance").json() == []


def test_students_cannot_mutate_or_read_staff_resources(client, token, session_data, academic):
    client.headers["Authorization"] = (
        f"Bearer {token(subject=academic.students[0], roles=['student'])}"
    )
    base = f"/api/v1/sessions/{session_data['id']}"
    for path in [
        "/api/v1/sessions",
        base,
        base + "/records",
        base + "/history",
        f"/api/v1/sections/{academic.section.id}/summary",
        f"/api/v1/sections/{academic.section.id}/attendance",
        f"/api/v1/sections/{academic.section.id}/students/{academic.students[1]}/summary",
        "/api/v1/reports/low-attendance",
    ]:
        assert client.get(path).status_code == 403
    assert (
        client.post(
            "/api/v1/sessions",
            json={"section_id": str(academic.section.id), "session_date": "2026-10-08"},
        ).status_code
        == 403
    )
    assert client.put(base + "/records", json=bulk_payload(academic)).status_code == 403
    assert (
        client.patch(
            base + f"/records/{academic.students[0]}",
            json={
                "status": "PRESENT",
                "reason": "Self marking",
            },
        ).status_code
        == 403
    )
    assert (
        client.patch(base, json={"starts_at": "08:00", "reason": "Self change"}).status_code == 403
    )
    for action in ("finalize", "reopen", "cancel"):
        assert client.post(base + "/" + action, json={"reason": "Override"}).status_code == 403


def test_student_self_views_never_return_other_students_or_call_academic(
    client, token, session_data, academic
):
    base = f"/api/v1/sessions/{session_data['id']}"
    client.put(base + "/records", json=bulk_payload(academic))
    before = academic.calls
    student_id = academic.students[0]
    client.headers["Authorization"] = f"Bearer {token(subject=student_id, roles=['student'])}"
    response = client.get(f"/api/v1/students/me/attendance?student_user_id={academic.students[1]}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["student_user_id"] == str(student_id)
    assert response.json()[0]["session_status"] == "OPEN"
    assert (
        client.get("/api/v1/students/me/attendance/summary").json()["totals"][
            "attendance_percentage"
        ]
        is None
    )
    assert academic.calls == before


def test_finalized_statistics_course_breakdown_and_low_events(
    client, token, session_data, academic, db
):
    base = f"/api/v1/sessions/{session_data['id']}"
    client.put(base + "/records", json=bulk_payload(academic))
    assert client.post(base + "/finalize").status_code == 200
    summary = client.get(f"/api/v1/sections/{academic.section.id}/summary").json()
    assert summary == {
        "present_sessions": 1,
        "absent_sessions": 1,
        "late_sessions": 1,
        "excused_sessions": 0,
        "total_considered_sessions": 3,
        "attendance_percentage": 66.67,
        "is_low_attendance": True,
    }
    report = client.get("/api/v1/reports/low-attendance").json()
    assert len(report) == 1 and report[0]["student_user_id"] == str(academic.students[1])
    events = list(
        db.scalars(
            select(OutboxEvent).where(
                OutboxEvent.event_type == "attendance.low_attendance_detected",
            )
        )
    )
    assert len(events) == 1
    assert events[0].payload["student_user_id"] == str(academic.students[1])
    for student_id, percent in zip(academic.students, [100.0, 0.0, 100.0], strict=True):
        client.headers["Authorization"] = f"Bearer {token(subject=student_id, roles=['student'])}"
        result = client.get("/api/v1/students/me/attendance/summary").json()
        assert result["totals"]["attendance_percentage"] == percent
        assert result["by_section"][0]["section_id"] == str(academic.section.id)
        assert result["by_course"][0]["course_id"] == str(academic.section.course_id)


def test_excused_and_cancelled_are_excluded_from_percentage(client, token, session_data, academic):
    base = f"/api/v1/sessions/{session_data['id']}"
    client.put(base + "/records", json=bulk_payload(academic, ["EXCUSED", "PRESENT", "LATE"]))
    client.post(base + "/finalize")
    summary = client.get(f"/api/v1/sections/{academic.section.id}/summary").json()
    assert summary["attendance_percentage"] == 100.0
    assert summary["total_considered_sessions"] == 2
    assert summary["excused_sessions"] == 1
    client.post(base + "/cancel", json={"reason": "Class cancelled"})
    assert (
        client.get(f"/api/v1/sections/{academic.section.id}/summary").json()[
            "attendance_percentage"
        ]
        is None
    )
    client.headers["Authorization"] = (
        f"Bearer {token(subject=academic.students[0], roles=['student'])}"
    )
    assert client.get("/api/v1/students/me/attendance").json() == []


def test_admin_self_endpoint_requires_student_role(client):
    assert client.get("/api/v1/students/me/attendance").status_code == 403


def test_date_filters_pagination_and_consistent_errors(client, session_data):
    assert len(client.get("/api/v1/sessions?limit=1").json()) == 1
    assert client.get("/api/v1/sessions?date_from=2026-10-08").json() == []
    response = client.get("/api/v1/sessions?date_from=2026-10-08&date_to=2026-10-01")
    assert response.status_code == 422
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert client.get("/api/v1/sessions?limit=101").status_code == 422
    assert client.get("/api/v1/sessions?offset=-1").status_code == 422


@pytest.mark.parametrize(
    ("statuses", "percentage", "low"),
    [
        ([], None, False),
        (["EXCUSED"], None, False),
        (["LATE"], 100.0, False),
        (["PRESENT", "ABSENT", "PRESENT", "PRESENT"], 75.0, False),
        (["PRESENT", "ABSENT", "ABSENT"], 33.33, True),
    ],
)
def test_percentage_policy(statuses, percentage, low):
    rows = [{"status": status, "count": 1} for status in statuses]
    result = calculate_counts(rows, 75)
    assert result.attendance_percentage == percentage
    assert result.is_low_attendance == low


def test_role_headers_do_not_grant_access(client, token, academic):
    client.headers["Authorization"] = f"Bearer {token(roles=['student'])}"
    assert (
        client.post(
            "/api/v1/sessions",
            headers={"X-Role": "admin"},
            json={
                "section_id": str(academic.section.id),
                "session_date": "2026-10-07",
            },
        ).status_code
        == 403
    )
