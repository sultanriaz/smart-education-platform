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

    def list_users(self, offset: int = 0, limit: int = 100) -> list[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def create(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        roles: list[Role],
        is_verified: bool = False,
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            password_hash=password_hash,
            roles=roles,
            is_verified=is_verified,
        )
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return self.get_by_id(user.id)

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return self.get_by_id(user.id)
