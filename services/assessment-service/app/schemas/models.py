from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChoiceCreate(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool = False


class QuestionCreate(BaseModel):
    bank_id: uuid.UUID
    question_type: str = Field(pattern=r"^(MCQ_SINGLE|TRUE_FALSE|SHORT_TEXT)$")
    prompt: str = Field(min_length=1)
    points: float = Field(default=1.0, gt=0)
    correct_text: str | None = None
    explanation: str | None = None
    choices: list[ChoiceCreate] = []

    @model_validator(mode="after")
    def validate_question(self):
        if self.question_type in {"MCQ_SINGLE", "TRUE_FALSE"}:
            if len(self.choices) < 2:
                raise ValueError("Objective questions require at least two choices.")
            if sum(1 for c in self.choices if c.is_correct) != 1:
                raise ValueError("Objective questions require exactly one correct choice.")
        if self.question_type == "SHORT_TEXT" and self.choices:
            raise ValueError("Written questions cannot have objective choices.")
        return self


class QuestionBankCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    course_id: uuid.UUID | None = None


class QuizUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    pass_percent: float | None = Field(default=None, ge=0, le=100)


class QuizCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    course_id: uuid.UUID
    duration_minutes: int | None = Field(default=None, gt=0)
    pass_percent: float = Field(default=50, ge=0, le=100)


class QuizQuestionAdd(BaseModel):
    question_id: uuid.UUID
    position: int = Field(default=0, ge=0)
    points_override: float | None = Field(default=None, gt=0)


class AssignmentCreate(BaseModel):
    section_id: uuid.UUID
    opens_at: datetime
    due_at: datetime
    attempt_limit: int = Field(default=1, ge=1, le=20)

    @model_validator(mode="after")
    def dates(self):
        if self.opens_at.tzinfo is None or self.opens_at.utcoffset() is None:
            raise ValueError("opens_at must include a timezone offset")
        if self.due_at.tzinfo is None or self.due_at.utcoffset() is None:
            raise ValueError("due_at must include a timezone offset")
        if self.due_at <= self.opens_at:
            raise ValueError("due_at must be after opens_at")
        return self


class AnswerUpsert(BaseModel):
    selected_choice_id: uuid.UUID | None = None
    text_answer: str | None = None


class ManualGrade(BaseModel):
    answer_id: uuid.UUID
    score: float = Field(ge=0)
    feedback: str | None = None
    reason: str = Field(min_length=2)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BasicOut(ORMModel):
    id: uuid.UUID


class AttemptOut(ORMModel):
    id: uuid.UUID
    assignment_id: uuid.UUID
    student_user_id: uuid.UUID
    attempt_number: int
    status: str
    score: float | None
    max_score: float | None
    percent: float | None
    passed: bool | None
    started_at: datetime
    expires_at: datetime | None
    server_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    submitted_at: datetime | None
    graded_at: datetime | None
