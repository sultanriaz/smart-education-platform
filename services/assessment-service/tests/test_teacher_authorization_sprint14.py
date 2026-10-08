from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.authoring import create_question
from app.schemas.models import ChoiceCreate, QuestionBankCreate, QuestionCreate
from app.security.auth import Principal


def test_teacher_cannot_add_question_to_another_teachers_bank(service, ids):
    owner = ids["teacher"]
    other = uuid.uuid4()

    bank = service.create_bank(
        QuestionBankCreate(name="Owner bank", course_id=ids["course"]),
        owner,
    )

    payload = QuestionCreate(
        bank_id=bank.id,
        question_type="MCQ_SINGLE",
        prompt="Protected question",
        points=1,
        choices=[
            ChoiceCreate(text="A", is_correct=True),
            ChoiceCreate(text="B", is_correct=False),
        ],
    )

    principal = Principal(
        user_id=other,
        roles={"teacher"},
        token="teacher-token",
    )

    with pytest.raises(HTTPException) as exc:
        create_question(payload=payload, p=principal, service=service)

    assert exc.value.status_code == 403


def test_admin_can_add_question_to_teacher_bank(service, ids):
    bank = service.create_bank(
        QuestionBankCreate(name="Teacher bank", course_id=ids["course"]),
        ids["teacher"],
    )

    payload = QuestionCreate(
        bank_id=bank.id,
        question_type="MCQ_SINGLE",
        prompt="Admin managed question",
        points=1,
        choices=[
            ChoiceCreate(text="A", is_correct=True),
            ChoiceCreate(text="B", is_correct=False),
        ],
    )

    principal = Principal(
        user_id=uuid.uuid4(),
        roles={"admin"},
        token="admin-token",
    )

    created = create_question(payload=payload, p=principal, service=service)
    assert created.bank_id == bank.id
