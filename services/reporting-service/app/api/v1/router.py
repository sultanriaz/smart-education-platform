from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import dashboard, internal, metrics, reports

api_router = APIRouter()
api_router.include_router(internal.router)
api_router.include_router(dashboard.router)
api_router.include_router(metrics.router)
api_router.include_router(reports.router)
