from __future__ import annotations

from dataclasses import dataclass

from .lockout import LockoutStore
from .passwords import PasswordPolicy, validate_password


@dataclass(slots=True)
class LoginSecurityGuard:
    lockout: LockoutStore

    async def precheck(self, subject: str):
        return await self.lockout.check(subject)

    async def failed(self, subject: str):
        return await self.lockout.failure(subject)

    async def succeeded(self, subject: str) -> None:
        await self.lockout.success(subject)


def enforce_new_password(
    password: str,
    *,
    email: str | None,
    full_name: str | None,
    min_length: int = 12,
    max_length: int = 128,
) -> None:
    validate_password(
        password,
        email=email,
        full_name=full_name,
        policy=PasswordPolicy(
            min_length=min_length,
            max_length=max_length,
        ),
    )
