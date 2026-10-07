from __future__ import annotations

from typing import Protocol
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.config import Settings
from app.core.exceptions import DependencyUnavailable, ForbiddenError, NotFoundError


class AcademicSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: UUID
    course_id: UUID
    semester_id: UUID
    is_active: bool


class RosterMember(BaseModel):
    external_user_id: UUID


class RosterPage(BaseModel):
    section_id: UUID
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    students: list[RosterMember]


class AcademicClient(Protocol):
    def get_section(self, section_id: UUID, token: str) -> AcademicSection: ...
    def validate_teacher_assignment(self, section_id: UUID, token: str) -> None: ...
    def assigned_sections(self, token: str) -> set[UUID]: ...
    def get_section_roster(self, section_id: UUID, token: str) -> set[UUID]: ...
    def validate_student_enrollment(
        self, section_id: UUID, student_id: UUID, token: str
    ) -> None: ...


class HttpAcademicClient:
    """Request-scoped adapter; forwards only the verified caller's bearer token.

    Academic's section endpoint enforces the caller's active teacher assignment.
    No elevated service credential or student-to-admin token exchange is required.
    """

    def __init__(self, settings: Settings, http: httpx.Client) -> None:
        self.settings = settings
        self.http = http
        self._sections: dict[tuple[UUID, str], AcademicSection] = {}
        self._rosters: dict[tuple[UUID, str], set[UUID]] = {}

    def _get(self, path: str, token: str, *, params: dict | None = None):
        try:
            response = self.http.get(
                f"{self.settings.ACADEMIC_SERVICE_BASE_URL.rstrip('/')}/api/v1{path}",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=self.settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS,
                follow_redirects=False,
            )
        except httpx.RequestError as exc:
            raise DependencyUnavailable() from exc
        if response.status_code == 404:
            raise NotFoundError("Academic section")
        if response.status_code in {401, 403}:
            raise ForbiddenError("Academic Service denied access to this section.")
        if response.status_code != 200:
            raise DependencyUnavailable()
        try:
            return response.json()
        except ValueError as exc:
            raise DependencyUnavailable() from exc

    def get_section(self, section_id: UUID, token: str) -> AcademicSection:
        cache_key = (section_id, token)
        if cache_key not in self._sections:
            try:
                section = AcademicSection.model_validate(
                    self._get(f"/sections/{section_id}", token)
                )
                if section.id != section_id:
                    raise ValueError("Section identifier mismatch")
            except (ValidationError, ValueError) as exc:
                raise DependencyUnavailable() from exc
            self._sections[cache_key] = section
        return self._sections[cache_key]

    def validate_teacher_assignment(self, section_id: UUID, token: str) -> None:
        # The bearer subject selects the teacher in Academic; no user-controlled
        # teacher ID or role header can widen this check.
        self.get_section(section_id, token)

    def assigned_sections(self, token: str) -> set[UUID]:
        sections: set[UUID] = set()
        for page in range(self.settings.ACADEMIC_SERVICE_MAX_PAGES):
            payload = self._get("/sections", token, params={"limit": 100, "offset": page * 100})
            try:
                if not isinstance(payload, list) or len(payload) > 100:
                    raise ValueError("Invalid section list")
                batch = [AcademicSection.model_validate(item) for item in payload]
                ids = {item.id for item in batch}
                if len(ids) != len(batch) or sections.intersection(ids):
                    raise ValueError("Duplicate section identifiers")
            except (ValidationError, ValueError) as exc:
                raise DependencyUnavailable() from exc
            sections.update(ids)
            if len(batch) < 100:
                return sections
        raise DependencyUnavailable("Academic section pagination exceeded its configured bound.")

    def get_section_roster(self, section_id: UUID, token: str) -> set[UUID]:
        cache_key = (section_id, token)
        if cache_key in self._rosters:
            return self._rosters[cache_key]
        members: set[UUID] = set()
        total = None
        for page in range(self.settings.ACADEMIC_SERVICE_MAX_PAGES):
            offset = page * 100
            try:
                result = RosterPage.model_validate(
                    self._get(
                        f"/sections/{section_id}/roster",
                        token,
                        params={"limit": 100, "offset": offset},
                    )
                )
                if (
                    result.section_id != section_id
                    or result.offset != offset
                    or result.limit != 100
                ):
                    raise ValueError("Invalid roster pagination metadata")
                if total is None:
                    total = result.total
                if result.total != total or len(result.students) != min(
                    100, max(0, total - offset)
                ):
                    raise ValueError("Roster changed or returned incomplete pagination")
                ids = {item.external_user_id for item in result.students}
                if len(ids) != len(result.students) or members.intersection(ids):
                    raise ValueError("Duplicate roster members")
            except (ValidationError, ValueError) as exc:
                raise DependencyUnavailable() from exc
            members.update(ids)
            if len(members) == total:
                self._rosters[cache_key] = members
                return members
        raise DependencyUnavailable("Academic roster pagination exceeded its configured bound.")

    def validate_student_enrollment(self, section_id: UUID, student_id: UUID, token: str) -> None:
        if student_id not in self.get_section_roster(section_id, token):
            raise ForbiddenError("Student is not enrolled in the Academic section roster.")
