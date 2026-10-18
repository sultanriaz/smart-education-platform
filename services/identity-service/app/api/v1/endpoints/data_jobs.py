"""Identity-owned, transactionally idempotent account onboarding (no plaintext secrets)."""
import hashlib
import json
import secrets
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from smartedu_contracts import internal_auth_dependency
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.transaction import transaction
from app.domain.entities.import_batch import IdentityImportBatch
from app.domain.entities.outbox import OutboxEvent
from app.repositories.audit_repository import AuditRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password
from app.sprint16 import internal_token_verifier

router = APIRouter(prefix="/internal", tags=["Identity data jobs"])
Import = Annotated[object, Depends(internal_auth_dependency(internal_token_verifier(), audience="identity-service", required_scopes=("identity:data:import",)))]
Export = Annotated[object, Depends(internal_auth_dependency(internal_token_verifier(), audience="identity-service", required_scopes=("identity:data:export",)))]


class ImportUser(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    role: Literal["student", "teacher"] = "student"


class ImportBatch(BaseModel):
    items: list[ImportUser] = Field(min_length=1, max_length=100)


def only_platform(principal):
    if principal.service_name != "platform-service":
        raise HTTPException(403, "This contract is reserved for the Platform service")


def digest(batch: ImportBatch) -> str:
    return hashlib.sha256(json.dumps(batch.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@router.post("/imports/users")
def import_users(payload: ImportBatch, principal: Import, db: Annotated[Session, Depends(get_db)], dry_run: bool = Query(default=False), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", min_length=8, max_length=160)):
    only_platform(principal)
    repository = UserRepository(db)
    roles = RoleRepository(db)
    emails = [str(user.email).lower() for user in payload.items]
    if len(set(emails)) != len(emails):
        raise HTTPException(422, "Duplicate email address in import batch")
    content_hash = digest(payload)
    # Replays produce the exact first response, or fail on changed input.
    if idempotency_key:
        existing = db.scalar(select(IdentityImportBatch).where(IdentityImportBatch.idempotency_key == idempotency_key))
        if existing:
            if existing.content_digest != content_hash:
                raise HTTPException(409, "Idempotency-Key belongs to a different batch")
            return existing.result
    elif not dry_run:
        raise HTTPException(422, "Idempotency-Key is mandatory for execution")
    for user in payload.items:
        if roles.get_by_name(user.role) is None:
            raise HTTPException(422, "Target role has not been seeded")
        if repository.get_by_email(str(user.email)):
            raise HTTPException(409, "An import account already exists")
    if dry_run:
        return {"dry_run": True, "valid_rows": len(payload.items), "imported": 0, "errors": []}
    created = []
    with transaction(db, conflict_message="Import conflicted with another transaction"):
        for item in payload.items:
            role = roles.get_by_name(item.role)
            user = repository.create(email=str(item.email), full_name=item.full_name.strip(), password_hash=hash_password(secrets.token_urlsafe(48)), roles=[role], is_verified=False)
            # User must complete normal account recovery before first sign-in.
            created.append({"user_id": str(user.id), "email": str(user.email), "role": item.role, "onboarding": "verify_email_and_reset_password_required"})
            db.add(OutboxEvent(event_type="identity.user_created", aggregate_id=user.id, payload={"user_id": str(user.id), "role": item.role}))
            AuditRepository(db).record(action="user.imported", user_id=user.id, details={"source": "platform-job"})
        result = {"dry_run": False, "imported": len(created), "items": created}
        db.add(IdentityImportBatch(idempotency_key=idempotency_key, content_digest=content_hash, result=result))
    return result


@router.get("/exports/users")
def export_users(principal: Export, db: Annotated[Session, Depends(get_db)], limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    only_platform(principal)
    users = UserRepository(db).list_users(limit=limit, offset=offset)
    # Whitelisted fields only; never include passwords, tokens, or audit details.
    return {"items": [{"id": str(user.id), "email": str(user.email), "full_name": user.full_name, "roles": [role.name for role in user.roles], "is_active": user.is_active, "is_verified": user.is_verified} for user in users], "limit": limit, "offset": offset}
