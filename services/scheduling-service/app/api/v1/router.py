from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import schedules, timetable

api_router = APIRouter()
api_router.include_router(schedules.router)
api_router.include_router(timetable.router)
