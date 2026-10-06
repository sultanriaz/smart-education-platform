from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import assignments, catalog, enrollments, profiles, sections

router = APIRouter()
for resource in (catalog, profiles, sections, enrollments, assignments):
    router.include_router(resource.router)
