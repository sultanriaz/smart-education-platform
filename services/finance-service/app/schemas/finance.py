from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Base pagination
class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    size: int


# Fee Structures
class FeeComponentIn(BaseModel):
    name: str
    component_type: str = "TUITION"  # TUITION, EXAMINATION, LABORATORY, LIBRARY, OTHER
    amount: Decimal
    is_refundable: bool = False
    eligible_for_scholarship: bool = True


class FeeComponentOut(FeeComponentIn):
    id: uuid.UUID
    fee_structure_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class FeeStructureIn(BaseModel):
    name: str
    program_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    is_active: bool = True
    components: list[FeeComponentIn] = Field(default_factory=list)


class FeeStructureOut(BaseModel):
    id: uuid.UUID
    name: str
    program_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    components: list[FeeComponentOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Scholarships
class ScholarshipIn(BaseModel):
    name: str
    code: str
    scholarship_type: str = "MERIT"  # MERIT, NEED_BASED, SPECIAL
    percentage: Decimal
    applies_to_components: list[str] = Field(default_factory=lambda: ["TUITION"])
    is_active: bool = True


class ScholarshipOut(ScholarshipIn):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScholarshipAwardIn(BaseModel):
    scholarship_id: uuid.UUID
    student_user_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int


class ScholarshipAwardOut(BaseModel):
    id: uuid.UUID
    scholarship_id: uuid.UUID
    student_user_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    status: str
    granted_by_user_id: uuid.UUID
    created_at: datetime
    scholarship: ScholarshipOut | None = None

    model_config = ConfigDict(from_attributes=True)


# Student Accounts
class StudentFinancialAccountOut(BaseModel):
    id: uuid.UUID
    student_user_id: uuid.UUID
    account_number: str
    status: str
    total_invoiced: Decimal
    total_paid: Decimal
    total_scholarships: Decimal
    outstanding_balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Invoices
class InvoiceLineItemOut(BaseModel):
    id: uuid.UUID
    component_name: str
    component_type: str
    amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class InvoiceInstallmentOut(BaseModel):
    id: uuid.UUID
    installment_number: int
    due_date: date
    amount: Decimal
    paid_amount: Decimal
    late_fee_amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceOut(BaseModel):
    id: uuid.UUID
    invoice_number: str
    student_user_id: uuid.UUID
    account_id: uuid.UUID
    program_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    issue_date: date
    due_date: date
    subtotal: Decimal
    scholarship_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    late_fee_applied: bool
    late_fee_amount: Decimal
    status: str
    created_at: datetime
    items: list[InvoiceLineItemOut] = Field(default_factory=list)
    installments: list[InvoiceInstallmentOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SingleInvoiceCreateIn(BaseModel):
    student_user_id: uuid.UUID
    program_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    due_date: date | None = None
    installments_count: int = 3


class BulkInvoiceCreateIn(BaseModel):
    program_id: uuid.UUID
    academic_year_id: uuid.UUID
    semester_number: int
    due_date: date | None = None
    installments_count: int = 3
    preview: bool = False


class ProcessOverdueInvoicesIn(BaseModel):
    as_of_date: date | None = None
    grace_days: int | None = None
    penalty_amount: Decimal | None = None


# Payments & Intents
class PaymentIntentCreateIn(BaseModel):
    invoice_id: uuid.UUID
    installment_id: uuid.UUID | None = None
    amount: Decimal
    provider: str = "JAZZ_CASH"  # JAZZ_CASH, EASYPAISA, BANK_TRANSFER, CASH


class PaymentIntentOut(BaseModel):
    id: uuid.UUID
    student_user_id: uuid.UUID
    invoice_id: uuid.UUID
    installment_id: uuid.UUID | None = None
    amount: Decimal
    currency: str
    provider: str
    status: str
    client_secret: str
    provider_reference: str | None = None
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulatePaymentIn(BaseModel):
    payment_intent_id: uuid.UUID
    fail: bool = False
    transaction_ref: str | None = None
    verification_note: str | None = None


class PaymentAllocationOut(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    installment_id: uuid.UUID | None = None
    amount: Decimal
    allocated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentOut(BaseModel):
    id: uuid.UUID
    payment_intent_id: uuid.UUID | None = None
    student_user_id: uuid.UUID
    amount: Decimal
    currency: str
    method: str
    provider_transaction_id: str
    status: str
    paid_at: datetime
    receipt_number: str
    created_at: datetime
    allocations: list[PaymentAllocationOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReceiptOut(BaseModel):
    id: uuid.UUID
    receipt_number: str
    payment_id: uuid.UUID
    student_user_id: uuid.UUID
    amount: Decimal
    currency: str
    issued_at: datetime
    receipt_data: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# Refunds
class RefundRequestIn(BaseModel):
    payment_id: uuid.UUID
    amount: Decimal
    reason: str


class RefundApprovalIn(BaseModel):
    approved: bool
    notes: str | None = None


class RefundRequestOut(BaseModel):
    id: uuid.UUID
    payment_id: uuid.UUID
    invoice_id: uuid.UUID
    student_user_id: uuid.UUID
    amount: Decimal
    reason: str
    status: str
    requested_by_user_id: uuid.UUID
    approved_by_user_id: uuid.UUID | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Accounting & GL
class AccountOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    account_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class JournalLineOut(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    debit: Decimal
    credit: Decimal
    description: str | None = None
    account: AccountOut | None = None

    model_config = ConfigDict(from_attributes=True)


class JournalEntryOut(BaseModel):
    id: uuid.UUID
    entry_number: str
    entry_date: date
    reference: str
    description: str
    is_posted: bool
    created_at: datetime
    lines: list[JournalLineOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TrialBalanceItem(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    total_debit: Decimal
    total_credit: Decimal
    balance: Decimal


class TrialBalanceOut(BaseModel):
    as_of: date
    items: list[TrialBalanceItem]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool


# Reconciliation
class ReconciliationItemOut(BaseModel):
    id: uuid.UUID
    transaction_ref: str
    amount: Decimal
    statement_date: date
    match_status: str
    resolved: bool
    resolution_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReconciliationBatchOut(BaseModel):
    id: uuid.UUID
    filename: str
    provider: str
    total_rows: int
    matched_rows: int
    exception_rows: int
    status: str
    created_at: datetime
    items: list[ReconciliationItemOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

