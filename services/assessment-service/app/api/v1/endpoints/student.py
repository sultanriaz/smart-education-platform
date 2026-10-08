from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_service
from app.core.errors import DomainError
from app.schemas.models import AnswerUpsert, AttemptOut
from app.security.auth import Principal, require_roles
from app.services.assessment_service import AssessmentService

router = APIRouter(tags=["Student Assessments"])


def fail(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/assignments/{assignment_id}/attempts", response_model=AttemptOut)
def start_attempt(
    assignment_id: uuid.UUID,
    p: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return service.start_attempt(assignment_id, p.user_id, p.token)
    except DomainError as exc:
        fail(exc)


@router.put("/attempts/{attempt_id}/answers/{question_id}")
def answer(
    attempt_id: uuid.UUID,
    question_id: uuid.UUID,
    payload: AnswerUpsert,
    p: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return service.answer_question(attempt_id, question_id, payload, p.user_id)
    except DomainError as exc:
        fail(exc)


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptOut)
def submit(
    attempt_id: uuid.UUID,
    p: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return service.submit_attempt(attempt_id, p.user_id)
    except DomainError as exc:
        fail(exc)
