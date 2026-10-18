from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    accounting,
    fee_structures,
    invoices,
    payments,
    portal,
    reconciliation,
    refunds,
    reports,
    scholarships,
    student_accounts,
)

api_router = APIRouter()
api_router.include_router(fee_structures.router)
api_router.include_router(scholarships.router)
api_router.include_router(student_accounts.router)
api_router.include_router(invoices.router)
api_router.include_router(payments.router)
api_router.include_router(refunds.router)
api_router.include_router(reconciliation.router)
api_router.include_router(accounting.router)
api_router.include_router(reports.router)
api_router.include_router(portal.router)

