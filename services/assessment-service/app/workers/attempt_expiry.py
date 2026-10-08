"""Finalize expired attempts independently of browser activity or API requests."""

from sqlalchemy import select

from app.domain.entities.models import Attempt, AttemptStatus
from app.services.assessment_service import AssessmentService, now


def expire_attempts(session_factory, batch_size: int = 25) -> int:
    completed = 0
    for _ in range(batch_size):
        with session_factory() as db:
            attempt = db.scalar(
                select(Attempt)
                .where(
                    Attempt.status == AttemptStatus.IN_PROGRESS.value,
                    Attempt.expires_at <= now(),
                )
                .order_by(Attempt.expires_at, Attempt.id)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            if attempt is None:
                break
            if AssessmentService(db).finalize_if_expired(attempt):
                completed += 1
    return completed
