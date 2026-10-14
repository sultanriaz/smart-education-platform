from __future__ import annotations
from smartedu_security.live_access import LiveAccessMiddleware

from fastapi import FastAPI

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Cross-service reporting projections and administrative analytics.",
)

app.add_middleware(LiveAccessMiddleware)
app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
