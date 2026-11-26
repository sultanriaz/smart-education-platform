from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.responses import Response

from .logging import configure_logging
from .metrics import Metrics
from .middleware import ObservabilityMiddleware
from .settings import ObservabilitySettings
from .tracing import configure_tracing, instrument_fastapi, instrument_httpx


@dataclass(frozen=True, slots=True)
class ObservabilityRuntime:
    settings: ObservabilitySettings
    metrics: Metrics


def install_observability(
    app: FastAPI,
    *,
    settings: ObservabilitySettings | None = None,
) -> ObservabilityRuntime:
    settings = settings or ObservabilitySettings()

    configure_logging(
        service_name=settings.service_name,
        environment=settings.environment,
        service_version=settings.service_version,
        level=settings.log_level,
        json_logs=settings.json_logs,
    )

    metrics = Metrics(
        service_name=settings.service_name,
        service_version=settings.service_version,
        environment=settings.environment,
    )

    if not settings.enabled:
        return ObservabilityRuntime(settings=settings, metrics=metrics)

    logger = logging.getLogger("smartedu.http")

    if settings.metrics_enabled:

        @app.get(
            settings.metrics_path,
            include_in_schema=False,
            tags=["operations"],
        )
        async def metrics_endpoint():
            return Response(
                metrics.exposition(),
                media_type="text/plain; version=0.0.4; charset=utf-8",
            )

    app.add_middleware(
        ObservabilityMiddleware,
        metrics=metrics,
        logger=logger,
        service_name=settings.service_name,
        request_id_header=settings.request_id_header,
        correlation_id_header=settings.correlation_id_header,
        excluded_paths=(
            "/health",
            "/ready",
            settings.metrics_path,
        ),
    )

    if settings.tracing_enabled:
        configure_tracing(
            service_name=settings.service_name,
            service_version=settings.service_version,
            environment=settings.environment,
            otlp_endpoint=settings.otlp_endpoint,
            sample_ratio=settings.trace_sample_ratio,
        )
        instrument_fastapi(app)
        instrument_httpx()

    return ObservabilityRuntime(
        settings=settings,
        metrics=metrics,
    )
