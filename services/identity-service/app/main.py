from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.jwks import router as jwks_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.security.jwt import get_signing_keys


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_signing_keys()  # Refuse startup with missing or invalid signing material.
    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

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
