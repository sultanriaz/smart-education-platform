from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_reporting_service
from app.security.auth import require_roles
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def _admin(_principal=Depends(require_roles("admin"))):
    return _principal


@router.get("/attendance")
def attendance(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._attendance_dicts()}


@router.get("/assessments")
def assessments(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._assessment_dicts()}


@router.get("/facilities")
def facilities(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._facility_dicts()}


@router.get("/notifications")
def notifications(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._notification_dicts()}


@router.get("/scheduling")
def scheduling(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._schedule_dicts()}


@router.get("/enrollment")
def enrollment(
    _principal=Depends(_admin),
    service: ReportingService = Depends(get_reporting_service),
):
    return {"rows": service._enrollment_dicts()}
