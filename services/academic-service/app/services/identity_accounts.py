"""Fail-closed, signed Identity owner lookup for new Academic relationships.

This client never reads Identity's database and does not cache role/activation state.
"""
from __future__ import annotations

import os
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.exceptions import ConflictError, DomainError
from app.sprint16 import internal_token_signer


class IdentityAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    is_active: bool
    roles: list[str]
    auth_version: int


class IdentityAccountClient:
    def __init__(self, base_url: str, *, signer, transport=None) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("IDENTITY_SERVICE_BASE_URL must be an HTTP(S) origin")
        self.base_url = base_url.rstrip("/")
        self.signer = signer
        self.transport = transport

    @classmethod
    def from_environment(cls) -> "IdentityAccountClient":
        return cls(
            os.getenv("IDENTITY_SERVICE_BASE_URL", "http://identity-service:8000"),
            signer=internal_token_signer(),
        )

    def lookup(self, user_id: UUID) -> IdentityAccount | None:
        """Read even inactive users; None means the Identity account is absent."""
        token = self.signer.issue(
            audience="identity-service", scopes=("identity:academic:read",)
        )
        try:
            with httpx.Client(
                timeout=httpx.Timeout(3.0, connect=1.0),
                transport=self.transport,
                follow_redirects=False,
            ) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/internal/users/academic-accounts/{user_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.RequestError as exc:
            raise DomainError(503, "Identity account verification is unavailable.") from exc
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise DomainError(503, "Identity account verification is unavailable.")
        try:
            account = IdentityAccount.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise DomainError(503, "Invalid Identity account verification response.") from exc
        if account.id != user_id:
            raise DomainError(503, "Identity account verification returned a mismatched identity.")
        return account

    def require_eligible(self, user_id: UUID, required_role: str) -> IdentityAccount:
        # Fresh read on every eligibility-changing operation: role changes and
        # deactivation cannot be bypassed with an old Academic profile flag.
        account = self.lookup(user_id)
        if account is None:
            raise ConflictError("Linked Identity account does not exist.")
        if not account.is_active or required_role not in {role.lower() for role in account.roles}:
            raise ConflictError(f"Linked Identity account must be an active {required_role}.")
        return account
