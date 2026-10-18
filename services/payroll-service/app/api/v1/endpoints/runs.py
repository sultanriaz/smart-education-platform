from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import PayrollRun
from app.schemas.payroll import PayrollApprovalIn, PayrollRunCreateIn, PayrollRunOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/runs", tags=["Payroll Runs"])


@router.get("", response_model=list[PayrollRunOut])
def list_runs(
    period_id: uuid.UUID | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.runs.read", "admin", "payroll_officer")),
):
    query = select(PayrollRun).order_by(PayrollRun.created_at.desc())
    if period_id is not None:
        query = query.where(PayrollRun.period_id == period_id)
    if status is not None:
        query = query.where(PayrollRun.status == status.upper())
    return list(db.scalars(query).all())


@router.post("", response_model=PayrollRunOut, status_code=201)
def calculate_run(
    data: PayrollRunCreateIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.runs.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.calculate_payroll_run(
            period_id=data.period_id,
            created_by_user_id=principal.user_id,
            notes=data.notes,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{id}", response_model=PayrollRunOut)
def get_run(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.runs.read", "admin", "payroll_officer")),
):
    run = db.get(PayrollRun, id)
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    return run


@router.post("/{id}/decision", response_model=PayrollRunOut)
def decide_run(
    id: uuid.UUID,
    data: PayrollApprovalIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.runs.approve", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.approve_payroll_run(
            run_id=id,
            approved_by_user_id=principal.user_id,
            approved=data.approved,
            notes=data.notes,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

