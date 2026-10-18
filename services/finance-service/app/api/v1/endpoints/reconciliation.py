from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import ReconciliationBatch
from app.schemas.finance import ReconciliationBatchOut
from app.security.auth import Principal, require_scoped_roles
from app.services.reconciliation_service import ReconciliationService

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])


@router.get("/batches", response_model=list[ReconciliationBatchOut])
def list_batches(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.reconciliation.read", "admin", "finance_officer")),
):
    query = select(ReconciliationBatch).order_by(ReconciliationBatch.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/batches/{id}", response_model=ReconciliationBatchOut)
def get_batch(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.reconciliation.read", "admin", "finance_officer")),
):
    batch = db.get(ReconciliationBatch, id)
    if not batch:
        raise HTTPException(status_code=404, detail="Reconciliation batch not found")
    return batch


@router.post("/upload", response_model=ReconciliationBatchOut)
async def upload_settlement_csv(
    provider: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.reconciliation.manage", "admin", "finance_officer")),
):
    svc = ReconciliationService(db)
    content = (await file.read()).decode("utf-8", errors="replace")
    try:
        return svc.process_settlement_csv(
            filename=file.filename or "settlement.csv",
            provider=provider,
            csv_content=content,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

