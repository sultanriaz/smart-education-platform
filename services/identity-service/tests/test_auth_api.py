def test_register_login_and_me(client):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@example.edu",
            "full_name": "Test Student",
            "password": "StrongPass123!",
        },
    )
    assert register.status_code == 201, register.text
    assert "student" in register.json()["roles"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.edu", "password": "StrongPass123!"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "student@example.edu"


def test_duplicate_registration_rejected(client):
    payload = {
        "email": "duplicate@example.edu",
        "full_name": "Duplicate Student",
        "password": "StrongPass123!",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_refresh_logout_and_wrong_token_types(client):
    payload = {
        "email": "rotate@example.edu",
        "full_name": "Rotate Student",
        "password": "StrongPass123!",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    login = client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200
    assert "refresh_token" not in login.json()
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=strict" in login.headers["set-cookie"]
    original = client.cookies.get("sep_refresh")
    assert (
        client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {original}"}).status_code
        == 401
    )
    client.cookies.clear()
    client.cookies.set(
        "sep_refresh", login.json()["access_token"], domain="testserver.local", path="/api/v1/auth"
    )
    assert client.post("/api/v1/auth/refresh").status_code == 401
    client.cookies.clear()
    client.cookies.set("sep_refresh", original, domain="testserver.local", path="/api/v1/auth")
    replacement = client.post("/api/v1/auth/refresh")
    assert replacement.status_code == 200
    current = client.cookies.get("sep_refresh")
    assert current != original
    client.cookies.clear()
    client.cookies.set("sep_refresh", original, domain="testserver.local", path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401
    client.cookies.clear()
    client.cookies.set("sep_refresh", current, domain="testserver.local", path="/api/v1/auth")
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.cookies.get("sep_refresh") is None
    client.cookies.set("sep_refresh", current, domain="testserver.local", path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_refresh_rejects_untrusted_and_missing_origins(client):
    client.headers.pop("Origin")
    assert client.post("/api/v1/auth/refresh").status_code == 403
    assert (
        client.post("/api/v1/auth/logout", headers={"Origin": "https://evil.example"}).status_code
        == 403
    )


def test_login_account_lockout_applies_to_unknown_accounts(client):
    payload = {"email": "unknown@example.edu", "password": "WrongPassword123!"}
    for _ in range(5):
        assert client.post("/api/v1/auth/login", json=payload).status_code == 401
    locked = client.post("/api/v1/auth/login", json=payload)
    assert locked.status_code == 429
    assert int(locked.headers["retry-after"]) > 0


def test_weak_registration_password_is_rejected(client):
    result = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.edu", "full_name": "Weak User", "password": "password123"},
    )
    assert result.status_code == 422


def test_admin_user_and_role_writes_commit(client, db):
    from sqlalchemy import select

    from app.domain.entities.role import Role
    from app.domain.entities.user import User

    registration = {
        "email": "admin-test@example.edu",
        "full_name": "Test Admin",
        "password": "StrongPass123!",
    }
    assert client.post("/api/v1/auth/register", json=registration).status_code == 201
    admin = db.scalar(select(User).where(User.email == registration["email"]))
    admin.roles = [db.scalar(select(Role).where(Role.name == "admin"))]
    db.commit()
    pair = client.post("/api/v1/auth/login", json=registration).json()
    headers = {"Authorization": f"Bearer {pair['access_token']}"}
    created = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "managed@example.edu",
            "full_name": "Managed Student",
            "password": "StrongPass123!",
        },
    )
    assert created.status_code == 201
    assert not db.in_transaction()
    assert (
        client.patch(
            f"/api/v1/users/{created.json()['id']}",
            headers=headers,
            json={
                "full_name": "Updated Student",
            },
        ).status_code
        == 200
    )
    assert not db.in_transaction()
    assert (
        client.post(
            "/api/v1/roles",
            headers=headers,
            json={
                "name": "catalog-reader",
                "permissions": [],
            },
        ).status_code
        == 201
    )
    assert not db.in_transaction()
    assert (
        client.post(
            "/api/v1/roles",
            headers=headers,
            json={
                "name": "catalog-reader",
                "permissions": [],
            },
        ).status_code
        == 409
    )
    assert not db.in_transaction()
    assert (
        client.delete(f"/api/v1/users/{created.json()['id']}", headers=headers).status_code == 200
    )
    assert not db.in_transaction()
