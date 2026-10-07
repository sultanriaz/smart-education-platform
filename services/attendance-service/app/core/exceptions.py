from __future__ import annotations


class DomainError(Exception):
    def __init__(self, status_code: int, detail: str, code: str) -> None:
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(detail)


class NotFoundError(DomainError):
    def __init__(self, resource: str = "Attendance session") -> None:
        super().__init__(404, f"{resource} not found.", "not_found")


class ConflictError(DomainError):
    def __init__(self, detail: str) -> None:
        super().__init__(409, detail, "attendance_conflict")


class ForbiddenError(DomainError):
    def __init__(
        self, detail: str = "Insufficient permissions for this attendance resource."
    ) -> None:
        super().__init__(403, detail, "forbidden")


class DependencyUnavailable(DomainError):
    def __init__(self, detail: str = "Academic Service is unavailable or returned invalid data."):
        super().__init__(503, detail, "academic_unavailable")
