from __future__ import annotations


class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ForbiddenError(DomainError):
    pass


class DependencyUnavailableError(DomainError):
    pass


class DependencyContractError(DomainError):
    pass


class TemplateRenderError(DomainError):
    pass
