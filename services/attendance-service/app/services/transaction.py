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
            "Duplicate attendance session or record; no changes were committed."
        ) from exc
    except OperationalError as exc:
        db.rollback()
        raise DomainError(
            503,
            "Attendance database is temporarily unavailable; retry the request.",
            "database_unavailable",
        ) from exc
    except Exception:
        db.rollback()
        raise
