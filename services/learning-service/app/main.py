from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.sprint16 import install_sprint16
from app.sprint18 import install_sprint18
from app.sprint21 import install_sprint21

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

install_sprint21(app)

install_sprint16(app)

install_sprint18(app)
app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
