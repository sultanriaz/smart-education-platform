from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import blocks, bookings, facilities, internal

api_router = APIRouter()
api_router.include_router(facilities.router)
api_router.include_router(facilities.equipment_router)
api_router.include_router(bookings.router)
api_router.include_router(blocks.router)
api_router.include_router(internal.router)
