from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_service
from app.core.errors import DomainError, ForbiddenError
from app.domain.entities.models import (
    Attempt,
    Question,
    QuestionBank,
    Quiz,
    QuizAssignment,
)
from app.security.auth import Principal, require_roles
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/teachers/me", tags=["Teacher Assessment Read API"])


def _fail(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _teacher_assignment_allowed(
    service: AssessmentService,
    principal: Principal,
    assignment: QuizAssignment,
) -> bool:
    if "admin" in principal.roles:
        return True
    if assignment.created_by_user_id == principal.user_id:
        return True
    if service.academic:
        return bool(
            service.academic.validate_teacher_assignment(
                principal.user_id,
                assignment.section_id,
                principal.token,
            )
        )
    return False


@router.get("/banks")
def list_my_banks(
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: AssessmentService = Depends(get_service),
):
    stmt = select(QuestionBank).order_by(QuestionBank.created_at.desc())
    if "admin" not in principal.roles:
        stmt = stmt.where(QuestionBank.created_by_user_id == principal.user_id)
    rows = list(service.db.scalars(stmt).all())
    return {
        "items": [
            {
                "id": row.id,
                "name": row.name,
                "course_id": row.course_id,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    }


@router.get("/questions")
def list_my_questions(
    bank_id: uuid.UUID | None = Query(default=None),
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: AssessmentService = Depends(get_service),
):
    stmt = (
        select(Question)
        .options(selectinload(Question.choices))
        .order_by(Question.created_at.desc())
    )
    if bank_id:
        stmt = stmt.where(Question.bank_id == bank_id)
    if "admin" not in principal.roles:
        stmt = stmt.where(Question.created_by_user_id == principal.user_id)

    rows = list(service.db.scalars(stmt).all())
    return {
        "items": [
            {
                "id": row.id,
                "bank_id": row.bank_id,
                "question_type": row.question_type,
                "prompt": row.prompt,
                "points": row.points,
                "correct_text": row.correct_text,
                "explanation": row.explanation,
                "choices": [
                    {
                        "id": choice.id,
                        "text": choice.text,
                        "is_correct": choice.is_correct,
                    }
                    for choice in sorted(row.choices, key=lambda item: item.position)
                ],
                "created_at": row.created_at,
            }
            for row in rows
        ]
    }


@router.get("/quizzes")
def list_my_quizzes(
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: AssessmentService = Depends(get_service),
):
    stmt = select(Quiz).options(selectinload(Quiz.questions)).order_by(Quiz.updated_at.desc())
    if "admin" not in principal.roles:
        stmt = stmt.where(Quiz.created_by_user_id == principal.user_id)
    rows = list(service.db.scalars(stmt).all())
    return {
        "items": [
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "course_id": row.course_id,
                "status": row.status,
                "duration_minutes": row.duration_minutes,
                "pass_percent": row.pass_percent,
                "question_count": len(row.questions),
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]
    }


@router.get("/assignments")
def list_my_assignments(
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: AssessmentService = Depends(get_service),
):
    assignments = list(
        service.db.scalars(select(QuizAssignment).order_by(QuizAssignment.created_at.desc())).all()
    )
    visible = []
    try:
        for assignment in assignments:
            if not _teacher_assignment_allowed(service, principal, assignment):
                continue
            quiz = service.repo.get_quiz(assignment.quiz_id)
            visible.append(
                {
                    "id": assignment.id,
                    "assignment_id": assignment.id,
                    "quiz_id": assignment.quiz_id,
                    "quiz_title": quiz.title if quiz else None,
                    "section_id": assignment.section_id,
                    "opens_at": assignment.opens_at,
                    "due_at": assignment.due_at,
                    "attempt_limit": assignment.attempt_limit,
                    "created_at": assignment.created_at,
                }
            )
    except DomainError as exc:
        _fail(exc)
    return {"items": visible}


@router.get("/assignments/{assignment_id}/attempts")
def list_assignment_attempts(
    assignment_id: uuid.UUID,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: AssessmentService = Depends(get_service),
):
    assignment = service.repo.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    try:
        if not _teacher_assignment_allowed(service, principal, assignment):
            raise ForbiddenError("Teacher is not assigned to this assessment section")
    except DomainError as exc:
        _fail(exc)

    quiz = service.repo.get_quiz(assignment.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    points_by_question = {
        item.question_id: (
            item.points_override if item.points_override is not None else item.question.points
        )
        for item in quiz.questions
    }

    attempts = list(
        service.db.scalars(
            select(Attempt)
            .options(selectinload(Attempt.answers))
            .where(
                Attempt.assignment_id == assignment_id,
                Attempt.status.in_(["SUBMITTED", "GRADED"]),
            )
            .order_by(Attempt.started_at.desc())
        ).all()
    )

    items = []
    for attempt in attempts:
        answers = []
        for answer in attempt.answers:
            question = service.repo.get_question(answer.question_id)
            answers.append(
                {
                    "id": answer.id,
                    "answer_id": answer.id,
                    "question_id": answer.question_id,
                    "prompt": question.prompt if question else None,
                    "question_type": question.question_type if question else None,
                    "points": points_by_question.get(answer.question_id),
                    "selected_choice_id": answer.selected_choice_id,
                    "text_answer": answer.text_answer,
                    "auto_score": answer.auto_score,
                    "manual_score": answer.manual_score,
                    "feedback": answer.feedback,
                }
            )

        items.append(
            {
                "id": attempt.id,
                "attempt_id": attempt.id,
                "assignment_id": attempt.assignment_id,
                "student_user_id": attempt.student_user_id,
                "attempt_number": attempt.attempt_number,
                "status": attempt.status,
                "score": attempt.score,
                "max_score": attempt.max_score,
                "percent": attempt.percent,
                "passed": attempt.passed,
                "started_at": attempt.started_at,
                "submitted_at": attempt.submitted_at,
                "graded_at": attempt.graded_at,
                "answers": answers,
            }
        )

    return {"items": items}
