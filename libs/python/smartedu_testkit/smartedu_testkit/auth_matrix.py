from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationCase:
    role: str
    expected_statuses: tuple[int, ...]


def cases(
    *,
    admin: Iterable[int] = (200, 201, 204),
    teacher: Iterable[int] = (403,),
    student: Iterable[int] = (403,),
    anonymous: Iterable[int] = (401,),
) -> tuple[AuthorizationCase, ...]:
    return (
        AuthorizationCase("admin", tuple(admin)),
        AuthorizationCase("teacher", tuple(teacher)),
        AuthorizationCase("student", tuple(student)),
        AuthorizationCase("anonymous", tuple(anonymous)),
    )
