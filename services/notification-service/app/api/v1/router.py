from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    internal,
    notifications,
    preferences,
    teacher,
)

api_router = APIRouter()
api_router.include_router(notifications.router)
api_router.include_router(preferences.router)
api_router.include_router(teacher.router)
api_router.include_router(admin.router)
api_router.include_router(internal.router)
