from datetime import timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker
from test_workflow import build_objective

from app.core.errors import ConflictError, ForbiddenError
from app.domain.entities.models import OutboxEvent
from app.schemas.models import AnswerUpsert, ManualGrade
from app.services.assessment_service import aware, now
from app.workers.attempt_expiry import expire_attempts


@pytest.mark.parametrize("minutes,expected_seconds", [(1, 60), (120, 3600), (None, 3600)])
def test_expiry_uses_earlier_of_timer_and_deadline(service, ids, minutes, expected_seconds):
    _, quiz, assignment = build_objective(service, ids)
    quiz.duration_minutes = minutes
    service.db.commit()
    attempt = service.start_attempt(assignment.id, ids["student"])
    seconds = (aware(attempt.expires_at) - aware(attempt.started_at)).total_seconds()
    assert expected_seconds - 2 < seconds <= expected_seconds


def test_late_edit_finalizes_only_previously_saved_answers(service, ids):
    q, _, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    correct = next(choice for choice in q.choices if choice.is_correct)
    wrong = next(choice for choice in q.choices if not choice.is_correct)
    service.answer_question(
        attempt.id, q.id, AnswerUpsert(selected_choice_id=correct.id), ids["student"]
    )
    attempt.expires_at = now() - timedelta(seconds=1)
    service.db.commit()
    with pytest.raises(ConflictError, match="expired"):
        service.answer_question(
            attempt.id, q.id, AnswerUpsert(selected_choice_id=wrong.id), ids["student"]
        )
    result = service.read_student_attempt(attempt.id, ids["student"])
    assert result.percent == 100 and result.status == "GRADED"
    assert result.answers[0].selected_choice_id == correct.id
    events = service.db.scalar(select(func.count()).select_from(OutboxEvent))
    assert service.submit_attempt(attempt.id, ids["student"]).percent == 100
    assert service.db.scalar(select(func.count()).select_from(OutboxEvent)) == events


def test_owner_check_precedes_expiry_effects(service, ids):
    import uuid

    _, _, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    attempt.expires_at = now() - timedelta(seconds=1)
    service.db.commit()
    with pytest.raises(ForbiddenError):
        service.read_student_attempt(attempt.id, uuid.uuid4())
    assert service.repo.get_attempt(attempt.id).status == "IN_PROGRESS"


def test_worker_expires_attempt_without_browser_and_does_not_repeat_events(service, ids):
    _, _, assignment = build_objective(service, ids)
    attempt = service.start_attempt(assignment.id, ids["student"])
    attempt.expires_at = now() - timedelta(seconds=1)
    service.db.commit()
    factory = sessionmaker(bind=service.db.get_bind(), expire_on_commit=False)
    assert expire_attempts(factory) == 1
    assert expire_attempts(factory) == 0
    service.db.expire_all()
    assert service.repo.get_attempt(attempt.id).status == "GRADED"
    assert service.repo.get_attempt(attempt.id).percent == 0


def test_unanswered_subjective_question_can_be_graded_after_expiry(service, ids):
    q, _, assignment = build_objective(service, ids)
    q.question_type = "SHORT_TEXT"
    service.db.commit()
    attempt = service.start_attempt(assignment.id, ids["student"])
    attempt.expires_at = now() - timedelta(seconds=1)
    service.db.commit()
    submitted = service.read_student_attempt(attempt.id, ids["student"])
    assert submitted.status == "SUBMITTED"
    assert len(submitted.answers) == 1 and submitted.answers[0].text_answer == ""
    result = service.manual_grade(
        attempt.id,
        ManualGrade(answer_id=submitted.answers[0].id, score=0, reason="Blank response"),
        ids["teacher"],
    )
    assert result.status == "GRADED" and result.percent == 0
