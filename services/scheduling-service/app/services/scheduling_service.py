from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient
from app.clients.facility import FacilityClient, get_facility_client
from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.domain.models import OutboxEvent, ScheduleAudit, ScheduleEntry, ScheduleOverride
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import OverrideCreate, ScheduleCreate, ScheduleUpdate
from app.security.auth import Principal


def _schedule_dict(schedule: ScheduleEntry) -> dict:
    return {
        "id": str(schedule.id),
        "section_id": str(schedule.section_id),
        "course_id": str(schedule.course_id) if schedule.course_id else None,
        "semester_id": str(schedule.semester_id) if schedule.semester_id else None,
        "teacher_user_id": str(schedule.teacher_user_id),
        "room_id": str(schedule.room_id) if schedule.room_id else None,
        "weekday": schedule.weekday,
        "starts_at": schedule.starts_at.isoformat(),
        "ends_at": schedule.ends_at.isoformat(),
        "effective_from": schedule.effective_from.isoformat(),
        "effective_to": schedule.effective_to.isoformat(),
        "timezone_name": schedule.timezone_name,
        "status": schedule.status,
        "version": schedule.version,
    }


class SchedulingService:
    def __init__(self, db: Session, academic: AcademicClient, facility: FacilityClient | None = None):
        self.db = db
        self.repo = ScheduleRepository(db)
        self.outbox = OutboxRepository(db)
        self.academic = academic
        self.facility = facility if facility is not None else get_facility_client()

    def _desired_reservations(self, schedule: ScheduleEntry) -> list[dict]:
        if schedule.status != "ACTIVE" or schedule.room_id is None:
            return []
        overrides = {o.occurrence_date: o for o in schedule.overrides}
        current = schedule.effective_from
        while current.weekday() != schedule.weekday:
            current += timedelta(days=1)
        slots = []
        timezone = ZoneInfo(schedule.timezone_name)
        while current <= schedule.effective_to:
            override = overrides.get(current)
            if not override or override.kind != "CANCELLED":
                room = (override.room_id if override and override.kind == "RESCHEDULED"
                        and override.room_id is not None else schedule.room_id)
                start = override.starts_at if override and override.kind == "RESCHEDULED" else schedule.starts_at
                end = override.ends_at if override and override.kind == "RESCHEDULED" else schedule.ends_at
                if room is not None:
                    slots.append({
                        "occurrence_date": current.isoformat(), "facility_id": str(room),
                        "starts_at": datetime.combine(current, start, tzinfo=timezone).astimezone(UTC).isoformat(),
                        "ends_at": datetime.combine(current, end, tzinfo=timezone).astimezone(UTC).isoformat(),
                    })
            current += timedelta(days=7)
            if len(slots) > settings.MAX_SCHEDULE_RESERVATION_OCCURRENCES:
                raise ConflictError("Schedule has too many classroom occurrences")
        return slots

    def _sync_reservations(self, schedule: ScheduleEntry) -> None:
        self.facility.replace_schedule(schedule.id, self._desired_reservations(schedule))

    def _commit_with_reservations(self, schedule: ScheduleEntry, previous: list[dict] | None = None) -> None:
        # The Facility authoritative conflict check must precede the schedule commit.
        # All failures must roll back the uncommitted local schedule transaction.
        synced = False
        try:
            self._sync_reservations(schedule)
            synced = True
            self.db.commit()
        except Exception:
            self.db.rollback()
            # A failed local commit can leave reservations held in Facility.
            # Restore the previous state when possible (no distributed atomicity).
            if synced and previous is not None:
                try:
                    self.facility.replace_schedule(schedule.id, previous)
                except Exception:
                    pass
            raise

    def _require_teacher_assignment(
        self, principal: Principal, teacher_user_id: uuid.UUID, section_id: uuid.UUID
    ) -> None:
        if principal.can_manage_schedules:
            if not self.academic.validate_teacher_assignment(
                teacher_user_id, section_id, principal.raw_token
            ):
                raise ConflictError("Teacher is not assigned to this section")
            return
        if not principal.has_role("teacher") or principal.user_id != teacher_user_id:
            raise ForbiddenError("Teachers may only schedule their own assigned sections")
        if not self.academic.validate_teacher_assignment(
            teacher_user_id, section_id, principal.raw_token
        ):
            raise ForbiddenError("Teacher is not assigned to this section")

    def _validate_conflicts(
        self,
        *,
        section_id: uuid.UUID,
        teacher_user_id: uuid.UUID,
        room_id: uuid.UUID | None,
        weekday: int,
        starts_at,
        ends_at,
        effective_from,
        effective_to,
        exclude_schedule_id: uuid.UUID | None = None,
    ) -> None:
        self.repo.acquire_conflict_locks(
            section_id=section_id,
            teacher_user_id=teacher_user_id,
            room_id=room_id,
            weekday=weekday,
        )
        conflicts = self.repo.find_recurring_conflicts(
            section_id=section_id,
            teacher_user_id=teacher_user_id,
            room_id=room_id,
            weekday=weekday,
            starts_at=starts_at,
            ends_at=ends_at,
            effective_from=effective_from,
            effective_to=effective_to,
            exclude_schedule_id=exclude_schedule_id,
        )
        if conflicts:
            raise ConflictError(
                "Schedule conflicts with an existing section, teacher, or room allocation"
            )

    def create_schedule(self, payload: ScheduleCreate, principal: Principal) -> ScheduleEntry:
        section = self.academic.get_section(payload.section_id, principal.raw_token)
        teacher_user_id = payload.teacher_user_id or principal.user_id
        self._require_teacher_assignment(principal, teacher_user_id, payload.section_id)
        if payload.publish:
            self._validate_conflicts(
            section_id=payload.section_id,
            teacher_user_id=teacher_user_id,
            room_id=payload.room_id,
            weekday=payload.weekday,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
        )
        schedule = ScheduleEntry(
            section_id=payload.section_id,
            course_id=section.course_id,
            semester_id=section.semester_id,
            teacher_user_id=teacher_user_id,
            room_id=payload.room_id,
            weekday=payload.weekday,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            timezone_name=payload.timezone_name or settings.DEFAULT_TIMEZONE,
            created_by_user_id=principal.user_id,
            status="ACTIVE" if payload.publish else "DRAFT",
        )
        try:
            self.repo.add_schedule(schedule)
            self.db.flush()
            self.repo.add_audit(
                ScheduleAudit(
                    schedule_id=schedule.id,
                    action="schedule.created" if payload.publish else "schedule.drafted",
                    actor_user_id=principal.user_id,
                    before_data=None,
                    after_data=_schedule_dict(schedule),
                )
            )
            self.outbox.add_event(
                OutboxEvent(
                    aggregate_type="schedule",
                    aggregate_id=schedule.id,
                    event_type="schedule.created" if payload.publish else "schedule.drafted",
                    payload=_schedule_dict(schedule),
                )
            )
            if payload.publish:
                self._commit_with_reservations(schedule, [])
            else:
                self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                "Schedule could not be created because of a concurrent conflict"
            ) from exc
        self.db.refresh(schedule)
        return schedule

    def update_schedule(
        self, schedule_id: uuid.UUID, payload: ScheduleUpdate, principal: Principal
    ) -> ScheduleEntry:
        schedule = self.repo.get_schedule(schedule_id, for_update=True)
        if not schedule:
            raise NotFoundError("Schedule not found")
        if schedule.status not in {"ACTIVE", "DRAFT"}:
            raise ConflictError("Only draft or active schedules can be updated")
        if not principal.can_manage_schedules and schedule.teacher_user_id != principal.user_id:
            raise ForbiddenError("Teacher does not own this schedule")

        before = _schedule_dict(schedule)
        previous_reservations = self._desired_reservations(schedule) if schedule.status == "ACTIVE" else []
        teacher_user_id = payload.teacher_user_id or schedule.teacher_user_id
        weekday = payload.weekday if payload.weekday is not None else schedule.weekday
        starts_at = payload.starts_at or schedule.starts_at
        ends_at = payload.ends_at or schedule.ends_at
        effective_from = payload.effective_from or schedule.effective_from
        effective_to = payload.effective_to or schedule.effective_to
        room_id = payload.room_id if "room_id" in payload.model_fields_set else schedule.room_id

        if starts_at >= ends_at:
            raise ConflictError("starts_at must be earlier than ends_at")
        if effective_from > effective_to:
            raise ConflictError("effective_from must be on or before effective_to")
        self._require_teacher_assignment(principal, teacher_user_id, schedule.section_id)
        self._validate_conflicts(
            section_id=schedule.section_id,
            teacher_user_id=teacher_user_id,
            room_id=room_id,
            weekday=weekday,
            starts_at=starts_at,
            ends_at=ends_at,
            effective_from=effective_from,
            effective_to=effective_to,
            exclude_schedule_id=schedule.id,
        )

        schedule.teacher_user_id = teacher_user_id
        schedule.weekday = weekday
        schedule.starts_at = starts_at
        schedule.ends_at = ends_at
        schedule.effective_from = effective_from
        schedule.effective_to = effective_to
        schedule.room_id = room_id
        if payload.timezone_name is not None:
            schedule.timezone_name = payload.timezone_name
        schedule.version += 1
        after = _schedule_dict(schedule)
        self.repo.add_audit(
            ScheduleAudit(
                schedule_id=schedule.id,
                action="schedule.updated",
                actor_user_id=principal.user_id,
                before_data=before,
                after_data=after,
            )
        )
        self.outbox.add_event(
            OutboxEvent(
                aggregate_type="schedule",
                aggregate_id=schedule.id,
                event_type="schedule.updated",
                payload=after,
            )
        )
        if schedule.status == "ACTIVE":
            self._commit_with_reservations(schedule, previous_reservations)
        else:
            self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def publish_schedule(self, schedule_id: uuid.UUID, principal: Principal) -> ScheduleEntry:
        if not principal.can_manage_schedules:
            raise ForbiddenError("Administrator role required to publish schedules")
        schedule = self.repo.get_schedule(schedule_id, for_update=True)
        if schedule is None:
            raise NotFoundError("Schedule not found")
        if schedule.status == "ACTIVE":
            return schedule  # Repeat publishes do not double-emit.
        if schedule.status != "DRAFT":
            raise ConflictError("Only draft schedules can be published")
        self._require_teacher_assignment(principal, schedule.teacher_user_id, schedule.section_id)
        self._validate_conflicts(
            section_id=schedule.section_id,
            teacher_user_id=schedule.teacher_user_id,
            room_id=schedule.room_id,
            weekday=schedule.weekday,
            starts_at=schedule.starts_at,
            ends_at=schedule.ends_at,
            effective_from=schedule.effective_from,
            effective_to=schedule.effective_to,
            exclude_schedule_id=schedule.id,
        )
        before = _schedule_dict(schedule)
        schedule.status = "ACTIVE"
        schedule.version += 1
        after = _schedule_dict(schedule)
        self.repo.add_audit(ScheduleAudit(
            schedule_id=schedule.id, action="schedule.published",
            actor_user_id=principal.user_id, before_data=before, after_data=after,
        ))
        self.outbox.add_event(OutboxEvent(
            aggregate_type="schedule", aggregate_id=schedule.id,
            event_type="schedule.published", payload=after,
        ))
        self._commit_with_reservations(schedule, [])
        self.db.refresh(schedule)
        return schedule

    def cancel_schedule(self, schedule_id: uuid.UUID, reason: str | None, principal: Principal):
        schedule = self.repo.get_schedule(schedule_id, for_update=True)
        if not schedule:
            raise NotFoundError("Schedule not found")
        if not principal.can_manage_schedules and schedule.teacher_user_id != principal.user_id:
            raise ForbiddenError("Teacher does not own this schedule")
        if schedule.status == "CANCELLED":
            return schedule
        before = _schedule_dict(schedule)
        previous_reservations = self._desired_reservations(schedule)
        schedule.status = "CANCELLED"
        schedule.version += 1
        after = _schedule_dict(schedule)
        self.repo.add_audit(
            ScheduleAudit(
                schedule_id=schedule.id,
                action="schedule.cancelled",
                actor_user_id=principal.user_id,
                before_data=before,
                after_data={**after, "reason": reason},
            )
        )
        self.outbox.add_event(
            OutboxEvent(
                aggregate_type="schedule",
                aggregate_id=schedule.id,
                event_type="schedule.cancelled",
                payload={**after, "reason": reason},
            )
        )
        self._commit_with_reservations(schedule, previous_reservations)
        self.db.refresh(schedule)
        return schedule

    def set_override(
        self, schedule_id: uuid.UUID, payload: OverrideCreate, principal: Principal
    ) -> ScheduleOverride:
        schedule = self.repo.get_schedule(schedule_id, for_update=True)
        if not schedule:
            raise NotFoundError("Schedule not found")
        if schedule.status != "ACTIVE":
            raise ConflictError("Cannot override a cancelled schedule")
        if not principal.can_manage_schedules and schedule.teacher_user_id != principal.user_id:
            raise ForbiddenError("Teacher does not own this schedule")
        if not (schedule.effective_from <= payload.occurrence_date <= schedule.effective_to):
            raise ConflictError("Occurrence date is outside the schedule effective range")
        if payload.occurrence_date.weekday() != schedule.weekday:
            raise ConflictError("Occurrence date does not match schedule weekday")

        previous_reservations = self._desired_reservations(schedule)
        override = self.repo.get_override(schedule_id, payload.occurrence_date)
        if override is None:
            override = ScheduleOverride(
                schedule_id=schedule.id,
                occurrence_date=payload.occurrence_date,
                kind=payload.kind,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                room_id=payload.room_id,
                reason=payload.reason,
                created_by_user_id=principal.user_id,
            )
            self.repo.add_override(override)
        else:
            override.kind = payload.kind
            override.starts_at = payload.starts_at
            override.ends_at = payload.ends_at
            override.room_id = payload.room_id
            override.reason = payload.reason
            override.created_by_user_id = principal.user_id

        if payload.kind == "RESCHEDULED":
            self.repo.acquire_conflict_locks(
                section_id=schedule.section_id,
                teacher_user_id=schedule.teacher_user_id,
                room_id=payload.room_id if payload.room_id is not None else schedule.room_id,
                weekday=payload.occurrence_date.weekday(),
            )
            self._assert_occurrence_conflict_free(
                schedule=schedule,
                occurrence_date=payload.occurrence_date,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                room_id=payload.room_id if payload.room_id is not None else schedule.room_id,
            )

        self.repo.add_audit(
            ScheduleAudit(
                schedule_id=schedule.id,
                action="schedule.occurrence_overridden",
                actor_user_id=principal.user_id,
                before_data=None,
                after_data={
                    "occurrence_date": payload.occurrence_date.isoformat(),
                    "kind": payload.kind,
                    "starts_at": payload.starts_at.isoformat() if payload.starts_at else None,
                    "ends_at": payload.ends_at.isoformat() if payload.ends_at else None,
                    "room_id": str(payload.room_id) if payload.room_id else None,
                    "reason": payload.reason,
                },
            )
        )
        self.outbox.add_event(
            OutboxEvent(
                aggregate_type="schedule",
                aggregate_id=schedule.id,
                event_type="schedule.occurrence_changed",
                payload={
                    "schedule_id": str(schedule.id),
                    "section_id": str(schedule.section_id),
                    "teacher_user_id": str(schedule.teacher_user_id),
                    "occurrence_date": payload.occurrence_date.isoformat(),
                    "kind": payload.kind,
                },
            )
        )
        self.db.flush()
        self.db.expire(schedule, ["overrides"])
        self._commit_with_reservations(schedule, previous_reservations)
        self.db.refresh(override)
        return override

    def _assert_occurrence_conflict_free(
        self, *, schedule: ScheduleEntry, occurrence_date: date, starts_at, ends_at, room_id
    ) -> None:
        candidates = self.repo.list_active_overlapping_range(
            start_date=occurrence_date, end_date=occurrence_date
        )
        for candidate in candidates:
            if candidate.id == schedule.id or candidate.weekday != occurrence_date.weekday():
                continue
            override = next(
                (o for o in candidate.overrides if o.occurrence_date == occurrence_date), None
            )
            if override and override.kind == "CANCELLED":
                continue
            candidate_start = (
                override.starts_at
                if override and override.kind == "RESCHEDULED"
                else candidate.starts_at
            )
            candidate_end = (
                override.ends_at
                if override and override.kind == "RESCHEDULED"
                else candidate.ends_at
            )
            candidate_room = (
                override.room_id
                if override and override.kind == "RESCHEDULED" and override.room_id is not None
                else candidate.room_id
            )
            overlaps = candidate_start < ends_at and candidate_end > starts_at
            same_resource = (
                candidate.section_id == schedule.section_id
                or candidate.teacher_user_id == schedule.teacher_user_id
                or (room_id is not None and candidate_room == room_id)
            )
            if overlaps and same_resource:
                raise ConflictError("Rescheduled occurrence conflicts with another occurrence")

    def generate_occurrences(
        self,
        *,
        start_date: date,
        end_date: date,
        principal: Principal,
        section_id: uuid.UUID | None = None,
        teacher_user_id: uuid.UUID | None = None,
        room_id: uuid.UUID | None = None,
        me: bool = False,
    ) -> list[dict]:
        if end_date < start_date:
            raise ConflictError("end_date must not be before start_date")
        if (end_date - start_date).days > settings.MAX_TIMETABLE_RANGE_DAYS:
            raise ConflictError("Requested timetable range is too large")

        section_ids = None
        teacher_filter = teacher_user_id
        if me:
            if principal.has_role("student"):
                section_ids = self.academic.list_student_section_ids(
                    principal.user_id, principal.raw_token
                )
            elif principal.has_role("teacher") and not principal.can_manage_schedules:
                teacher_filter = principal.user_id
        elif section_id:
            if principal.has_role("student") and not self.academic.validate_student_enrollment(
                principal.user_id, section_id, principal.raw_token
            ):
                raise ForbiddenError("Student is not enrolled in this section")
            if principal.has_role("teacher") and not principal.can_manage_schedules:
                if not self.academic.validate_teacher_assignment(
                    principal.user_id, section_id, principal.raw_token
                ):
                    raise ForbiddenError("Teacher is not assigned to this section")
            section_ids = [section_id]
        elif teacher_filter and not principal.can_manage_schedules:
            if principal.user_id != teacher_filter:
                raise ForbiddenError("Teachers may only view their own timetable")

        schedules = self.repo.list_active_overlapping_range(
            start_date=start_date,
            end_date=end_date,
            section_ids=section_ids,
            teacher_user_id=teacher_filter,
            room_id=room_id,
        )
        occurrences: list[dict] = []
        for schedule in schedules:
            first = max(start_date, schedule.effective_from)
            last = min(end_date, schedule.effective_to)
            cursor = first
            while cursor.weekday() != schedule.weekday:
                cursor += timedelta(days=1)
            overrides = {item.occurrence_date: item for item in schedule.overrides}
            while cursor <= last:
                override = overrides.get(cursor)
                if not override or override.kind != "CANCELLED":
                    starts_at = (
                        override.starts_at
                        if override and override.kind == "RESCHEDULED"
                        else schedule.starts_at
                    )
                    ends_at = (
                        override.ends_at
                        if override and override.kind == "RESCHEDULED"
                        else schedule.ends_at
                    )
                    override_room = (
                        override.room_id
                        if override
                        and override.kind == "RESCHEDULED"
                        and override.room_id is not None
                        else schedule.room_id
                    )
                    occurrence_id = uuid.uuid5(schedule.id, cursor.isoformat())
                    occurrences.append(
                        {
                            "occurrence_id": occurrence_id,
                            "schedule_id": schedule.id,
                            "occurrence_date": cursor,
                            "section_id": schedule.section_id,
                            "course_id": schedule.course_id,
                            "semester_id": schedule.semester_id,
                            "teacher_user_id": schedule.teacher_user_id,
                            "room_id": override_room,
                            "starts_at": starts_at,
                            "ends_at": ends_at,
                            "timezone_name": schedule.timezone_name,
                            "source": "override" if override else "recurring",
                        }
                    )
                cursor += timedelta(days=7)
        occurrences.sort(
            key=lambda item: (item["occurrence_date"], item["starts_at"], str(item["schedule_id"]))
        )
        return occurrences
