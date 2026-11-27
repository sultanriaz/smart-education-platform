"""Gateway integration security tests for api/index.py (Vercel unified serverless entrypoint)."""

from __future__ import annotations

import importlib
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


def test_gateway_auth_idor_cors_and_access_status(tmp_path, monkeypatch):
    db_file = (tmp_path / "gateway_test.db").as_posix()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_file}")
    monkeypatch.setenv("ENVIRONMENT", "test")

    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.insert(0, root)
    if "api.index" in sys.modules:
        del sys.modules["api.index"]

    gw = importlib.import_module("api.index")

    with TestClient(gw.app) as client:
        # 1. AUTH-1: Unauthenticated access-status and protected routes return 401
        assert client.get("/api/v1/auth/access-status").status_code == 401
        assert client.get("/api/v1/identity/auth/access-status").status_code == 401
        assert client.get("/api/v1/identity/users/me").status_code == 401

        # Forged unsigned/wrong-key JWT must be rejected (401), never verify_signature=False
        import jwt as pyjwt
        forged = pyjwt.encode({"sub": str(uuid.uuid4()), "roles": ["admin"]}, "secret", algorithm="HS256")
        assert (
            client.get("/api/v1/auth/access-status", headers={"Authorization": f"Bearer {forged}"}).status_code
            == 401
        )

        # 2. CORS: Arbitrary origin & attacker *.vercel.app must not get ACAO reflection
        for bad_origin in ("https://attacker.vercel.app", "https://evil.example"):
            pre = client.options(
                "/api/v1/identity/auth/login",
                headers={"Origin": bad_origin, "Access-Control-Request-Method": "POST"},
            )
            assert pre.headers.get("access-control-allow-origin") != bad_origin
            assert pre.headers.get("access-control-allow-origin") != "*"

        # 3. Working demo logins still work & issue Argon2id-verified sessions
        for identifier, pwd, expected_role in [
            ("admin@smartedu.local", "AdminPass123!", "admin"),
            ("FAC-101", "TeacherPass123!", "teacher"),
            ("BCS-155", "StudentPass123!", "student"),
        ]:
            login = client.post(
                "/api/v1/identity/auth/login",
                headers={"Origin": "http://localhost:5173"},
                json={"identifier": identifier, "password": pwd},
            )
            assert login.status_code == 200, f"Login failed for {identifier}: {login.text}"
            tok = login.json()["access_token"]
            status_res = client.get(
                "/api/v1/auth/access-status",
                headers={"Authorization": f"Bearer {tok}"},
            )
            assert status_res.status_code == 200
            assert expected_role in status_res.json()["roles"]

        # 4. AUTH-4: Logout revokes active access token on gateway /access-status too
        stud_login = client.post(
            "/api/v1/identity/auth/login",
            headers={"Origin": "http://localhost:5173"},
            json={"identifier": "student@smartedu.local", "password": "StudentPass123!"},
        )
        assert stud_login.status_code == 200
        stud_tok = stud_login.json()["access_token"]
        stud_hdr = {"Authorization": f"Bearer {stud_tok}", "Origin": "http://localhost:5173"}
        assert client.get("/api/v1/auth/access-status", headers=stud_hdr).status_code == 200

        logout_res = client.post("/api/v1/identity/auth/logout", headers=stud_hdr)
        assert logout_res.status_code == 204
        assert client.get("/api/v1/auth/access-status", headers=stud_hdr).status_code == 401

        # 5. AUTH-2: Gateway Academic resolver does NOT blindly return True for unassigned teacher/student
        t_login = client.post(
            "/api/v1/identity/auth/login",
            headers={"Origin": "http://localhost:5173"},
            json={"identifier": "teacher@smartedu.local", "password": "TeacherPass123!"},
        )
        t_tok = t_login.json()["access_token"]
        t_uid = client.get("/api/v1/auth/access-status", headers={"Authorization": f"Bearer {t_tok}"}).json()["user_id"]
        other_uid = str(uuid.uuid4())
        random_sec = str(uuid.uuid4())

        code, _body = gw._resolve_academic_in_process(
            f"http://localhost:8002/api/v1/teachers/{other_uid}/sections/{random_sec}/assignment",
            {"Authorization": f"Bearer {t_tok}"},
        )
        assert code == 403  # IDOR across teacher IDs rejected!

        code2, body2 = gw._resolve_academic_in_process(
            f"http://localhost:8002/api/v1/teachers/{t_uid}/sections/{random_sec}/assignment",
            {"Authorization": f"Bearer {t_tok}"},
        )
        assert code2 == 200
        assert body2["assigned"] is False and body2["valid"] is False
