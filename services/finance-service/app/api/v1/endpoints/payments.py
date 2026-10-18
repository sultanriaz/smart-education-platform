from __future__ import annotations

import time
import uuid
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import Payment, PaymentIntent, Receipt
from app.schemas.finance import PaymentIntentCreateIn, PaymentIntentOut, PaymentOut, ReceiptOut, SimulatePaymentIn
from app.security.auth import Principal, require_scoped_roles
from app.services.payment_adapters import get_adapter
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/intent")
def create_payment_intent(
    data: PaymentIntentCreateIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.payments.create", "admin", "student", "finance_officer")),
):
    svc = PaymentService(db)
    try:
        intent, checkout = svc.create_payment_intent(
            student_user_id=principal.user_id,
            invoice_id=data.invoice_id,
            installment_id=data.installment_id,
            amount=data.amount,
            provider=data.provider,
        )
        return {
            "intent": PaymentIntentOut.model_validate(intent),
            "checkout_data": checkout,
        }
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/callback/{provider}")
async def payment_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(None),
    x_timestamp: str | None = Header(None),
):
    adapter = get_adapter(provider)
    payload = await request.json()

    signature = x_signature or payload.get("signature") or ""
    try:
        ts = float(x_timestamp or payload.get("timestamp") or payload.get("pp_TxnDateTime") or time.time())
    except Exception:
        ts = 0.0

    if not adapter.verify_callback(payload, signature, ts):
        raise HTTPException(status_code=400, detail="Invalid callback signature or expired timestamp")

    # Extract transaction reference and intent
    txn_ref = payload.get("pp_TxnRefNo") or payload.get("orderId") or payload.get("transaction_id") or str(uuid.uuid4())
    intent_id_str = payload.get("intent_id") or payload.get("client_reference")

    svc = PaymentService(db)
    if not intent_id_str:
        # Search by provider reference
        intent = db.scalar(select(PaymentIntent).where(PaymentIntent.provider_reference == txn_ref))
        if not intent:
            return {"status": "ignored", "reason": "No matching intent"}
        intent_id = intent.id
    else:
        intent_id = uuid.UUID(str(intent_id_str))

    payment = svc.confirm_payment(
        payment_intent_id=intent_id,
        provider_transaction_id=txn_ref,
        method=provider.upper(),
    )
    return {"status": "confirmed", "payment_id": str(payment.id), "receipt_number": payment.receipt_number}


@router.post("/simulate", response_model=PaymentOut)
def simulate_payment(
    data: SimulatePaymentIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.payments.manage", "admin", "student", "finance_officer")),
):
    svc = PaymentService(db)
    intent = db.get(PaymentIntent, data.payment_intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    if data.fail:
        intent.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail="Simulated payment failure")

    txn_ref = data.transaction_ref or f"SIM-{intent.provider[:3]}-{uuid.uuid4().hex[:10].upper()}"
    try:
        return svc.confirm_payment(
            payment_intent_id=intent.id,
            provider_transaction_id=txn_ref,
            method=intent.provider,
            actor_id=principal.user_id,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("", response_model=list[PaymentOut])
def list_payments(
    student_user_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.payments.read", "admin", "teacher", "finance_officer", "student")),
):
    query = select(Payment).order_by(Payment.created_at.desc())
    if "student" in principal.roles and "admin" not in principal.roles:
        query = query.where(Payment.student_user_id == principal.user_id)
    elif student_user_id is not None:
        query = query.where(Payment.student_user_id == student_user_id)
    return list(db.scalars(query).all())


@router.get("/{id}", response_model=PaymentOut)
def get_payment(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.payments.read", "admin", "teacher", "finance_officer", "student")),
):
    payment = db.get(Payment, id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if "student" in principal.roles and "admin" not in principal.roles and principal.user_id != payment.student_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another student's payment record")

    return payment


@router.get("/receipts/{id}", response_model=ReceiptOut)
def get_receipt(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.payments.read", "admin", "teacher", "finance_officer", "student")),
):
    receipt = db.get(Receipt, id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    if "student" in principal.roles and "admin" not in principal.roles and principal.user_id != receipt.student_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another student's receipt")

    return receipt

