from __future__ import annotations

from tests.conftest import OTHER_TEACHER_ID, ROOM_2_ID, SECTION_2_ID, STUDENT_ID, TEACHER_ID


def test_admin_creates_schedule(client, schedule_payload):
    response = client.post("/api/v1/schedules", json=schedule_payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["section_id"] == schedule_payload["section_id"]
    assert body["course_id"] is not None
    assert body["status"] == "ACTIVE"


def test_teacher_creates_own_assigned_schedule(client, set_role, schedule_payload):
    set_role("teacher", TEACHER_ID)
    schedule_payload["teacher_user_id"] = None
    response = client.post("/api/v1/schedules", json=schedule_payload)
    assert response.status_code == 201, response.text
    assert response.json()["teacher_user_id"] == str(TEACHER_ID)


def test_teacher_cannot_create_for_another_teacher(client, set_role, schedule_payload):
    set_role("teacher", TEACHER_ID)
    schedule_payload["teacher_user_id"] = str(OTHER_TEACHER_ID)
    response = client.post("/api/v1/schedules", json=schedule_payload)
    assert response.status_code == 403


def test_student_cannot_create_schedule(client, set_role, schedule_payload):
    set_role("student", STUDENT_ID)
    response = client.post("/api/v1/schedules", json=schedule_payload)
    assert response.status_code == 403


def test_section_overlap_is_rejected(client, schedule_payload):
    assert client.post("/api/v1/schedules", json=schedule_payload).status_code == 201
    second = dict(schedule_payload)
    second["teacher_user_id"] = str(OTHER_TEACHER_ID)
    second["room_id"] = str(ROOM_2_ID)
    second["starts_at"] = "09:30:00"
    second["ends_at"] = "10:30:00"
    response = client.post("/api/v1/schedules", json=second)
    assert response.status_code == 409


def test_teacher_overlap_is_rejected(client, schedule_payload):
    assert client.post("/api/v1/schedules", json=schedule_payload).status_code == 201
    second = dict(schedule_payload)
    second["section_id"] = str(SECTION_2_ID)
    second["room_id"] = str(ROOM_2_ID)
    second["starts_at"] = "09:15:00"
    response = client.post("/api/v1/schedules", json=second)
    assert response.status_code == 409


def test_adjacent_times_do_not_conflict(client, schedule_payload):
    assert client.post("/api/v1/schedules", json=schedule_payload).status_code == 201
    second = dict(schedule_payload)
    second["section_id"] = str(SECTION_2_ID)
    second["room_id"] = str(ROOM_2_ID)
    second["starts_at"] = "10:00:00"
    second["ends_at"] = "11:00:00"
    response = client.post("/api/v1/schedules", json=second)
    assert response.status_code == 201, response.text


def test_update_schedule(client, schedule_payload):
    created = client.post("/api/v1/schedules", json=schedule_payload).json()
    response = client.patch(
        f"/api/v1/schedules/{created['id']}",
        json={"starts_at": "11:00:00", "ends_at": "12:00:00"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["starts_at"] == "11:00:00"
    assert response.json()["version"] == 2


def test_cancel_schedule(client, schedule_payload):
    created = client.post("/api/v1/schedules", json=schedule_payload).json()
    response = client.post(
        f"/api/v1/schedules/{created['id']}/cancel",
        json={"reason": "semester adjustment"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_cancelled_schedule_rejects_update(client, schedule_payload):
    created = client.post("/api/v1/schedules", json=schedule_payload).json()
    client.post(f"/api/v1/schedules/{created['id']}/cancel", json={})
    response = client.patch(
        f"/api/v1/schedules/{created['id']}",
        json={"starts_at": "11:00:00", "ends_at": "12:00:00"},
    )
    assert response.status_code == 409


def test_teacher_lists_only_own_schedules(client, set_role, schedule_payload):
    client.post("/api/v1/schedules", json=schedule_payload)
    set_role("teacher", TEACHER_ID)
    response = client.get("/api/v1/schedules")
    assert response.status_code == 200
    assert len(response.json()) == 1
