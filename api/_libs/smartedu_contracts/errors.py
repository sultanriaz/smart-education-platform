from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .context import get_correlation_id, get_request_id


@dataclass(slots=True)
class SmartEduError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Any = None

    def __str__(self) -> str:
        return self.message


def error_payload(
    code: str,
    message: str,
    *,
    details: Any = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": request_id or get_request_id(),
        "correlation_id": correlation_id or get_correlation_id(),
    }
    if details is not None:
        error["details"] = details
    return {"error": error}


def install_error_handlers(
    app: FastAPI,
    *,
    expose_internal_errors: bool = False,
) -> None:
    @app.exception_handler(SmartEduError)
    async def _smartedu_error(_request: Request, exc: SmartEduError):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                exc.code,
                exc.message,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_payload(
                "validation_error",
                "Request validation failed",
                details=[
                    {"loc": list(row["loc"]), "msg": row["msg"], "type": row["type"]}
                    for row in exc.errors()
                ],
            ),
        )

    @app.exception_handler(HTTPException)
    async def _http_error(_request: Request, exc: HTTPException):
        detail = exc.detail
        message = detail if isinstance(detail, str) else "Request failed"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                f"http_{exc.status_code}",
                message,
                details=None if isinstance(detail, str) else detail,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def _unexpected_error(_request: Request, exc: Exception):
        details = str(exc) if expose_internal_errors else None
        return JSONResponse(
            status_code=500,
            content=error_payload(
                "internal_error",
                "An unexpected server error occurred",
                details=details,
            ),
        )
