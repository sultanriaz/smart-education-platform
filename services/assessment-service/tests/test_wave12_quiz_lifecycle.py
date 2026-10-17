from uuid import uuid4

import pytest

from app.core.errors import ConflictError
from app.schemas.models import QuizCreate, QuizUpdate
from app.services.assessment_service import AssessmentService


def test_draft_edit_then_archive_idempotent(db):
    service = AssessmentService(db)
    quiz = service.create_quiz(QuizCreate(title="Intro Quiz", course_id=uuid4()), uuid4())
    changed = service.edit_quiz(quiz.id, QuizUpdate(title="Revised Quiz"))
    assert changed.title == "Revised Quiz"
    archived = service.archive_quiz(quiz.id)
    assert archived.status == "ARCHIVED"
    assert service.archive_quiz(quiz.id).id == quiz.id
    with pytest.raises(ConflictError):
        service.edit_quiz(quiz.id, QuizUpdate(title="Must reject"))
