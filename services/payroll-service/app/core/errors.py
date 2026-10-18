from __future__ import annotations


class PayrollDomainError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ConcurrencyConflictError(PayrollDomainError):
    def __init__(self, message: str = "Concurrent modification detected; please retry"):
        super().__init__(message, status_code=409)


class InsufficientPermissionsError(PayrollDomainError):
    def __init__(self, message: str = "Insufficient permissions for requested payroll action"):
        super().__init__(message, status_code=403)


class EntityNotFoundError(PayrollDomainError):
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message, status_code=404)

