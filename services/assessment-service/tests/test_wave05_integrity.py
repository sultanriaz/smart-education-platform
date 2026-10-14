from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.core.errors import ConflictError
from app.schemas.models import (
    AssignmentCreate, ChoiceCreate, QuestionBankCreate, QuestionCreate,
    QuizCreate, QuizQuestionAdd, AnswerUpsert,
)
from app.api.v1.endpoints.student_read import _attempt_summary


def test_question_type_is_allowlisted_and_objective_must_have_correct_choice():
    with pytest.raises(ValidationError):
        QuestionCreate(bank_id=uuid.uuid4(), question_type="ESSAY", prompt="essay")
    with pytest.raises(ValidationError):
        QuestionCreate(bank_id=uuid.uuid4(), question_type="SHORT_TEXT", prompt="why",
                       choices=[ChoiceCreate(text="not a text choice")])


def test_assignment_requires_explicit_timezone_and_order():
    start = datetime.now(UTC)
    with pytest.raises(ValidationError, match="timezone offset"):
        AssignmentCreate(section_id=uuid.uuid4(), opens_at=start.replace(tzinfo=None),
                         due_at=start + timedelta(hours=1))
    with pytest.raises(ValidationError, match="timezone offset"):
        AssignmentCreate(section_id=uuid.uuid4(), opens_at=start,
                         due_at=(start + timedelta(hours=1)).replace(tzinfo=None))


def test_reject_question_from_other_course(service, ids):
    bank = service.create_bank(QuestionBankCreate(name="Bank", course_id=uuid.uuid4()), ids["teacher"])
    question = service.create_question(QuestionCreate(bank_id=bank.id, question_type="SHORT_TEXT", prompt="explain"), ids["teacher"])
    quiz = service.create_quiz(QuizCreate(title="Course quiz", course_id=ids["course"]), ids["teacher"])
    with pytest.raises(ConflictError, match="another course"):
        service.add_question(quiz.id, QuizQuestionAdd(question_id=question.id))


def test_reject_assignment_to_section_of_another_course(service, ids):
    bank = service.create_bank(QuestionBankCreate(name="Bank", course_id=ids["course"]), ids["teacher"])
    question = service.create_question(QuestionCreate(bank_id=bank.id, question_type="SHORT_TEXT", prompt="explain"), ids["teacher"])
    quiz = service.create_quiz(QuizCreate(title="Course quiz", course_id=ids["course"]), ids["teacher"])
    service.add_question(quiz.id, QuizQuestionAdd(question_id=question.id))
    service.publish_quiz(quiz.id)
    service.academic.course_id = uuid.uuid4()
    start = datetime.now(UTC)
    with pytest.raises(ConflictError, match="does not match"):
        service.create_assignment(quiz.id, AssignmentCreate(section_id=ids["section"], opens_at=start,
                                          due_at=start + timedelta(days=1)), ids["teacher"], {"teacher"})


def test_manual_attempt_has_no_provisional_marks_in_student_detail(service, ids):
    bank = service.create_bank(QuestionBankCreate(name="Manual", course_id=ids["course"]), ids["teacher"])
    question = service.create_question(QuestionCreate(bank_id=bank.id, question_type="SHORT_TEXT", prompt="explain", points=5), ids["teacher"])
    quiz = service.create_quiz(QuizCreate(title="Manual quiz", course_id=ids["course"]), ids["teacher"])
    service.add_question(quiz.id, QuizQuestionAdd(question_id=question.id))
    service.publish_quiz(quiz.id)
    start = datetime.now(UTC)
    assignment = service.create_assignment(quiz.id, AssignmentCreate(section_id=ids["section"],
            opens_at=start - timedelta(minutes=1),due_at=start+timedelta(hours=1)), ids["teacher"], {"teacher"})
    attempt = service.start_attempt(assignment.id, ids["student"])
    service.answer_question(attempt.id, question.id, AnswerUpsert(text_answer="draft"), ids["student"])
    pending = service.submit_attempt(attempt.id, ids["student"])
    assert pending.status == "SUBMITTED"
    assert _attempt_summary(pending)["score"] is None
    assert _attempt_summary(pending)["percent"] is None
