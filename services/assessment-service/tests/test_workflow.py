from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.api.v1.endpoints.student_read import get_active_attempt, get_my_attempt
from app.core.errors import ConflictError, ForbiddenError
from app.schemas.models import (
    AnswerUpsert,
    AssignmentCreate,
    ChoiceCreate,
    ManualGrade,
    QuestionBankCreate,
    QuestionCreate,
    QuizCreate,
    QuizQuestionAdd,
)
from app.security.auth import Principal


def build_objective(service, ids):
    bank = service.create_bank(
        QuestionBankCreate(name="Midterm", course_id=ids["course"]), ids["teacher"]
    )
    q = service.create_question(
        QuestionCreate(
            bank_id=bank.id,
            question_type="MCQ_SINGLE",
            prompt="2 + 2?",
            points=2,
            choices=[
                ChoiceCreate(text="3", is_correct=False),
                ChoiceCreate(text="4", is_correct=True),
            ],
        ),
        ids["teacher"],
    )
    quiz = service.create_quiz(
        QuizCreate(title="Quiz 1", course_id=ids["course"], pass_percent=50),
        ids["teacher"],
    )
    quiz = service.add_question(quiz.id, QuizQuestionAdd(question_id=q.id))
    quiz = service.publish_quiz(quiz.id)
    now = datetime.now(UTC)
    assignment = service.create_assignment(
        quiz.id,
        AssignmentCreate(
            section_id=ids["section"],
            opens_at=now - timedelta(minutes=1),
            due_at=now + timedelta(hours=1),
            attempt_limit=1,
        ),
        ids["teacher"],
        {"teacher"},
    )
    return q, quiz, assignment


def test_objective_autograding(service, ids):
    q, quiz, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    correct = next(c for c in q.choices if c.is_correct)
    service.answer_question(
        attempt.id, q.id, AnswerUpsert(selected_choice_id=correct.id), ids["student"]
    )
    result = service.submit_attempt(attempt.id, ids["student"])
    assert result.status == "GRADED"
    assert result.score == 2
    assert result.percent == 100
    assert result.passed is True


def test_attempt_limit(service, ids):
    _, _, assignment = build_objective(service, ids)
    service.start_attempt(assignment.id, ids["student"])
    with pytest.raises(ConflictError):
        service.start_attempt(assignment.id, ids["student"])


def test_saved_attempt_and_result_survive_reload(service, ids):
    q, _, assignment = build_objective(service, ids)
    principal = Principal(ids["student"], {"student"}, "test-token")
    assert get_active_attempt(assignment.id, principal, service) is None
    attempt = service.start_attempt(assignment.id, ids["student"])
    correct = next(c for c in q.choices if c.is_correct)
    service.answer_question(
        attempt.id, q.id, AnswerUpsert(selected_choice_id=correct.id), ids["student"]
    )
    resumed = get_active_attempt(assignment.id, principal, service)
    assert resumed["id"] == attempt.id
    assert resumed["answers"][0]["selected_choice_id"] == correct.id
    assert service.repo.count_attempts(assignment.id, ids["student"]) == 1
    assert (
        get_active_attempt(assignment.id, Principal(uuid.uuid4(), {"student"}, "other"), service)
        is None
    )
    service.submit_attempt(attempt.id, ids["student"])
    result = get_my_attempt(attempt.id, principal, service)
    assert result["percent"] == 100 and result["passed"] is True
    assert get_active_attempt(assignment.id, principal, service) is None
    assert "is_correct" not in str(result) and "correct_text" not in str(result)


def test_choice_from_another_question_is_rejected(service, ids):
    q, _, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    with pytest.raises(ConflictError, match="does not belong"):
        service.answer_question(
            attempt.id, q.id, AnswerUpsert(selected_choice_id=uuid.uuid4()), ids["student"]
        )
    assert service.repo.get_answer(attempt.id, q.id) is None


def test_answer_other_students_attempt_forbidden(service, ids):
    q, _, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    with pytest.raises(ForbiddenError):
        service.answer_question(attempt.id, q.id, AnswerUpsert(), uuid.uuid4())


def test_publish_empty_quiz_rejected(service, ids):
    quiz = service.create_quiz(
        QuizCreate(title="Empty", course_id=ids["course"]),
        ids["teacher"],
    )
    with pytest.raises(ConflictError):
        service.publish_quiz(quiz.id)


def test_manual_grading(service, ids):
    bank = service.create_bank(
        QuestionBankCreate(name="Written", course_id=ids["course"]), ids["teacher"]
    )
    q = service.create_question(
        QuestionCreate(
            bank_id=bank.id,
            question_type="SHORT_TEXT",
            prompt="Explain polymorphism",
            points=5,
        ),
        ids["teacher"],
    )
    quiz = service.create_quiz(
        QuizCreate(title="Written Quiz", course_id=ids["course"]), ids["teacher"]
    )
    service.add_question(quiz.id, QuizQuestionAdd(question_id=q.id))
    service.publish_quiz(quiz.id)
    now = datetime.now(UTC)
    assignment = service.create_assignment(
        quiz.id,
        AssignmentCreate(
            section_id=ids["section"],
            opens_at=now - timedelta(minutes=1),
            due_at=now + timedelta(hours=1),
        ),
        ids["teacher"],
        {"teacher"},
    )
    attempt = service.start_attempt(assignment.id, ids["student"])
    ans = service.answer_question(
        attempt.id,
        q.id,
        AnswerUpsert(text_answer="Runtime subtype behavior"),
        ids["student"],
    )
    submitted = service.submit_attempt(attempt.id, ids["student"])
    assert submitted.status == "SUBMITTED"
    graded = service.manual_grade(
        attempt.id,
        ManualGrade(answer_id=ans.id, score=4, reason="Reviewed response"),
        ids["teacher"],
    )
    assert graded.status == "GRADED"
    assert graded.score == 4
    assert graded.percent == 80
    assert graded.passed is True
