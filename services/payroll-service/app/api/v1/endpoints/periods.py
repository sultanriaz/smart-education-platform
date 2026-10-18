from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import PayrollPeriod
from app.schemas.payroll import PayrollPeriodIn, PayrollPeriodOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/periods", tags=["Payroll Periods"])


@router.get("", response_model=list[PayrollPeriodOut])
def list_periods(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.periods.read", "admin", "payroll_officer")),
):
    query = select(PayrollPeriod).order_by(PayrollPeriod.year.desc(), PayrollPeriod.month.desc())
    return list(db.scalars(query).all())


@router.post("", response_model=PayrollPeriodOut, status_code=201)
def create_period(
    data: PayrollPeriodIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.periods.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.create_period(
            year=data.year,
            month=data.month,
            start_date=data.start_date,
            end_date=data.end_date,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

