from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import PayrollDomainError
from app.domain.models import DisbursementBatch
from app.schemas.payroll import (
    BatchReconciliationOut,
    DisburseRunIn,
    DisbursementBatchOut,
    DisbursementRecordOut,
    DisbursementRetryIn,
)
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
    body: DisburseRunIn | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    simulate_failures = body.simulate_failures if body else False
    fail_employee_ids = body.fail_employee_ids if body else []
    try:
        return svc.execute_disbursements(
            run_id=run_id,
            actor_id=principal.user_id,
            simulate_failures=simulate_failures,
            fail_employee_ids=fail_employee_ids,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/records/{record_id}/retry", response_model=DisbursementRecordOut)
def retry_disbursement_record(
    record_id: uuid.UUID,
    body: DisbursementRetryIn | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    corrected_bank = body.corrected_bank_name if body else None
    corrected_acc = body.corrected_account_number if body else None
    try:
        return svc.retry_disbursement_record(
            record_id=record_id,
            corrected_bank_name=corrected_bank,
            corrected_account_number=corrected_acc,
            actor_id=principal.user_id,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/batches/{batch_id}/reconcile", response_model=BatchReconciliationOut)
def reconcile_batch(
    batch_id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.disbursement.manage", "admin", "payroll_officer")),
):
    svc = PayrollService(db)
    try:
        return svc.reconcile_disbursement_batch(
            batch_id=batch_id,
            actor_id=principal.user_id,
        )
    except PayrollDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


