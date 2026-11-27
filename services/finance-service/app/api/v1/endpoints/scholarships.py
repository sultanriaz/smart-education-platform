from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import Scholarship, ScholarshipAward
from app.schemas.finance import ScholarshipAwardIn, ScholarshipAwardOut, ScholarshipIn, ScholarshipOut
from app.security.auth import Principal, require_scoped_roles
from app.services.fee_service import FeeService

router = APIRouter(prefix="/scholarships", tags=["Scholarships"])


@router.get("", response_model=list[ScholarshipOut])
def list_scholarships(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.scholarships.read", "admin", "teacher", "finance_officer")),
):
    query = select(Scholarship).order_by(Scholarship.created_at.desc())
    if is_active is not None:
        query = query.where(Scholarship.is_active == is_active)
    return list(db.scalars(query).all())


@router.post("", response_model=ScholarshipOut, status_code=201)
def create_scholarship(
    data: ScholarshipIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.scholarships.manage", "admin", "finance_officer")),
):
    svc = FeeService(db)
    try:
        return svc.create_scholarship(
            name=data.name,
            code=data.code,
            scholarship_type=data.scholarship_type,
            percentage=data.percentage,
            applies_to_components=data.applies_to_components,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/awards", response_model=list[ScholarshipAwardOut])
def list_scholarship_awards(
    student_user_id: uuid.UUID | None = None,
    academic_year_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.scholarships.read", "admin", "finance_officer", "student")),
):
    query = select(ScholarshipAward).order_by(ScholarshipAward.created_at.desc())
    is_finance_staff = bool(principal.roles.intersection({"admin", "finance_officer"})) or (
        "finance.scholarships.read" in principal.permissions
    )
    if not is_finance_staff:
        query = query.where(ScholarshipAward.student_user_id == principal.user_id)
    elif student_user_id is not None:
        query = query.where(ScholarshipAward.student_user_id == student_user_id)
    if academic_year_id is not None:
        query = query.where(ScholarshipAward.academic_year_id == academic_year_id)
    return list(db.scalars(query).all())


@router.post("/awards", response_model=ScholarshipAwardOut, status_code=201)
def award_scholarship(
    data: ScholarshipAwardIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.scholarships.manage", "admin", "finance_officer")),
):
    svc = FeeService(db)
    try:
        return svc.award_scholarship(
            scholarship_id=data.scholarship_id,
            student_user_id=data.student_user_id,
            academic_year_id=data.academic_year_id,
            semester_number=data.semester_number,
            granted_by_user_id=principal.user_id,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

