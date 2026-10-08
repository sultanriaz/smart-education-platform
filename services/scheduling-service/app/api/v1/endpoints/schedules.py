from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient, get_academic_client
from app.core.errors import DomainError
from app.db.session import get_db
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    AuditOut,
    CancelRequest,
    OverrideCreate,
    OverrideOut,
    ScheduleCreate,
    ScheduleOut,
    ScheduleUpdate,
)
from app.security.auth import Principal, get_current_principal
from app.security.authorization import require_roles
from app.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/schedules", tags=["Schedules"])


def _raise(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    try:
        return SchedulingService(db, academic).create_schedule(payload, principal)
    except DomainError as exc:
        _raise(exc)


@router.get("", response_model=list[ScheduleOut])
def list_schedules(
    section_id: uuid.UUID | None = None,
    teacher_user_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
    schedule_status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    if principal.has_role("student"):
        raise HTTPException(status_code=403, detail="Students use timetable endpoints")
    if principal.has_role("teacher") and not principal.has_role("admin"):
        if teacher_user_id and teacher_user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Teachers may only list their schedules")
        teacher_user_id = principal.user_id
    return ScheduleRepository(db).list_schedules(
        section_id=section_id,
        teacher_user_id=teacher_user_id,
        room_id=room_id,
        status=schedule_status,
        offset=offset,
        limit=limit,
    )


@router.get("/{schedule_id}", response_model=ScheduleOut)
def get_schedule(
    schedule_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    schedule = ScheduleRepository(db).get_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if principal.has_role("student"):
        raise HTTPException(status_code=403, detail="Students use timetable endpoints")
    if principal.has_role("teacher") and not principal.has_role("admin"):
        if schedule.teacher_user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Teacher does not own this schedule")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleOut)
def update_schedule(
    schedule_id: uuid.UUID,
    payload: ScheduleUpdate,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    try:
        return SchedulingService(db, academic).update_schedule(schedule_id, payload, principal)
    except DomainError as exc:
        _raise(exc)


@router.post("/{schedule_id}/cancel", response_model=ScheduleOut)
def cancel_schedule(
    schedule_id: uuid.UUID,
    payload: CancelRequest,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    try:
        return SchedulingService(db, academic).cancel_schedule(
            schedule_id, payload.reason, principal
        )
    except DomainError as exc:
        _raise(exc)


@router.post(
    "/{schedule_id}/overrides",
    response_model=OverrideOut,
    status_code=status.HTTP_201_CREATED,
)
def set_override(
    schedule_id: uuid.UUID,
    payload: OverrideCreate,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    try:
        return SchedulingService(db, academic).set_override(schedule_id, payload, principal)
    except DomainError as exc:
        _raise(exc)


@router.get("/{schedule_id}/overrides", response_model=list[OverrideOut])
def list_overrides(
    schedule_id: uuid.UUID,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    schedule = ScheduleRepository(db).get_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if principal.has_role("teacher") and not principal.has_role("admin"):
        if schedule.teacher_user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Teacher does not own this schedule")
    return sorted(schedule.overrides, key=lambda item: item.occurrence_date)


@router.get("/{schedule_id}/history", response_model=list[AuditOut])
def schedule_history(
    schedule_id: uuid.UUID,
    principal: Principal = Depends(require_roles("admin", "teacher")),
    db: Session = Depends(get_db),
):
    schedule = ScheduleRepository(db).get_schedule(schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if principal.has_role("teacher") and not principal.has_role("admin"):
        if schedule.teacher_user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Teacher does not own this schedule")
    return ScheduleRepository(db).list_audits(schedule_id)
