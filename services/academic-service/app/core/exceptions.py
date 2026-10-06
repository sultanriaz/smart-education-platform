from __future__ import annotations


class DomainError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundError(DomainError):
    def __init__(self, resource: str) -> None:
        super().__init__(404, f"{resource} not found.")


class ConflictError(DomainError):
    def __init__(self, detail: str) -> None:
        super().__init__(409, detail)


class ForbiddenError(DomainError):
    def __init__(self) -> None:
        super().__init__(403, "Insufficient permissions for this academic resource.")
