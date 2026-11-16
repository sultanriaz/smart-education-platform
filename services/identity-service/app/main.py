from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jwks import router as jwks_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import get_db
from app.security.jwt import get_signing_keys
from app.sprint16 import install_sprint16
from app.sprint18 import identity_rate_limiter, install_sprint18, security_settings
from app.sprint18_security.adapters import (
    AccountAdapter,
    SecurityAuditAdapter,
    SecurityNotificationAdapter,
)
from app.sprint18_security.router import build_identity_security_router
from app.sprint21 import install_sprint21


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_signing_keys()  # Refuse startup with missing or invalid signing material.
    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)


install_sprint21(app)


install_sprint16(app)


install_sprint18(app)

# Trailing slash normalizer
@app.middleware("http")
async def trailing_slash_middleware(request: Request, call_next):
    curr_path = request.scope.get("path", "")
    if len(curr_path) > 1 and curr_path.endswith("/"):
        request.scope["path"] = curr_path.rstrip("/")
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(jwks_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(
    build_identity_security_router(
        get_db=get_db,
        account_adapter_factory=AccountAdapter,
        notification_sink_factory=SecurityNotificationAdapter,
        audit_sink_factory=SecurityAuditAdapter,
        rate_limiter=identity_rate_limiter(),
        settings=security_settings(),
    ),
    prefix=settings.API_V1_PREFIX,
)


@app.options("/{full_path:path}")
async def global_options_catchall(full_path: str, request: Request):
    origin = request.headers.get("origin") or "*"
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Idempotency-Key, Accept, Origin",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        },
    )
