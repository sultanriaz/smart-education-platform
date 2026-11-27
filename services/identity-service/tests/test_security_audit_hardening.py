"""End-to-end security verification tests for Identity & Gateway hardening (AUTH-1..AUTH-5)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.v1.endpoints.auth import login_guard
from app.db.session import get_db
from app.domain.entities.user import User
from app.main import app
from app.sprint18 import security_settings
from app.sprint18_security.adapters import AccountAdapter, SecurityAuditAdapter, SecurityNotificationAdapter
from app.sprint18_security.service import IdentitySecurityService


def _register_and_login(client: TestClient, email: str, full_name: str, password: str = "StrongPass123!") -> dict:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert reg.status_code == 201, reg.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return {"user": reg.json(), "access_token": login.json()["access_token"]}


def test_unauthenticated_and_non_admin_access_rejected(client: TestClient):
    # AUTH-1: Unauthenticated requests to protected endpoints return 401
    for method, path in [
        ("GET", "/api/v1/users/me"),
        ("PATCH", "/api/v1/users/me"),
        ("GET", "/api/v1/users"),
        ("POST", "/api/v1/users"),
        ("GET", "/api/v1/roles"),
        ("POST", "/api/v1/roles"),
        ("GET", "/api/v1/users/me/security-history"),
        ("GET", "/api/v1/users/security-history"),
        ("GET", "/api/v1/auth/access-status"),
    ]:
        res = client.request(method, path)
        assert res.status_code == 401, f"{method} {path} returned {res.status_code}"

    # AUTH-3: Non-admin (student) calling admin routes gets 403
    student = _register_and_login(client, "stud-sec@example.edu", "Student Sec")
    headers = {"Authorization": f"Bearer {student['access_token']}"}
    assert client.get("/api/v1/users", headers=headers).status_code == 403
    assert client.post(
        "/api/v1/users",
        headers=headers,
        json={"email": "x@example.edu", "full_name": "X Y", "password": "StrongPass123!"},
    ).status_code == 403
    assert client.get("/api/v1/roles", headers=headers).status_code == 403
    assert client.post(
        "/api/v1/roles",
        headers=headers,
        json={"name": "rogue-role", "permissions": []},
    ).status_code == 403
    assert client.get("/api/v1/users/security-history", headers=headers).status_code == 403
    assert client.get(f"/api/v1/users/{uuid.uuid4()}", headers=headers).status_code == 403


def test_mass_assignment_rejected_on_register_and_self_update(client: TestClient):
    # AUTH-3: Role / privilege mass assignment rejected with 422
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "mass@example.edu",
            "full_name": "Mass Assign",
            "password": "StrongPass123!",
            "roles": ["admin"],
            "is_active": True,
        },
    )
    assert reg.status_code == 422

    student = _register_and_login(client, "selfupd@example.edu", "Self Update")
    headers = {"Authorization": f"Bearer {student['access_token']}"}
    patch = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Updated Self", "roles": ["admin"], "is_verified": True},
    )
    assert patch.status_code == 422


def test_logout_revokes_both_refresh_and_active_access_tokens(client: TestClient):
    # AUTH-4: Logout invalidates refresh session AND live access tokens via auth_version bump
    user = _register_and_login(client, "logout@example.edu", "Logout User")
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    assert client.get("/api/v1/users/me", headers=headers).status_code == 200
    assert client.get("/api/v1/auth/access-status", headers=headers).status_code == 200

    res = client.post("/api/v1/auth/logout", headers=headers)
    assert res.status_code == 204
    assert res.headers.get("cache-control") == "no-store"

    # Active access token must now be rejected immediately!
    assert client.get("/api/v1/users/me", headers=headers).status_code == 401
    assert client.get("/api/v1/auth/access-status", headers=headers).status_code == 401
    # Refresh cookie must also fail!
    assert client.post("/api/v1/auth/refresh").status_code == 401


def test_csrf_and_cors_reject_arbitrary_origins_and_vercel_subdomains(client: TestClient):
    # AUTH-4: No wildcard CORS or arbitrary *.vercel.app CSRF bypass
    user = _register_and_login(client, "csrf@example.edu", "CSRF User")
    assert user["access_token"]

    for bad_origin in ("https://attacker.vercel.app", "https://evil.example"):
        resp_refresh = client.post("/api/v1/auth/refresh", headers={"Origin": bad_origin})
        assert resp_refresh.status_code == 403
        resp_logout = client.post("/api/v1/auth/logout", headers={"Origin": bad_origin})
        assert resp_logout.status_code == 403

        preflight = client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": bad_origin,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert preflight.headers.get("access-control-allow-origin") != "*"
        assert preflight.headers.get("access-control-allow-origin") != bad_origin


def test_argon2_hash_and_identifier_lookup_safety(client: TestClient, db):
    # AUTH-4 & AUTH-5: Argon2id stored, and broad substring identifier login rejected
    _register_and_login(client, "alice.unique@example.edu", "Alice Unique")
    user = db.scalar(select(User).where(User.email == "alice.unique@example.edu"))
    assert user is not None
    assert user.password_hash.startswith("$argon2id$")

    # Substring '@' or 'Alice' must NOT match user
    assert client.post(
        "/api/v1/auth/login", json={"identifier": "alice", "password": "StrongPass123!"}
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/login", json={"identifier": "@", "password": "StrongPass123!"}
    ).status_code == 401
    # Full email succeeds
    assert client.post(
        "/api/v1/auth/login",
        json={"email": "alice.unique@example.edu", "password": "StrongPass123!"},
    ).status_code == 200


def test_db_backed_lockout_and_account_flow_throttling_without_redis(db):
    # AUTH-5: Persistent DB-backed login lockout + alias rotation defense + forgot throttling (no Redis)
    from sqlalchemy.orm import sessionmaker
    from tests.conftest import engine

    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    # Ensure login_guard uses DB fallback (not MemoryLockoutStore)
    app.dependency_overrides.pop(login_guard, None)

    from app.sprint18_security.throttle_store import DatabaseLockoutStore
    from smartedu_security import LoginSecurityGuard

    db_guard = LoginSecurityGuard(DatabaseLockoutStore(TestSession, max_failures=5))
    app.dependency_overrides[login_guard] = lambda: db_guard
    security_settings().refresh_cookie_path = "/api/v1/auth"

    with TestClient(app) as tc:
        tc.headers["Origin"] = "http://localhost:5173"
        user_res = tc.post(
            "/api/v1/auth/register",
            json={
                "email": "student@smartedu.local",
                "full_name": "Student Alias",
                "password": "StrongPass123!",
            },
        )
        assert user_res.status_code == 201

        # 3 failed attempts via BCS-155 alias, 2 via full email -> locked on 6th regardless of alias!
        for i in range(3):
            assert (
                tc.post("/api/v1/auth/login", json={"identifier": "BCS-155", "password": "WrongPassword123!"}).status_code
                == 401
            )
        for i in range(2):
            assert (
                tc.post("/api/v1/auth/login", json={"email": "student@smartedu.local", "password": "WrongPassword123!"}).status_code
                == 401
            )
        locked = tc.post("/api/v1/auth/login", json={"identifier": "student", "password": "StrongPass123!"})
        assert locked.status_code == 429

        # Forgot-password throttling (limit=5 per 900s) active even without Redis
        for _ in range(5):
            r = tc.post("/api/v1/auth/password/forgot", json={"email": "nonexistent@example.edu"})
            assert r.status_code == 202
            assert r.json() == {"message": "If the account is eligible, instructions will be sent."}
        throttled = tc.post("/api/v1/auth/password/forgot", json={"email": "nonexistent@example.edu"})
        assert throttled.status_code == 429
    app.dependency_overrides.clear()


def test_password_reset_single_use_and_revokes_access_tokens(client: TestClient, db):
    # AUTH-5: Reset token is single-use and bumps auth_version, revoking prior access tokens
    user_data = _register_and_login(client, "resetme@example.edu", "Reset User")
    old_headers = {"Authorization": f"Bearer {user_data['access_token']}"}
    assert client.get("/api/v1/users/me", headers=old_headers).status_code == 200

    # Capture plaintext token via custom notification sink
    captured = {}

    class CaptureNotify(SecurityNotificationAdapter):
        def queue_password_reset(self, *, user_id, email, token, expires_in_seconds):
            captured["token"] = token
            captured["ttl"] = expires_in_seconds

    svc = IdentitySecurityService(
        db=db,
        accounts=AccountAdapter(db),
        notifications=CaptureNotify(db),
        audit=SecurityAuditAdapter(db),
        settings=security_settings(),
    )
    svc.request_password_reset("resetme@example.edu")
    assert "token" in captured
    assert captured["ttl"] == 1800

    # First reset succeeds
    r1 = client.post(
        "/api/v1/auth/password/reset",
        json={"token": captured["token"], "new_password": "BrandNewStrongPass99!"},
    )
    assert r1.status_code == 204
    # Replay of the same token fails (single-use)
    r2 = client.post(
        "/api/v1/auth/password/reset",
        json={"token": captured["token"], "new_password": "AnotherStrongPass99!"},
    )
    assert r2.status_code == 400

    # Pre-reset access token is revoked!
    assert client.get("/api/v1/users/me", headers=old_headers).status_code == 401
    # New password works
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetme@example.edu", "password": "BrandNewStrongPass99!"},
    )
    assert new_login.status_code == 200
