from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.models import (
    Attempt,
    AttemptAnswer,
    Question,
    QuestionBank,
    Quiz,
    QuizAssignment,
    QuizQuestion,
)


class AssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_bank(self, bank_id: uuid.UUID):
        return self.db.get(QuestionBank, bank_id)

    def get_question(self, question_id: uuid.UUID):
        stmt = (
            select(Question)
            .options(selectinload(Question.choices))
            .where(Question.id == question_id)
        )
        return self.db.scalar(stmt)

    def get_quiz(self, quiz_id: uuid.UUID):
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.questions)
                .selectinload(QuizQuestion.question)
                .selectinload(Question.choices)
            )
            .where(Quiz.id == quiz_id)
        )
        return self.db.scalar(stmt)

    def get_assignment(self, assignment_id: uuid.UUID):
        return self.db.get(QuizAssignment, assignment_id)

    def get_attempt(self, attempt_id: uuid.UUID, *, lock: bool = False):
        stmt = (
            select(Attempt).options(selectinload(Attempt.answers)).where(Attempt.id == attempt_id)
        )
        if lock:
            stmt = stmt.with_for_update().execution_options(populate_existing=True)
        return self.db.scalar(stmt)

    def active_attempt(self, assignment_id: uuid.UUID, student_id: uuid.UUID):
        return self.db.scalar(
            select(Attempt)
            .options(selectinload(Attempt.answers))
            .where(
                Attempt.assignment_id == assignment_id,
                Attempt.student_user_id == student_id,
                Attempt.status == "IN_PROGRESS",
            )
            .order_by(Attempt.started_at.desc())
            .limit(1)
        )

    def count_attempts(self, assignment_id: uuid.UUID, student_user_id: uuid.UUID) -> int:
        stmt = select(func.count(Attempt.id)).where(
            Attempt.assignment_id == assignment_id,
            Attempt.student_user_id == student_user_id,
        )
        return int(self.db.scalar(stmt) or 0)

    def list_student_attempts(self, student_user_id: uuid.UUID):
        stmt = (
            select(Attempt)
            .where(Attempt.student_user_id == student_user_id)
            .order_by(Attempt.started_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_answer(self, attempt_id: uuid.UUID, question_id: uuid.UUID):
        stmt = select(AttemptAnswer).where(
            AttemptAnswer.attempt_id == attempt_id,
            AttemptAnswer.question_id == question_id,
        )
        return self.db.scalar(stmt)
