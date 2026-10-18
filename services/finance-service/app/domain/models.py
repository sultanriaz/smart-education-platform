from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class InstitutionConfig(Base):
    __tablename__ = "institution_configs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_name: Mapped[str] = mapped_column(String(160), default="SmartEdu Demo University")
    currency: Mapped[str] = mapped_column(String(3), default="PKR")
    timezone_name: Mapped[str] = mapped_column(String(60), default="Asia/Karachi")
    late_fee_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("500.00"))
    late_fee_grace_days: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), index=True)
    program_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    semester_number: Mapped[int] = mapped_column(Integer, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    components: Mapped[list[FeeComponent]] = relationship(
        "FeeComponent", back_populates="fee_structure", cascade="all, delete-orphan"
    )


class FeeComponent(Base):
    __tablename__ = "fee_components"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fee_structure_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("fee_structures.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    component_type: Mapped[str] = mapped_column(String(50))  # TUITION, EXAMINATION, LABORATORY, LIBRARY, OTHER
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    is_refundable: Mapped[bool] = mapped_column(Boolean, default=False)
    eligible_for_scholarship: Mapped[bool] = mapped_column(Boolean, default=True)

    fee_structure: Mapped[FeeStructure] = relationship("FeeStructure", back_populates="components")


class StudentFinancialAccount(Base):
    __tablename__ = "student_financial_accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    account_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True)  # ACTIVE, SUSPENDED, HOLD
    total_invoiced: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    total_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    total_scholarships: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    outstanding_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    invoices: Mapped[list[Invoice]] = relationship("Invoice", back_populates="account")


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    scholarship_type: Mapped[str] = mapped_column(String(50))  # MERIT, NEED_BASED, SPECIAL
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2))  # e.g. 25.00
    applies_to_components: Mapped[list[str]] = mapped_column(JSON, default=list)  # ["TUITION"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ScholarshipAward(Base):
    __tablename__ = "scholarship_awards"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholarship_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("scholarships.id"), index=True)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    semester_number: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True)  # ACTIVE, REVOKED, EXPIRED
    granted_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    scholarship: Mapped[Scholarship] = relationship("Scholarship")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("student_financial_accounts.id"), index=True
    )
    program_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    academic_year_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    semester_number: Mapped[int] = mapped_column(Integer, index=True)
    issue_date: Mapped[date] = mapped_column(Date, index=True)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    scholarship_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    balance_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    late_fee_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    late_fee_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(
        String(30), default="ISSUED", index=True
    )  # DRAFT, ISSUED, PARTIALLY_PAID, PAID, OVERDUE, CANCELLED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    account: Mapped[StudentFinancialAccount] = relationship("StudentFinancialAccount", back_populates="invoices")
    items: Mapped[list[InvoiceLineItem]] = relationship(
        "InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    installments: Mapped[list[InvoiceInstallment]] = relationship(
        "InvoiceInstallment", back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    component_name: Mapped[str] = mapped_column(String(100))
    component_type: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="items")


class InvoiceInstallment(Base):
    __tablename__ = "invoice_installments"
    __table_args__ = (
        UniqueConstraint("invoice_id", "installment_number", name="uq_invoice_installment_num"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    installment_number: Mapped[int] = mapped_column(Integer)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    late_fee_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(
        String(20), default="PENDING", index=True
    )  # PENDING, PARTIALLY_PAID, PAID, OVERDUE

    invoice: Mapped[Invoice] = relationship("Invoice", back_populates="installments")


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("invoices.id"), index=True)
    installment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PKR")
    provider: Mapped[str] = mapped_column(String(50))  # JAZZ_CASH, EASYPAISA, BANK_TRANSFER, CASH
    status: Mapped[str] = mapped_column(
        String(30), default="CREATED", index=True
    )  # CREATED, PENDING, SUCCEEDED, FAILED, EXPIRED, CANCELLED
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    client_secret: Mapped[str] = mapped_column(String(120), default=lambda: uuid.uuid4().hex)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payment_intents.id"), nullable=True, unique=True
    )
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PKR")
    method: Mapped[str] = mapped_column(String(50))
    provider_transaction_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="CONFIRMED", index=True)  # CONFIRMED, FAILED, REVERSED
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    receipt_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    allocations: Mapped[list[PaymentAllocation]] = relationship(
        "PaymentAllocation", back_populates="payment", cascade="all, delete-orphan"
    )
    receipt: Mapped[Receipt | None] = relationship("Receipt", back_populates="payment", uselist=False)


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), index=True
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("invoices.id"), index=True)
    installment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    allocated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    payment: Mapped[Payment] = relationship("Payment", back_populates="allocations")


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payments.id"), unique=True, index=True
    )
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="PKR")
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    receipt_data: Mapped[dict] = mapped_column(JSON, default=dict)

    payment: Mapped[Payment] = relationship("Payment", back_populates="receipt")


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("payments.id"), index=True)
    invoice_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("invoices.id"), index=True)
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(30), default="REQUESTED", index=True
    )  # REQUESTED, APPROVED, REJECTED, SETTLED
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ReconciliationBatch(Base):
    __tablename__ = "reconciliation_batches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50), index=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    matched_rows: Mapped[int] = mapped_column(Integer, default=0)
    exception_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="PROCESSED", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    items: Mapped[list[ReconciliationItem]] = relationship(
        "ReconciliationItem", back_populates="batch", cascade="all, delete-orphan"
    )


class ReconciliationItem(Base):
    __tablename__ = "reconciliation_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("reconciliation_batches.id", ondelete="CASCADE"), index=True
    )
    transaction_ref: Mapped[str] = mapped_column(String(120), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    statement_date: Mapped[date] = mapped_column(Date)
    match_status: Mapped[str] = mapped_column(
        String(40), index=True
    )  # MATCHED, UNMATCHED_PROVIDER, UNMATCHED_BANK, AMOUNT_MISMATCH
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    batch: Mapped[ReconciliationBatch] = relationship("ReconciliationBatch", back_populates="items")


# General Ledger Double-Entry Models
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    account_type: Mapped[str] = mapped_column(String(30), index=True)  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_number: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date, index=True)
    reference: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(String(255))
    is_posted: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    lines: Mapped[list[JournalLine]] = relationship(
        "JournalLine", back_populates="journal_entry", cascade="all, delete-orphan"
    )


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("accounts.id"), index=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    journal_entry: Mapped[JournalEntry] = relationship("JournalEntry", back_populates="lines")
    account: Mapped[Account] = relationship("Account")


class FinanceAuditEvent(Base):
    __tablename__ = "finance_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[str] = mapped_column(String(60), index=True)
    resource_id: Mapped[str] = mapped_column(String(100), index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class FinanceOutboxEvent(Base):
    __tablename__ = "finance_outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    relay_attempts: Mapped[int] = mapped_column(Integer, default=0)
    relay_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    relay_error: Mapped[str | None] = mapped_column(String(240), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FinanceInboxEvent(Base):
    __tablename__ = "finance_inbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), unique=True, index=True)
    source_service: Mapped[str] = mapped_column(String(80))
    event_type: Mapped[str] = mapped_column(String(160))
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

