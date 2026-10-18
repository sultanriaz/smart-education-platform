from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import Response

from app.api.dependencies import get_reporting_service
from app.core.errors import DomainError
from app.clients.academic import require_teacher_section
from app.schemas.reports import SnapshotCreate, SnapshotOut
from app.security.auth import Principal, require_roles, require_scoped_roles
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/academic/students/me")
def my_academic_report(
    principal: Principal = Depends(require_roles("student")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.academic_report(student_user_id=principal.user_id)


@router.get("/academic/sections/{section_id}")
def section_academic_report(
    section_id: uuid.UUID,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    if "admin" not in principal.roles:
        require_teacher_section(principal.user_id, section_id, principal.token)
    return service.academic_report(section_id=section_id)


@router.get("/academic/courses/{course_id}")
def course_academic_report(
    course_id: uuid.UUID,
    _principal: Principal = Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.academic_report(course_id=course_id)


@router.post("/snapshots", response_model=SnapshotOut)
def create_snapshot(
    payload: SnapshotCreate,
    principal: Principal = Depends(require_scoped_roles("reporting.snapshots.write", "admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.create_snapshot(payload.report_type, payload.filters, principal.user_id)


@router.get("/snapshots", response_model=list[SnapshotOut])
def list_snapshots(
    _principal=Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    return service.repo.list_snapshots()


def filters_from_request(request: Request):
    # Shared parsing for paginated screen and CSV: arbitrary filter keys are denied.
    return {key: value for key, value in request.query_params.items() if key not in {"limit", "offset"}}


@router.get("/{report_type}.csv")
def export_csv(
    report_type: str,
    request: Request,
    principal: Principal = Depends(require_roles("admin")),
    service: ReportingService = Depends(get_reporting_service),
):
    try:
        content, _count = service.export_csv(report_type, principal.user_id, filters_from_request(request))
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{report_type}-report.csv"'},
    )


@router.get("/{report_type}")
def report_page(report_type: str, request: Request, offset: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=200), _admin=Depends(require_roles("admin")), service: ReportingService = Depends(get_reporting_service)):
    try:
        return service.report_page(report_type, filters_from_request(request), limit=limit, offset=offset)
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
