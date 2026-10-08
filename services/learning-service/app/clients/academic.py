from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

import httpx
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import DependencyUnavailableError
from app.domain.entities.models import TargetType
from app.sprint16 import internal_token_signer


@dataclass(frozen=True)
class AccessibleTargets:
    section_ids: set[uuid.UUID]
    course_ids: set[uuid.UUID]


class AcademicClient(Protocol):
    def actor_can_manage_target(
        self, user_id: uuid.UUID, role: str, target_type: TargetType, target_id: uuid.UUID
    ) -> bool: ...
    def student_can_access_target(
        self, user_id: uuid.UUID, target_type: TargetType, target_id: uuid.UUID
    ) -> bool: ...
    def get_student_accessible_targets(self, user_id: uuid.UUID) -> AccessibleTargets: ...


class HttpAcademicClient:
    def __init__(self):
        self.base_url = settings.ACADEMIC_SERVICE_BASE_URL.rstrip("/")
        self.timeout = settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS

    def _get(self, path: str) -> dict:
        headers = {
            "Authorization": "Bearer "
            + internal_token_signer().issue(
                audience="academic-service", scopes=("academic:relationships:read",)
            )
        }
        try:
            response = shared_http_client(self.base_url).get(
                f"{self.base_url}{path}", headers=headers, timeout=self.timeout
            )
        except httpx.HTTPError as exc:
            raise DependencyUnavailableError("Academic Service unavailable") from exc
        if response.status_code >= 500:
            raise DependencyUnavailableError("Academic Service unavailable")
        if response.status_code == 404:
            return {"allowed": False}
        if response.status_code >= 400:
            return {"allowed": False}
        try:
            return response.json()
        except ValueError as exc:
            raise DependencyUnavailableError("Academic Service returned malformed JSON") from exc

    def actor_can_manage_target(
        self,
        user_id: uuid.UUID,
        role: str,
        target_type: TargetType,
        target_id: uuid.UUID,
    ) -> bool:
        if role == "admin":
            return True
        plural = "sections" if target_type == TargetType.SECTION else "courses"
        data = self._get(f"/api/v1/internal/access/teachers/{user_id}/{plural}/{target_id}")
        return bool(data.get("allowed"))

    def student_can_access_target(
        self, user_id: uuid.UUID, target_type: TargetType, target_id: uuid.UUID
    ) -> bool:
        plural = "sections" if target_type == TargetType.SECTION else "courses"
        data = self._get(f"/api/v1/internal/access/students/{user_id}/{plural}/{target_id}")
        return bool(data.get("allowed"))

    def get_student_accessible_targets(self, user_id: uuid.UUID) -> AccessibleTargets:
        data = self._get(f"/api/v1/internal/access/students/{user_id}/targets")
        try:
            return AccessibleTargets(
                section_ids={uuid.UUID(str(x)) for x in data.get("section_ids", [])},
                course_ids={uuid.UUID(str(x)) for x in data.get("course_ids", [])},
            )
        except Exception as exc:
            raise DependencyUnavailableError(
                "Academic Service returned malformed target data"
            ) from exc


_academic_client = HttpAcademicClient()


def get_academic_client() -> AcademicClient:
    return _academic_client
