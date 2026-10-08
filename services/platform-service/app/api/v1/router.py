from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import admin, internal, search, settings, support

api_router = APIRouter()
api_router.include_router(internal.router)
api_router.include_router(search.router)
api_router.include_router(support.router)
api_router.include_router(settings.router)
api_router.include_router(admin.router)
