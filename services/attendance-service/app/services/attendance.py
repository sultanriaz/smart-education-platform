from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient
from app.core.config import Settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.domain.models import (
    AttendanceCorrection,
    AttendanceRecord,
    AttendanceSession,
    OutboxEvent,
    SessionHistory,
    SessionStatus,
)
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance import (
    AttendanceRead,
    AttendanceSummary,
    BulkMark,
    Correction,
    Counts,
    SessionCreate,
    SessionPatch,
    SessionRead,
    StudentAttendance,
    StudentSummary,
)
from app.security.jwt import Principal
from app.services.statistics import calculate_counts, grouped_summaries
from app.services.transaction import transaction


class AttendanceService:
    def __init__(self, db: Session, academic: AcademicClient, settings: Settings) -> None:
        self.db = db
        self.repo = AttendanceRepository(db)
        self.academic = academic
        self.settings = settings

    def _staff(self, actor: Principal) -> None:
        if actor.roles.isdisjoint({"admin", "teacher"}):
            raise ForbiddenError()

    def _section_access(self, actor: Principal, section_id: UUID) -> None:
        self._staff(actor)
        if not actor.is_admin:
            self.academic.validate_teacher_assignment(section_id, actor.access_token)

    def _session(self, session_id: UUID, *, lock: bool = False) -> AttendanceSession:
        session = self.repo.get_session(session_id, lock=lock)
        if session is None:
            raise NotFoundError()
        return session

    def _open(self, session: AttendanceSession) -> None:
        if session.status != SessionStatus.OPEN:
            raise ConflictError("Normal attendance writes require an OPEN session.")

    def _event(
        self, event_type: str, session: AttendanceSession, actor: Principal, **payload
    ) -> None:
        now = datetime.now(UTC)
        self.repo.add(
            OutboxEvent(
                aggregate_id=session.id,
                event_type=event_type,
                available_at=now,
                payload={
                    "version": 1,
                    "session_id": str(session.id),
                    "section_id": str(session.section_id),
                    "course_id": str(session.course_id),
                    "session_date": session.session_date.isoformat(),
                    "actor_user_id": str(actor.user_id),
                    "occurred_at": now.isoformat(),
                    **payload,
                },
            )
        )

    def _history(self, session, actor, action, reason, previous, new) -> None:
        self.repo.add(
            SessionHistory(
                attendance_session_id=session.id,
                action=action,
                reason=reason,
                previous_values=previous,
                new_values=new,
                changed_by_user_id=actor.user_id,
                changed_at=datetime.now(UTC),
            )
        )

    def create_session(self, actor: Principal, payload: SessionCreate) -> AttendanceSession:
        self._staff(actor)
        section = self.academic.get_section(payload.section_id, actor.access_token)
        self._section_access(actor, payload.section_id)
        if not section.is_active:
            raise ConflictError("Attendance sessions require an active academic section.")
        if payload.schedule_occurrence_id and (
            self.settings.ENVIRONMENT.lower() in {"production", "prod", "staging"}
            or self.settings.VERIFY_SCHEDULE_OCCURRENCES
        ):
            from app.clients.scheduling import verify_schedule_occurrence
            verify_schedule_occurrence(
                self.settings, payload.section_id, payload.session_date,
                payload.schedule_occurrence_id, actor.access_token,
            )
        with transaction(self.db):
            session = self.repo.add(
                AttendanceSession(
                    **payload.model_dump(),
                    course_id=section.course_id,
                    semester_id=section.semester_id,
                    created_by_user_id=actor.user_id,
                )
            )
            self._event(
                "attendance.session_created",
                session,
                actor,
                session_date=session.session_date.isoformat(),
            )
        return session

    def get_session(self, actor: Principal, session_id: UUID) -> AttendanceSession:
        self._staff(actor)
        session = self._session(session_id)
        self._section_access(actor, session.section_id)
        return session

    def list_sessions(
        self,
        actor: Principal,
        *,
        section_id: UUID | None = None,
        limit: int,
        offset: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttendanceSession]:
        self._staff(actor)
        if section_id:
            self._section_access(actor, section_id)
            section_ids = {section_id}
        else:
            section_ids = (
                None if actor.is_admin else self.academic.assigned_sections(actor.access_token)
            )
        return self.repo.sessions(
            section_ids=section_ids,
            limit=limit,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
        )

    def update_session(
        self, actor: Principal, session_id: UUID, payload: SessionPatch
    ) -> AttendanceSession:
        self.get_session(actor, session_id)
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            self._open(session)
            previous = SessionRead.model_validate(session).model_dump(mode="json")
            starts_at = (
                payload.starts_at if "starts_at" in payload.model_fields_set else session.starts_at
            )
            ends_at = payload.ends_at if "ends_at" in payload.model_fields_set else session.ends_at
            if (starts_at is None) != (ends_at is None) or (
                starts_at is not None and ends_at <= starts_at
            ):
                raise ConflictError("Session requires a valid pair of institution-local times.")
            session.starts_at, session.ends_at = starts_at, ends_at
            self.db.flush()
            self._history(
                session,
                actor,
                "TIMES_UPDATED",
                payload.reason,
                previous,
                SessionRead.model_validate(session).model_dump(mode="json"),
            )
            self._event("attendance.session_updated", session, actor)
        return session

    def bulk_mark(
        self, actor: Principal, session_id: UUID, payload: BulkMark
    ) -> list[AttendanceRecord]:
        session = self.get_session(actor, session_id)
        # No DB mutations happen until every student has passed the external check.
        for mark in payload.records:
            self.academic.validate_student_enrollment(
                session.section_id, mark.student_user_id, actor.access_token
            )
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            self._open(session)
            results = []
            for mark in payload.records:
                existing = self.repo.get_record(session_id, mark.student_user_id)
                if existing is not None:
                    if existing.status != mark.status or existing.notes != mark.notes:
                        raise ConflictError(
                            "Record already marked differently; use an audited correction."
                        )
                    results.append(existing)
                    continue
                record = self.repo.add(
                    AttendanceRecord(
                        attendance_session_id=session_id,
                        **mark.model_dump(),
                        marked_by_user_id=actor.user_id,
                        marked_at=datetime.now(UTC),
                    )
                )
                results.append(record)
                self._event(
                    "attendance.recorded",
                    session,
                    actor,
                    record_id=str(record.id),
                    student_user_id=str(record.student_user_id),
                    status=record.status,
                )
        return results

    def correct(
        self,
        actor: Principal,
        session_id: UUID,
        student_id: UUID,
        payload: Correction,
    ) -> AttendanceRecord:
        session = self.get_session(actor, session_id)
        if not actor.is_admin:
            self.academic.validate_student_enrollment(
                session.section_id, student_id, actor.access_token
            )
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            if session.status == SessionStatus.CANCELLED:
                raise ConflictError("Cancelled sessions are immutable.")
            if session.status == SessionStatus.FINALIZED and not actor.is_admin:
                raise ConflictError("Only administrators can correct finalized attendance.")
            record = self.repo.get_record(session_id, student_id)
            if record is None:
                raise NotFoundError("Attendance record")
            notes = payload.notes if "notes" in payload.model_fields_set else record.notes
            if record.status == payload.status and record.notes == notes:
                return record
            self.repo.add(
                AttendanceCorrection(
                    attendance_record_id=record.id,
                    previous_status=record.status,
                    new_status=payload.status,
                    previous_notes=record.notes,
                    new_notes=notes,
                    reason=payload.reason,
                    changed_by_user_id=actor.user_id,
                    changed_at=datetime.now(UTC),
                )
            )
            record.status, record.notes = payload.status, notes
            # Initial marker/time are retained. Correction history identifies later actors.
            self.db.flush()
            self._event(
                "attendance.updated",
                session,
                actor,
                record_id=str(record.id),
                student_user_id=str(student_id),
                status=record.status,
            )
            if session.status == SessionStatus.FINALIZED:
                self._low_events(actor, session)
        return record

    def finalize(self, actor: Principal, session_id: UUID) -> AttendanceSession:
        session = self.get_session(actor, session_id)
        roster = self.academic.get_section_roster(session.section_id, actor.access_token)
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            self._open(session)
            if not roster.issubset(self.repo.recorded_students(session_id)):
                raise ConflictError("Mark every current roster member before finalizing.")
            session.status = SessionStatus.FINALIZED
            session.finalized_at = datetime.now(UTC)
            session.finalized_by_user_id = actor.user_id
            self.db.flush()
            self._history(
                session,
                actor,
                "FINALIZED",
                "Attendance sheet finalized.",
                {"status": "OPEN"},
                {"status": "FINALIZED"},
            )
            self._event("attendance.session_finalized", session, actor)
            self._low_events(actor, session)
        return session

    def _low_events(self, actor: Principal, session: AttendanceSession) -> None:
        rows = self.repo.counts(section_ids={session.section_id}, group_by=("student_user_id",))
        for summary in grouped_summaries(
            rows, ("student_user_id",), self.settings.LOW_ATTENDANCE_THRESHOLD_PERCENT
        ):
            if summary.is_low_attendance:
                self._event(
                    "attendance.low_attendance_detected",
                    session,
                    actor,
                    student_user_id=str(summary.student_user_id),
                    attendance_percentage=summary.attendance_percentage,
                    threshold_percent=self.settings.LOW_ATTENDANCE_THRESHOLD_PERCENT,
                )

    def reopen(self, actor: Principal, session_id: UUID, reason: str) -> AttendanceSession:
        if not actor.is_admin:
            raise ForbiddenError("Only administrators can reopen attendance.")
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            if session.status != SessionStatus.FINALIZED:
                raise ConflictError("Only finalized sessions can be reopened.")
            previous = SessionRead.model_validate(session).model_dump(mode="json")
            session.status = SessionStatus.OPEN
            session.finalized_at = session.finalized_by_user_id = None
            self.db.flush()
            self._history(
                session,
                actor,
                "REOPENED",
                reason,
                previous,
                SessionRead.model_validate(session).model_dump(mode="json"),
            )
            self._event("attendance.session_reopened", session, actor, reason=reason)
        return session

    def cancel(self, actor: Principal, session_id: UUID, reason: str) -> AttendanceSession:
        self.get_session(actor, session_id)
        with transaction(self.db):
            session = self._session(session_id, lock=True)
            if session.status == SessionStatus.CANCELLED:
                raise ConflictError("Session is already cancelled.")
            if session.status == SessionStatus.FINALIZED and not actor.is_admin:
                raise ForbiddenError("Only administrators can cancel finalized attendance.")
            previous = SessionRead.model_validate(session).model_dump(mode="json")
            session.status = SessionStatus.CANCELLED
            session.finalized_at = session.finalized_by_user_id = None
            self.db.flush()
            self._history(
                session,
                actor,
                "CANCELLED",
                reason,
                previous,
                SessionRead.model_validate(session).model_dump(mode="json"),
            )
            self._event("attendance.session_cancelled", session, actor, reason=reason)
        return session

    def records(self, actor, session_id, *, limit, offset):
        self.get_session(actor, session_id)
        return self.repo.records(session_id, limit=limit, offset=offset)

    def history(self, actor, session_id, *, student_id=None, limit, offset):
        self.get_session(actor, session_id)
        if student_id is None:
            return self.repo.session_history(session_id, limit=limit, offset=offset)
        record = self.repo.get_record(session_id, student_id)
        if record is None:
            raise NotFoundError("Attendance record")
        return self.repo.corrections(record.id, limit=limit, offset=offset)

    def _self(self, actor: Principal) -> None:
        if "student" not in actor.roles:
            raise ForbiddenError("Student role required for self attendance.")

    def attendance(
        self, actor: Principal, *, self_view=False, section_id=None, limit, offset, **filters
    ):
        if self_view:
            self._self(actor)
            filters["student_id"] = actor.user_id
        else:
            self._section_access(actor, section_id)
        if section_id is not None:
            filters["section_ids"] = {section_id}
        return [
            StudentAttendance(
                **AttendanceRead.model_validate(record).model_dump(),
                section_id=session.section_id,
                course_id=session.course_id,
                semester_id=session.semester_id,
                session_date=session.session_date,
                session_status=session.status,
            )
            for record, session in self.repo.attendance(limit=limit, offset=offset, **filters)
        ]

    def student_summary(
        self, actor: Principal, *, limit: int, offset: int, **filters
    ) -> StudentSummary:
        self._self(actor)
        filters["student_id"] = actor.user_id
        threshold = self.settings.LOW_ATTENDANCE_THRESHOLD_PERCENT
        return StudentSummary(
            student_user_id=actor.user_id,
            totals=calculate_counts(self.repo.counts(**filters), threshold),
            by_section=grouped_summaries(
                self.repo.counts(group_by=("section_id", "course_id"), **filters),
                ("section_id", "course_id"),
                threshold,
            )[offset : offset + limit],
            by_course=grouped_summaries(
                self.repo.counts(group_by=("course_id",), **filters), ("course_id",), threshold
            )[offset : offset + limit],
            limit=limit,
            offset=offset,
        )

    def section_summary(
        self,
        actor: Principal,
        section_id: UUID,
        *,
        student_id: UUID | None = None,
        **filters,
    ) -> Counts:
        self._section_access(actor, section_id)
        return calculate_counts(
            self.repo.counts(section_ids={section_id}, student_id=student_id, **filters),
            self.settings.LOW_ATTENDANCE_THRESHOLD_PERCENT,
        )

    def low_attendance(
        self, actor: Principal, *, section_id=None, limit, offset, **filters
    ) -> list[AttendanceSummary]:
        self._staff(actor)
        if section_id:
            self._section_access(actor, section_id)
            section_ids = {section_id}
        else:
            section_ids = (
                None if actor.is_admin else self.academic.assigned_sections(actor.access_token)
            )
        summaries = grouped_summaries(
            self.repo.counts(
                section_ids=section_ids,
                group_by=("student_user_id", "section_id", "course_id"),
                **filters,
            ),
            ("student_user_id", "section_id", "course_id"),
            self.settings.LOW_ATTENDANCE_THRESHOLD_PERCENT,
        )
        return [row for row in summaries if row.is_low_attendance][offset : offset + limit]
