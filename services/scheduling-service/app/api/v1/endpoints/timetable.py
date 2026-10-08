from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient, get_academic_client
from app.core.errors import DomainError
from app.db.session import get_db
from app.schemas.schedule import OccurrenceOut
from app.security.auth import Principal, get_current_principal
from app.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/timetable", tags=["Timetable"])


def _run(service: SchedulingService, **kwargs):
    try:
        return service.generate_occurrences(**kwargs)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/me", response_model=list[OccurrenceOut])
def my_timetable(
    start_date: date = Query(...),
    end_date: date = Query(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    return _run(
        SchedulingService(db, academic),
        start_date=start_date,
        end_date=end_date,
        principal=principal,
        me=True,
    )


@router.get("/sections/{section_id}", response_model=list[OccurrenceOut])
def section_timetable(
    section_id: uuid.UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    return _run(
        SchedulingService(db, academic),
        start_date=start_date,
        end_date=end_date,
        principal=principal,
        section_id=section_id,
    )


@router.get("/teachers/{teacher_user_id}", response_model=list[OccurrenceOut])
def teacher_timetable(
    teacher_user_id: uuid.UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    return _run(
        SchedulingService(db, academic),
        start_date=start_date,
        end_date=end_date,
        principal=principal,
        teacher_user_id=teacher_user_id,
    )


@router.get("/rooms/{room_id}", response_model=list[OccurrenceOut])
def room_timetable(
    room_id: uuid.UUID,
    start_date: date = Query(...),
    end_date: date = Query(...),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
):
    if principal.has_role("student"):
        raise HTTPException(status_code=403, detail="Room timetable is restricted")
    return _run(
        SchedulingService(db, academic),
        start_date=start_date,
        end_date=end_date,
        principal=principal,
        room_id=room_id,
    )
