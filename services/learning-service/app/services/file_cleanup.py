"""Idempotent learning file deletions. Run only by the owned event worker."""
from __future__ import annotations
from datetime import UTC, datetime, timedelta
from sqlalchemy import select
from app.db.session import SessionLocal
from app.domain.entities.models import FileDeletionTask, FileOperationAudit, ResourceVersion
from app.storage.dependencies import get_storage_backend


def run_file_cleanup(*, limit: int = 12) -> int:
    now = datetime.now(UTC)
    worked = 0
    with SessionLocal() as db:
        stmt = (select(FileDeletionTask)
                .where(FileDeletionTask.deleted_at.is_(None))
                .where((FileDeletionTask.next_attempt_at.is_(None)) | (FileDeletionTask.next_attempt_at <= now))
                .order_by(FileDeletionTask.created_at, FileDeletionTask.id)
                .limit(limit).with_for_update(skip_locked=True))
        for item in db.scalars(stmt).all():
            # A hard safety boundary: never remove an object still referenced.
            if db.scalar(select(ResourceVersion.id).where(ResourceVersion.storage_key == item.storage_key).limit(1)):
                item.attempts += 1
                item.error = "OBJECT_STILL_REFERENCED"
                item.next_attempt_at = now + timedelta(hours=1)
                continue
            try:
                get_storage_backend().delete(item.storage_key)
                item.deleted_at = now
                item.error = None
                item.next_attempt_at = None
                db.add(FileOperationAudit(resource_id=item.resource_id, actor_user_id=item.actor_user_id,
                                           operation="DELETED"))
                worked += 1
            except Exception as exc:
                item.attempts += 1
                item.error = type(exc).__name__[:160]  # no secrets or file paths
                item.next_attempt_at = now + timedelta(seconds=min(3600, 2 ** min(item.attempts, 11)))
        db.commit()
    return worked
