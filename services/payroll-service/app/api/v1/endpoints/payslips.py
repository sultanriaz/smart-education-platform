from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.domain.models import EmployeePayrollProfile, Payslip
from app.schemas.payroll import PayslipOut
from app.security.auth import Principal, require_scoped_roles

router = APIRouter(prefix="/payslips", tags=["Payslips"])


@router.get("", response_model=list[PayslipOut])
def list_payslips(
    employee_profile_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.payslips.read", "admin", "payroll_officer")),
):
    query = select(Payslip).order_by(Payslip.created_at.desc())
    if employee_profile_id is not None:
        query = query.where(Payslip.employee_profile_id == employee_profile_id)
    if period_id is not None:
        query = query.where(Payslip.period_id == period_id)
    return list(db.scalars(query).all())


@router.get("/my/list", response_model=list[PayslipOut])
@router.get("/my-payslips", response_model=list[PayslipOut])
def list_my_payslips(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.my.payslips", "teacher", "admin", "employee")),
):
    profile = db.scalar(select(EmployeePayrollProfile).where(EmployeePayrollProfile.user_id == principal.user_id))
    if not profile:
        return []
    query = (
        select(Payslip)
        .where(Payslip.employee_profile_id == profile.id, Payslip.is_published == True)
        .order_by(Payslip.created_at.desc())
    )
    return list(db.scalars(query).all())


@router.get("/{id}", response_model=PayslipOut)
def get_payslip(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.payslips.read", "admin", "teacher", "employee", "payroll_officer")),
):
    payslip = db.get(Payslip, id)
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    # Enforce strict employee isolation: teacher/employee can only view their own payslip
    if "teacher" in principal.roles and "admin" not in principal.roles:
        profile = db.get(EmployeePayrollProfile, payslip.employee_profile_id)
        if not profile or profile.user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Cannot access another employee's payslip")

    return payslip


@router.get("/{id}/download")
def download_payslip(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.payslips.read", "admin", "teacher", "employee", "payroll_officer")),
):
    payslip = db.get(Payslip, id)
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")

    if "teacher" in principal.roles and "admin" not in principal.roles:
        profile = db.get(EmployeePayrollProfile, payslip.employee_profile_id)
        if not profile or profile.user_id != principal.user_id:
            raise HTTPException(status_code=403, detail="Cannot access another employee's payslip")

    profile = db.get(EmployeePayrollProfile, payslip.employee_profile_id)
    emp_name = profile.full_name if profile else "Employee"
    emp_no = profile.employee_number if profile else "N/A"

    text_slip = f"""==================================================
           SMART EDUCATION PLATFORM
              OFFICIAL SALARY PAYSLIP
==================================================
Payslip Number:  {payslip.payslip_number}
Issue Date:      {payslip.issue_date.isoformat()}
Employee Number: {emp_no}
Employee Name:   {emp_name}
Designation:     {profile.designation if profile else 'Faculty'}
--------------------------------------------------
EARNINGS & ALLOWANCES:
Gross Salary:    PKR {payslip.gross_salary}
Net Salary:      PKR {payslip.net_salary}
--------------------------------------------------
Status: DISBURSED / PAID
Generated electronically by SmartEdu Payroll System.
==================================================
"""
    return PlainTextResponse(
        content=text_slip,
        headers={"Content-Disposition": f"attachment; filename=payslip-{payslip.payslip_number}.txt"},
    )
