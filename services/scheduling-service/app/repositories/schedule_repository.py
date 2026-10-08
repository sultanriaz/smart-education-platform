from __future__ import annotations

import hashlib
import uuid
from datetime import date, time

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session, selectinload

from app.domain.models import ScheduleAudit, ScheduleEntry, ScheduleOverride


class ScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_schedule(
        self, schedule_id: uuid.UUID, *, for_update: bool = False
    ) -> ScheduleEntry | None:
        stmt = (
            select(ScheduleEntry)
            .options(selectinload(ScheduleEntry.overrides))
            .where(ScheduleEntry.id == schedule_id)
        )
        if for_update:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_schedules(
        self,
        *,
        section_id: uuid.UUID | None = None,
        teacher_user_id: uuid.UUID | None = None,
        room_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ScheduleEntry]:
        stmt = select(ScheduleEntry).order_by(ScheduleEntry.weekday, ScheduleEntry.starts_at)
        if section_id:
            stmt = stmt.where(ScheduleEntry.section_id == section_id)
        if teacher_user_id:
            stmt = stmt.where(ScheduleEntry.teacher_user_id == teacher_user_id)
        if room_id:
            stmt = stmt.where(ScheduleEntry.room_id == room_id)
        if status:
            stmt = stmt.where(ScheduleEntry.status == status)
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def list_active_overlapping_range(
        self,
        *,
        start_date: date,
        end_date: date,
        section_ids: list[uuid.UUID] | None = None,
        teacher_user_id: uuid.UUID | None = None,
        room_id: uuid.UUID | None = None,
    ) -> list[ScheduleEntry]:
        stmt = (
            select(ScheduleEntry)
            .options(selectinload(ScheduleEntry.overrides))
            .where(
                ScheduleEntry.status == "ACTIVE",
                ScheduleEntry.effective_from <= end_date,
                ScheduleEntry.effective_to >= start_date,
            )
        )
        if section_ids is not None:
            if not section_ids:
                return []
            stmt = stmt.where(ScheduleEntry.section_id.in_(section_ids))
        if teacher_user_id:
            stmt = stmt.where(ScheduleEntry.teacher_user_id == teacher_user_id)
        if room_id:
            stmt = stmt.where(ScheduleEntry.room_id == room_id)
        return list(self.db.scalars(stmt).unique().all())

    def find_recurring_conflicts(
        self,
        *,
        section_id: uuid.UUID,
        teacher_user_id: uuid.UUID,
        room_id: uuid.UUID | None,
        weekday: int,
        starts_at: time,
        ends_at: time,
        effective_from: date,
        effective_to: date,
        exclude_schedule_id: uuid.UUID | None = None,
    ) -> list[ScheduleEntry]:
        resource_conflict = or_(
            ScheduleEntry.section_id == section_id,
            ScheduleEntry.teacher_user_id == teacher_user_id,
        )
        if room_id is not None:
            resource_conflict = or_(resource_conflict, ScheduleEntry.room_id == room_id)

        stmt = select(ScheduleEntry).where(
            ScheduleEntry.status == "ACTIVE",
            ScheduleEntry.weekday == weekday,
            ScheduleEntry.effective_from <= effective_to,
            ScheduleEntry.effective_to >= effective_from,
            ScheduleEntry.starts_at < ends_at,
            ScheduleEntry.ends_at > starts_at,
            resource_conflict,
        )
        if exclude_schedule_id:
            stmt = stmt.where(ScheduleEntry.id != exclude_schedule_id)
        return list(self.db.scalars(stmt).all())

    def acquire_conflict_locks(
        self,
        *,
        section_id: uuid.UUID,
        teacher_user_id: uuid.UUID,
        room_id: uuid.UUID | None,
        weekday: int,
    ) -> None:
        if self.db.get_bind().dialect.name != "postgresql":
            return
        keys = [f"section:{section_id}:{weekday}", f"teacher:{teacher_user_id}:{weekday}"]
        if room_id:
            keys.append(f"room:{room_id}:{weekday}")
        for raw in sorted(keys):
            digest = hashlib.sha256(raw.encode("utf-8")).digest()
            key = int.from_bytes(digest[:8], "big", signed=True)
            self.db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})

    def add_schedule(self, schedule: ScheduleEntry) -> ScheduleEntry:
        self.db.add(schedule)
        self.db.flush()
        return schedule

    def add_override(self, override: ScheduleOverride) -> ScheduleOverride:
        self.db.add(override)
        self.db.flush()
        return override

    def get_override(
        self, schedule_id: uuid.UUID, occurrence_date: date
    ) -> ScheduleOverride | None:
        return self.db.scalar(
            select(ScheduleOverride).where(
                ScheduleOverride.schedule_id == schedule_id,
                ScheduleOverride.occurrence_date == occurrence_date,
            )
        )

    def add_audit(self, audit: ScheduleAudit) -> None:
        self.db.add(audit)
        self.db.flush()

    def list_audits(self, schedule_id: uuid.UUID) -> list[ScheduleAudit]:
        stmt = (
            select(ScheduleAudit)
            .where(ScheduleAudit.schedule_id == schedule_id)
            .order_by(ScheduleAudit.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())
