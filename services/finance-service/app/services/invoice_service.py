from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import EntityNotFoundError, FinanceDomainError
from app.domain.models import (
    FeeStructure,
    FinanceAuditEvent,
    FinanceOutboxEvent,
    InstitutionConfig,
    Invoice,
    InvoiceInstallment,
    InvoiceLineItem,
    StudentFinancialAccount,
)
from app.services.accounting_service import AccountingService
from app.services.fee_service import FeeService


class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.accounting = AccountingService(db)
        self.fee_svc = FeeService(db)

    def get_or_create_account(self, student_user_id: uuid.UUID) -> StudentFinancialAccount:
        account = self.db.scalar(
            select(StudentFinancialAccount)
            .where(StudentFinancialAccount.student_user_id == student_user_id)
            .with_for_update()
        )
        if account is None:
            acct_num = f"SFA-{datetime.now(UTC).strftime('%Y')}-{uuid.uuid4().hex[:8].upper()}"
            account = StudentFinancialAccount(
                student_user_id=student_user_id,
                account_number=acct_num,
                status="ACTIVE",
            )
            self.db.add(account)
            self.db.flush()
        return account

    def create_invoice(
        self,
        *,
        student_user_id: uuid.UUID,
        program_id: uuid.UUID,
        academic_year_id: uuid.UUID,
        semester_number: int,
        due_date: date | None = None,
        installments_count: int = 3,
        actor_id: uuid.UUID | None = None,
    ) -> Invoice:
        # Check duplicate invoice prevention for same student, program, semester, year
        existing = self.db.scalar(
            select(Invoice).where(
                Invoice.student_user_id == student_user_id,
                Invoice.program_id == program_id,
                Invoice.academic_year_id == academic_year_id,
                Invoice.semester_number == semester_number,
                Invoice.status != "CANCELLED",
            )
        )
        if existing:
            raise FinanceDomainError(
                f"Active invoice {existing.invoice_number} already exists for student in this semester"
            )

        fee_struct = self.fee_svc.find_fee_structure(program_id, academic_year_id, semester_number)
        if not fee_struct or not fee_struct.components:
            raise FinanceDomainError(
                f"No active fee structure found for program {program_id}, semester {semester_number}"
            )

        account = self.get_or_create_account(student_user_id)
        now_date = datetime.now(UTC).date()
        target_due_date = due_date or (now_date + timedelta(days=21))

        # Calculate line items & subtotal
        subtotal = sum(c.amount for c in fee_struct.components)
        scholarship_concession, discounts = self.fee_svc.calculate_concession(
            student_user_id, academic_year_id, semester_number, fee_struct.components
        )
        total_payable = max(Decimal("0.00"), subtotal - scholarship_concession)

        inv_num = f"INV-{now_date.strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
        invoice = Invoice(
            invoice_number=inv_num,
            student_user_id=student_user_id,
            account_id=account.id,
            program_id=program_id,
            academic_year_id=academic_year_id,
            semester_number=semester_number,
            issue_date=now_date,
            due_date=target_due_date,
            subtotal=subtotal,
            scholarship_amount=scholarship_concession,
            total_amount=total_payable,
            paid_amount=Decimal("0.00"),
            balance_amount=total_payable,
            status="ISSUED",
        )
        self.db.add(invoice)
        self.db.flush()

        # Add line items
        for comp in fee_struct.components:
            disc = discounts.get(comp.name, Decimal("0.00"))
            net = comp.amount - disc
            line = InvoiceLineItem(
                invoice_id=invoice.id,
                component_name=comp.name,
                component_type=comp.component_type,
                amount=comp.amount,
                discount_amount=disc,
                net_amount=net,
            )
            self.db.add(line)

        # Generate installments (default 3 installments)
        count = max(1, min(installments_count, 6))
        base_inst = (total_payable / count).quantize(Decimal("0.01"))
        accumulated = Decimal("0.00")

        for i in range(1, count + 1):
            inst_due = target_due_date + timedelta(days=(i - 1) * 30)
            if i == count:
                inst_amount = total_payable - accumulated
            else:
                inst_amount = base_inst
                accumulated += inst_amount

            inst = InvoiceInstallment(
                invoice_id=invoice.id,
                installment_number=i,
                due_date=inst_due,
                amount=inst_amount,
                paid_amount=Decimal("0.00"),
                status="PENDING",
            )
            self.db.add(inst)

        # Update Account Balances
        account.total_invoiced += total_payable
        account.total_scholarships += scholarship_concession
        account.outstanding_balance += total_payable

        # General Ledger Double-Entry Posting
        self.accounting.record_invoice_issuance(invoice)

        # Outbox event
        self.db.add(
            FinanceOutboxEvent(
                aggregate_id=invoice.id,
                event_type="finance.invoice.issued.v1",
                payload={
                    "invoice_id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "student_user_id": str(student_user_id),
                    "total_amount": str(invoice.total_amount),
                    "due_date": invoice.due_date.isoformat(),
                    "issue_date": invoice.issue_date.isoformat(),
                },
            )
        )

        # Audit event
        self.db.add(
            FinanceAuditEvent(
                actor_id=actor_id,
                action="INVOICE_ISSUED",
                resource_type="INVOICE",
                resource_id=str(invoice.id),
                details={"invoice_number": invoice.invoice_number, "total_amount": str(invoice.total_amount)},
            )
        )

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def apply_late_fee_if_overdue(
        self,
        invoice_id: uuid.UUID,
        as_of_date: date | None = None,
    ) -> Invoice:
        invoice = self.db.scalar(select(Invoice).where(Invoice.id == invoice_id).with_for_update())
        if not invoice:
            raise EntityNotFoundError(f"Invoice {invoice_id} not found")

        current_date = as_of_date or datetime.now(UTC).date()
        grace_days = settings.LATE_FEE_GRACE_DAYS
        overdue_threshold = invoice.due_date + timedelta(days=grace_days)

        if current_date > overdue_threshold and invoice.status in {"ISSUED", "PARTIALLY_PAID"} and not invoice.late_fee_applied:
            fee_amount = Decimal(str(settings.LATE_FEE_AMOUNT)).quantize(Decimal("0.01"))
            invoice.late_fee_applied = True
            invoice.late_fee_amount = fee_amount
            invoice.total_amount += fee_amount
            invoice.balance_amount += fee_amount
            invoice.status = "OVERDUE"

            account = self.db.scalar(
                select(StudentFinancialAccount)
                .where(StudentFinancialAccount.id == invoice.account_id)
                .with_for_update()
            )
            if account:
                account.outstanding_balance += fee_amount
                account.total_invoiced += fee_amount

            # General Ledger posting
            self.accounting.record_late_fee(invoice, fee_amount)

            # Outbox event
            self.db.add(
                FinanceOutboxEvent(
                    aggregate_id=invoice.id,
                    event_type="finance.invoice.overdue.v1",
                    payload={
                        "invoice_id": str(invoice.id),
                        "invoice_number": invoice.invoice_number,
                        "student_user_id": str(invoice.student_user_id),
                        "late_fee_amount": str(fee_amount),
                    },
                )
            )
            self.db.commit()
            self.db.refresh(invoice)

        return invoice

