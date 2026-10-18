from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import FeeStructure
from app.schemas.finance import FeeStructureIn, FeeStructureOut
from app.security.auth import Principal, require_scoped_roles
from app.services.fee_service import FeeService

router = APIRouter(prefix="/fee-structures", tags=["Fee Structures"])


@router.get("", response_model=list[FeeStructureOut])
def list_fee_structures(
    program_id: uuid.UUID | None = None,
    academic_year_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.fees.read", "admin", "teacher", "finance_officer")),
):
    svc = FeeService(db)
    return svc.list_fee_structures(program_id=program_id, academic_year_id=academic_year_id, is_active=is_active)


@router.post("", response_model=FeeStructureOut, status_code=201)
def create_fee_structure(
    data: FeeStructureIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.fees.manage", "admin", "finance_officer")),
):
    svc = FeeService(db)
    try:
        return svc.create_fee_structure(
            name=data.name,
            program_id=data.program_id,
            academic_year_id=data.academic_year_id,
            semester_number=data.semester_number,
            components_data=[c.model_dump() for c in data.components],
            is_active=data.is_active,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{id}", response_model=FeeStructureOut)
def get_fee_structure(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.fees.read", "admin", "teacher", "finance_officer")),
):
    svc = FeeService(db)
    try:
        return svc.get_fee_structure(id)
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

