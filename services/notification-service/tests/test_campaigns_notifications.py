from __future__ import annotations

import uuid

from app.domain.models import DeliveryAttempt, NotificationPreference
from app.services.delivery_service import DeliveryService
from app.services.target_resolver import ResolvedRecipient


def _admin(client, identities):
    client.set_principal(identities["admin"], {"admin"})


def _student(client, identities):
    client.set_principal(identities["student"], {"student"})


def test_admin_can_create_direct_campaign(client, identities, dispatcher):
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {
                "kind": "DIRECT",
                "recipients": [{"user_id": str(identities["student"])}],
            },
            "title": "Class update",
            "body": "Room changed",
            "category": "schedule",
            "channels": ["IN_APP"],
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["recipient_count"] == 1
    assert dispatcher.deliveries == []

    _student(client, identities)
    response = client.get("/api/v1/notifications")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Class update"


def test_non_admin_cannot_create_campaign(client, identities):
    _student(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "title": "No",
            "body": "No",
        },
    )
    assert response.status_code == 403


def test_notification_cannot_be_read_by_another_user(client, identities):
    _admin(client, identities)
    created = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "title": "Private",
            "body": "Student only",
        },
    )
    assert created.status_code == 201
    _student(client, identities)
    notification_id = client.get("/api/v1/notifications").json()["items"][0]["id"]
    client.set_principal(identities["other"], {"student"})
    response = client.get(f"/api/v1/notifications/{notification_id}")
    assert response.status_code == 403


def test_mark_read_and_unread_count(client, identities):
    _admin(client, identities)
    client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "title": "Hello",
            "body": "World",
        },
    )
    _student(client, identities)
    assert client.get("/api/v1/notifications/unread-count").json()["unread_count"] == 1
    notification_id = client.get("/api/v1/notifications").json()["items"][0]["id"]
    response = client.post(f"/api/v1/notifications/{notification_id}/read")
    assert response.status_code == 200
    assert response.json()["status"] == "READ"
    assert client.get("/api/v1/notifications/unread-count").json()["unread_count"] == 0


def test_mark_all_read(client, identities):
    _admin(client, identities)
    for index in range(2):
        client.post(
            "/api/v1/admin/campaigns",
            json={
                "target": {
                    "kind": "DIRECT",
                    "recipients": [{"user_id": str(identities["student"])}],
                },
                "title": f"N{index}",
                "body": "Body",
            },
        )
    _student(client, identities)
    response = client.post("/api/v1/notifications/read-all")
    assert response.status_code == 200
    assert "2" in response.json()["message"]
    assert client.get("/api/v1/notifications/unread-count").json()["unread_count"] == 0


def test_archive_removes_from_list(client, identities):
    _admin(client, identities)
    client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "title": "Archive me",
            "body": "Body",
        },
    )
    _student(client, identities)
    notification_id = client.get("/api/v1/notifications").json()["items"][0]["id"]
    assert client.delete(f"/api/v1/notifications/{notification_id}").status_code == 200
    assert client.get("/api/v1/notifications").json()["total"] == 0


def test_muted_category_is_not_visible(client, identities, db):
    db.add(
        NotificationPreference(
            user_id=identities["student"],
            in_app_enabled=True,
            email_enabled=True,
            muted_categories=["schedule"],
        )
    )
    db.commit()
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {
                "kind": "DIRECT",
                "recipients": [{"user_id": str(identities["student"]), "email": "s@example.edu"}],
            },
            "title": "Muted",
            "body": "Body",
            "category": "schedule",
            "channels": ["IN_APP", "EMAIL"],
        },
    )
    assert response.status_code == 201
    _student(client, identities)
    assert client.get("/api/v1/notifications").json()["total"] == 0
    attempts = db.query(DeliveryAttempt).all()
    assert {item.status for item in attempts} == {"SKIPPED"}


def test_role_target_uses_resolver(client, identities, fake_resolver):
    fake_resolver.role_users = [ResolvedRecipient(identities["student"])]
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "ROLE", "role": "student"},
            "title": "All students",
            "body": "Campus update",
        },
    )
    assert response.status_code == 201
    assert response.json()["recipient_count"] == 1


def test_section_target_uses_resolver(client, identities, fake_resolver):
    fake_resolver.section_users = [ResolvedRecipient(identities["student"])]
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "SECTION", "section_id": str(uuid.uuid4())},
            "title": "Section",
            "body": "Section update",
        },
    )
    assert response.status_code == 201
    assert response.json()["recipient_count"] == 1


class FakeEmailProvider:
    def __init__(self, fail=False):
        self.fail = fail
        self.sent = []

    def send(self, *, to_email, subject, body):
        if self.fail:
            raise RuntimeError("provider down")
        self.sent.append((to_email, subject, body))
        return "message-1"


def test_email_delivery_can_be_processed(client, identities, db, dispatcher):
    db.add(
        NotificationPreference(
            user_id=identities["student"],
            in_app_enabled=True,
            email_enabled=True,
            muted_categories=[],
        )
    )
    db.commit()
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {
                "kind": "DIRECT",
                "recipients": [
                    {"user_id": str(identities["student"]), "email": "student@example.edu"}
                ],
            },
            "title": "Email",
            "body": "Email body",
            "channels": ["EMAIL"],
        },
    )
    assert response.status_code == 201
    assert len(dispatcher.deliveries) == 1
    provider = FakeEmailProvider()
    DeliveryService(db, provider).deliver(dispatcher.deliveries[0])
    attempt = db.get(DeliveryAttempt, dispatcher.deliveries[0])
    assert attempt.status == "SENT"
    assert provider.sent[0][0] == "student@example.edu"


def test_email_failure_creates_retry(client, identities, db, dispatcher):
    db.add(
        NotificationPreference(
            user_id=identities["student"],
            in_app_enabled=True,
            email_enabled=True,
            muted_categories=[],
        )
    )
    db.commit()
    _admin(client, identities)
    client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {
                "kind": "DIRECT",
                "recipients": [
                    {"user_id": str(identities["student"]), "email": "student@example.edu"}
                ],
            },
            "title": "Email",
            "body": "Email body",
            "channels": ["EMAIL"],
        },
    )
    retry_id = DeliveryService(db, FakeEmailProvider(fail=True)).deliver(dispatcher.deliveries[0])
    assert retry_id is not None
    assert db.get(DeliveryAttempt, retry_id).attempt_number == 2
