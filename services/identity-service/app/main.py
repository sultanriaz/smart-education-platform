from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jwks import router as jwks_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.security.jwt import get_signing_keys
from app.sprint16 import install_sprint16
from app.sprint18 import install_sprint18, security_settings
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


def _allowed_cors_origins() -> list[str]:
    origins = [*settings.CORS_ORIGINS, *security_settings().frontend_origins]
    return list(dict.fromkeys(o.strip().rstrip("/") for o in origins if o and o.strip() != "*"))


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Idempotency-Key"],
)

app.include_router(health_router)
app.include_router(jwks_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
