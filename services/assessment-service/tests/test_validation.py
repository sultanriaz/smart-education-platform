import pytest
from pydantic import ValidationError

from app.schemas.models import ChoiceCreate, QuestionCreate


def test_mcq_requires_single_correct_choice():
    with pytest.raises(ValidationError):
        QuestionCreate(
            bank_id="00000000-0000-0000-0000-000000000001",
            question_type="MCQ_SINGLE",
            prompt="x",
            choices=[
                ChoiceCreate(text="a", is_correct=True),
                ChoiceCreate(text="b", is_correct=True),
            ],
        )
