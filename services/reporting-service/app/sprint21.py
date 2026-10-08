from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI
from smartedu_observability import (
    ObservabilitySettings,
    install_observability,
)


@lru_cache
def observability_settings() -> ObservabilitySettings:
    return ObservabilitySettings(
        SERVICE_NAME="reporting-service",
    )


def install_sprint21(app: FastAPI):
    return install_observability(
        app,
        settings=observability_settings(),
    )
