from __future__ import annotations

import csv
import io
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.domain.entities.models import AnalyticsEvent, ExportAudit, ReportSnapshot
from app.repositories.reporting_repository import ReportingRepository
from app.schemas.events import InternalEventIn
from app.services.event_projector import EventProjector


class ReportingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ReportingRepository(db)
        self.projector = EventProjector(db)

    def ingest_event(self, data: InternalEventIn) -> str:
        if self.repo.event_by_external_id(data.event_id):
            return "duplicate"

        event = AnalyticsEvent(
            event_id=data.event_id,
            source_service=data.source_service,
            event_type=data.event_type,
            payload=data.payload,
            occurred_at=data.effective_occurred_at(),
            processed=False,
        )
        self.db.add(event)
        try:
            self.db.flush()
            self.projector.project(event)
            event.processed = True
            self.db.commit()
            return "processed"
        except IntegrityError:
            self.db.rollback()
            if self.repo.event_by_external_id(data.event_id):
                return "duplicate"
            raise

    def overview(self) -> dict:
        return self.repo.overview()

    def create_snapshot(self, report_type: str, filters: dict, actor_id: uuid.UUID):
        if report_type == "overview" and filters:
            raise DomainError("Overview has no row filters; choose a detailed report")
        if report_type == "overview":
            payload = self.overview()
        elif report_type == "attendance":
            payload = {"rows": self._attendance_dicts()}
        elif report_type == "assessment":
            payload = {"rows": self._assessment_dicts()}
        elif report_type == "facility":
            payload = {"rows": self._facility_dicts()}
        elif report_type == "notification":
            payload = {"rows": self._notification_dicts()}
        elif report_type == "schedule":
            payload = {"rows": self._schedule_dicts()}
        elif report_type == "enrollment":
            payload = {"rows": self._enrollment_dicts()}
        else:
            raise DomainError("Unsupported report type")

        if filters:
            fields = {
                "attendance": {
                    "attendance_session_id",
                    "student_user_id",
                    "section_id",
                    "course_id",
                    "status",
                    "session_date",
                },
                "assessment": {
                    "attempt_id",
                    "student_user_id",
                    "quiz_id",
                    "section_id",
                    "course_id",
                    "percent",
                    "passed",
                    "graded_at",
                },
                "facility": {
                    "booking_id",
                    "facility_id",
                    "requested_by_user_id",
                    "status",
                    "starts_at",
                    "ends_at",
                },
                "notification": {
                    "delivery_id",
                    "notification_id",
                    "channel",
                    "status",
                    "occurred_at",
                },
                "schedule": {
                    "source_event_id",
                    "section_id",
                    "teacher_user_id",
                    "room_id",
                    "activity_type",
                    "occurred_at",
                },
                "enrollment": {"student_user_id", "section_id", "program_id", "status"},
            }[report_type]
            if set(filters) - fields or any(
                isinstance(value, (dict, list)) for value in filters.values()
            ):
                raise DomainError("Filters must be scalar equality values for report columns")
            payload["rows"] = [
                row
                for row in payload["rows"]
                if all(str(row[key]) == str(value) for key, value in filters.items())
            ]

        snapshot = ReportSnapshot(
            report_type=report_type,
            filters=filters,
            payload=payload,
            generated_by_user_id=actor_id,
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def export_csv(self, report_type: str, actor_id: uuid.UUID) -> tuple[str, int]:
        row_sets = {
            "attendance": self._attendance_dicts,
            "assessment": self._assessment_dicts,
            "facility": self._facility_dicts,
            "notification": self._notification_dicts,
            "schedule": self._schedule_dicts,
            "enrollment": self._enrollment_dicts,
        }
        if report_type not in row_sets:
            raise DomainError("Unsupported report type")
        rows = row_sets[report_type]()
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        self.db.add(
            ExportAudit(
                report_type=report_type,
                format="csv",
                generated_by_user_id=actor_id,
                row_count=len(rows),
            )
        )
        self.db.commit()
        return output.getvalue(), len(rows)

    def _attendance_dicts(self):
        return [
            {
                "attendance_session_id": str(r.attendance_session_id),
                "student_user_id": str(r.student_user_id),
                "section_id": str(r.section_id),
                "course_id": str(r.course_id) if r.course_id else "",
                "status": r.status,
                "session_date": r.session_date.isoformat() if r.session_date else "",
            }
            for r in self.repo.attendance_rows()
        ]

    def _assessment_dicts(self):
        return [
            {
                "attempt_id": str(r.attempt_id),
                "student_user_id": str(r.student_user_id),
                "quiz_id": str(r.quiz_id) if r.quiz_id else "",
                "section_id": str(r.section_id) if r.section_id else "",
                "course_id": str(r.course_id) if r.course_id else "",
                "percent": r.percent,
                "passed": r.passed,
                "graded_at": r.graded_at.isoformat(),
            }
            for r in self.repo.assessment_rows()
        ]

    def _facility_dicts(self):
        return [
            {
                "booking_id": str(r.booking_id),
                "facility_id": str(r.facility_id),
                "requested_by_user_id": str(r.requested_by_user_id)
                if r.requested_by_user_id
                else "",
                "status": r.status,
                "starts_at": r.starts_at.isoformat() if r.starts_at else "",
                "ends_at": r.ends_at.isoformat() if r.ends_at else "",
            }
            for r in self.repo.facility_rows()
        ]

    def _notification_dicts(self):
        return [
            {
                "delivery_id": r.delivery_id,
                "notification_id": str(r.notification_id) if r.notification_id else "",
                "channel": r.channel,
                "status": r.status,
                "occurred_at": r.occurred_at.isoformat(),
            }
            for r in self.repo.notification_rows()
        ]

    def _schedule_dicts(self):
        return [
            {
                "source_event_id": str(r.source_event_id),
                "section_id": str(r.section_id) if r.section_id else "",
                "teacher_user_id": str(r.teacher_user_id) if r.teacher_user_id else "",
                "room_id": str(r.room_id) if r.room_id else "",
                "activity_type": r.activity_type,
                "occurred_at": r.occurred_at.isoformat(),
            }
            for r in self.repo.schedule_rows()
        ]

    def _enrollment_dicts(self):
        return [
            {
                "student_user_id": str(r.student_user_id),
                "section_id": str(r.section_id),
                "program_id": str(r.program_id) if r.program_id else "",
                "status": r.status,
            }
            for r in self.repo.enrollment_rows()
        ]
