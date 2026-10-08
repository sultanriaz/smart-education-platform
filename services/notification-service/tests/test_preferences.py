from __future__ import annotations


def test_default_preferences(client):
    response = client.get("/api/v1/preferences/me")
    assert response.status_code == 200
    body = response.json()
    assert body["in_app_enabled"] is True
    assert body["email_enabled"] is False


def test_update_preferences(client):
    response = client.patch(
        "/api/v1/preferences/me",
        json={"email_enabled": True, "muted_categories": ["finance", "finance"]},
    )
    assert response.status_code == 200
    assert response.json()["email_enabled"] is True
    assert response.json()["muted_categories"] == ["finance"]
