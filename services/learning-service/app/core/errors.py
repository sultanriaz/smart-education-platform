from __future__ import annotations


class DomainError(Exception):
    status_code = 400


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class ForbiddenError(DomainError):
    status_code = 403


class ValidationDomainError(DomainError):
    status_code = 422


class DependencyUnavailableError(DomainError):
    status_code = 503
