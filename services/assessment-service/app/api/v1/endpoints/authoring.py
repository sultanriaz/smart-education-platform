from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_service
from app.core.errors import DomainError, ForbiddenError, NotFoundError
from app.schemas.models import (
    AssignmentCreate,
    QuestionBankCreate,
    QuestionCreate,
    QuizCreate,
    QuizUpdate,
    QuizQuestionAdd,
)
from app.security.auth import Principal, require_roles
from app.services.assessment_service import AssessmentService

router = APIRouter(tags=["Assessment Authoring"])


def fail(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _teacher_only_owner(principal: Principal, owner_id: uuid.UUID, message: str):
    if "admin" in principal.roles:
        return
    if owner_id != principal.user_id:
        raise ForbiddenError(message)


@router.post("/banks")
def create_bank(
    payload: QuestionBankCreate,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return service.create_bank(payload, p.user_id)
    except DomainError as exc:
        fail(exc)


@router.post("/questions")
def create_question(
    payload: QuestionCreate,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        bank = service.repo.get_bank(payload.bank_id)
        if not bank:
            raise NotFoundError("Question bank not found")
        _teacher_only_owner(
            p,
            bank.created_by_user_id,
            "Teachers may only add questions to their own question banks",
        )
        return service.create_question(payload, p.user_id)
    except DomainError as exc:
        fail(exc)


@router.post("/quizzes")
def create_quiz(
    payload: QuizCreate,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        return service.create_quiz(payload, p.user_id)
    except DomainError as exc:
        fail(exc)


@router.patch("/quizzes/{quiz_id}")
def edit_quiz(
    quiz_id: uuid.UUID, payload: QuizUpdate,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        quiz = service.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        _teacher_only_owner(p, quiz.created_by_user_id, "Teachers may only edit their own quizzes")
        return service.edit_quiz(quiz_id, payload)
    except DomainError as exc:
        fail(exc)


@router.post("/quizzes/{quiz_id}/archive")
def archive_quiz(
    quiz_id: uuid.UUID,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        quiz = service.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        _teacher_only_owner(p, quiz.created_by_user_id, "Teachers may only archive their own quizzes")
        return service.archive_quiz(quiz_id)
    except DomainError as exc:
        fail(exc)


@router.post("/quizzes/{quiz_id}/questions")
def add_question(
    quiz_id: uuid.UUID,
    payload: QuizQuestionAdd,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        quiz = service.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        question = service.repo.get_question(payload.question_id)
        if not question:
            raise NotFoundError("Question not found")
        _teacher_only_owner(
            p,
            quiz.created_by_user_id,
            "Teachers may only modify their own quizzes",
        )
        _teacher_only_owner(
            p,
            question.created_by_user_id,
            "Teachers may only attach their own questions",
        )
        return service.add_question(quiz_id, payload)
    except DomainError as exc:
        fail(exc)


@router.post("/quizzes/{quiz_id}/publish")
def publish_quiz(
    quiz_id: uuid.UUID,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        quiz = service.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        _teacher_only_owner(
            p,
            quiz.created_by_user_id,
            "Teachers may only publish their own quizzes",
        )
        return service.publish_quiz(quiz_id)
    except DomainError as exc:
        fail(exc)


@router.post("/quizzes/{quiz_id}/assignments")
def create_assignment(
    quiz_id: uuid.UUID,
    payload: AssignmentCreate,
    p: Principal = Depends(require_roles("admin", "teacher")),
    service: AssessmentService = Depends(get_service),
):
    try:
        quiz = service.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        _teacher_only_owner(
            p,
            quiz.created_by_user_id,
            "Teachers may only assign their own quizzes",
        )
        return service.create_assignment(
            quiz_id,
            payload,
            p.user_id,
            p.roles,
            p.token,
        )
    except DomainError as exc:
        fail(exc)
