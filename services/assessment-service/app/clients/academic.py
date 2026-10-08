from __future__ import annotations

import uuid

import httpx
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import DependencyUnavailableError, ForbiddenError, NotFoundError


class AcademicClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = (base_url or settings.ACADEMIC_SERVICE_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS

    def _get(self, path: str, bearer_token: str | None = None) -> dict | list:
        headers = {"Authorization": f"Bearer {bearer_token}"} if bearer_token else {}
        try:
            response = shared_http_client(self.base_url).get(
                f"{self.base_url}{path}",
                headers=headers,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise DependencyUnavailableError("Academic Service unavailable") from exc

        if response.status_code == 404:
            raise NotFoundError("Academic resource not found")
        if response.status_code in {401, 403}:
            raise ForbiddenError("Academic relationship validation denied")
        if response.status_code >= 500:
            raise DependencyUnavailableError("Academic Service unavailable")
        response.raise_for_status()
        return response.json()

    def get_section(self, section_id: uuid.UUID, token: str | None = None) -> dict:
        return self._get(f"/api/v1/sections/{section_id}", token)

    def validate_teacher_assignment(
        self, teacher_user_id: uuid.UUID, section_id: uuid.UUID, token: str | None = None
    ) -> bool:
        data = self._get(
            f"/api/v1/teachers/{teacher_user_id}/sections/{section_id}/assignment",
            token,
        )
        return isinstance(data, dict) and data.get("assigned") is True

    def validate_student_enrollment(
        self, student_user_id: uuid.UUID, section_id: uuid.UUID, token: str | None = None
    ) -> bool:
        data = self._get(
            f"/api/v1/students/{student_user_id}/sections/{section_id}/enrollment",
            token,
        )
        return isinstance(data, dict) and data.get("enrolled") is True
