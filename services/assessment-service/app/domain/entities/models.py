from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from smartedu_infra.runtime import RelayState
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class QuestionType(enum.StrEnum):
    MCQ_SINGLE = "MCQ_SINGLE"
    TRUE_FALSE = "TRUE_FALSE"
    SHORT_TEXT = "SHORT_TEXT"


class QuizStatus(enum.StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AttemptStatus(enum.StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"


class QuestionBank(Base):
    __tablename__ = "question_banks"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), index=True)
    course_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("question_banks.id", ondelete="CASCADE"), index=True
    )
    question_type: Mapped[str] = mapped_column(String(32), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    points: Mapped[float] = mapped_column(Float, default=1.0)
    correct_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    choices: Mapped[list[QuestionChoice]] = relationship(
        back_populates="question", cascade="all, delete-orphan", lazy="selectin"
    )


class QuestionChoice(Base):
    __tablename__ = "question_choices"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    question: Mapped[Question] = relationship(back_populates="choices")


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    status: Mapped[str] = mapped_column(String(24), default=QuizStatus.DRAFT.value, index=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pass_percent: Mapped[float] = mapped_column(Float, default=50.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    questions: Mapped[list[QuizQuestion]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan", lazy="selectin"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (UniqueConstraint("quiz_id", "question_id", name="uq_quiz_question"),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    points_override: Mapped[float | None] = mapped_column(Float, nullable=True)
    quiz: Mapped[Quiz] = relationship(back_populates="questions")
    question: Mapped[Question] = relationship(lazy="selectin")


class QuizAssignment(Base):
    __tablename__ = "quiz_assignments"
    __table_args__ = (UniqueConstraint("quiz_id", "section_id", name="uq_quiz_assignment_section"),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), index=True
    )
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempt_limit: Mapped[int] = mapped_column(Integer, default=1)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "student_user_id",
            "attempt_number",
            name="uq_assignment_student_attempt",
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("quiz_assignments.id", ondelete="CASCADE"), index=True
    )
    student_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    attempt_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(24), default=AttemptStatus.IN_PROGRESS.value, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    graded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answers: Mapped[list[AttemptAnswer]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", lazy="selectin"
    )


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_answer"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("attempts.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), index=True
    )
    selected_choice_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    text_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    auto_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    manual_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    attempt: Mapped[Attempt] = relationship(back_populates="answers")


class GradeReview(Base):
    __tablename__ = "grade_reviews"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("attempts.id", ondelete="CASCADE"), index=True
    )
    answer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("attempt_answers.id", ondelete="SET NULL"), nullable=True
    )
    previous_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    graded_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OutboxEvent(RelayState, Base):
    __tablename__ = "outbox_events"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    aggregate_type: Mapped[str] = mapped_column(String(80))
    aggregate_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
