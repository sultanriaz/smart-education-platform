from contextlib import asynccontextmanager

from fastapi import FastAPI
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
