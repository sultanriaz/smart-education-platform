"""SmartEdu Platform — Unified Vercel Serverless API Gateway.

Dispatches all /api/v1/{service}/... endpoints to microservice routers
and connects directly to Neon PostgreSQL via DATABASE_URL or POSTGRES_URL.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger("smartedu.vercel_gateway")
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# 1. Environment & Path Resolution
# ==============================================================================
ROOT = Path(__file__).resolve().parent.parent

# Add libs to sys.path
libs_dir = ROOT / "libs" / "python"
if libs_dir.exists():
    for lib in sorted(libs_dir.iterdir()):
        if lib.is_dir() and str(lib) not in sys.path:
            sys.path.insert(0, str(lib))

# ==============================================================================
# 2. Database Connection Normalization (Neon PostgreSQL Support)
# ==============================================================================
def resolve_database_url() -> str:
    """Normalize Neon PostgreSQL URL or fallback to SQLite."""
    raw_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
        or os.environ.get("POSTGRES_URL_NON_POOLING")
        or ""
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


DB_URL = resolve_database_url()
os.environ["DATABASE_URL"] = DB_URL
os.environ["ENVIRONMENT"] = os.environ.get("ENVIRONMENT", "development")
os.environ["JWT_ISSUER"] = os.environ.get(
    "JWT_ISSUER", "https://smart-education-platform-teal.vercel.app"
)
os.environ["JWT_KEY_ID"] = os.environ.get("JWT_KEY_ID", "smartedu-identity-key-1")

# ==============================================================================
# 3. JWT Signing Key Setup (RSA 2048-bit)
# ==============================================================================
def setup_jwt_keys():
    """Ensure RSA private key exists for token signing."""
    local_key = ROOT / "services" / "identity-service" / ".secrets" / "identity-private.pem"
    if local_key.exists():
        os.environ["JWT_PRIVATE_KEY_FILE"] = str(local_key)
        return

    import tempfile
    tmp_key = Path(tempfile.gettempdir()) / "identity-private.pem"
    if not tmp_key.exists():
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa

            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            tmp_key.write_bytes(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
        except Exception as exc:
            logger.warning("Could not generate ephemeral RSA key: %s", exc)

    if tmp_key.exists():
        os.environ["JWT_PRIVATE_KEY_FILE"] = str(tmp_key)


setup_jwt_keys()

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
        from app.db.base import Base
        from app.db.session import SessionLocal, engine
        from app.domain.entities.role import Role
        from app.domain.entities.user import User
        from app.security.password import hash_password

        # Create all tables on the connected Neon DB if not already present
        Base.metadata.create_all(bind=engine)

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

            # Seed default admin user if missing
            admin_email = "admin@smartedu.local"
            if not db.query(User).filter_by(email=admin_email).first():
                admin_role = db.query(Role).filter_by(name="admin").first()
                if admin_role:
                    admin_user = User(
                        email=admin_email,
                        full_name="Platform Administrator",
                        password_hash=hash_password("AdminPass123!"),
                        roles=[admin_role],
                        is_active=True,
                    )
                    db.add(admin_user)
                    db.commit()
                    logger.info("Successfully seeded default admin: %s", admin_email)
    except Exception as exc:
        logger.warning("Database auto-init note: %s", exc)


# ==============================================================================
# 5. Dynamic Router Loader
# ==============================================================================
def load_service_router(service_dir_name: str) -> Any:
    """Dynamically import a microservice router without module namespace collisions."""
    router_file = ROOT / "services" / service_dir_name / "app" / "api" / "v1" / "router.py"
    if not router_file.exists():
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
)

# CORS Middleware (Allows credentials, cookies, and headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Serverless lockout guard override (Memory store when Redis is absent)
try:
    if not os.environ.get("REDIS_URL") and not os.environ.get("REDIS_CACHE_URL"):
        from smartedu_security import LoginSecurityGuard
        from smartedu_security.lockout import MemoryLockoutStore

        id_service_path = str(ROOT / "services" / "identity-service")
        if id_service_path not in sys.path:
            sys.path.insert(0, id_service_path)
        for k in list(sys.modules.keys()):
            if k == "app" or k.startswith("app."):
                sys.modules.pop(k, None)

        from app.api.v1.endpoints.auth import login_guard
        memory_guard = LoginSecurityGuard(MemoryLockoutStore())
        app.dependency_overrides[login_guard] = lambda: memory_guard
        logger.info("Configured in-memory lockout guard for serverless.")
except Exception as exc:
    logger.warning("Lockout override note: %s", exc)

logger.info("Mounted services on Vercel: %s", mounted_services)


# ==============================================================================
# 7. Health & Status Endpoints
# ==============================================================================
@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check():
    is_neon = "neon.tech" in DB_URL or "postgresql" in DB_URL
    return {
        "status": "healthy",
        "platform": "SmartEdu",
        "runtime": "Vercel Serverless Python",
        "database_type": "Neon PostgreSQL" if is_neon else "SQLite Ephemeral",
        "mounted_services": mounted_services,
    }


@app.get("/api")
@app.get("/api/v1")
async def api_root():
    return {
        "message": "SmartEdu API Gateway is active",
        "docs": "/api/docs",
        "version": "1.0.0",
        "mounted_services": mounted_services,
    }
