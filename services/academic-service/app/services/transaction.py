from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, DomainError


@contextmanager
def transaction(db: Session) -> Iterator[None]:
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "Duplicate record or a referenced academic record prevents this change."
        ) from exc
    except OperationalError as exc:
        db.rollback()
        raise DomainError(
            503, "Academic database is temporarily unavailable; retry the request."
        ) from exc
    except Exception:
        db.rollback()
        raise
