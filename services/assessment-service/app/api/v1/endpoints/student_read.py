from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.dependencies import get_service
from app.core.errors import DomainError, ForbiddenError, NotFoundError
from app.domain.entities.models import QuizAssignment
from app.security.auth import Principal, require_roles
from app.services.assessment_service import AssessmentService, aware

router = APIRouter(tags=["Student Assessment Read API"])


def _fail(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _assignment_summary(
    service: AssessmentService, assignment: QuizAssignment, student_id: uuid.UUID
):
    quiz = service.repo.get_quiz(assignment.quiz_id)
    attempts_used = service.repo.count_attempts(assignment.id, student_id)
    now = datetime.now(UTC)

    active = service.repo.active_attempt(assignment.id, student_id)
    if active:
        active = service.read_student_attempt(active.id, student_id)
        if active.status != "IN_PROGRESS":
            active = None
    if now < aware(assignment.opens_at):
        status = "UPCOMING"
    elif now > aware(assignment.due_at):
        status = "CLOSED"
    elif active:
        status = "IN_PROGRESS"
    elif attempts_used >= assignment.attempt_limit:
        status = "LIMIT_REACHED"
    else:
        status = "AVAILABLE"

    return {
        "id": assignment.id,
        "assignment_id": assignment.id,
        "quiz_id": assignment.quiz_id,
        "title": quiz.title if quiz else "Assessment",
        "description": quiz.description if quiz else None,
        "section_id": assignment.section_id,
        "opens_at": assignment.opens_at,
        "due_at": assignment.due_at,
        "attempt_limit": assignment.attempt_limit,
        "attempts_used": attempts_used,
        "active_attempt_id": active.id if active else None,
        "status": status,
    }


@router.get("/students/me/assignments")
def list_my_assignments(
    principal: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    assignments = list(
        service.db.scalars(select(QuizAssignment).order_by(QuizAssignment.due_at.asc())).all()
    )

    visible = []
    for assignment in assignments:
        try:
            if service.academic and not service.academic.validate_student_enrollment(
                principal.user_id,
                assignment.section_id,
                principal.token,
            ):
                continue
        except DomainError as exc:
            _fail(exc)
        visible.append(_assignment_summary(service, assignment, principal.user_id))

    return {"items": visible}


@router.get("/students/me/assignments/{assignment_id}")
def get_my_assignment(
    assignment_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    try:
        assignment = service.repo.get_assignment(assignment_id)
        if not assignment:
            raise NotFoundError("Assignment not found")

        if service.academic and not service.academic.validate_student_enrollment(
            principal.user_id,
            assignment.section_id,
            principal.token,
        ):
            raise ForbiddenError("Student is not enrolled in this section")

        quiz = service.repo.get_quiz(assignment.quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")

        summary = _assignment_summary(service, assignment, principal.user_id)

        # Deliberately omit correct choice flags, correct_text, and explanations
        # so the Student API cannot leak answer keys before grading.
        summary.update(
            {
                "duration_minutes": quiz.duration_minutes,
                "questions": [
                    {
                        "id": item.question.id,
                        "question_id": item.question.id,
                        "question_type": item.question.question_type,
                        "prompt": item.question.prompt,
                        "points": (
                            item.points_override
                            if item.points_override is not None
                            else item.question.points
                        ),
                        "choices": [
                            {"id": choice.id, "text": choice.text}
                            for choice in sorted(
                                item.question.choices,
                                key=lambda choice: choice.position,
                            )
                        ],
                    }
                    for item in sorted(quiz.questions, key=lambda item: item.position)
                ],
            }
        )
        return summary
    except DomainError as exc:
        _fail(exc)


@router.get("/students/me/results")
def list_my_results(
    principal: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    attempts = service.repo.list_student_attempts(principal.user_id)
    rows = []

    for attempt in attempts:
        assignment = service.repo.get_assignment(attempt.assignment_id)
        quiz = service.repo.get_quiz(assignment.quiz_id) if assignment else None
        rows.append(
            {
                "attempt_id": attempt.id,
                "assignment_id": attempt.assignment_id,
                "quiz_id": assignment.quiz_id if assignment else None,
                "title": quiz.title if quiz else "Assessment",
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percent": attempt.percent,
                "passed": attempt.passed,
                "status": attempt.status,
                "submitted_at": attempt.submitted_at,
                "graded_at": attempt.graded_at,
            }
        )

    return {"items": rows}


@router.get("/attempts/{attempt_id}")
def get_my_attempt(
    attempt_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return _attempt_summary(service.read_student_attempt(attempt_id, principal.user_id))
    except DomainError as exc:
        _fail(exc)


def _attempt_summary(attempt):
    return {
        "id": attempt.id,
        "attempt_id": attempt.id,
        "assignment_id": attempt.assignment_id,
        "attempt_number": attempt.attempt_number,
        "status": attempt.status,
        "started_at": attempt.started_at,
        "expires_at": attempt.expires_at,
        "server_time": datetime.now(UTC),
        "submitted_at": attempt.submitted_at,
        "graded_at": attempt.graded_at,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "percent": attempt.percent,
        "passed": attempt.passed,
        "answers": [
            {
                "question_id": answer.question_id,
                "selected_choice_id": answer.selected_choice_id,
                "text_answer": answer.text_answer,
            }
            for answer in attempt.answers
        ],
    }


@router.get("/students/me/assignments/{assignment_id}/active-attempt")
def get_active_attempt(
    assignment_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student")),
    service: AssessmentService = Depends(get_service),
):
    # Reuse the same enrollment check and safe question projection as detail.
    get_my_assignment(assignment_id, principal, service)
    attempt = service.repo.active_attempt(assignment_id, principal.user_id)
    return _attempt_summary(attempt) if attempt else None
