import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.transaction import transaction
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserSelfUpdate
from app.security.password import hash_password
from app.sprint18 import security_settings
from app.sprint18_security.registration import enforce_registration_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.roles = RoleRepository(db)

    def create_by_admin(self, payload: AdminUserCreate):
        enforce_registration_password(
            password=payload.password,
            email=str(payload.email),
            full_name=payload.full_name,
            settings=security_settings(),
        )
        with transaction(self.db, conflict_message="An account with this email already exists."):
            email = str(payload.email).lower()
            if self.users.get_by_email(email):
                raise ConflictError("An account with this email already exists.")
            role = self.roles.get_by_name(payload.role)
            if role is None:
                raise NotFoundError(f"Role '{payload.role}' does not exist.")
            return self.users.create(
                email=email,
                full_name=payload.full_name.strip(),
                password_hash=hash_password(payload.password),
                roles=[role],
                is_verified=True,
            )

    def update_self(self, user, payload: UserSelfUpdate):
        with transaction(self.db):
            if payload.full_name is not None:
                user.full_name = payload.full_name.strip()
            return self.users.save(user)

    def update_by_admin(self, user_id: uuid.UUID, payload: AdminUserUpdate):
        with transaction(self.db):
            return self._update_by_admin(user_id, payload)

    def _update_by_admin(self, user_id: uuid.UUID, payload: AdminUserUpdate):
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
        with transaction(self.db):
            user = self.users.get_by_id(user_id)
            if user is None:
                raise NotFoundError("User not found.")
            user.is_active = False
            return self.users.save(user)
