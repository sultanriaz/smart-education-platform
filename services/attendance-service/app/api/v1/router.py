from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import reports, sessions

router = APIRouter()
router.include_router(sessions.router)
router.include_router(reports.router)
