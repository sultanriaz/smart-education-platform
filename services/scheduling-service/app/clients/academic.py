from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, ValidationError
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import DependencyContractError, DependencyUnavailableError, NotFoundError


class AcademicSection(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID | None = None
    semester_id: uuid.UUID | None = None


@dataclass(slots=True)
class AcademicClient:
    base_url: str = settings.ACADEMIC_SERVICE_BASE_URL
    timeout: float = settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS

    def _get(self, path: str, token: str, params: dict | None = None):
        try:
            response = shared_http_client(self.base_url).get(
                f"{self.base_url.rstrip('/')}{path}",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )
        except httpx.RequestError as exc:
            raise DependencyUnavailableError("Academic Service is unavailable") from exc

        if response.status_code == 404:
            raise NotFoundError("Academic resource not found")
        if response.status_code in {401, 403}:
            raise DependencyContractError("Academic Service rejected service request")
        if response.status_code >= 500:
            raise DependencyUnavailableError("Academic Service is unavailable")
        if response.status_code >= 400:
            raise DependencyContractError(
                f"Academic Service returned unexpected status {response.status_code}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise DependencyContractError("Academic Service returned malformed JSON") from exc

    def get_section(self, section_id: uuid.UUID, token: str) -> AcademicSection:
        path = settings.ACADEMIC_SECTION_PATH_TEMPLATE.format(section_id=section_id)
        payload = self._get(path, token)
        try:
            return AcademicSection.model_validate(payload)
        except ValidationError as exc:
            raise DependencyContractError("Academic section contract is invalid") from exc

    def validate_teacher_assignment(
        self, teacher_user_id: uuid.UUID, section_id: uuid.UUID, token: str
    ) -> bool:
        payload = self._get(
            settings.ACADEMIC_TEACHER_ASSIGNMENT_PATH,
            token,
            {"teacher_user_id": str(teacher_user_id), "section_id": str(section_id)},
        )
        return bool(payload.get("valid") or payload.get("assigned") or payload.get("is_assigned"))

    def validate_student_enrollment(
        self, student_user_id: uuid.UUID, section_id: uuid.UUID, token: str
    ) -> bool:
        payload = self._get(
            settings.ACADEMIC_STUDENT_ENROLLMENT_PATH,
            token,
            {"student_user_id": str(student_user_id), "section_id": str(section_id)},
        )
        return bool(payload.get("valid") or payload.get("enrolled") or payload.get("is_enrolled"))

    def list_student_section_ids(self, student_user_id: uuid.UUID, token: str) -> list[uuid.UUID]:
        path = settings.ACADEMIC_STUDENT_SECTIONS_PATH_TEMPLATE.format(
            student_user_id=student_user_id
        )
        payload = self._get(path, token)
        values = payload.get("section_ids", payload) if isinstance(payload, dict) else payload
        try:
            return [uuid.UUID(str(value)) for value in values]
        except (TypeError, ValueError) as exc:
            raise DependencyContractError("Academic student-sections contract is invalid") from exc


def get_academic_client() -> AcademicClient:
    return AcademicClient()
