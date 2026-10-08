from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_reporting_service
from app.schemas.reports import DashboardOverview
from app.security.auth import require_roles
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def overview(
    _principal=Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.overview()
