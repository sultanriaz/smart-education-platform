from __future__ import annotations


def _admin(client, identities):
    client.set_principal(identities["admin"], {"admin"})


def test_create_template(client, identities):
    _admin(client, identities)
    response = client.post(
        "/api/v1/admin/templates",
        json={
            "code": "schedule.changed",
            "title_template": "Schedule changed: {course}",
            "body_template": "Your class is now in {room}",
            "category": "schedule",
            "default_channels": ["IN_APP"],
        },
    )
    assert response.status_code == 201
    assert response.json()["code"] == "schedule.changed"


def test_duplicate_template_code_rejected(client, identities):
    _admin(client, identities)
    payload = {
        "code": "same.code",
        "title_template": "Title",
        "body_template": "Body",
        "default_channels": ["IN_APP"],
    }
    assert client.post("/api/v1/admin/templates", json=payload).status_code == 201
    assert client.post("/api/v1/admin/templates", json=payload).status_code == 409


def test_template_campaign_renders(client, identities):
    _admin(client, identities)
    client.post(
        "/api/v1/admin/templates",
        json={
            "code": "exam.reminder",
            "title_template": "Exam: {course}",
            "body_template": "Starts at {time}",
            "category": "assessment",
            "default_channels": ["IN_APP"],
        },
    )
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "template_code": "exam.reminder",
            "template_data": {"course": "SE", "time": "09:00"},
        },
    )
    assert response.status_code == 201, response.text
    client.set_principal(identities["student"], {"student"})
    item = client.get("/api/v1/notifications").json()["items"][0]
    assert item["title"] == "Exam: SE"
    assert item["body"] == "Starts at 09:00"


def test_template_missing_variable_rejected(client, identities):
    _admin(client, identities)
    client.post(
        "/api/v1/admin/templates",
        json={
            "code": "missing.variable",
            "title_template": "Hello {name}",
            "body_template": "Body",
            "default_channels": ["IN_APP"],
        },
    )
    response = client.post(
        "/api/v1/admin/campaigns",
        json={
            "target": {"kind": "DIRECT", "recipients": [{"user_id": str(identities["student"])}]},
            "template_code": "missing.variable",
            "template_data": {},
        },
    )
    assert response.status_code == 422
