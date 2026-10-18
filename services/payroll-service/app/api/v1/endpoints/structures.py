from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import SalaryStructure
from app.schemas.payroll import SalaryStructureIn, SalaryStructureOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/structures", tags=["Salary Structures"])


@router.post("", response_model=SalaryStructureOut, status_code=201)
def assign_salary_structure(
    data: SalaryStructureIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.structures.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.assign_salary_structure(
            employee_profile_id=data.employee_profile_id,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            base_salary=data.base_salary,
            components_data=[c.model_dump() for c in data.components],
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/by-profile/{profile_id}", response_model=list[SalaryStructureOut])
def get_structures_by_profile(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.structures.read", "admin", "payroll_officer")),
):
    query = (
        select(SalaryStructure)
        .where(SalaryStructure.employee_profile_id == profile_id)
        .order_by(SalaryStructure.created_at.desc())
    )
    return list(db.scalars(query).all())

