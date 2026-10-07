from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import Actor, Filters, Limit, Offset, Service
from app.schemas.attendance import AttendanceSummary, Counts, StudentAttendance, StudentSummary

router = APIRouter(tags=["attendance reports"])


@router.get("/students/me/attendance", response_model=list[StudentAttendance])
def my_attendance(
    actor: Actor,
    service: Service,
    filters: Filters,
    section_id: UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    return service.attendance(
        actor, self_view=True, section_id=section_id, limit=limit, offset=offset, **filters
    )


@router.get("/students/me/attendance/summary", response_model=StudentSummary)
def my_summary(
    actor: Actor,
    service: Service,
    filters: Filters,
    section_id: UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    if section_id:
        filters["section_ids"] = {section_id}
    return service.student_summary(actor, limit=limit, offset=offset, **filters)


@router.get("/sections/{section_id}/attendance", response_model=list[StudentAttendance])
def section_attendance(
    section_id: UUID,
    actor: Actor,
    service: Service,
    filters: Filters,
    limit: Limit = 50,
    offset: Offset = 0,
):
    return service.attendance(actor, section_id=section_id, limit=limit, offset=offset, **filters)


@router.get("/sections/{section_id}/summary", response_model=Counts)
def section_summary(section_id: UUID, actor: Actor, service: Service, filters: Filters):
    return service.section_summary(actor, section_id, **filters)


@router.get("/sections/{section_id}/students/{student_user_id}/summary", response_model=Counts)
def student_section_summary(
    section_id: UUID, student_user_id: UUID, actor: Actor, service: Service, filters: Filters
):
    return service.section_summary(actor, section_id, student_id=student_user_id, **filters)


@router.get("/reports/low-attendance", response_model=list[AttendanceSummary])
def low_attendance(
    actor: Actor,
    service: Service,
    filters: Filters,
    section_id: UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    return service.low_attendance(
        actor, section_id=section_id, limit=limit, offset=offset, **filters
    )
