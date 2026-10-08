from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DashboardOverview(BaseModel):
    active_enrollments: int
    attendance_records: int
    attendance_percentage: float | None
    graded_attempts: int
    assessment_average_percent: float | None
    assessment_pass_rate: float | None
    facility_bookings: int
    approved_facility_bookings: int
    notification_deliveries: int
    notification_success_rate: float | None
    schedule_changes: int


class SnapshotCreate(BaseModel):
    report_type: str
    filters: dict = {}


class SnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_type: str
    filters: dict
    payload: dict
    generated_by_user_id: uuid.UUID
    created_at: datetime


class DateRangeFilter(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
