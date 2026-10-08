from __future__ import annotations

from tests.conftest import SECTION_ID, STUDENT_ID, TEACHER_ID


def create_schedule(client, payload):
    response = client.post("/api/v1/schedules", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_recurring_occurrences_generated(client, schedule_payload):
    create_schedule(client, schedule_payload)
    response = client.get(
        "/api/v1/timetable/teachers/00000000-0000-0000-0000-000000000002",
        params={"start_date": "2026-10-05", "end_date": "2026-10-19"},
    )
    assert response.status_code == 200, response.text
    assert [item["occurrence_date"] for item in response.json()] == [
        "2026-10-05",
        "2026-10-12",
        "2026-10-19",
    ]


def test_cancelled_occurrence_is_omitted(client, schedule_payload):
    created = create_schedule(client, schedule_payload)
    response = client.post(
        f"/api/v1/schedules/{created['id']}/overrides",
        json={
            "occurrence_date": "2026-10-12",
            "kind": "CANCELLED",
            "reason": "holiday",
        },
    )
    assert response.status_code == 201, response.text
    timetable = client.get(
        "/api/v1/timetable/me",
        params={"start_date": "2026-10-05", "end_date": "2026-10-19"},
    )
    dates = [item["occurrence_date"] for item in timetable.json()]
    assert "2026-10-12" not in dates


def test_rescheduled_occurrence_changes_time(client, schedule_payload):
    created = create_schedule(client, schedule_payload)
    response = client.post(
        f"/api/v1/schedules/{created['id']}/overrides",
        json={
            "occurrence_date": "2026-10-12",
            "kind": "RESCHEDULED",
            "starts_at": "13:00:00",
            "ends_at": "14:00:00",
            "reason": "guest lecture",
        },
    )
    assert response.status_code == 201, response.text
    timetable = client.get(
        "/api/v1/timetable/me",
        params={"start_date": "2026-10-12", "end_date": "2026-10-12"},
    )
    assert timetable.status_code == 200
    assert timetable.json()[0]["starts_at"] == "13:00:00"
    assert timetable.json()[0]["source"] == "override"


def test_student_me_timetable_uses_academic_sections(client, set_role, schedule_payload):
    create_schedule(client, schedule_payload)
    set_role("student", STUDENT_ID)
    response = client.get(
        "/api/v1/timetable/me",
        params={"start_date": "2026-10-05", "end_date": "2026-10-05"},
    )
    assert response.status_code == 200
    assert response.json()[0]["section_id"] == str(SECTION_ID)


def test_student_cannot_view_unenrolled_section(client, set_role, schedule_payload):
    create_schedule(client, schedule_payload)
    set_role("student", STUDENT_ID)
    response = client.get(
        "/api/v1/timetable/sections/10000000-0000-0000-0000-000000000002",
        params={"start_date": "2026-10-05", "end_date": "2026-10-05"},
    )
    assert response.status_code == 403


def test_teacher_me_timetable_is_scoped(client, set_role, schedule_payload):
    create_schedule(client, schedule_payload)
    set_role("teacher", TEACHER_ID)
    response = client.get(
        "/api/v1/timetable/me",
        params={"start_date": "2026-10-05", "end_date": "2026-10-05"},
    )
    assert response.status_code == 200
    assert response.json()[0]["teacher_user_id"] == str(TEACHER_ID)


def test_large_date_range_rejected(client, schedule_payload):
    create_schedule(client, schedule_payload)
    response = client.get(
        "/api/v1/timetable/me",
        params={"start_date": "2026-01-01", "end_date": "2026-12-31"},
    )
    assert response.status_code == 409
