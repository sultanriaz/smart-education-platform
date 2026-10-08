from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_service
from app.core.errors import ConflictError, DomainError, ForbiddenError, NotFoundError
from app.schemas.models import AttemptOut, ManualGrade
from app.security.auth import Principal, require_roles
from app.services.assessment_service import AssessmentService

router = APIRouter(tags=["Grading"])


@router.post("/attempts/{attempt_id}/grade", response_model=AttemptOut)
def grade(
    attempt_id: uuid.UUID,
    payload: ManualGrade,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        attempt = service.repo.get_attempt(attempt_id)
        if not attempt:
            raise NotFoundError("Attempt not found")
        if attempt.status not in {"SUBMITTED", "GRADED"}:
            raise ConflictError("Attempt must be submitted before manual grading")

        assignment = service.repo.get_assignment(attempt.assignment_id)
        if not assignment:
            raise NotFoundError("Assignment not found")

        if "admin" not in p.roles:
            allowed = assignment.created_by_user_id == p.user_id
            if service.academic:
                allowed = allowed or service.academic.validate_teacher_assignment(
                    p.user_id,
                    assignment.section_id,
                    p.token,
                )
            if not allowed:
                raise ForbiddenError("Teacher is not assigned to the assessment section")

        return service.manual_grade(attempt_id, payload, p.user_id)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
