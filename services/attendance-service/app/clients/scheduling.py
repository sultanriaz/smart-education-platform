"""Verify linked Attendance occurrences via Scheduling owner API.

Turn VERIFY_SCHEDULE_OCCURRENCES on in local/staging after Scheduling is online;
production always enforces verification for linked sessions.
"""
from __future__ import annotations
from datetime import date
from uuid import UUID
import httpx
from smartedu_infra.http_pool import shared_http_client
from app.core.config import Settings
from app.core.exceptions import ConflictError, DependencyUnavailable


def verify_schedule_occurrence(settings: Settings, section_id: UUID, day: date, occurrence_id: UUID, bearer: str) -> None:
    params = {"start_date": day.isoformat(), "end_date": day.isoformat()}
    url = f"{settings.SCHEDULING_SERVICE_BASE_URL.rstrip('/')}/api/v1/timetable/sections/{section_id}"
    try:
        response = shared_http_client(settings.SCHEDULING_SERVICE_BASE_URL).get(
            url, params=params, headers={"Authorization": f"Bearer {bearer}"},
            timeout=settings.SCHEDULING_SERVICE_TIMEOUT_SECONDS,
        )
        if response.status_code in (401, 403):
            raise ConflictError("Scheduling did not authorize this occurrence.")
        if response.status_code != 200:
            raise DependencyUnavailable("Scheduling Service could not verify the occurrence.")
        rows = response.json()
    except (httpx.RequestError, ValueError, TypeError) as exc:
        raise DependencyUnavailable("Scheduling Service is unavailable or returned invalid occurrences.") from exc
    if not isinstance(rows, list):
        raise DependencyUnavailable("Scheduling Service returned an invalid occurrence list.")
    matching = [row for row in rows if isinstance(row, dict) and
        row.get("occurrence_id") == str(occurrence_id) and
        row.get("section_id") == str(section_id) and
        row.get("occurrence_date") == day.isoformat()]
    if len(matching) != 1:
        raise ConflictError("Attendance occurrence does not belong to this section/date or was cancelled.")
