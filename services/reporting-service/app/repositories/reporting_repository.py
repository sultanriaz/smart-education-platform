from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.models import (
    AnalyticsEvent,
    AssessmentProjection,
    AttendanceProjection,
    EnrollmentProjection,
    FacilityBookingProjection,
    NotificationDeliveryProjection,
    ReportSnapshot,
    ScheduleActivityProjection,
)


class ReportingRepository:
    def __init__(self, db: Session):
        self.db = db

    def event_by_external_id(self, event_id: uuid.UUID):
        return self.db.scalar(select(AnalyticsEvent).where(AnalyticsEvent.event_id == event_id))

    def attendance_by_logical_key(self, session_id: uuid.UUID, student_id: uuid.UUID):
        return self.db.scalar(
            select(AttendanceProjection).where(
                AttendanceProjection.attendance_session_id == session_id,
                AttendanceProjection.student_user_id == student_id,
            )
        )

    def assessment_by_attempt(self, attempt_id: uuid.UUID):
        return self.db.scalar(
            select(AssessmentProjection).where(AssessmentProjection.attempt_id == attempt_id)
        )

    def facility_by_booking(self, booking_id: uuid.UUID):
        return self.db.scalar(
            select(FacilityBookingProjection).where(
                FacilityBookingProjection.booking_id == booking_id
            )
        )

    def delivery_by_id(self, delivery_id: str):
        return self.db.scalar(
            select(NotificationDeliveryProjection).where(
                NotificationDeliveryProjection.delivery_id == delivery_id
            )
        )

    def enrollment(self, student_id: uuid.UUID, section_id: uuid.UUID):
        return self.db.scalar(
            select(EnrollmentProjection).where(
                EnrollmentProjection.student_user_id == student_id,
                EnrollmentProjection.section_id == section_id,
            )
        )

    def overview(self) -> dict:
        active_enrollments = (
            self.db.scalar(
                select(func.count(EnrollmentProjection.id)).where(
                    EnrollmentProjection.status == "ACTIVE"
                )
            )
            or 0
        )

        attendance_records = self.db.scalar(select(func.count(AttendanceProjection.id))) or 0
        present_like = (
            self.db.scalar(
                select(func.count(AttendanceProjection.id)).where(
                    AttendanceProjection.status.in_(["PRESENT", "LATE"])
                )
            )
            or 0
        )
        considered = (
            self.db.scalar(
                select(func.count(AttendanceProjection.id)).where(
                    AttendanceProjection.status.in_(["PRESENT", "LATE", "ABSENT"])
                )
            )
            or 0
        )

        graded_attempts = self.db.scalar(select(func.count(AssessmentProjection.id))) or 0
        assessment_avg = self.db.scalar(select(func.avg(AssessmentProjection.percent)))
        assessment_passed = (
            self.db.scalar(
                select(func.count(AssessmentProjection.id)).where(
                    AssessmentProjection.passed.is_(True)
                )
            )
            or 0
        )

        facility_bookings = self.db.scalar(select(func.count(FacilityBookingProjection.id))) or 0
        approved = (
            self.db.scalar(
                select(func.count(FacilityBookingProjection.id)).where(
                    FacilityBookingProjection.status == "APPROVED"
                )
            )
            or 0
        )

        deliveries = self.db.scalar(select(func.count(NotificationDeliveryProjection.id))) or 0
        successful_deliveries = (
            self.db.scalar(
                select(func.count(NotificationDeliveryProjection.id)).where(
                    NotificationDeliveryProjection.status.in_(["DELIVERED", "SENT"])
                )
            )
            or 0
        )

        schedule_changes = self.db.scalar(select(func.count(ScheduleActivityProjection.id))) or 0

        return {
            "active_enrollments": int(active_enrollments),
            "attendance_records": int(attendance_records),
            "attendance_percentage": round((present_like / considered * 100), 2)
            if considered
            else None,
            "graded_attempts": int(graded_attempts),
            "assessment_average_percent": round(float(assessment_avg), 2)
            if assessment_avg is not None
            else None,
            "assessment_pass_rate": round((assessment_passed / graded_attempts * 100), 2)
            if graded_attempts
            else None,
            "facility_bookings": int(facility_bookings),
            "approved_facility_bookings": int(approved),
            "notification_deliveries": int(deliveries),
            "notification_success_rate": round(successful_deliveries / deliveries * 100, 2)
            if deliveries
            else None,
            "schedule_changes": int(schedule_changes),
        }

    def attendance_rows(self):
        return list(
            self.db.scalars(
                select(AttendanceProjection).order_by(
                    AttendanceProjection.session_date.desc().nullslast()
                )
            ).all()
        )

    def assessment_rows(self):
        return list(
            self.db.scalars(
                select(AssessmentProjection).order_by(AssessmentProjection.graded_at.desc())
            ).all()
        )

    def facility_rows(self):
        return list(
            self.db.scalars(
                select(FacilityBookingProjection).order_by(
                    FacilityBookingProjection.updated_at.desc()
                )
            ).all()
        )

    def notification_rows(self):
        return list(
            self.db.scalars(
                select(NotificationDeliveryProjection).order_by(
                    NotificationDeliveryProjection.occurred_at.desc()
                )
            ).all()
        )

    def schedule_rows(self):
        return list(
            self.db.scalars(
                select(ScheduleActivityProjection).order_by(
                    ScheduleActivityProjection.occurred_at.desc()
                )
            ).all()
        )

    def enrollment_rows(self):
        return list(
            self.db.scalars(
                select(EnrollmentProjection).order_by(EnrollmentProjection.updated_at.desc())
            ).all()
        )

    def list_snapshots(self, limit: int = 50):
        stmt = select(ReportSnapshot).order_by(ReportSnapshot.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())
