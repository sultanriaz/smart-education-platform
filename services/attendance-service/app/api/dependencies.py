from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient, HttpAcademicClient
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.db.session import get_db
from app.security.dependencies import get_principal
from app.security.jwt import Principal
from app.services.attendance import AttendanceService


def get_academic_client() -> Iterator[AcademicClient]:
    with httpx.Client() as http:
        yield HttpAcademicClient(get_settings(), http)


def get_service(
    db: Annotated[Session, Depends(get_db)],
    academic: Annotated[AcademicClient, Depends(get_academic_client)],
) -> AttendanceService:
    return AttendanceService(db, academic, get_settings())


def date_filters(date_from: date | None = None, date_to: date | None = None) -> dict:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise DomainError(422, "date_from must not be after date_to.", "validation_error")
    return {"date_from": date_from, "date_to": date_to}


def report_filters(
    dates: Annotated[dict, Depends(date_filters)],
    course_id: UUID | None = None,
    semester_id: UUID | None = None,
) -> dict:
    return {**dates, "course_id": course_id, "semester_id": semester_id}


Service = Annotated[AttendanceService, Depends(get_service)]
Actor = Annotated[Principal, Depends(get_principal)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]
Dates = Annotated[dict, Depends(date_filters)]
Filters = Annotated[dict, Depends(report_filters)]
