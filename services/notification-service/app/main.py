from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import (
    ConflictError,
    DependencyContractError,
    DependencyUnavailableError,
    ForbiddenError,
    NotFoundError,
    TemplateRenderError,
)
from app.sprint16 import install_sprint16
from app.sprint18 import install_sprint18
from app.sprint21 import install_sprint21

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

install_sprint21(app)

install_sprint16(app)

install_sprint18(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def handler(status_code: int):
    async def _handler(_request: Request, exc: Exception):
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return _handler


app.add_exception_handler(NotFoundError, handler(404))
app.add_exception_handler(ForbiddenError, handler(403))
app.add_exception_handler(ConflictError, handler(409))
app.add_exception_handler(TemplateRenderError, handler(422))
app.add_exception_handler(DependencyUnavailableError, handler(503))
app.add_exception_handler(DependencyContractError, handler(502))

app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
