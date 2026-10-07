from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from app.api.health import router as health_router
from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.core.exceptions import DomainError


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, version="0.3.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def correlation_id(request: Request, call_next):
        request.state.request_id = uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    def error(request: Request, status: int, detail: str, code: str, *, headers=None, errors=None):
        body = {"detail": detail, "code": code, "request_id": request.state.request_id}
        if errors is not None:
            body["errors"] = errors
        return JSONResponse(
            status_code=status,
            content=body,
            headers={"X-Request-ID": request.state.request_id, **(headers or {})},
        )

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return error(request, exc.status_code, exc.detail, exc.code)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return error(
            request,
            exc.status_code,
            str(exc.detail),
            f"http_{exc.status_code}",
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Exclude input values and exception context from errors; neither tokens
        # nor sensitive free-text notes should be echoed in failure responses.
        errors = [
            {"loc": list(row["loc"]), "msg": row["msg"], "type": row["type"]}
            for row in exc.errors()
        ]
        return error(
            request, 422, "Invalid request.", "validation_error", errors=jsonable_encoder(errors)
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError):
        return error(request, 503, "Attendance database is unavailable.", "database_unavailable")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        return error(request, 500, "Unexpected attendance service error.", "internal_error")

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
