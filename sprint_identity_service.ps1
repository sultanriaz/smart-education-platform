param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

function Write-RepoFile {
    param(
        [Parameter(Mandatory=$true)][string]$RelativePath,
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Content
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    $parent = Split-Path $fullPath -Parent
    if ($parent) {
        New-Item -ItemType Directory -Force $parent | Out-Null
    }
    Set-Content -Path $fullPath -Value $Content -Encoding utf8
    Write-Host "WROTE  $RelativePath"
}

$svc = "services/identity-service"

$packageFiles = @(
    "$svc/app/__init__.py",
    "$svc/app/api/__init__.py",
    "$svc/app/api/v1/__init__.py",
    "$svc/app/api/v1/endpoints/__init__.py",
    "$svc/app/core/__init__.py",
    "$svc/app/db/__init__.py",
    "$svc/app/domain/__init__.py",
    "$svc/app/domain/entities/__init__.py",
    "$svc/app/repositories/__init__.py",
    "$svc/app/schemas/__init__.py",
    "$svc/app/security/__init__.py",
    "$svc/app/services/__init__.py",
    "$svc/app/scripts/__init__.py",
    "$svc/tests/__init__.py"
)
foreach ($p in $packageFiles) { Write-RepoFile $p "" }

Write-RepoFile "$svc/requirements.txt" @'
fastapi>=0.115,<1
uvicorn[standard]>=0.30,<1
sqlalchemy>=2.0,<3
psycopg[binary]>=3.2,<4
alembic>=1.13,<2
pydantic-settings>=2.5,<3
PyJWT>=2.9,<3
pwdlib[argon2]>=0.2,<1
email-validator>=2.2,<3
python-multipart>=0.0.12,<1
'@

Write-RepoFile "$svc/requirements-dev.txt" @'
-r requirements.txt
pytest>=8,<9
pytest-cov>=5,<7
httpx>=0.27,<1
ruff>=0.6,<1
'@

Write-RepoFile "$svc/.env.example" @'
APP_NAME=Smart Education Identity Service
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://identity:identity@localhost:5433/identity_db
JWT_SECRET_KEY=CHANGE_ME_TO_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=15
REFRESH_TOKEN_DAYS=14
CORS_ORIGINS=["http://localhost:5173"]
BOOTSTRAP_ADMIN_EMAIL=admin@example.edu
BOOTSTRAP_ADMIN_PASSWORD=ChangeMe123!
BOOTSTRAP_ADMIN_NAME=Platform Administrator
'@

Write-RepoFile "$svc/.gitignore" @'
.venv/
__pycache__/
.pytest_cache/
.coverage
htmlcov/
.env
*.pyc
'@

Write-RepoFile "$svc/pyproject.toml" @'
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
'@

Write-RepoFile "$svc/app/core/config.py" @'
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Identity Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://identity:identity@localhost:5433/identity_db"
    JWT_SECRET_KEY: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 14
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    BOOTSTRAP_ADMIN_EMAIL: str | None = None
    BOOTSTRAP_ADMIN_PASSWORD: str | None = None
    BOOTSTRAP_ADMIN_NAME: str = "Platform Administrator"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
'@

Write-RepoFile "$svc/app/core/exceptions.py" @'
class DomainError(Exception):
    pass


class ConflictError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass
'@

Write-RepoFile "$svc/app/db/base_class.py" @'
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
'@

Write-RepoFile "$svc/app/db/session.py" @'
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'@

Write-RepoFile "$svc/app/domain/entities/associations.py" @'
from sqlalchemy import Column, ForeignKey, Table, Uuid

from app.db.base_class import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Uuid(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)
'@

Write-RepoFile "$svc/app/domain/entities/role.py" @'
import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.domain.entities.associations import role_permissions, user_roles


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list["Role"]] = relationship(secondary=role_permissions, back_populates="permissions")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(secondary=user_roles, back_populates="roles")


from app.domain.entities.user import User  # noqa: E402
'@

Write-RepoFile "$svc/app/domain/entities/user.py" @'
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.domain.entities.associations import user_roles


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )


from app.domain.entities.role import Role  # noqa: E402
'@

Write-RepoFile "$svc/app/domain/entities/refresh_token.py" @'
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
'@

Write-RepoFile "$svc/app/domain/entities/audit.py" @'
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SecurityAuditEvent(Base):
    __tablename__ = "security_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
'@

Write-RepoFile "$svc/app/db/base.py" @'
from app.db.base_class import Base
from app.domain.entities.associations import role_permissions, user_roles  # noqa: F401
from app.domain.entities.audit import SecurityAuditEvent  # noqa: F401
from app.domain.entities.refresh_token import RefreshToken  # noqa: F401
from app.domain.entities.role import Permission, Role  # noqa: F401
from app.domain.entities.user import User  # noqa: F401

__all__ = ["Base"]
'@

Write-RepoFile "$svc/app/schemas/user.py" @'
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)


class AdminUserCreate(UserRegister):
    role: str = "student"


class UserSelfUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)


class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    is_active: bool | None = None
    is_verified: bool | None = None
    roles: list[str] | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[str] = []
    created_at: datetime

    @field_validator("roles", mode="before")
    @classmethod
    def role_names(cls, value):
        if value is None:
            return []
        return [item.name if hasattr(item, "name") else str(item) for item in value]
'@

Write-RepoFile "$svc/app/schemas/auth.py" @'
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
'@

Write-RepoFile "$svc/app/schemas/role.py" @'
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    permissions: list[str] = []


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    permissions: list[str] = []

    @field_validator("permissions", mode="before")
    @classmethod
    def permission_codes(cls, value):
        if value is None:
            return []
        return [item.code if hasattr(item, "code") else str(item) for item in value]


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    description: str | None
'@

Write-RepoFile "$svc/app/security/password.py" @'
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)
'@

Write-RepoFile "$svc/app/security/jwt.py" @'
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: uuid.UUID, roles: list[str]) -> tuple[str, datetime]:
    now = _now()
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    payload = {"sub": str(user_id), "type": "access", "roles": roles, "iat": now, "exp": expires_at}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def create_refresh_token(user_id: uuid.UUID, roles: list[str]) -> tuple[str, str, datetime]:
    now = _now()
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_DAYS)
    jti = uuid.uuid4().hex
    payload = {"sub": str(user_id), "type": "refresh", "roles": roles, "jti": jti, "iat": now, "exp": expires_at}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expires_at


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
'@

Write-RepoFile "$svc/app/repositories/user_repository.py" @'
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.role import Role
from app.domain.entities.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).options(selectinload(User.roles)).where(User.email == email.lower())
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).options(selectinload(User.roles)).where(User.id == user_id)
        return self.db.scalar(stmt)

    def list(self, offset: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).options(selectinload(User.roles)).order_by(User.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).unique().all())

    def create(self, *, email: str, full_name: str, password_hash: str, roles: list[Role], is_verified: bool = False) -> User:
        user = User(email=email.lower(), full_name=full_name, password_hash=password_hash, roles=roles, is_verified=is_verified)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.get_by_id(user.id)

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.get_by_id(user.id)
'@

Write-RepoFile "$svc/app/repositories/role_repository.py" @'
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.role import Permission, Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).options(selectinload(Role.permissions)).where(Role.name == name.lower())
        return self.db.scalar(stmt)

    def list(self) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.name)
        return list(self.db.scalars(stmt).unique().all())

    def list_permissions(self) -> list[Permission]:
        return list(self.db.scalars(select(Permission).order_by(Permission.code)).all())

    def get_permission(self, code: str) -> Permission | None:
        return self.db.scalar(select(Permission).where(Permission.code == code))

    def create_role(self, *, name: str, description: str | None, permissions: list[Permission]) -> Role:
        role = Role(name=name.lower(), description=description, permissions=permissions)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self.get_by_name(role.name)
'@

Write-RepoFile "$svc/app/repositories/token_repository.py" @'
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.refresh_token import RefreshToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, user_id: uuid.UUID, jti: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        return token

    def get_valid(self, jti: str) -> RefreshToken | None:
        token = self.db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
        if token is None or token.revoked_at is not None:
            return None
        now = datetime.now(timezone.utc)
        expiry = token.expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry <= now:
            return None
        return token

    def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        self.db.add(token)
        self.db.commit()
'@

Write-RepoFile "$svc/app/repositories/audit_repository.py" @'
import uuid

from sqlalchemy.orm import Session

from app.domain.entities.audit import SecurityAuditEvent


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def record(self, *, action: str, user_id: uuid.UUID | None = None, ip_address: str | None = None, details: dict | None = None) -> None:
        self.db.add(SecurityAuditEvent(action=action, user_id=user_id, ip_address=ip_address, details=details or {}))
        self.db.commit()
'@

Write-RepoFile "$svc/app/services/auth_service.py" @'
import uuid

import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.repositories.audit_repository import AuditRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair
from app.schemas.user import UserRegister
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)
        self.tokens = TokenRepository(db)
        self.audit = AuditRepository(db)

    def register(self, payload: UserRegister, ip_address: str | None = None):
        email = str(payload.email).lower()
        if self.users.get_by_email(email):
            raise ConflictError("An account with this email already exists.")
        student_role = self.roles.get_by_name("student")
        if student_role is None:
            raise RuntimeError("RBAC is not seeded. Run the seed command first.")
        user = self.users.create(email=email, full_name=payload.full_name.strip(), password_hash=hash_password(payload.password), roles=[student_role])
        self.audit.record(action="user.registered", user_id=user.id, ip_address=ip_address)
        return user

    def login(self, email: str, password: str, ip_address: str | None = None) -> TokenPair:
        user = self.users.get_by_email(email.lower())
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            self.audit.record(action="auth.login_failed", user_id=user.id if user else None, ip_address=ip_address, details={"email": email.lower()})
            raise AuthenticationError("Invalid email or password.")
        pair = self._issue_pair(user.id, [role.name for role in user.roles])
        self.audit.record(action="auth.login_succeeded", user_id=user.id, ip_address=ip_address)
        return pair

    def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid refresh token.") from exc
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type.")
        jti = payload.get("jti")
        subject = payload.get("sub")
        if not jti or not subject:
            raise AuthenticationError("Malformed refresh token.")
        stored = self.tokens.get_valid(jti)
        if stored is None:
            raise AuthenticationError("Refresh token is expired or revoked.")
        try:
            user_id = uuid.UUID(subject)
        except ValueError as exc:
            raise AuthenticationError("Malformed refresh token.") from exc
        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User account is unavailable.")
        self.tokens.revoke(stored)
        return self._issue_pair(user.id, [role.name for role in user.roles])

    def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except jwt.PyJWTError:
            return
        if payload.get("type") != "refresh" or not payload.get("jti"):
            return
        stored = self.tokens.get_valid(payload["jti"])
        if stored:
            self.tokens.revoke(stored)

    def _issue_pair(self, user_id: uuid.UUID, roles: list[str]) -> TokenPair:
        access_token, _ = create_access_token(user_id, roles)
        refresh_token, jti, refresh_expires_at = create_refresh_token(user_id, roles)
        self.tokens.create(user_id=user_id, jti=jti, expires_at=refresh_expires_at)
        return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=settings.ACCESS_TOKEN_MINUTES * 60)
'@

Write-RepoFile "$svc/app/services/user_service.py" @'
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserSelfUpdate
from app.security.password import hash_password


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    def create_by_admin(self, payload: AdminUserCreate):
        email = str(payload.email).lower()
        if self.users.get_by_email(email):
            raise ConflictError("An account with this email already exists.")
        role = self.roles.get_by_name(payload.role)
        if role is None:
            raise NotFoundError(f"Role '{payload.role}' does not exist.")
        return self.users.create(email=email, full_name=payload.full_name.strip(), password_hash=hash_password(payload.password), roles=[role], is_verified=True)

    def update_self(self, user, payload: UserSelfUpdate):
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        return self.users.save(user)

    def update_by_admin(self, user_id: uuid.UUID, payload: AdminUserUpdate):
        user = self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.is_verified is not None:
            user.is_verified = payload.is_verified
        if payload.roles is not None:
            roles = []
            for role_name in payload.roles:
                role = self.roles.get_by_name(role_name)
                if role is None:
                    raise NotFoundError(f"Role '{role_name}' does not exist.")
                roles.append(role)
            user.roles = roles
        return self.users.save(user)

    def deactivate(self, user_id: uuid.UUID):
        user = self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        user.is_active = False
        return self.users.save(user)
'@

Write-RepoFile "$svc/app/security/dependencies.py" @'
import uuid
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise credentials_error from exc
    if payload.get("type") != "access" or not payload.get("sub"):
        raise credentials_error
    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError as exc:
        raise credentials_error from exc
    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_roles(*required_roles: str) -> Callable:
    required = {role.lower() for role in required_roles}

    def dependency(user=Depends(get_current_user)):
        actual = {role.name.lower() for role in user.roles}
        if required.isdisjoint(actual):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return user

    return dependency
'@

Write-RepoFile "$svc/app/api/v1/endpoints/auth.py" @'
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair
from app.schemas.user import UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(payload, client_ip(request))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    try:
        return AuthService(db).login(str(payload.email), payload.password, client_ip(request))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return AuthService(db).refresh(payload.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    AuthService(db).logout(payload.refresh_token)
    return None
'@

Write-RepoFile "$svc/app/api/v1/endpoints/users.py" @'
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserOut, UserSelfUpdate
from app.security.dependencies import get_current_user, require_roles
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserSelfUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return UserService(db).update_self(user, payload)


@router.get("", response_model=list[UserOut])
def list_users(offset: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=200), _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return UserRepository(db).list(offset=offset, limit=limit)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminUserCreate, _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    try:
        return UserService(db).create_by_admin(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: uuid.UUID, _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: uuid.UUID, payload: AdminUserUpdate, _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    try:
        return UserService(db).update_by_admin(user_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{user_id}", response_model=UserOut)
def deactivate_user(user_id: uuid.UUID, _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    try:
        return UserService(db).deactivate(user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
'@

Write-RepoFile "$svc/app/api/v1/endpoints/roles.py" @'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.role_repository import RoleRepository
from app.schemas.role import PermissionOut, RoleCreate, RoleOut
from app.security.dependencies import require_roles

router = APIRouter(tags=["RBAC"])


@router.get("/roles", response_model=list[RoleOut])
def list_roles(_admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return RoleRepository(db).list()


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    repo = RoleRepository(db)
    if repo.get_by_name(payload.name):
        raise HTTPException(status_code=409, detail="Role already exists.")
    permissions = []
    for code in payload.permissions:
        permission = repo.get_permission(code)
        if permission is None:
            raise HTTPException(status_code=404, detail=f"Permission '{code}' does not exist.")
        permissions.append(permission)
    return repo.create_role(name=payload.name, description=payload.description, permissions=permissions)


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(_admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return RoleRepository(db).list_permissions()
'@

Write-RepoFile "$svc/app/api/v1/endpoints/health.py" @'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    return {"status": "ready"}
'@

Write-RepoFile "$svc/app/api/v1/router.py" @'
from fastapi import APIRouter

from app.api.v1.endpoints import auth, roles, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
'@

Write-RepoFile "$svc/app/main.py" @'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
'@

Write-RepoFile "$svc/app/scripts/seed_rbac.py" @'
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.entities.role import Permission, Role
from app.domain.entities.user import User
from app.security.password import hash_password

PERMISSIONS = {
    "identity.users.read": "Read user accounts",
    "identity.users.write": "Create and update user accounts",
    "identity.roles.read": "Read roles and permissions",
    "identity.roles.write": "Manage roles and permissions",
}

ROLE_PERMISSIONS = {
    "student": [],
    "teacher": [],
    "admin": list(PERMISSIONS.keys()),
}


def main():
    db = SessionLocal()
    try:
        permission_map = {}
        for code, description in PERMISSIONS.items():
            permission = db.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=description)
                db.add(permission)
                db.flush()
            permission_map[code] = permission

        role_map = {}
        for role_name, permission_codes in ROLE_PERMISSIONS.items():
            role = db.scalar(select(Role).where(Role.name == role_name))
            if role is None:
                role = Role(name=role_name, description=f"Built-in {role_name} role")
                db.add(role)
                db.flush()
            role.permissions = [permission_map[code] for code in permission_codes]
            role_map[role_name] = role

        db.commit()

        if settings.BOOTSTRAP_ADMIN_EMAIL and settings.BOOTSTRAP_ADMIN_PASSWORD:
            email = settings.BOOTSTRAP_ADMIN_EMAIL.lower()
            admin = db.scalar(select(User).where(User.email == email))
            if admin is None:
                admin = User(
                    email=email,
                    full_name=settings.BOOTSTRAP_ADMIN_NAME,
                    password_hash=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
                    is_active=True,
                    is_verified=True,
                    roles=[role_map["admin"]],
                )
                db.add(admin)
                db.commit()
                print(f"Created bootstrap admin: {email}")
            else:
                if role_map["admin"] not in admin.roles:
                    admin.roles.append(role_map["admin"])
                    db.commit()
                print(f"Bootstrap admin already exists: {email}")

        print("RBAC seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
'@

Write-RepoFile "$svc/alembic.ini" @'
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = postgresql+psycopg://identity:identity@localhost:5433/identity_db

[loggers]
keys = root,sqlalchemy,alembic
[handlers]
keys = console
[formatters]
keys = generic
[logger_root]
level = WARN
handlers = console
qualname =
[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine
[logger_alembic]
level = INFO
handlers =
qualname = alembic
[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
'@

Write-RepoFile "$svc/migrations/env.py" @'
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=settings.DATABASE_URL, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section) or {}, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'@

Write-RepoFile "$svc/migrations/script.py.mako" @'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'@

Write-RepoFile "$svc/migrations/versions/.gitkeep" ""

Write-RepoFile "$svc/Dockerfile" @'
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'@

Write-RepoFile "docker-compose.identity.yml" @'
services:
  identity-db:
    image: postgres:16
    environment:
      POSTGRES_DB: identity_db
      POSTGRES_USER: identity
      POSTGRES_PASSWORD: identity
    ports:
      - "5433:5432"
    volumes:
      - identity_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U identity -d identity_db"]
      interval: 5s
      timeout: 5s
      retries: 10

  identity-service:
    build:
      context: ./services/identity-service
    environment:
      APP_NAME: Smart Education Identity Service
      ENVIRONMENT: development
      API_V1_PREFIX: /api/v1
      DATABASE_URL: postgresql+psycopg://identity:identity@identity-db:5432/identity_db
      JWT_SECRET_KEY: CHANGE_ME_BEFORE_REAL_DEPLOYMENT
      JWT_ALGORITHM: HS256
      ACCESS_TOKEN_MINUTES: 15
      REFRESH_TOKEN_DAYS: 14
      CORS_ORIGINS: '["http://localhost:5173"]'
    ports:
      - "8001:8000"
    depends_on:
      identity-db:
        condition: service_healthy

volumes:
  identity_postgres_data:
'@

Write-RepoFile "$svc/tests/conftest.py" @'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.domain.entities.role import Role
from app.main import app

engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add_all([
        Role(name="student", description="Student"),
        Role(name="teacher", description="Teacher"),
        Role(name="admin", description="Admin"),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
'@

Write-RepoFile "$svc/tests/test_password.py" @'
from app.security.password import hash_password, verify_password


def test_password_hashing_round_trip():
    password = "StrongPassword123!"
    encoded = hash_password(password)
    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("wrong-password", encoded)
'@

Write-RepoFile "$svc/tests/test_auth_api.py" @'
def test_register_login_and_me(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "student@example.edu", "full_name": "Test Student", "password": "StrongPass123!"},
    )
    assert register.status_code == 201, register.text
    assert "student" in register.json()["roles"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.edu", "password": "StrongPass123!"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "student@example.edu"


def test_duplicate_registration_rejected(client):
    payload = {"email": "duplicate@example.edu", "full_name": "Duplicate Student", "password": "StrongPass123!"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409
'@

Write-RepoFile "$svc/README.md" @'
# Identity Service

Independent FastAPI service for authentication, user identity, refresh sessions and RBAC.

## Local URLs
- API: http://localhost:8001
- Swagger: http://localhost:8001/docs
- PostgreSQL host port: 5433

## First run
From repository root:

```powershell
docker compose -f docker-compose.identity.yml up -d identity-db
cd services/identity-service
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
alembic revision --autogenerate -m "initial identity schema"
alembic upgrade head
python -m app.scripts.seed_rbac
uvicorn app.main:app --reload --port 8001
```

Run tests with `pytest -q`.
'@

Write-Host ""
Write-Host "==============================================================="
Write-Host "Identity Service sprint files have been written successfully."
Write-Host "==============================================================="

