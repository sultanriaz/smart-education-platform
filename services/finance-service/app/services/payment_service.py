from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import EntityNotFoundError, FinanceDomainError
from app.domain.models import (
    FinanceAuditEvent,
    FinanceOutboxEvent,
    Invoice,
    InvoiceInstallment,
    Payment,
    PaymentAllocation,
    PaymentIntent,
    Receipt,
    RefundRequest,
    StudentFinancialAccount,
)
from app.services.accounting_service import AccountingService
from app.services.payment_adapters import get_adapter


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.accounting = AccountingService(db)

    def create_payment_intent(
        self,
        *,
        student_user_id: uuid.UUID,
        invoice_id: uuid.UUID,
        installment_id: uuid.UUID | None = None,
        amount: Decimal,
        provider: str = "JAZZ_CASH",
        allow_any_student: bool = False,
    ) -> tuple[PaymentIntent, dict[str, Any]]:
        invoice = self.db.scalar(select(Invoice).where(Invoice.id == invoice_id).with_for_update())
        if not invoice:
            raise EntityNotFoundError(f"Invoice {invoice_id} not found")

        if not allow_any_student and invoice.student_user_id != student_user_id:
            raise FinanceDomainError("Cannot create a payment intent for another student's invoice", status_code=403)

        if invoice.status in {"PAID", "CANCELLED"}:
            raise FinanceDomainError(f"Invoice {invoice.invoice_number} is already {invoice.status}")

        amt = Decimal(str(amount)).quantize(Decimal("0.01"))
        if amt <= Decimal("0.00"):
            raise FinanceDomainError("Payment amount must be greater than zero")

        if amt > invoice.balance_amount:
            raise FinanceDomainError(
                f"Payment amount ({amt}) exceeds remaining invoice balance ({invoice.balance_amount})"
            )

        now = datetime.now(UTC)
        intent = PaymentIntent(
            student_user_id=student_user_id,
            invoice_id=invoice_id,
            installment_id=installment_id,
            amount=amt,
            currency=settings.DEFAULT_CURRENCY,
            provider=provider.upper(),
            status="CREATED",
            expires_at=now + timedelta(hours=2),
        )
        self.db.add(intent)
        self.db.flush()

        adapter = get_adapter(provider)
        checkout_data = adapter.generate_checkout_payload(intent)
        intent.provider_reference = str(checkout_data.get("pp_TxnRefNo") or checkout_data.get("orderId") or checkout_data.get("consumer_number") or checkout_data.get("payment_code"))
        intent.status = "PENDING"

        self.db.commit()
        self.db.refresh(intent)
        return intent, checkout_data

    def confirm_payment(
        self,
        *,
        payment_intent_id: uuid.UUID,
        provider_transaction_id: str,
        method: str,
        actor_id: uuid.UUID | None = None,
    ) -> Payment:
        # 1. Idempotency check: if transaction already confirmed, return existing payment
        existing_payment = self.db.scalar(
            select(Payment).where(Payment.provider_transaction_id == provider_transaction_id)
        )
        if existing_payment:
            return existing_payment

        # 2. Lock intent
        intent = self.db.scalar(
            select(PaymentIntent).where(PaymentIntent.id == payment_intent_id).with_for_update()
        )
        if not intent:
            raise EntityNotFoundError(f"Payment intent {payment_intent_id} not found")

        if intent.status == "SUCCEEDED":
            # Already succeeded; fetch existing payment
            p = self.db.scalar(select(Payment).where(Payment.payment_intent_id == intent.id))
            if p:
                return p

        # 3. Lock invoice
        invoice = self.db.scalar(
            select(Invoice).where(Invoice.id == intent.invoice_id).with_for_update()
        )
        if not invoice:
            raise EntityNotFoundError(f"Invoice {intent.invoice_id} not found")

        # 4. Check for overpayment race
        if intent.amount > invoice.balance_amount:
            raise FinanceDomainError(
                f"Payment amount ({intent.amount}) exceeds remaining balance ({invoice.balance_amount})"
            )

        now = datetime.now(UTC)
        intent.status = "SUCCEEDED"

        receipt_no = f"REC-{now.strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
        payment = Payment(
            payment_intent_id=intent.id,
            student_user_id=intent.student_user_id,
            amount=intent.amount,
            currency=intent.currency,
            method=method,
            provider_transaction_id=provider_transaction_id,
            status="CONFIRMED",
            paid_at=now,
            receipt_number=receipt_no,
        )
        self.db.add(payment)
        self.db.flush()

        # Allocate payment to invoice
        invoice.paid_amount += intent.amount
        invoice.balance_amount -= intent.amount
        if invoice.balance_amount == Decimal("0.00"):
            invoice.status = "PAID"
        else:
            invoice.status = "PARTIALLY_PAID"

        # Allocate against installments
        remaining_alloc = intent.amount
        installments = self.db.scalars(
            select(InvoiceInstallment)
            .where(InvoiceInstallment.invoice_id == invoice.id)
            .order_by(InvoiceInstallment.installment_number)
            .with_for_update()
        ).all()

        for inst in installments:
            if remaining_alloc <= Decimal("0.00"):
                break
            inst_balance = inst.amount - inst.paid_amount
            if inst_balance > Decimal("0.00"):
                alloc_to_inst = min(remaining_alloc, inst_balance)
                inst.paid_amount += alloc_to_inst
                remaining_alloc -= alloc_to_inst
                if inst.paid_amount >= inst.amount:
                    inst.status = "PAID"
                else:
                    inst.status = "PARTIALLY_PAID"

                alloc = PaymentAllocation(
                    payment_id=payment.id,
                    invoice_id=invoice.id,
                    installment_id=inst.id,
                    amount=alloc_to_inst,
                    allocated_at=now,
                )
                self.db.add(alloc)

        # Update Student Account
        account = self.db.scalar(
            select(StudentFinancialAccount)
            .where(StudentFinancialAccount.id == invoice.account_id)
            .with_for_update()
        )
        if account:
            account.total_paid += intent.amount
            account.outstanding_balance = max(Decimal("0.00"), account.outstanding_balance - intent.amount)

        # Create Receipt
        receipt = Receipt(
            receipt_number=receipt_no,
            payment_id=payment.id,
            student_user_id=intent.student_user_id,
            amount=intent.amount,
            currency=intent.currency,
            issued_at=now,
            receipt_data={
                "receipt_number": receipt_no,
                "invoice_number": invoice.invoice_number,
                "student_user_id": str(intent.student_user_id),
                "amount": str(intent.amount),
                "currency": intent.currency,
                "payment_method": method,
                "provider_transaction_id": provider_transaction_id,
                "paid_at": now.isoformat(),
                "remaining_balance": str(invoice.balance_amount),
            },
        )
        self.db.add(receipt)

        # Post to General Ledger (Double-Entry Invariant: Debits == Credits)
        self.accounting.record_payment_receipt(payment, invoice)

        # Outbox event
        self.db.add(
            FinanceOutboxEvent(
                aggregate_id=payment.id,
                event_type="finance.payment.confirmed.v1",
                payload={
                    "payment_id": str(payment.id),
                    "invoice_id": str(invoice.id),
                    "student_user_id": str(intent.student_user_id),
                    "amount": str(payment.amount),
                    "method": method,
                    "receipt_number": receipt_no,
                },
            )
        )

        # Audit event
        self.db.add(
            FinanceAuditEvent(
                actor_id=actor_id,
                action="PAYMENT_CONFIRMED",
                resource_type="PAYMENT",
                resource_id=str(payment.id),
                details={"amount": str(payment.amount), "receipt_number": receipt_no},
            )
        )

        self.db.commit()
        self.db.refresh(payment)
        return payment

    def request_refund(
        self,
        *,
        payment_id: uuid.UUID,
        amount: Decimal,
        reason: str,
        requested_by_user_id: uuid.UUID,
    ) -> RefundRequest:
        payment = self.db.get(Payment, payment_id)
        if not payment or payment.status != "CONFIRMED":
            raise FinanceDomainError("Refund can only be requested for confirmed payments")

        amt = Decimal(str(amount)).quantize(Decimal("0.01"))
        if amt <= Decimal("0.00") or amt > payment.amount:
            raise FinanceDomainError(f"Refund amount must be between 0.01 and settled payment amount ({payment.amount})")

        # Check existing refunds
        existing_refunds = self.db.scalars(
            select(RefundRequest).where(
                RefundRequest.payment_id == payment_id,
                RefundRequest.status.in_({"REQUESTED", "APPROVED", "SETTLED"}),
            )
        ).all()
        total_refunded = sum(r.amount for r in existing_refunds)
        if total_refunded + amt > payment.amount:
            raise FinanceDomainError(
                f"Total requested/approved refunds ({total_refunded + amt}) would exceed payment amount ({payment.amount})"
            )

        invoice_id = payment.allocations[0].invoice_id if payment.allocations else None
        if not invoice_id:
            # Look up from intent
            intent = self.db.get(PaymentIntent, payment.payment_intent_id)
            invoice_id = intent.invoice_id if intent else None

        req = RefundRequest(
            payment_id=payment.id,
            invoice_id=invoice_id,
            student_user_id=payment.student_user_id,
            amount=amt,
            reason=reason,
            status="REQUESTED",
            requested_by_user_id=requested_by_user_id,
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def process_refund_decision(
        self,
        *,
        refund_id: uuid.UUID,
        approved_by_user_id: uuid.UUID,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> RefundRequest:
        refund = self.db.scalar(select(RefundRequest).where(RefundRequest.id == refund_id).with_for_update())
        if not refund or refund.status != "REQUESTED":
            raise FinanceDomainError("Refund request is not in a pending state")

        # Strict Maker-Checker Invariant
        if refund.requested_by_user_id == approved_by_user_id:
            raise FinanceDomainError("Maker-checker violation: An operator cannot approve their own refund request")

        refund.approved_by_user_id = approved_by_user_id
        if not approved:
            refund.status = "REJECTED"
            refund.rejection_reason = rejection_reason or "Rejected by reviewer"
            self.db.commit()
            return refund

        refund.status = "SETTLED"
        # Reverse balance on invoice and student account
        if refund.invoice_id:
            invoice = self.db.scalar(select(Invoice).where(Invoice.id == refund.invoice_id).with_for_update())
            if invoice:
                invoice.paid_amount -= refund.amount
                invoice.balance_amount += refund.amount
                if invoice.status == "PAID":
                    invoice.status = "PARTIALLY_PAID"

            account = self.db.scalar(
                select(StudentFinancialAccount)
                .where(StudentFinancialAccount.student_user_id == refund.student_user_id)
                .with_for_update()
            )
            if account:
                account.total_paid -= refund.amount
                account.outstanding_balance += refund.amount

        # Post general ledger adjustment
        self.accounting.record_refund(refund)

        # Outbox event
        self.db.add(
            FinanceOutboxEvent(
                aggregate_id=refund.id,
                event_type="finance.refund.completed.v1",
                payload={
                    "refund_id": str(refund.id),
                    "payment_id": str(refund.payment_id),
                    "student_user_id": str(refund.student_user_id),
                    "amount": str(refund.amount),
                },
            )
        )
        self.db.commit()
        self.db.refresh(refund)
        return refund

