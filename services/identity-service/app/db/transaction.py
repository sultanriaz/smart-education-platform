from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError


@contextmanager
def transaction(db: Session, *, conflict_message: str | None = None) -> Iterator[None]:
    """Finish the application operation, including reads begun by auth dependencies."""
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        is_unique_violation = (
            getattr(exc.orig, "sqlstate", None) == "23505"
            or getattr(exc.orig, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE"
        )
        if conflict_message and is_unique_violation:
            raise ConflictError(conflict_message) from exc
        raise
    except Exception:
        db.rollback()
        raise
