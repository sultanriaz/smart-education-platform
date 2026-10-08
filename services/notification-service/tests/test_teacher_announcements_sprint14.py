from __future__ import annotations

import uuid

from app.services.target_resolver import ResolvedRecipient


class AllowAcademic:
    def validate_teacher_assignment(self, teacher_user_id, section_id, forwarded_token=None):
        return True


class DenyAcademic:
    def validate_teacher_assignment(self, teacher_user_id, section_id, forwarded_token=None):
        return False


def test_teacher_can_send_assigned_section_announcement(
    client,
    identities,
    fake_resolver,
):
    fake_resolver.academic = AllowAcademic()
    fake_resolver.section_users = [ResolvedRecipient(identities["student"])]

    client.set_principal(identities["teacher"], {"teacher"})
    section_id = uuid.uuid4()

    response = client.post(
        "/api/v1/teacher/announcements",
        json={
            "section_id": str(section_id),
            "title": "Lab moved",
            "body": "Use Lab 4 today.",
            "channels": ["IN_APP"],
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["recipient_count"] == 1
    assert body["target_kind"] == "SECTION"

    listed = client.get("/api/v1/teacher/announcements")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_teacher_cannot_announce_to_unassigned_section(
    client,
    identities,
    fake_resolver,
):
    fake_resolver.academic = DenyAcademic()
    client.set_principal(identities["teacher"], {"teacher"})

    response = client.post(
        "/api/v1/teacher/announcements",
        json={
            "section_id": str(uuid.uuid4()),
            "title": "No access",
            "body": "Should be rejected.",
            "channels": ["IN_APP"],
        },
    )

    assert response.status_code == 403


def test_student_cannot_use_teacher_announcement_api(client, identities):
    client.set_principal(identities["student"], {"student"})

    response = client.post(
        "/api/v1/teacher/announcements",
        json={
            "section_id": str(uuid.uuid4()),
            "title": "No",
            "body": "No",
            "channels": ["IN_APP"],
        },
    )

    assert response.status_code == 403
