from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    assignments,
    catalog,
    data_jobs,
    enrollments,
    profiles,
    relationships,
    sections,
)

router = APIRouter()
router.include_router(relationships.router)
router.include_router(data_jobs.router)
for resource in (catalog, profiles, sections, enrollments, assignments):
    router.include_router(resource.router)
