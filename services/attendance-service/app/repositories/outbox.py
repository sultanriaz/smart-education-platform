from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.models import OutboxEvent


class OutboxRepository:
    """Persistence primitives for a future worker; callers own transactions.

    A worker claims rows with SKIP LOCKED, sets a lease, and commits before external
    delivery. It later locks its leased row to acknowledge or release it.
    Pass a fresh owner ID for each claim batch, never reused across leases.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def claim(
        self, worker_id: str, *, now: datetime, lease_until: datetime, limit: int
    ) -> list[OutboxEvent]:
        rows = list(
            self.db.scalars(
                select(OutboxEvent)
                .where(
                    OutboxEvent.published_at.is_(None),
                    OutboxEvent.available_at <= now,
                    or_(OutboxEvent.locked_until.is_(None), OutboxEvent.locked_until <= now),
                )
                .order_by(OutboxEvent.available_at, OutboxEvent.id)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        )
        for row in rows:
            row.claimed_by = worker_id
            row.locked_until = lease_until
            row.attempts += 1
        self.db.flush()
        return rows

    def acknowledge(self, event_id, worker_id: str, *, now: datetime) -> bool:
        row = self.db.scalar(
            select(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.claimed_by == worker_id,
                OutboxEvent.locked_until > now,
                OutboxEvent.published_at.is_(None),
            )
            .with_for_update()
        )
        if row is None:
            return False
        row.published_at = now
        row.claimed_by = None
        row.locked_until = None
        self.db.flush()
        return True

    def release(
        self, event_id, worker_id: str, *, now: datetime, retry_at: datetime, error: str
    ) -> bool:
        row = self.db.scalar(
            select(OutboxEvent)
            .where(
                OutboxEvent.id == event_id,
                OutboxEvent.claimed_by == worker_id,
                OutboxEvent.locked_until > now,
                OutboxEvent.published_at.is_(None),
            )
            .with_for_update()
        )
        if row is None:
            return False
        row.available_at = retry_at
        row.last_error = error[:2000]
        row.claimed_by = None
        row.locked_until = None
        self.db.flush()
        return True
