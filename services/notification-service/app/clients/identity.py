from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, EmailStr, ValidationError
from smartedu_infra.http_pool import shared_http_client

from app.core.config import settings
from app.core.errors import DependencyContractError, DependencyUnavailableError
from app.sprint16 import internal_token_signer


class IdentityUser(BaseModel):
    id: uuid.UUID
    email: EmailStr | None = None
    roles: list[str] = []


@dataclass(slots=True)
class IdentityClient:
    base_url: str = settings.IDENTITY_SERVICE_BASE_URL
    timeout: float = settings.IDENTITY_SERVICE_TIMEOUT_SECONDS

    def _token(self, forwarded_token: str | None) -> str:
        return forwarded_token or internal_token_signer().issue(
            audience="identity-service", scopes=("identity:recipients:read",)
        )

    def _get(self, path: str, token: str, params: dict | None = None):
        try:
            response = shared_http_client(self.base_url).get(
                f"{self.base_url.rstrip('/')}{path}",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=self.timeout,
            )
        except httpx.RequestError as exc:
            raise DependencyUnavailableError("Identity Service is unavailable") from exc
        if response.status_code >= 500:
            raise DependencyUnavailableError("Identity Service is unavailable")
        if response.status_code in {401, 403}:
            raise DependencyContractError("Identity Service rejected service request")
        if response.status_code >= 400:
            raise DependencyContractError(
                f"Identity Service returned unexpected status {response.status_code}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise DependencyContractError("Identity Service returned malformed JSON") from exc

    def list_users_by_role(
        self, role: str, forwarded_token: str | None = None
    ) -> list[IdentityUser]:
        token = self._token(forwarded_token)
        offset = 0
        page_size = 200
        matched: list[IdentityUser] = []
        while True:
            payload = self._get(
                "/api/v1/users" if forwarded_token else "/api/v1/internal/users",
                token,
                {"offset": offset, "limit": page_size},
            )
            values = payload.get("items", payload) if isinstance(payload, dict) else payload
            if not isinstance(values, list):
                raise DependencyContractError("Identity users contract is invalid")
            try:
                users = [IdentityUser.model_validate(item) for item in values]
            except ValidationError as exc:
                raise DependencyContractError("Identity user contract is invalid") from exc
            matched.extend(u for u in users if role.lower() in {r.lower() for r in u.roles})
            if len(users) < page_size:
                break
            offset += page_size
        return matched

    def get_users(
        self, user_ids: list[uuid.UUID], forwarded_token: str | None = None
    ) -> list[IdentityUser]:
        users: list[IdentityUser] = []
        for user_id in user_ids:
            payload = self._get(f"/api/v1/internal/users/{user_id}", self._token(None))
            try:
                users.append(IdentityUser.model_validate(payload))
            except ValidationError as exc:
                raise DependencyContractError("Identity user contract is invalid") from exc
        return users
