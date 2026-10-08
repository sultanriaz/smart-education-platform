from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.schemas.models import (
    AssignmentCreate,
    ChoiceCreate,
    QuestionBankCreate,
    QuestionCreate,
    QuizCreate,
    QuizQuestionAdd,
)


def test_student_assignment_detail_must_not_expose_correct_answer(service, ids):
    bank = service.create_bank(
        QuestionBankCreate(name="Safe bank", course_id=ids["course"]),
        ids["teacher"],
    )
    question = service.create_question(
        QuestionCreate(
            bank_id=bank.id,
            question_type="MCQ_SINGLE",
            prompt="Correct option must stay private",
            points=1,
            choices=[
                ChoiceCreate(text="A", is_correct=True),
                ChoiceCreate(text="B", is_correct=False),
            ],
        ),
        ids["teacher"],
    )
    quiz = service.create_quiz(
        QuizCreate(title="Safe quiz", course_id=ids["course"]),
        ids["teacher"],
    )
    service.add_question(quiz.id, QuizQuestionAdd(question_id=question.id))
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

    loaded = service.repo.get_quiz(assignment.quiz_id)
    assert loaded is not None
    # Endpoint projection must only serialize choice id/text.
    safe_choices = [
        {"id": choice.id, "text": choice.text} for choice in loaded.questions[0].question.choices
    ]
    assert all("is_correct" not in choice for choice in safe_choices)
