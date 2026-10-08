from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import DependencyContractError, DependencyUnavailableError
from app.sprint16 import internal_token_signer


@dataclass(slots=True)
class AcademicClient:
    base_url: str = settings.ACADEMIC_SERVICE_BASE_URL
    timeout: float = settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS

    def _request(
        self,
        path: str,
        forwarded_token: str | None = None,
    ) -> dict | list:
        token = forwarded_token or internal_token_signer().issue(
            audience="academic-service", scopes=("academic:relationships:read",)
        )

        try:
            response = shared_http_client(self.base_url).get(
                f"{self.base_url.rstrip('/')}{path}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )
        except httpx.RequestError as exc:
            raise DependencyUnavailableError("Academic Service is unavailable") from exc

        if response.status_code >= 500:
            raise DependencyUnavailableError("Academic Service is unavailable")
        if response.status_code in {401, 403}:
            raise DependencyContractError("Academic Service rejected service request")
        if response.status_code >= 400:
            raise DependencyContractError(
                f"Academic Service returned unexpected status {response.status_code}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise DependencyContractError("Academic Service returned malformed JSON") from exc

    def list_section_member_ids(
        self,
        section_id: uuid.UUID,
        forwarded_token: str | None = None,
    ) -> list[uuid.UUID]:
        path = settings.ACADEMIC_SECTION_ROSTER_PATH_TEMPLATE.format(section_id=section_id)
        if not forwarded_token:
            path = f"/api/v1/internal/sections/{section_id}/roster"
        offset, result = 0, []
        while True:
            payload = self._request(f"{path}?limit=100&offset={offset}", forwarded_token)
            page = self._roster_ids(payload)
            result.extend(page)
            total = payload.get("total") if isinstance(payload, dict) else None
            if len(page) < 100 or (isinstance(total, int) and len(result) >= total):
                return list(dict.fromkeys(result))
            offset += 100
            if offset >= 100_000:
                raise DependencyContractError("Academic roster exceeds the supported batch size")

    @staticmethod
    def _roster_ids(payload):

        values = payload.get("student_user_ids") if isinstance(payload, dict) else None
        if values is None and isinstance(payload, dict):
            values = payload.get(
                "students",
                payload.get("items", payload.get("roster")),
            )

        if not isinstance(values, list):
            raise DependencyContractError("Academic roster contract is invalid")

        result: list[uuid.UUID] = []
        for item in values:
            raw = item
            if isinstance(item, dict):
                raw = item.get(
                    "student_user_id",
                    item.get("external_user_id", item.get("user_id", item.get("id"))),
                )
            try:
                result.append(uuid.UUID(str(raw)))
            except (TypeError, ValueError) as exc:
                raise DependencyContractError("Academic roster contract is invalid") from exc
        return result

    def list_course_member_ids(self, course_id: uuid.UUID) -> list[uuid.UUID]:
        result, offset = [], 0
        while offset < 100_000:
            payload = self._request(
                f"/api/v1/internal/courses/{course_id}/members?limit=100&offset={offset}"
            )
            page = self._roster_ids(payload)
            result.extend(page)
            if len(page) < 100:
                return list(dict.fromkeys(result))
            offset += 100
        raise DependencyContractError("Academic course exceeds the supported batch size")

    def validate_teacher_assignment(
        self,
        teacher_user_id: uuid.UUID,
        section_id: uuid.UUID,
        forwarded_token: str | None = None,
    ) -> bool:
        payload = self._request(
            f"/api/v1/teachers/{teacher_user_id}/sections/{section_id}/assignment",
            forwarded_token,
        )
        if not isinstance(payload, dict):
            raise DependencyContractError("Academic teacher-assignment contract is invalid")
        return bool(
            payload.get(
                "assigned",
                payload.get("allowed", False),
            )
        )
