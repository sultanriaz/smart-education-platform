from __future__ import annotations

from app.db.base_class import Base
from app.domain.entities.models import (  # noqa: F401
    Attempt,
    AttemptAnswer,
    GradeReview,
    OutboxEvent,
    Question,
    QuestionBank,
    QuestionChoice,
    Quiz,
    QuizAssignment,
    QuizQuestion,
)

__all__ = ["Base"]
