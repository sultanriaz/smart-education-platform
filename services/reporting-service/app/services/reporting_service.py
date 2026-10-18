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

    def academic_report(
        self, *, student_user_id: uuid.UUID | None = None,
        section_id: uuid.UUID | None = None,
        course_id: uuid.UUID | None = None,
    ) -> dict:
        """Owner-fed projection view. Caller MUST enforce audience before invocation.

        Never fetch an unscoped report from a Student/Teacher endpoint; this
        function is an aggregation layer, not an authorization policy.
        """
        if not any([student_user_id, section_id, course_id]):
            raise DomainError("Academic report requires a student, section or course scope")
        attendance = self._attendance_dicts()
        assessment = self._assessment_dicts()
        enrollments = self._enrollment_dicts()

        def allowed(row):
            if student_user_id is not None and row.get("student_user_id") != str(student_user_id):
                return False
            if section_id is not None and row.get("section_id") != str(section_id):
                return False
            if course_id is not None and row.get("course_id") != str(course_id):
                return False
            return True

        attendance = [r for r in attendance if allowed(r)]
        assessment = [r for r in assessment if allowed(r)]
        # Enrollment projection doesn't carry a course_id. Do not count
        # program members as course members, as that would inflate reports.
        enrollments = [r for r in enrollments if allowed(r)] if course_id is None else []
        marked = [r for r in attendance if r["status"] in {"PRESENT", "ABSENT", "LATE"}]
        present = sum(r["status"] in {"PRESENT", "LATE"} for r in marked)
        grades = [r["percent"] for r in assessment if r["percent"] is not None]
        return {
            "scope": {
                "student_user_id": str(student_user_id) if student_user_id else None,
                "section_id": str(section_id) if section_id else None,
                "course_id": str(course_id) if course_id else None,
            },
            "source": "asynchronous_reporting_projections",
            "active_enrollments": sum(row["status"] == "ACTIVE" for row in enrollments),
            "attendance_marked": len(marked),
            "attendance_percent": round(present * 100 / len(marked), 2) if marked else None,
            "graded_attempts": len(grades),
            "assessment_average_percent": round(sum(grades) / len(grades), 2) if grades else None,
            "attendance": attendance,
            "assessment": assessment,
            "enrollments": enrollments,
        }

    def overview(self) -> dict:
        return self.repo.overview()

    REPORT_FIELDS = {
        "attendance": {"attendance_session_id", "student_user_id", "section_id", "course_id", "status", "session_date"},
        "assessment": {"attempt_id", "student_user_id", "quiz_id", "section_id", "course_id", "percent", "passed", "graded_at"},
        "facility": {"booking_id", "facility_id", "requested_by_user_id", "status", "starts_at", "ends_at"},
        "notification": {"delivery_id", "notification_id", "channel", "status", "occurred_at"},
        "schedule": {"source_event_id", "section_id", "teacher_user_id", "room_id", "activity_type", "occurred_at"},
        "enrollment": {"student_user_id", "section_id", "program_id", "status"},
    }

    def report_rows(self, report_type: str, filters: dict | None = None):
        row_sets = {"attendance": self._attendance_dicts, "assessment": self._assessment_dicts, "facility": self._facility_dicts, "notification": self._notification_dicts, "schedule": self._schedule_dicts, "enrollment": self._enrollment_dicts}
        if report_type not in row_sets:
            raise DomainError("Unsupported report type")
        filters = filters or {}
        if set(filters) - self.REPORT_FIELDS[report_type] or any(isinstance(value, (dict,list)) for value in filters.values()):
            raise DomainError("Filters must be scalar equality values for report columns")
        return [row for row in row_sets[report_type]() if all(str(row[field]) == str(value) for field, value in filters.items())]

    @staticmethod
    def csv_cell(value):
        if not isinstance(value, str):
            return value
        if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) or value.lstrip(" ").startswith(("=", "+", "-", "@")):
            return "'" + value
        return value

    def report_page(self, report_type: str, filters: dict | None = None, *, limit: int = 50, offset: int = 0):
        rows = self.report_rows(report_type, filters)
        return {"rows": rows[offset:offset+limit], "total": len(rows), "limit": limit, "offset": offset, "filters": filters or {}, "source": "reporting_projections"}

    def create_snapshot(self, report_type: str, filters: dict, actor_id: uuid.UUID):
        if report_type == "overview":
            if filters:
                raise DomainError("Overview has no row filters; choose a detailed report")
            payload = self.overview()
        else:
            payload = {"rows": self.report_rows(report_type, filters)}

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

    def export_csv(self, report_type: str, actor_id: uuid.UUID, filters: dict | None = None) -> tuple[str, int]:
        rows = self.report_rows(report_type, filters)
        if len(rows) > 10000:
            raise DomainError("Export too large; narrow the filters")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=sorted(self.REPORT_FIELDS[report_type]), lineterminator="\r\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: self.csv_cell(value) for key, value in row.items()})
        self.db.add(ExportAudit(report_type=report_type, format="csv", generated_by_user_id=actor_id, row_count=len(rows)))
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
