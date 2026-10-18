from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import DisbursementBatch
from app.schemas.payroll import DisbursementBatchOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/disbursements", tags=["Disbursements"])


@router.get("/batches", response_model=list[DisbursementBatchOut])
def list_batches(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.read", "admin", "payroll_officer")),
):
    query = select(DisbursementBatch).order_by(DisbursementBatch.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/batches/{id}", response_model=DisbursementBatchOut)
def get_batch(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.read", "admin", "payroll_officer")),
):
    batch = db.get(DisbursementBatch, id)
    if not batch:
        raise HTTPException(status_code=404, detail="Disbursement batch not found")
    return batch


@router.post("/runs/{run_id}/disburse", response_model=DisbursementBatchOut)
def disburse_run(
    run_id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.execute_disbursements(run_id=run_id, actor_id=principal.user_id)
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

