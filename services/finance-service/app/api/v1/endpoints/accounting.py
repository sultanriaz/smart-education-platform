from __future__ import annotations

import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.domain.models import Account, JournalEntry
from app.schemas.finance import AccountOut, JournalEntryOut, TrialBalanceOut
from app.security.auth import Principal, require_scoped_roles
from app.services.accounting_service import AccountingService

router = APIRouter(prefix="/accounting", tags=["Accounting & Ledger"])


@router.get("/accounts", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounting.read", "admin", "finance_officer")),
):
    svc = AccountingService(db)
    svc.ensure_default_accounts()
    query = select(Account).order_by(Account.code)
    return list(db.scalars(query).all())


@router.get("/journal-entries", response_model=list[JournalEntryOut])
def list_journal_entries(
    reference: str | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounting.read", "admin", "finance_officer")),
):
    query = select(JournalEntry).order_by(JournalEntry.created_at.desc())
    if reference:
        query = query.where(JournalEntry.reference.ilike(f"%{reference}%"))
    return list(db.scalars(query).all())


@router.get("/trial-balance", response_model=TrialBalanceOut)
def get_trial_balance(
    as_of: date | None = None,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.accounting.read", "admin", "finance_officer")),
):
    svc = AccountingService(db)
    return svc.get_trial_balance(as_of)

