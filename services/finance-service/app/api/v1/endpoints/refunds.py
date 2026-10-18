from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import RefundRequest
from app.schemas.finance import RefundApprovalIn, RefundRequestIn, RefundRequestOut
from app.security.auth import Principal, require_scoped_roles
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.get("", response_model=list[RefundRequestOut])
def list_refunds(
    status: str | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.refunds.read", "admin", "finance_officer")),
):
    query = select(RefundRequest).order_by(RefundRequest.created_at.desc())
    if status is not None:
        query = query.where(RefundRequest.status == status.upper())
    return list(db.scalars(query).all())


@router.post("", response_model=RefundRequestOut, status_code=201)
@router.post("/request", response_model=RefundRequestOut, status_code=201)
def request_refund(
    data: RefundRequestIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.refunds.manage", "admin", "finance_officer")),
):
    svc = PaymentService(db)
    try:
        return svc.request_refund(
            payment_id=data.payment_id,
            amount=data.amount,
            reason=data.reason,
            requested_by_user_id=principal.user_id,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{id}/approve", response_model=RefundRequestOut)
def approve_refund(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.refunds.approve", "admin", "finance_officer")),
):
    svc = PaymentService(db)
    try:
        return svc.process_refund_decision(
            refund_id=id,
            approved_by_user_id=principal.user_id,
            approved=True,
            rejection_reason=None,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{id}/decision", response_model=RefundRequestOut)
def decide_refund(
    id: uuid.UUID,
    data: RefundApprovalIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.refunds.approve", "admin", "finance_officer")),
):
    svc = PaymentService(db)
    try:
        return svc.process_refund_decision(
            refund_id=id,
            approved_by_user_id=principal.user_id,
            approved=data.approved,
            rejection_reason=data.notes,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
