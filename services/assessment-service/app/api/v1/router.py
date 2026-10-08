from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    authoring,
    grading,
    student,
    student_read,
    teacher_read,
)

api_router = APIRouter()
api_router.include_router(authoring.router)
api_router.include_router(student.router)
api_router.include_router(student_read.router)
api_router.include_router(teacher_read.router)
api_router.include_router(grading.router)
