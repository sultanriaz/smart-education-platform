from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.domain.entities.models import (
    AssessmentProjection,
    AttendanceProjection,
    EnrollmentProjection,
    FacilityBookingProjection,
    NotificationDeliveryProjection,
    ScheduleActivityProjection,
)
from app.repositories.reporting_repository import ReportingRepository


def _uuid(value):
    if value in (None, ""):
        return None
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


def _datetime(value, fallback):
    if not value:
        return fallback
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


class EventProjector:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportingRepository(db)

    def project(self, event):
        t = event.event_type
        p = event.payload or {}

        if t in {"attendance.recorded", "attendance.updated"}:
            self._attendance(p)
        elif t == "assessment.attempt_graded":
            self._assessment(p, event.occurred_at)
        elif t.startswith("facility.booking_"):
            self._facility(p, t)
        elif t in {
            "notification.sent",
            "notification.delivered",
            "notification.failed",
            "notification.delivery_updated",
        }:
            self._notification(p, t, event.occurred_at)
        elif t.startswith("schedule."):
            self._schedule(event)
        elif t in {
            "academic.enrollment_created",
            "academic.enrollment_activated",
            "academic.enrollment_dropped",
            "academic.enrollment_cancelled",
        }:
            self._enrollment(p, t)

    def _attendance(self, payload):
        session_id = _uuid(payload.get("attendance_session_id") or payload.get("session_id"))
        student_id = _uuid(payload.get("student_user_id"))
        section_id = _uuid(payload.get("section_id"))
        if not all([session_id, student_id, section_id]):
            return

        row = self.repo.attendance_by_logical_key(session_id, student_id)
        if row is None:
            row = AttendanceProjection(
                attendance_session_id=session_id,
                student_user_id=student_id,
                section_id=section_id,
                course_id=_uuid(payload.get("course_id")),
                status=str(payload.get("status", "ABSENT")).upper(),
                session_date=_date(payload.get("session_date")),
            )
            self.db.add(row)
        else:
            row.status = str(payload.get("status", row.status)).upper()
            row.section_id = section_id
            row.course_id = _uuid(payload.get("course_id")) or row.course_id
            row.session_date = _date(payload.get("session_date")) or row.session_date

    def _assessment(self, payload, occurred_at):
        attempt_id = _uuid(payload.get("attempt_id"))
        student_id = _uuid(payload.get("student_user_id"))
        if not attempt_id or not student_id:
            return
        row = self.repo.assessment_by_attempt(attempt_id)
        values = {
            "student_user_id": student_id,
            "quiz_id": _uuid(payload.get("quiz_id")),
            "section_id": _uuid(payload.get("section_id")),
            "course_id": _uuid(payload.get("course_id")),
            "percent": float(payload.get("percent", 0)),
            "passed": bool(payload.get("passed", False)),
            "graded_at": _datetime(payload.get("graded_at"), occurred_at),
        }
        if row is None:
            row = AssessmentProjection(attempt_id=attempt_id, **values)
            self.db.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)

    def _facility(self, payload, event_type):
        booking_id = _uuid(payload.get("booking_id"))
        facility_id = _uuid(payload.get("facility_id"))
        if not booking_id or not facility_id:
            return

        mapping = {
            "facility.booking_requested": "PENDING",
            "facility.booking_approved": "APPROVED",
            "facility.booking_rejected": "REJECTED",
            "facility.booking_cancelled": "CANCELLED",
        }
        status = str(payload.get("status") or mapping.get(event_type) or "UNKNOWN").upper()
        row = self.repo.facility_by_booking(booking_id)
        values = {
            "facility_id": facility_id,
            "requested_by_user_id": _uuid(
                payload.get("requested_by_user_id")
                or payload.get("requester_user_id")
                or payload.get("user_id")
            ),
            "status": status,
            "starts_at": _datetime(payload.get("starts_at"), None)
            if payload.get("starts_at")
            else None,
            "ends_at": _datetime(payload.get("ends_at"), None) if payload.get("ends_at") else None,
        }
        if row is None:
            row = FacilityBookingProjection(booking_id=booking_id, **values)
            self.db.add(row)
        else:
            for key, value in values.items():
                if value is not None or key == "status":
                    setattr(row, key, value)

    def _notification(self, payload, event_type, occurred_at):
        delivery_id = str(
            payload.get("delivery_id")
            or payload.get("attempt_id")
            or payload.get("notification_id")
            or ""
        )
        if not delivery_id:
            return
        row = self.repo.delivery_by_id(delivery_id)
        status = str(payload.get("status") or event_type.split(".")[-1]).upper()
        values = {
            "notification_id": _uuid(payload.get("notification_id")),
            "channel": str(payload.get("channel", "IN_APP")).upper(),
            "status": status,
            "occurred_at": _datetime(payload.get("occurred_at"), occurred_at),
        }
        if row is None:
            row = NotificationDeliveryProjection(delivery_id=delivery_id, **values)
            self.db.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)

    def _schedule(self, event):
        payload = event.payload or {}
        if (
            self.db.query(ScheduleActivityProjection)
            .filter(ScheduleActivityProjection.source_event_id == event.event_id)
            .first()
        ):
            return
        self.db.add(
            ScheduleActivityProjection(
                source_event_id=event.event_id,
                section_id=_uuid(payload.get("section_id")),
                teacher_user_id=_uuid(payload.get("teacher_user_id")),
                room_id=_uuid(payload.get("room_id") or payload.get("facility_id")),
                activity_type=event.event_type,
                occurred_at=event.occurred_at,
            )
        )

    def _enrollment(self, payload, event_type):
        student_id = _uuid(payload.get("student_user_id"))
        section_id = _uuid(payload.get("section_id"))
        if not student_id or not section_id:
            return
        row = self.repo.enrollment(student_id, section_id)
        default_status = (
            "ACTIVE"
            if event_type in {"academic.enrollment_created", "academic.enrollment_activated"}
            else "DROPPED"
        )
        if row is None:
            row = EnrollmentProjection(
                student_user_id=student_id,
                section_id=section_id,
                program_id=_uuid(payload.get("program_id")),
                status=str(payload.get("status") or default_status).upper(),
            )
            self.db.add(row)
        else:
            row.program_id = _uuid(payload.get("program_id")) or row.program_id
            row.status = str(payload.get("status") or default_status).upper()
