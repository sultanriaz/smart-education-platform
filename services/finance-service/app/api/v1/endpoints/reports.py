from __future__ import annotations

from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.endpoints.health import get_db
from app.domain.models import Invoice, Payment, RefundRequest, ScholarshipAward
from app.security.auth import Principal, require_scoped_roles

router = APIRouter(prefix="/reports", tags=["Finance Reports"])


@router.get("/overview")
def get_finance_overview(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_scoped_roles("finance.reports.read", "admin", "finance_officer")),
):
    invoices = db.scalars(select(Invoice).where(Invoice.status != "CANCELLED")).all()
    total_invoiced = sum(i.total_amount for i in invoices)
    total_collected = sum(i.paid_amount for i in invoices)
    total_receivable = sum(i.balance_amount for i in invoices)
    total_scholarships = sum(i.scholarship_amount for i in invoices)

    overdue_invoices = [i for i in invoices if i.status == "OVERDUE"]
    total_overdue = sum(i.balance_amount for i in overdue_invoices)

    refunds = db.scalars(select(RefundRequest).where(RefundRequest.status == "SETTLED")).all()
    total_refunds = sum(r.amount for r in refunds)

    payments = db.scalars(select(Payment).where(Payment.status == "CONFIRMED")).all()
    method_dist = {}
    for p in payments:
        method_dist[p.method] = str(Decimal(method_dist.get(p.method, "0.00")) + p.amount)

    return {
        "total_invoiced": str(total_invoiced),
        "total_collected": str(total_collected),
        "outstanding_receivables": str(total_receivable),
        "total_scholarships": str(total_scholarships),
        "total_overdue": str(total_overdue),
        "overdue_invoices_count": len(overdue_invoices),
        "total_refunds_settled": str(total_refunds),
        "payment_method_distribution": method_dist,
    }

