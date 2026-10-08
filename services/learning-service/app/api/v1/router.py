from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import categories, resources, students

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(resources.router)
api_router.include_router(students.router)
