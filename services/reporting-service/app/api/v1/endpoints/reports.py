from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.api.dependencies import get_reporting_service
from app.schemas.reports import SnapshotCreate, SnapshotOut
from app.security.auth import Principal, require_roles
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/snapshots", response_model=SnapshotOut)
def create_snapshot(
    payload: SnapshotCreate,
    principal: Principal = Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.create_snapshot(payload.report_type, payload.filters, principal.user_id)


@router.get("/snapshots", response_model=list[SnapshotOut])
def list_snapshots(
    _principal=Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.repo.list_snapshots()


@router.get("/{report_type}.csv")
def export_csv(
    report_type: str,
    principal: Principal = Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    content, _count = service.export_csv(report_type, principal.user_id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{report_type}-report.csv"'},
    )
