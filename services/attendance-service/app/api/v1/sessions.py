from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import Actor, Dates, Limit, Offset, Service
from app.schemas.attendance import (
    AttendanceRead,
    BulkMark,
    Correction,
    CorrectionRead,
    Reason,
    SessionCreate,
    SessionHistoryRead,
    SessionPatch,
    SessionRead,
)

router = APIRouter(prefix="/sessions", tags=["attendance sessions"])


@router.post("", response_model=SessionRead, status_code=201)
def create_session(payload: SessionCreate, actor: Actor, service: Service):
    return service.create_session(actor, payload)


@router.get("", response_model=list[SessionRead])
def list_sessions(
    actor: Actor,
    service: Service,
    dates: Dates,
    section_id: UUID | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    return service.list_sessions(actor, section_id=section_id, limit=limit, offset=offset, **dates)


@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: UUID, actor: Actor, service: Service):
    return service.get_session(actor, session_id)


@router.patch("/{session_id}", response_model=SessionRead)
def update_session(session_id: UUID, payload: SessionPatch, actor: Actor, service: Service):
    return service.update_session(actor, session_id, payload)


@router.post("/{session_id}/finalize", response_model=SessionRead)
def finalize_session(session_id: UUID, actor: Actor, service: Service):
    return service.finalize(actor, session_id)


@router.post("/{session_id}/reopen", response_model=SessionRead)
def reopen_session(session_id: UUID, payload: Reason, actor: Actor, service: Service):
    return service.reopen(actor, session_id, payload.reason)


@router.post("/{session_id}/cancel", response_model=SessionRead)
def cancel_session(session_id: UUID, payload: Reason, actor: Actor, service: Service):
    return service.cancel(actor, session_id, payload.reason)


@router.get("/{session_id}/records", response_model=list[AttendanceRead])
def get_records(
    session_id: UUID, actor: Actor, service: Service, limit: Limit = 50, offset: Offset = 0
):
    return service.records(actor, session_id, limit=limit, offset=offset)


@router.put("/{session_id}/records", response_model=list[AttendanceRead])
def mark_attendance(session_id: UUID, payload: BulkMark, actor: Actor, service: Service):
    return service.bulk_mark(actor, session_id, payload)


@router.patch("/{session_id}/records/{student_user_id}", response_model=AttendanceRead)
def correct_record(
    session_id: UUID, student_user_id: UUID, payload: Correction, actor: Actor, service: Service
):
    return service.correct(actor, session_id, student_user_id, payload)


@router.get("/{session_id}/history", response_model=list[SessionHistoryRead])
def session_history(
    session_id: UUID, actor: Actor, service: Service, limit: Limit = 50, offset: Offset = 0
):
    return service.history(actor, session_id, limit=limit, offset=offset)


@router.get("/{session_id}/records/{student_user_id}/history", response_model=list[CorrectionRead])
def correction_history(
    session_id: UUID,
    student_user_id: UUID,
    actor: Actor,
    service: Service,
    limit: Limit = 50,
    offset: Offset = 0,
):
    return service.history(
        actor, session_id, student_id=student_user_id, limit=limit, offset=offset
    )
