"""Ensure a narrowly scoped custom scheduling role is not a global admin."""
from __future__ import annotations

from tests.conftest import ADMIN_ID, TEACHER_ID
from app.security.auth import Principal


def test_custom_schedule_manager_can_publish_but_no_generic_role(client, principal_state, schedule_payload):
    custom = Principal(ADMIN_ID, frozenset({"scheduler"}), "test-token",
                       frozenset({"scheduling.schedules.manage"}))
    principal_state["principal"] = custom
    result = client.post("/api/v1/schedules", json={**schedule_payload, "publish": False})
    assert result.status_code == 201, result.text
    schedule_id = result.json()["id"]
    assert client.post(f"/api/v1/schedules/{schedule_id}/publish").status_code == 200
    assert client.get("/api/v1/schedules").status_code == 200


def test_custom_role_without_grant_is_denied(client, principal_state, schedule_payload):
    principal_state["principal"] = Principal(ADMIN_ID, frozenset({"scheduler"}), "test-token")
    assert client.post("/api/v1/schedules", json=schedule_payload).status_code == 403
    assert client.post("/api/v1/schedules/" + str(ADMIN_ID) + "/publish").status_code == 403


def test_student_cannot_publish_even_with_other_service_permission(client, principal_state, schedule_payload):
    principal_state["principal"] = Principal(TEACHER_ID, frozenset({"student"}), "test-token",
                                              frozenset({"identity.users.read"}))
    assert client.post("/api/v1/schedules", json=schedule_payload).status_code == 403
