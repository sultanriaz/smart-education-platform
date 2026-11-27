from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import FinanceDomainError
from app.domain.models import FeeStructure, Invoice, StudentFinancialAccount
from app.schemas.finance import BulkInvoiceCreateIn, InvoiceOut, ProcessOverdueInvoicesIn, SingleInvoiceCreateIn
from app.security.auth import Principal, require_scoped_roles
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    student_user_id: uuid.UUID | None = None,
    program_id: uuid.UUID | None = None,
    semester_number: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.read", "admin", "finance_officer", "student")),
):
    query = select(Invoice).order_by(Invoice.created_at.desc())
    is_finance_staff = bool(principal.roles.intersection({"admin", "finance_officer"})) or (
        "finance.invoices.read" in principal.permissions
    )
    if not is_finance_staff:
        # Enforce strict isolation for all non-privileged callers
        query = query.where(Invoice.student_user_id == principal.user_id)
    elif student_user_id is not None:
        query = query.where(Invoice.student_user_id == student_user_id)

    if program_id is not None:
        query = query.where(Invoice.program_id == program_id)
    if semester_number is not None:
        query = query.where(Invoice.semester_number == semester_number)
    if status is not None:
        query = query.where(Invoice.status == status.upper())

    return list(db.scalars(query).all())


@router.post("", response_model=InvoiceOut, status_code=201)
def create_single_invoice(
    data: SingleInvoiceCreateIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.manage", "admin", "finance_officer")),
):
    svc = InvoiceService(db)
    try:
        return svc.create_invoice(
            student_user_id=data.student_user_id,
            program_id=data.program_id,
            academic_year_id=data.academic_year_id,
            semester_number=data.semester_number,
            due_date=data.due_date,
            installments_count=data.installments_count,
            actor_id=principal.user_id,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/bulk")
def create_bulk_invoices(
    data: BulkInvoiceCreateIn,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.manage", "admin", "finance_officer")),
):
    fee_struct = FeeStructure
    svc = InvoiceService(db)

    # Fetch fee structure to confirm existence
    structure = svc.fee_svc.find_fee_structure(data.program_id, data.academic_year_id, data.semester_number)
    if not structure:
        raise HTTPException(status_code=400, detail="No active fee structure found for specified parameters")

    subtotal = sum(c.amount for c in structure.components)

    # In a full run, we find enrolled students via Academic integration or existing accounts
    accounts = db.scalars(select(StudentFinancialAccount)).all()
    target_students = [acct.student_user_id for acct in accounts]

    if data.preview:
        return {
            "preview": True,
            "program_id": str(data.program_id),
            "semester_number": data.semester_number,
            "eligible_students_count": len(target_students),
            "base_fee_per_student": str(subtotal),
            "estimated_total_billing": str(subtotal * len(target_students)),
        }

    created_invoices = []
    skipped = 0
    for student_id in target_students:
        try:
            inv = svc.create_invoice(
                student_user_id=student_id,
                program_id=data.program_id,
                academic_year_id=data.academic_year_id,
                semester_number=data.semester_number,
                due_date=data.due_date,
                installments_count=data.installments_count,
                actor_id=principal.user_id,
            )
            created_invoices.append(str(inv.id))
        except FinanceDomainError:
            skipped += 1

    return {
        "success": True,
        "created_count": len(created_invoices),
        "skipped_count": skipped,
        "invoice_ids": created_invoices,
    }


@router.get("/{id}", response_model=InvoiceOut)
def get_invoice(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.read", "admin", "finance_officer", "student")),
):
    inv = db.get(Invoice, id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    is_finance_staff = bool(principal.roles.intersection({"admin", "finance_officer"})) or (
        "finance.invoices.read" in principal.permissions
    )
    if not is_finance_staff and principal.user_id != inv.student_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another student's invoice")

    return inv


@router.post("/{id}/apply-late-fee", response_model=InvoiceOut)
def apply_late_fee(
    id: uuid.UUID,
    as_of: date | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.manage", "admin", "finance_officer")),
):
    svc = InvoiceService(db)
    try:
        return svc.apply_late_fee_if_overdue(id, as_of_date=as_of)
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/process-overdue")
def process_overdue_invoices(
    data: ProcessOverdueInvoicesIn | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.invoices.manage", "admin", "finance_officer")),
):
    svc = InvoiceService(db)
    try:
        req_data = data or ProcessOverdueInvoicesIn()
        return svc.process_overdue_invoices(
            as_of_date=req_data.as_of_date,
            grace_days=req_data.grace_days,
            penalty_amount=req_data.penalty_amount,
        )
    except FinanceDomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

