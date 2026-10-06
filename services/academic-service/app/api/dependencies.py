from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security.dependencies import require_admin, require_staff
from app.security.jwt import Principal
from app.services.academic import AcademicService


def get_service(db: Annotated[Session, Depends(get_db)]) -> AcademicService:
    return AcademicService(db)


Service = Annotated[AcademicService, Depends(get_service)]
Admin = Annotated[Principal, Depends(require_admin)]
Staff = Annotated[Principal, Depends(require_staff)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]
