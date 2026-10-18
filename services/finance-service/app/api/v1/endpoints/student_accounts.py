from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.core.errors import EntityNotFoundError
from app.domain.models import StudentFinancialAccount
from app.schemas.finance import StudentFinancialAccountOut
from app.security.auth import Principal, require_scoped_roles
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/student-accounts", tags=["Student Accounts"])


@router.get("", response_model=list[StudentFinancialAccountOut])
def list_student_accounts(
    status: str | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounts.read", "admin", "teacher", "finance_officer")),
):
    query = select(StudentFinancialAccount).order_by(StudentFinancialAccount.created_at.desc())
    if status is not None:
        query = query.where(StudentFinancialAccount.status == status.upper())
    return list(db.scalars(query).all())


@router.get("/by-user/{user_id}", response_model=StudentFinancialAccountOut)
def get_student_account_by_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounts.read", "admin", "teacher", "student", "finance_officer")),
):
    # Enforce student isolation: student can only access their own account
    if "student" in principal.roles and "admin" not in principal.roles and principal.user_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access another student's financial account")

    svc = InvoiceService(db)
    return svc.get_or_create_account(user_id)


@router.get("/{id}", response_model=StudentFinancialAccountOut)
def get_student_account(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounts.read", "admin", "teacher", "student", "finance_officer")),
):
    account = db.get(StudentFinancialAccount, id)
    if not account:
        raise HTTPException(status_code=404, detail="Student financial account not found")

    if "student" in principal.roles and "admin" not in principal.roles and principal.user_id != account.student_user_id:
        raise HTTPException(status_code=403, detail="Cannot access another student's financial account")

    return account

