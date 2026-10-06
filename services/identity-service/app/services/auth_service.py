import uuid

import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.db.transaction import transaction
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
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)
        self.tokens = TokenRepository(db)
        self.audit = AuditRepository(db)

    def register(self, payload: UserRegister, ip_address: str | None = None):
        with transaction(self.db, conflict_message="An account with this email already exists."):
            email = str(payload.email).lower()
            if self.users.get_by_email(email):
                raise ConflictError("An account with this email already exists.")
            student_role = self.roles.get_by_name("student")
            if student_role is None:
                raise RuntimeError("RBAC is not seeded. Run the seed command first.")
            user = self.users.create(
                email=email,
                full_name=payload.full_name.strip(),
                password_hash=hash_password(payload.password),
                roles=[student_role],
            )
            self.audit.record(action="user.registered", user_id=user.id, ip_address=ip_address)
        return user

    def login(self, email: str, password: str, ip_address: str | None = None) -> TokenPair:
        pair = None
        with transaction(self.db):
            user = self.users.get_by_email(email.lower())
            if (
                user is None
                or not user.is_active
                or not verify_password(password, user.password_hash)
            ):
                self.audit.record(
                    action="auth.login_failed",
                    user_id=user.id if user else None,
                    ip_address=ip_address,
                    details={"email": email.lower()},
                )
            else:
                pair = self._issue_pair(user.id, [role.name for role in user.roles])
                self.audit.record(
                    action="auth.login_succeeded",
                    user_id=user.id,
                    ip_address=ip_address,
                )
        # Rejected logins still commit their security audit record.
        if pair is None:
            raise AuthenticationError("Invalid email or password.")
        return pair

    def refresh(self, refresh_token: str) -> TokenPair:
        payload = self._decode_refresh(refresh_token)
        user_id = uuid.UUID(payload["sub"])
        with transaction(self.db):
            user = self.users.get_by_id(user_id)
            if user is None or not user.is_active:
                raise AuthenticationError("User account is unavailable.")
            if not self.tokens.consume(jti=payload["jti"], user_id=user_id):
                raise AuthenticationError("Refresh token is expired or revoked.")
            pair = self._issue_pair(user.id, [role.name for role in user.roles])
            self.audit.record(action="auth.refreshed", user_id=user.id)
        return pair

    def logout(self, refresh_token: str) -> None:
        try:
            payload = self._decode_refresh(refresh_token)
        except AuthenticationError:
            return
        with transaction(self.db):
            user_id = uuid.UUID(payload["sub"])
            if self.tokens.consume(jti=payload["jti"], user_id=user_id):
                self.audit.record(action="auth.logged_out", user_id=user_id)

    @staticmethod
    def _decode_refresh(token: str) -> dict:
        try:
            return decode_token(token, token_type="refresh")
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid refresh token.") from exc

    def _issue_pair(self, user_id: uuid.UUID, roles: list[str]) -> TokenPair:
        access_token, _ = create_access_token(user_id, roles)
        refresh_token, jti, refresh_expires_at = create_refresh_token(user_id, roles)
        self.tokens.create(user_id=user_id, jti=jti, expires_at=refresh_expires_at)
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_MINUTES * 60,
        )
