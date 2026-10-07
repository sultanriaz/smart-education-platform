from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.domain.models import (
    AttendanceCorrection,
    AttendanceRecord,
    AttendanceSession,
    SessionHistory,
    SessionStatus,
)


class AttendanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, record: Base):
        self.db.add(record)
        self.db.flush()
        return record

    def get_session(self, session_id: UUID, *, lock: bool = False) -> AttendanceSession | None:
        query = select(AttendanceSession).where(AttendanceSession.id == session_id)
        if lock:
            query = query.with_for_update().execution_options(populate_existing=True)
        return self.db.scalar(query)

    def sessions(
        self,
        *,
        section_ids: set[UUID] | None,
        limit: int,
        offset: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttendanceSession]:
        query = select(AttendanceSession)
        if section_ids is not None:
            query = query.where(AttendanceSession.section_id.in_(section_ids))
        if date_from is not None:
            query = query.where(AttendanceSession.session_date >= date_from)
        if date_to is not None:
            query = query.where(AttendanceSession.session_date <= date_to)
        return list(
            self.db.scalars(
                query.order_by(
                    AttendanceSession.session_date.desc(),
                    AttendanceSession.id,
                )
                .limit(limit)
                .offset(offset)
            )
        )

    def get_record(self, session_id: UUID, student_id: UUID) -> AttendanceRecord | None:
        return self.db.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == session_id,
                AttendanceRecord.student_user_id == student_id,
            )
        )

    def records(self, session_id: UUID, *, limit: int, offset: int) -> list[AttendanceRecord]:
        return list(
            self.db.scalars(
                select(AttendanceRecord)
                .where(
                    AttendanceRecord.attendance_session_id == session_id,
                )
                .order_by(AttendanceRecord.student_user_id)
                .limit(limit)
                .offset(offset)
            )
        )

    def recorded_students(self, session_id: UUID) -> set[UUID]:
        return set(
            self.db.scalars(
                select(AttendanceRecord.student_user_id).where(
                    AttendanceRecord.attendance_session_id == session_id,
                )
            )
        )

    def corrections(
        self, record_id: UUID, *, limit: int, offset: int
    ) -> list[AttendanceCorrection]:
        return list(
            self.db.scalars(
                select(AttendanceCorrection)
                .where(
                    AttendanceCorrection.attendance_record_id == record_id,
                )
                .order_by(AttendanceCorrection.changed_at, AttendanceCorrection.id)
                .limit(limit)
                .offset(offset)
            )
        )

    def session_history(self, session_id: UUID, *, limit: int, offset: int) -> list[SessionHistory]:
        return list(
            self.db.scalars(
                select(SessionHistory)
                .where(
                    SessionHistory.attendance_session_id == session_id,
                )
                .order_by(SessionHistory.changed_at, SessionHistory.id)
                .limit(limit)
                .offset(offset)
            )
        )

    def _record_query(
        self,
        *,
        finalized_only: bool,
        student_id: UUID | None = None,
        section_ids: set[UUID] | None = None,
        course_id: UUID | None = None,
        semester_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        query = select(AttendanceRecord, AttendanceSession).join(
            AttendanceSession,
            AttendanceRecord.attendance_session_id == AttendanceSession.id,
        )
        query = query.where(
            AttendanceSession.status == SessionStatus.FINALIZED
            if finalized_only
            else AttendanceSession.status != SessionStatus.CANCELLED
        )
        if student_id is not None:
            query = query.where(AttendanceRecord.student_user_id == student_id)
        if section_ids is not None:
            query = query.where(AttendanceSession.section_id.in_(section_ids))
        if course_id is not None:
            query = query.where(AttendanceSession.course_id == course_id)
        if semester_id is not None:
            query = query.where(AttendanceSession.semester_id == semester_id)
        if date_from is not None:
            query = query.where(AttendanceSession.session_date >= date_from)
        if date_to is not None:
            query = query.where(AttendanceSession.session_date <= date_to)
        return query

    def attendance(self, *, limit: int, offset: int, **filters: Any) -> list:
        query = self._record_query(finalized_only=False, **filters)
        return list(
            self.db.execute(
                query.order_by(
                    AttendanceSession.session_date.desc(),
                    AttendanceSession.id,
                    AttendanceRecord.student_user_id,
                )
                .limit(limit)
                .offset(offset)
            )
        )

    def counts(self, *, group_by: tuple[str, ...] = (), **filters: Any) -> list[dict]:
        # Only raw status counts are returned. Percentage/excused/late policy lives
        # entirely in the service layer.
        fields = {
            "student_user_id": AttendanceRecord.student_user_id,
            "section_id": AttendanceSession.section_id,
            "course_id": AttendanceSession.course_id,
        }
        columns = [fields[name] for name in group_by]
        query = (
            self._record_query(finalized_only=True, **filters)
            .with_only_columns(
                *columns,
                AttendanceRecord.status,
                func.count().label("count"),
                maintain_column_froms=True,
            )
            .group_by(*columns, AttendanceRecord.status)
        )
        return [dict(row._mapping) for row in self.db.execute(query)]
