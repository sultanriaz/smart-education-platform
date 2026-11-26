from __future__ import annotations

import re
import time
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .context import clear_request_context, set_request_context
from .logging import structured_log
from .metrics import Metrics

_SAFE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _safe_header_id(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    return value if _SAFE_ID.fullmatch(value) else None


def route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if isinstance(path, str) and path:
        return path
    return "unmatched"


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        metrics: Metrics,
        logger,
        service_name: str,
        request_id_header: str = "X-Request-ID",
        correlation_id_header: str = "X-Correlation-ID",
        excluded_paths: tuple[str, ...] = ("/health", "/ready", "/metrics"),
    ):
        super().__init__(app)
        self.metrics = metrics
        self.logger = logger
        self.service_name = service_name
        self.request_id_header = request_id_header
        self.correlation_id_header = correlation_id_header
        self.excluded_paths = set(excluded_paths)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        incoming_request = _safe_header_id(
            getattr(request.state, "request_id", None)
            or request.headers.get(self.request_id_header)
        )
        incoming_correlation = _safe_header_id(
            getattr(request.state, "correlation_id", None)
            or request.headers.get(self.correlation_id_header)
        )
        context = set_request_context(
            request_id=incoming_request,
            correlation_id=incoming_correlation,
        )

        started = time.perf_counter()
        status_code = 500
        observe = request.url.path not in self.excluded_paths

        if observe:
            self.metrics.http_inflight.labels(self.service_name).inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[self.request_id_header] = context.request_id
            response.headers[self.correlation_id_header] = context.correlation_id
            return response
        except Exception:
            structured_log(
                self.logger,
                40,
                "unhandled_request_exception",
                method=request.method,
                route=route_template(request),
            )
            raise
        finally:
            duration = time.perf_counter() - started
            route = route_template(request)
            status_class = f"{status_code // 100}xx"

            if observe:
                self.metrics.http_inflight.labels(self.service_name).dec()
                self.metrics.http_requests.labels(
                    self.service_name,
                    request.method,
                    route,
                    status_class,
                ).inc()
                self.metrics.http_duration.labels(
                    self.service_name,
                    request.method,
                    route,
                ).observe(duration)

                structured_log(
                    self.logger,
                    20,
                    "http_request_completed",
                    method=request.method,
                    route=route,
                    status_code=status_code,
                    duration_ms=round(duration * 1000, 3),
                    request_id=context.request_id,
                    correlation_id=context.correlation_id,
                )

            clear_request_context()
