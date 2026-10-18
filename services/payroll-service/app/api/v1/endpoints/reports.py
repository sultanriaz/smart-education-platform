from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.domain.models import DisbursementBatch, PayrollRun
from app.security.auth import Principal, require_scoped_roles

router = APIRouter(prefix="/reports", tags=["Payroll Reports"])


@router.get("/overview")
def get_payroll_overview(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("payroll.reports.read", "admin", "payroll_officer")),
):
    runs = db.scalars(select(PayrollRun)).all()
    disbursements = db.scalars(select(DisbursementBatch)).all()

    total_gross = sum(r.total_gross for r in runs if r.status in {"APPROVED", "PAID"})
    total_deductions = sum(r.total_deductions for r in runs if r.status in {"APPROVED", "PAID"})
    total_net = sum(r.total_net for r in runs if r.status in {"APPROVED", "PAID"})
    total_disbursed = sum(b.total_amount for b in disbursements if b.status == "COMPLETED")

    return {
        "total_gross_disbursed": str(total_gross),
        "total_deductions": str(total_deductions),
        "total_net_disbursed": str(total_net),
        "total_batches_disbursed": str(total_disbursed),
        "total_runs_count": len(runs),
        "completed_runs_count": sum(r.status == "PAID" for r in runs),
    }

