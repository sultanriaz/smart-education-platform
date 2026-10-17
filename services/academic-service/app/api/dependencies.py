from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security.dependencies import require_admin, require_admin_read, require_staff
from app.security.jwt import Principal
from app.services.academic import AcademicService
from app.services.identity_accounts import IdentityAccountClient


def get_identity_accounts() -> IdentityAccountClient:
    return IdentityAccountClient.from_environment()


def get_service(
    db: Annotated[Session, Depends(get_db)],
    identity_accounts: Annotated[IdentityAccountClient, Depends(get_identity_accounts)],
) -> AcademicService:
    return AcademicService(db, identity_accounts=identity_accounts)


Service = Annotated[AcademicService, Depends(get_service)]
Admin = Annotated[Principal, Depends(require_admin)]
AdminRead = Annotated[Principal, Depends(require_admin_read)]
Staff = Annotated[Principal, Depends(require_staff)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]
