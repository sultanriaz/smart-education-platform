from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    disbursements,
    payslips,
    periods,
    profiles,
    reports,
    runs,
    structures,
)

api_router = APIRouter()
api_router.include_router(profiles.router)
api_router.include_router(structures.router)
api_router.include_router(periods.router)
api_router.include_router(runs.router)
api_router.include_router(disbursements.router)
api_router.include_router(payslips.router)
api_router.include_router(reports.router)

