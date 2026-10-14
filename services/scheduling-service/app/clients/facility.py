from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import ConflictError, DependencyContractError, DependencyUnavailableError


@dataclass(slots=True)
class FacilityClient:
    base_url: str = settings.FACILITY_SERVICE_BASE_URL
    timeout: float = settings.FACILITY_SERVICE_TIMEOUT_SECONDS

    def replace_schedule(self, schedule_id: uuid.UUID, occurrences: list[dict]) -> None:
        if not settings.INTERNAL_SERVICE_TOKEN or settings.INTERNAL_SERVICE_TOKEN == "CHANGE_ME_INTERNAL_SERVICE_TOKEN":
            raise DependencyUnavailableError("Facility internal authentication is not configured")
        try:
            response = shared_http_client(self.base_url).put(
                f"{self.base_url.rstrip('/')}/api/v1/internal/reservations/schedules/{schedule_id}",
                json={"occurrences": occurrences},
                headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
                timeout=self.timeout,
            )
        except httpx.RequestError as exc:
            raise DependencyUnavailableError("Facility reservation synchronization unavailable") from exc
        if response.status_code in {404, 409}:
            raise ConflictError("Classroom reservation rejected by Facility Service")
        if response.status_code >= 500:
            raise DependencyUnavailableError("Facility Service unavailable during reservation synchronization")
        if response.status_code != 200:
            raise DependencyContractError(f"Facility reservation contract failed ({response.status_code})")
        try:
            result = response.json()
        except ValueError as exc:
            raise DependencyContractError("Facility response is not valid JSON") from exc
        if result.get("schedule_id") != str(schedule_id) or result.get("active_count") != len(occurrences):
            raise DependencyContractError("Facility reservation response did not match requested state")


def get_facility_client() -> FacilityClient:
    return FacilityClient()
