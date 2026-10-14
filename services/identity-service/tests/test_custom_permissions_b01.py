"""B01 verifies real signed tokens and real Identity route authorization."""
from __future__ import annotations

from sqlalchemy import select

from app.domain.entities.role import Permission, Role
from app.domain.entities.user import User
from app.security.jwt import decode_token


def _login(client, email):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123!"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_custom_permissions_read_only_and_revocation(client, db):
    for permission_code in ("identity.users.read", "identity.users.write", "identity.roles.read"):
        db.add(Permission(code=permission_code, description=permission_code))
    db.flush()
    custom = Role(name="auditor", description="Read accounts", permissions=[
        db.scalar(select(Permission).where(Permission.code == "identity.users.read"))
    ])
    db.add(custom)
    db.commit()
    email = "auditor-b01@example.edu"
    user = User(email=email, full_name="Campus Auditor", password_hash="", roles=[custom], is_verified=True)
    from app.security.password import hash_password
    user.password_hash = hash_password("StrongPass123!")
    db.add(user)
    db.commit()
    token = _login(client, email)
    claims = decode_token(token)
    assert claims["roles"] == ["auditor"]
    assert claims["permissions"] == ["identity.users.read"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/users", headers=headers).status_code == 200
    assert client.get(f"/api/v1/users/{user.id}", headers=headers).status_code == 200
    assert client.post("/api/v1/users", headers=headers, json={}).status_code == 403
    assert client.get("/api/v1/roles", headers=headers).status_code == 403
    # Remove the permission. Old signed tokens must no longer authorize reads.
    custom.permissions = []
    db.commit()
    assert client.get("/api/v1/users", headers=headers).status_code == 401
    fresh = _login(client, email)
    assert decode_token(fresh)["permissions"] == []
    assert client.get("/api/v1/users", headers={"Authorization": f"Bearer {fresh}"}).status_code == 403


def test_unassigned_custom_role_denied_and_admin_compatibility(client, db):
    from app.security.password import hash_password
    custom = Role(name="observer", permissions=[])
    admin = db.scalar(select(Role).where(Role.name == "admin"))
    db.add_all([
        custom,
        User(email="observer-b01@example.edu", full_name="Observer", password_hash=hash_password("StrongPass123!"), is_verified=True, roles=[custom]),
        User(email="admin-b01@example.edu", full_name="Administrator", password_hash=hash_password("StrongPass123!"), is_verified=True, roles=[admin]),
    ])
    db.commit()
    observer_token = _login(client, "observer-b01@example.edu")
    assert client.get("/api/v1/users", headers={"Authorization": f"Bearer {observer_token}"}).status_code == 403
    admin_token = _login(client, "admin-b01@example.edu")
    assert client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
