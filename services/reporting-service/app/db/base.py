from __future__ import annotations

from app.db.base_class import Base
from app.domain.entities.models import (  # noqa: F401
    AnalyticsEvent,
    AssessmentProjection,
    AttendanceProjection,
    EnrollmentProjection,
    ExportAudit,
    FacilityBookingProjection,
    NotificationDeliveryProjection,
    ReportSnapshot,
    ScheduleActivityProjection,
)

__all__ = ["Base"]
