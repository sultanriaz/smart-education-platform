from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import EmployeePayrollProfile
from app.schemas.payroll import EmployeePayrollProfileIn, EmployeePayrollProfileOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/profiles", tags=["Employee Profiles"])


@router.get("", response_model=list[EmployeePayrollProfileOut])
def list_profiles(
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.profiles.read", "admin", "payroll_officer")),
):
    query = select(EmployeePayrollProfile).order_by(EmployeePayrollProfile.created_at.desc())
    if is_active is not None:
        query = query.where(EmployeePayrollProfile.is_active == is_active)
    return list(db.scalars(query).all())


@router.post("", response_model=EmployeePayrollProfileOut, status_code=201)
def create_profile(
    data: EmployeePayrollProfileIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.profiles.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.create_employee_profile(
            user_id=data.user_id,
            employee_number=data.employee_number,
            full_name=data.full_name,
            email=data.email,
            designation=data.designation,
            employment_type=data.employment_type,
            department_id=data.department_id,
            bank_name=data.bank_name,
            bank_account_number=data.bank_account_number,
            is_active=data.is_active,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/by-user/{user_id}", response_model=EmployeePayrollProfileOut)
def get_profile_by_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.profiles.read", "admin", "payroll_officer", "teacher")),
):
    if "teacher" in principal.roles and "admin" not in principal.roles and principal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access another employee's profile")

    profile = db.scalar(select(EmployeePayrollProfile).where(EmployeePayrollProfile.user_id == user_id))
    if not profile:
        raise HTTPException(status_code=404, detail="Employee payroll profile not found")
    return profile


@router.get("/{id}", response_model=EmployeePayrollProfileOut)
def get_profile(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.profiles.read", "admin", "payroll_officer")),
):
    profile = db.get(EmployeePayrollProfile, id)
    if not profile:
        profile = db.scalar(select(EmployeePayrollProfile).where(EmployeePayrollProfile.user_id == id))
    if not profile:
        raise HTTPException(status_code=404, detail="Employee payroll profile not found")
    return profile

