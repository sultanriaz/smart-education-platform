"""SmartEdu Platform — Unified Vercel Serverless API Gateway.

Dispatches all /api/v1/{service}/... endpoints to microservice routers
and connects directly to Neon PostgreSQL via DATABASE_URL or POSTGRES_URL.
"""

from __future__ import annotations

import importlib
import json as _json
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger("smartedu.vercel_gateway")
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# 1. Environment & Path Resolution
# ==============================================================================
ROOT = Path(__file__).resolve().parent.parent

# Add local libs/python packages to sys.path
libs_dir = ROOT / "libs" / "python"
if libs_dir.exists():
    for lib in sorted(libs_dir.iterdir()):
        if lib.is_dir() and str(lib) not in sys.path:
            sys.path.insert(0, str(lib))

# ==============================================================================
# 2. Database Connection Normalization (Neon PostgreSQL Support)
# ==============================================================================
def resolve_database_url() -> str:
    """Normalize Neon PostgreSQL URL or fallback to user's live Neon DB."""
    raw_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or "postgresql://neondb_owner:npg_ZaFJXBUmo3Y2@ep-square-violet-bdeonh6f-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    ).strip()

    if raw_url:
        # Normalize postgres:// to postgresql+psycopg:// for SQLAlchemy + psycopg 3
        if raw_url.startswith("postgres://"):
            raw_url = "postgresql+psycopg://" + raw_url[len("postgres://"):]
        elif raw_url.startswith("postgresql://") and "+psycopg" not in raw_url:
            raw_url = "postgresql+psycopg://" + raw_url[len("postgresql://"):]
        return raw_url

    import tempfile
    tmp_db = (Path(tempfile.gettempdir()) / "smartedu_demo.db").as_posix()
    return f"sqlite+pysqlite:///{tmp_db}"


def _default_allowed_origins() -> list[str]:
    candidates = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://smart-education-platform-teal.vercel.app",
    ]
    for env_key in ("VERCEL_URL", "VERCEL_BRANCH_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        val = (os.environ.get(env_key) or "").strip()
        if val:
            origin = val if val.startswith(("http://", "https://")) else f"https://{val}"
            candidates.append(origin)
    for raw in (os.environ.get("TRUSTED_FRONTEND_ORIGINS") or "").split(","):
        item = raw.strip().rstrip("/")
        if item and item != "*" and item.startswith(("http://", "https://")):
            candidates.append(item)
    return list(dict.fromkeys(o.rstrip("/") for o in candidates))


ALLOWED_ORIGINS = _default_allowed_origins()

DB_URL = resolve_database_url()
os.environ["DATABASE_URL"] = DB_URL
os.environ["ENVIRONMENT"] = os.environ.get("ENVIRONMENT", "development")
os.environ["JWT_ISSUER"] = os.environ.get("JWT_ISSUER", "http://localhost:8001")
os.environ["JWT_KEY_ID"] = os.environ.get("JWT_KEY_ID", "identity-dev-1")
os.environ["TRUSTED_FRONTEND_ORIGINS"] = ",".join(ALLOWED_ORIGINS)
os.environ["CORS_ORIGINS"] = _json.dumps(ALLOWED_ORIGINS)
import tempfile
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    os.environ.setdefault("REFRESH_COOKIE_SECURE", "true")
    os.environ.setdefault(
        "LOCAL_STORAGE_PATH",
        (Path(tempfile.gettempdir()) / "smartedu-learning-objects").as_posix(),
    )
os.environ["IDENTITY_SERVICE_BASE_URL"] = "http://localhost:8001"
os.environ["JWT_JWKS_URL"] = "http://localhost:8001/.well-known/jwks.json"
os.environ["SECURITY_TOKEN_PEPPER"] = os.environ.get("SECURITY_TOKEN_PEPPER", "smartedu-serverless-pepper-key-2026")
if not os.environ.get("SECURITY_NOTIFICATION_ENCRYPTION_KEY"):
    import base64
    import hashlib
    os.environ["SECURITY_NOTIFICATION_ENCRYPTION_KEY"] = base64.urlsafe_b64encode(
        hashlib.sha256(b"smartedu-serverless-sec-notification-key-2026").digest()
    ).decode()

# ==============================================================================
# 3. Deterministic RSA Key & In-Memory JWKS Infrastructure
# ==============================================================================
STATIC_PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
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
bo5SdotnVXHdx+QQ8jrygA==
-----END PRIVATE KEY-----"""


STATIC_ED25519_PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIDVLMLM6bXaAj573iZi2xnThD3BUh29sb9Q7XejI4Heb
-----END PRIVATE KEY-----"""


def setup_jwt_keys():
    """Ensure persistent RSA private key and Ed25519 keys exist across all serverless invocations."""
    import tempfile

    env_rsa_pem = (os.environ.get("JWT_PRIVATE_KEY_PEM") or "").strip()
    local_key = ROOT / "services" / "identity-service" / ".secrets" / "identity-private.pem"
    if env_rsa_pem:
        tmp_key = Path(tempfile.gettempdir()) / "smartedu-identity-private.pem"
        tmp_key.write_text(env_rsa_pem, encoding="utf-8")
        os.environ["JWT_PRIVATE_KEY_FILE"] = str(tmp_key)
    elif local_key.exists():
        os.environ["JWT_PRIVATE_KEY_FILE"] = str(local_key)
    else:
        tmp_key = Path(tempfile.gettempdir()) / "smartedu-identity-private.pem"
        tmp_key.write_text(STATIC_PRIVATE_KEY_PEM.strip(), encoding="utf-8")
        os.environ["JWT_PRIVATE_KEY_FILE"] = str(tmp_key)

    env_ed_pem = (os.environ.get("INTERNAL_SERVICE_PRIVATE_KEY_PEM") or "").strip()
    ed_pem = env_ed_pem or STATIC_ED25519_PRIVATE_KEY_PEM.strip()
    tmp_ed_key = Path(tempfile.gettempdir()) / "smartedu-internal-ed25519-private.pem"
    tmp_ed_key.write_text(ed_pem, encoding="utf-8")
    os.environ["INTERNAL_SERVICE_PRIVATE_KEY_FILE"] = str(tmp_ed_key)
    os.environ["INTERNAL_SERVICE_PRIVATE_KEY_PEM"] = ed_pem
    os.environ["INTERNAL_SERVICE_KEY_ID"] = os.environ.get("INTERNAL_SERVICE_KEY_ID", "internal-service-key-1")


setup_jwt_keys()


def get_in_memory_jwks() -> dict:
    try:
        import jwt as _jwt
        from cryptography.hazmat.primitives import serialization as _ser

        key_path = Path(os.environ["JWT_PRIVATE_KEY_FILE"])
        priv = _ser.load_pem_private_key(key_path.read_bytes(), password=None)
        jwk = _jwt.algorithms.RSAAlgorithm.to_jwk(priv.public_key(), as_dict=True)
        jwk.update(kid=os.environ.get("JWT_KEY_ID", "identity-dev-1"), use="sig", alg="RS256")
        return {"keys": [jwk]}
    except Exception as exc:
        logger.warning("Could not generate in-memory JWKS: %s", exc)
        return {"keys": []}


_IN_PROCESS_ENGINES: dict[str, Any] = {}


def _gateway_engine():
    url = os.environ.get("DATABASE_URL") or DB_URL
    eng = _IN_PROCESS_ENGINES.get(url)
    if eng is None:
        from smartedu_infra import DatabaseSettings, build_engine

        eng = build_engine(DatabaseSettings(DATABASE_URL=url, DB_APPLICATION_NAME="smartedu-gateway"))
        _IN_PROCESS_ENGINES[url] = eng
    return eng


def _gateway_tables():
    from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table, Uuid

    md = MetaData()
    return {
        "users": Table("users", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("is_active", Boolean), Column("auth_version", Integer)),
        "roles": Table("roles", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("name", String)),
        "user_roles": Table("user_roles", md, Column("user_id", Uuid(as_uuid=True)), Column("role_id", Uuid(as_uuid=True))),
        "permissions": Table("permissions", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("code", String)),
        "role_permissions": Table("role_permissions", md, Column("role_id", Uuid(as_uuid=True)), Column("permission_id", Uuid(as_uuid=True))),
        "sections": Table("sections", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("course_id", Uuid(as_uuid=True)), Column("semester_id", Uuid(as_uuid=True)), Column("is_active", Boolean)),
        "enrollments": Table("enrollments", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("student_profile_id", Uuid(as_uuid=True)), Column("section_id", Uuid(as_uuid=True)), Column("status", String)),
        "student_profiles": Table("student_academic_profiles", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("external_user_id", Uuid(as_uuid=True)), Column("student_number", String), Column("is_active", Boolean)),
        "teacher_profiles": Table("teacher_academic_profiles", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("external_user_id", Uuid(as_uuid=True)), Column("is_active", Boolean)),
        "teacher_assignments": Table("teacher_assignments", md, Column("id", Uuid(as_uuid=True), primary_key=True), Column("teacher_profile_id", Uuid(as_uuid=True)), Column("section_id", Uuid(as_uuid=True)), Column("is_active", Boolean)),
    }


_GATEWAY_TABLES = None


def _tables():
    global _GATEWAY_TABLES
    if _GATEWAY_TABLES is None:
        _GATEWAY_TABLES = _gateway_tables()
    return _GATEWAY_TABLES


def _verify_access_status_in_process(headers: dict[str, str] | None) -> tuple[int, dict[str, Any]]:
    """Verify bearer JWT signature, active state, auth_version, roles, and permissions via DB without mutating sys.modules."""
    auth_header = ""
    if headers:
        for k, v in headers.items():
            if k.lower() == "authorization":
                auth_header = v
                break
    if not auth_header.startswith("Bearer "):
        return 401, {"detail": "Missing or invalid access token."}

    token = auth_header[7:].strip()
    try:
        import uuid as _uuid

        import jwt
        from smartedu_security import decode_service_access_jwt
        from sqlalchemy import select

        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        jwks = get_in_memory_jwks()
        key_data = next(k for k in jwks.get("keys", []) if k.get("kid") == kid)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        payload = decode_service_access_jwt(
            token,
            public_key,
            issuer=os.environ.get("JWT_ISSUER", "http://localhost:8001"),
            audience=os.environ.get("JWT_ACCESS_AUDIENCE", "smart-education-api"),
            algorithms=("RS256",),
            leeway=int(os.environ.get("JWT_LEEWAY_SECONDS", "5")),
        )
        user_id = _uuid.UUID(payload["sub"])
        t = _tables()

        with _gateway_engine().connect() as conn:
            row = conn.execute(
                select(t["users"].c.is_active, t["users"].c.auth_version).where(t["users"].c.id == user_id)
            ).first()
            if row is None or not bool(row.is_active):
                return 401, {"detail": "User account is unavailable."}
            if int(payload.get("auth_version", 0)) != int(row.auth_version):
                return 401, {"detail": "Access token has been invalidated."}

            role_rows = conn.execute(
                select(t["roles"].c.name)
                .select_from(t["roles"].join(t["user_roles"], t["user_roles"].c.role_id == t["roles"].c.id))
                .where(t["user_roles"].c.user_id == user_id)
            ).all()
            live_roles = {str(r.name).lower() for r in role_rows}
            perm_rows = conn.execute(
                select(t["permissions"].c.code)
                .select_from(
                    t["permissions"]
                    .join(t["role_permissions"], t["role_permissions"].c.permission_id == t["permissions"].c.id)
                    .join(t["user_roles"], t["user_roles"].c.role_id == t["role_permissions"].c.role_id)
                )
                .where(t["user_roles"].c.user_id == user_id)
            ).all()
            live_perms = {str(p.code) for p in perm_rows}

            token_roles = {str(r).lower() for r in payload.get("roles", [])}
            token_perms = set(payload.get("permissions", []))
            if token_roles != live_roles or token_perms != live_perms:
                return 401, {"detail": "Access token claims are stale."}

            return 200, {
                "active": True,
                "user_id": str(user_id),
                "roles": sorted(live_roles),
            }
    except Exception:
        return 401, {"detail": "Invalid or expired access token."}


def _resolve_academic_in_process(url: str, headers: dict[str, str] | None, params: dict[str, Any] | None = None) -> tuple[int, Any]:
    """Resolve internal Academic checks directly against PostgreSQL/SQLite without mutating sys.modules."""
    import re as _re
    import uuid as _uuid
    from urllib.parse import parse_qs, urlparse

    from sqlalchemy import func, select

    status_code, actor_info = _verify_access_status_in_process(headers)
    is_internal = "/internal/" in url
    if not is_internal and status_code != 200:
        return 401, {"detail": "Authentication required."}

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if params:
        for k, v in params.items():
            query[str(k)] = [str(v)]
    path = parsed.path
    t = _tables()
    sec, enr, sp, tp, ta = t["sections"], t["enrollments"], t["student_profiles"], t["teacher_profiles"], t["teacher_assignments"]

    with _gateway_engine().connect() as conn:
        def _teacher_has_section(uid: _uuid.UUID, sec_id: _uuid.UUID) -> bool:
            row = conn.execute(
                select(ta.c.id)
                .select_from(ta.join(tp, tp.c.id == ta.c.teacher_profile_id))
                .where(
                    tp.c.external_user_id == uid,
                    tp.c.is_active.is_(True),
                    ta.c.section_id == sec_id,
                    ta.c.is_active.is_(True),
                )
                .limit(1)
            ).first()
            return row is not None

        def _student_sections(uid: _uuid.UUID) -> list[Any]:
            return conn.execute(
                select(sec.c.id, sec.c.course_id, sec.c.semester_id, sec.c.is_active)
                .distinct()
                .select_from(
                    sec.join(enr, enr.c.section_id == sec.c.id).join(sp, sp.c.id == enr.c.student_profile_id)
                )
                .where(
                    sp.c.external_user_id == uid,
                    sp.c.is_active.is_(True),
                    func.upper(enr.c.status) == "ENROLLED",
                    sec.c.is_active.is_(True),
                )
                .order_by(sec.c.id)
            ).all()

        def _teacher_sections(uid: _uuid.UUID) -> list[Any]:
            return conn.execute(
                select(sec.c.id, sec.c.course_id, sec.c.semester_id, sec.c.is_active)
                .distinct()
                .select_from(
                    sec.join(ta, ta.c.section_id == sec.c.id).join(tp, tp.c.id == ta.c.teacher_profile_id)
                )
                .where(
                    tp.c.external_user_id == uid,
                    tp.c.is_active.is_(True),
                    ta.c.is_active.is_(True),
                    sec.c.is_active.is_(True),
                )
                .order_by(sec.c.id)
            ).all()

        actor_roles = set(actor_info.get("roles", [])) if status_code == 200 else set()
        actor_uid = _uuid.UUID(actor_info["user_id"]) if status_code == 200 else None
        is_priv = "admin" in actor_roles

        m = _re.search(r"/teachers/([0-9a-fA-F-]+)/sections/([0-9a-fA-F-]+)/assignment", path)
        if m:
            uid, sec_id = _uuid.UUID(m.group(1)), _uuid.UUID(m.group(2))
            if not is_priv and actor_uid != uid:
                return 403, {"detail": "Forbidden"}
            assigned = _teacher_has_section(uid, sec_id)
            return 200, {"assigned": assigned, "valid": assigned}

        if "teacher-assignments/validate" in path:
            uid = _uuid.UUID(query["teacher_user_id"][0])
            sec_id = _uuid.UUID(query["section_id"][0])
            if not is_priv and actor_uid != uid:
                return 403, {"detail": "Forbidden"}
            assigned = _teacher_has_section(uid, sec_id)
            return 200, {"assigned": assigned, "valid": assigned}

        m = _re.search(r"/students/([0-9a-fA-F-]+)/sections/([0-9a-fA-F-]+)/enrollment", path)
        if m:
            uid, sec_id = _uuid.UUID(m.group(1)), _uuid.UUID(m.group(2))
            if not is_priv and actor_uid != uid:
                return 403, {"detail": "Forbidden"}
            enrolled = any(s.id == sec_id for s in _student_sections(uid))
            return 200, {"enrolled": enrolled, "valid": enrolled}

        if "enrollments/validate" in path:
            uid = _uuid.UUID(query["student_user_id"][0])
            sec_id = _uuid.UUID(query["section_id"][0])
            if not is_priv and actor_uid != uid:
                return 403, {"detail": "Forbidden"}
            enrolled = any(s.id == sec_id for s in _student_sections(uid))
            return 200, {"enrolled": enrolled, "valid": enrolled}

        m = _re.search(r"/internal/access/students/([0-9a-fA-F-]+)/targets", path)
        if m:
            uid = _uuid.UUID(m.group(1))
            sections = _student_sections(uid)
            return 200, {
                "section_ids": [str(s.id) for s in sections],
                "course_ids": sorted({str(s.course_id) for s in sections}),
            }

        m = _re.search(r"/students/([0-9a-fA-F-]+)/sections/?$", path)
        if m:
            uid = _uuid.UUID(m.group(1))
            if not is_priv and actor_uid != uid:
                return 403, {"detail": "Forbidden"}
            sections = _student_sections(uid)
            return 200, {"section_ids": [str(s.id) for s in sections]}

        m = _re.search(r"/internal/access/(teachers|students)/([0-9a-fA-F-]+)/(courses|sections)/([0-9a-fA-F-]+)", path)
        if m:
            kind, uid, target_kind, target_id = m.group(1), _uuid.UUID(m.group(2)), m.group(3), _uuid.UUID(m.group(4))
            rows = _teacher_sections(uid) if kind == "teachers" else _student_sections(uid)
            allowed = any((s.course_id if target_kind == "courses" else s.id) == target_id for s in rows)
            return 200, {"allowed": allowed}

        m = _re.search(r"/sections/([0-9a-fA-F-]+)/roster", path)
        if m:
            sec_id = _uuid.UUID(m.group(1))
            if not is_internal and not is_priv and (actor_uid is None or not _teacher_has_section(actor_uid, sec_id)):
                return 403, {"detail": "Forbidden"}
            rows = conn.execute(
                select(enr.c.id.label("enrollment_id"), sp.c.id.label("sp_id"), sp.c.external_user_id, sp.c.student_number)
                .select_from(enr.join(sp, sp.c.id == enr.c.student_profile_id))
                .where(enr.c.section_id == sec_id, func.upper(enr.c.status) == "ENROLLED")
            ).all()
            return 200, {
                "section_id": str(sec_id),
                "total": len(rows),
                "limit": 1000,
                "offset": 0,
                "students": [
                    {
                        "enrollment_id": str(r.enrollment_id),
                        "student_profile_id": str(r.sp_id),
                        "external_user_id": str(r.external_user_id),
                        "student_number": r.student_number,
                    }
                    for r in rows
                ],
            }

        m = _re.search(r"/sections/([0-9a-fA-F-]+)$", path)
        if m:
            sec_id = _uuid.UUID(m.group(1))
            sec_row = conn.execute(
                select(sec.c.id, sec.c.course_id, sec.c.semester_id, sec.c.is_active).where(sec.c.id == sec_id)
            ).first()
            if sec_row is None:
                return 404, {"detail": "Section not found."}
            if not is_priv:
                if "teacher" in actor_roles and actor_uid and _teacher_has_section(actor_uid, sec_id):
                    pass
                elif "student" in actor_roles and actor_uid and any(s.id == sec_id for s in _student_sections(actor_uid)):
                    pass
                else:
                    return 403, {"detail": "Forbidden"}
            return 200, {
                "id": str(sec_row.id),
                "course_id": str(sec_row.course_id),
                "semester_id": str(sec_row.semester_id),
                "is_active": bool(sec_row.is_active),
            }
        return 404, {"detail": "Unknown internal academic route."}


# In-process JWKS, access-status, and academic relationship resolver for serverless calls
try:
    import httpx
    from jwt import PyJWKClient

    _orig_httpx_get = httpx.get
    _orig_client_get = httpx.Client.get
    _orig_async_get = httpx.AsyncClient.get

    def _in_process_response(url, kwargs):
        u = str(url)
        req = httpx.Request("GET", u)
        if "jwks.json" in u:
            return httpx.Response(200, json=get_in_memory_jwks(), request=req)
        if "access-status" in u:
            code, body = _verify_access_status_in_process(kwargs.get("headers"))
            return httpx.Response(code, json=body, request=req)
        if any(seg in u for seg in (":8002/", "academic-service", "/teacher-assignments/", "/enrollments/validate", "/internal/access/", "/students/", "/sections/")):
            if u.startswith(("http://localhost:8002", "http://127.0.0.1:8002", "http://academic")):
                code, body = _resolve_academic_in_process(u, kwargs.get("headers"), kwargs.get("params"))
                return httpx.Response(code, json=body, request=req)
        return None

    def patched_httpx_get(url, *args, **kwargs):
        resolved = _in_process_response(url, kwargs)
        if resolved is not None:
            return resolved
        return _orig_httpx_get(url, *args, **kwargs)

    def patched_client_get(self, url, *args, **kwargs):
        resolved = _in_process_response(url, kwargs)
        if resolved is not None:
            return resolved
        return _orig_client_get(self, url, *args, **kwargs)

    async def patched_async_get(self, url, *args, **kwargs):
        resolved = _in_process_response(url, kwargs)
        if resolved is not None:
            return resolved
        return await _orig_async_get(self, url, *args, **kwargs)

    httpx.get = patched_httpx_get
    httpx.Client.get = patched_client_get
    httpx.AsyncClient.get = patched_async_get
    PyJWKClient.fetch_data = lambda self: get_in_memory_jwks()
    logger.info("Installed strict in-process JWKS and relationship resolvers for serverless microservices.")
except Exception as exc:
    logger.warning("Could not install in-process resolvers: %s", exc)

# ==============================================================================
# 4. Database Bootstrap & Seeding (Auto-Migration & Seed on Startup)
# ==============================================================================
def init_database_tables():
    """Create tables and seed RBAC roles if empty."""
    try:
        service_path = str(ROOT / "services" / "identity-service")
        if service_path not in sys.path:
            sys.path.insert(0, service_path)

        for k in list(sys.modules.keys()):
            if k == "app" or k.startswith("app."):
                sys.modules.pop(k, None)

        import app.db.base  # noqa: F401
        from sqlalchemy import text
        from app.db.base import Base
        from app.db.session import SessionLocal, engine
        from app.domain.entities.role import Role
        from app.domain.entities.user import User
        from app.security.password import hash_password

        # Create all tables on the connected Neon DB if not already present
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
        except Exception as e:
            logger.debug("pgvector extension check note: %s", e)

        Base.metadata.create_all(bind=engine)

        for s_dir, mod_name in [
            ("finance-service", "app.domain.models"),
            ("learning-service", "app.domain.entities.models"),
            ("payroll-service", "app.domain.models"),
            ("facility-service", "app.domain.models"),
            ("attendance-service", "app.domain.models"),
            ("scheduling-service", "app.domain.models"),
            ("assessment-service", "app.domain.models"),
            ("academic-service", "app.domain.models"),
        ]:
            s_path = str(ROOT / "services" / s_dir)
            try:
                if Path(s_path).exists():
                    if s_path not in sys.path:
                        sys.path.insert(0, s_path)
                    for k in list(sys.modules.keys()):
                        if k == "app" or k.startswith("app."):
                            sys.modules.pop(k, None)
                    import importlib
                    importlib.import_module(mod_name)
                    db_m = importlib.import_module("app.db.base")
                    s_base = getattr(db_m, "Base", None)
                    if s_base and hasattr(s_base, "metadata"):
                        s_base.metadata.create_all(bind=engine)
            except Exception as e:
                logger.debug("Auto-init note for %s: %s", s_dir, e)
            finally:
                if s_path in sys.path:
                    sys.path.remove(s_path)

        with SessionLocal() as db:
            # Seed default roles if missing
            if not db.query(Role).first():
                db.add_all(
                    [
                        Role(name="student", description="Student Role"),
                        Role(name="teacher", description="Teacher Role"),
                        Role(name="admin", description="Platform Administrator"),
                    ]
                )
                db.commit()
                logger.info("Successfully seeded default RBAC roles.")

            # Seed default users across all core roles
            admin_role = db.query(Role).filter_by(name="admin").first()
            teacher_role = db.query(Role).filter_by(name="teacher").first()
            student_role = db.query(Role).filter_by(name="student").first()

            seed_accounts = [
                # Admin
                ("admin@smartedu.local", "Platform Administrator", "AdminPass123!", admin_role),
                # Faculty / Teacher
                ("teacher@smartedu.local", "Dr. Munir Ahmad (BCS Faculty)", "TeacherPass123!", teacher_role),
                ("teacher@demo.example.edu", "Dr. Munir Ahmad (BCS Faculty)", "TeacherPass123!", teacher_role),
                ("teacher@demo.example.edu", "Dr. Munir Ahmad (BCS Faculty)", "Q7!Oa8xZ24L2aX0dEnj8TuSWGEoDgN-vY8KxEVrnts6cbAaZ", teacher_role),
                # Student (Roll: BCS-155)
                ("student@smartedu.local", "Muhammad Ali (BCS-155)", "StudentPass123!", student_role),
                ("student@demo.example.edu", "Muhammad Ali (BCS-155)", "StudentPass123!", student_role),
                ("student@demo.example.edu", "Muhammad Ali (BCS-155)", "Q7!vEpzlshyGXIddiaOLN7GT73b1cUc71pLVJ1ybXGm5dUaZ", student_role),
            ]

            for s_email, s_name, s_pass, s_role in seed_accounts:
                if not s_role:
                    continue
                existing = db.query(User).filter_by(email=s_email).first()
                if not existing:
                    new_u = User(
                        email=s_email,
                        full_name=s_name,
                        password_hash=hash_password(s_pass),
                        roles=[s_role],
                        is_active=True,
                        is_verified=True,
                    )
                    db.add(new_u)
                    db.commit()
                    logger.info("Successfully seeded user: %s", s_email)
                else:
                    if s_role not in existing.roles:
                        existing.roles.append(s_role)
                    existing.is_verified = True
                    existing.is_active = True
                    db.commit()
    except Exception as exc:
        logger.warning("Database auto-init note: %s", exc)


# ==============================================================================
# 5. Dynamic Router Loader
# ==============================================================================
mount_errors: dict[str, str] = {}


def load_service_router(service_dir_name: str) -> Any:
    """Dynamically import a microservice router without module namespace collisions."""
    router_file = ROOT / "services" / service_dir_name / "app" / "api" / "v1" / "router.py"
    if not router_file.exists():
        mount_errors[service_dir_name] = f"missing router file: {router_file}"
        return None

    service_path = str(ROOT / "services" / service_dir_name)
    if service_path not in sys.path:
        sys.path.insert(0, service_path)

    # Evict cached 'app' modules to ensure clean import from target service
    app_mods = [k for k in list(sys.modules.keys()) if k == "app" or k.startswith("app.")]
    for k in app_mods:
        sys.modules.pop(k, None)

    try:
        mod = importlib.import_module("app.api.v1.router")
        return getattr(mod, "api_router", getattr(mod, "router", None))
    except Exception as exc:
        logger.warning("Failed to load router for %s: %s", service_dir_name, exc)
        mount_errors[service_dir_name] = f"{type(exc).__name__}: {exc}"
        return None
    finally:
        if service_path in sys.path:
            sys.path.remove(service_path)


# ==============================================================================
# 6. Lifespan & FastAPI Application Assembly
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database_tables()
    yield


app = FastAPI(
    title="SmartEdu Platform API Gateway (Serverless)",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)

# Vercel Path Fix Middleware
@app.middleware("http")
async def vercel_path_fix_middleware(request: Request, call_next):
    # Paths that mean "Vercel handed us the serverless entrypoint, not the real
    # request path" — i.e. the /api/(.*) rewrite resolved to the function file.
    _ENTRYPOINT_PATHS = ("/api/index.py", "/api/index", "/api", "/api/")
    curr_path = request.scope.get("path", "")

    if curr_path in _ENTRYPOINT_PATHS:
        # 1. Preferred: the original path is carried explicitly by the rewrite as
        #    ?__vpath=/api/... (deterministic, independent of Vercel header names).
        real_path = (request.query_params.get("__vpath") or "").strip()

        # 2. Fallback: headers Vercel/edge proxies may set with the matched path.
        if not real_path:
            real_path = (
                request.headers.get("x-matched-path")
                or request.headers.get("x-vercel-matched-path")
                or request.headers.get("x-forwarded-uri")
                or request.headers.get("x-now-route-matches")
                or ""
            ).strip()

        if real_path:
            clean_path = real_path.split("?")[0]
            # Only adopt it if it actually points at an API route; never loop back
            # to the entrypoint itself (that is what causes the 405 fallthrough).
            if clean_path.startswith("/api") and clean_path not in _ENTRYPOINT_PATHS:
                request.scope["path"] = clean_path
                request.scope["raw_path"] = clean_path.encode("utf-8")

    # Drop the internal __vpath marker so downstream handlers never see it.
    qs = request.scope.get("query_string", b"")
    if b"__vpath=" in qs:
        from urllib.parse import parse_qsl, urlencode
        filtered = [(k, v) for k, v in parse_qsl(qs.decode("latin-1"), keep_blank_values=True) if k != "__vpath"]
        request.scope["query_string"] = urlencode(filtered).encode("latin-1")

    # Normalize trailing slash to match route handlers without 307/308 redirects
    curr_path = request.scope.get("path", "")
    if len(curr_path) > 1 and curr_path.endswith("/"):
        request.scope["path"] = curr_path.rstrip("/")

    return await call_next(request)

# CORS Middleware (Strict explicit origins with credentials support)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Idempotency-Key"],
)

# Services mapping: {url_slug: directory_name}
SERVICES_MAP = [
    ("identity", "identity-service"),
    ("academic", "academic-service"),
    ("attendance", "attendance-service"),
    ("scheduling", "scheduling-service"),
    ("facility", "facility-service"),
    ("facilities", "facility-service"),
    ("learning", "learning-service"),
    ("assessment", "assessment-service"),
    ("assessments", "assessment-service"),
    ("reporting", "reporting-service"),
    ("platform", "platform-service"),
    ("finance", "finance-service"),
    ("payroll", "payroll-service"),
    ("notification", "notification-service"),
    ("notifications", "notification-service"),
]

mounted_services = []
for slug, service_dir in SERVICES_MAP:
    router = load_service_router(service_dir)
    if router is not None:
        prefix = f"/api/v1/{slug}"
        app.include_router(router, prefix=prefix)
        if slug not in mounted_services:
            mounted_services.append(slug)

logger.info("Mounted services on Vercel: %s", mounted_services)


# ==============================================================================
# 7. Health & Status Endpoints
# ==============================================================================
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    is_neon = "neon.tech" in DB_URL or "postgresql" in DB_URL
    payload = {
        "status": "healthy",
        "platform": "SmartEdu",
        "runtime": "Vercel Serverless Python",
        "database_type": "Neon PostgreSQL" if is_neon else "SQLite Ephemeral",
        "mounted_services": mounted_services,
    }
    if mount_errors:
        payload["mount_errors"] = mount_errors
    return payload


@app.get("/api")
@app.get("/api/v1")
async def api_root():
    return {
        "message": "SmartEdu API Gateway is active",
        "docs": "/api/docs",
        "version": "1.0.0",
        "mounted_services": mounted_services,
    }


@app.get("/.well-known/jwks.json")
@app.get("/api/v1/identity/.well-known/jwks.json")
async def jwks_endpoint():
    return get_in_memory_jwks()


@app.get("/api/v1/auth/access-status")
@app.get("/api/v1/identity/auth/access-status")
async def access_status_endpoint(request: Request):
    code, body = _verify_access_status_in_process(dict(request.headers))
    return JSONResponse(status_code=code, content=body, headers={"Cache-Control": "no-store"})
