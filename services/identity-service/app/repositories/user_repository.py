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

    def get_by_identifier(self, identifier: str) -> User | None:
        clean = identifier.strip().lower()
        if not clean:
            return None

        # 1. Direct email lookup
        user = self.get_by_email(clean)
        if user:
            return user

        # 2. Known institutional aliases & demo roles
        if clean in ("admin", "administrator", "sysadmin"):
            user = self.get_by_email("admin@smartedu.local")
            if user:
                return user

        if clean in ("teacher", "faculty", "fac-101", "emp-101", "munir", "dr-munir", "drmunir"):
            for cand in ("teacher@smartedu.local", "teacher@demo.example.edu"):
                user = self.get_by_email(cand)
                if user:
                    return user

        if clean in ("student", "155", "bcs-155", "bcs155", "stu-155", "fa21-bcs-155", "sp21-bcs-155", "stu-001"):
            for cand in ("student@smartedu.local", "student@demo.example.edu", "student_demo@example.com"):
                user = self.get_by_email(cand)
                if user:
                    return user

        # 3. Flexible resolution by prefix, domain, or name
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(
                (User.email.ilike(f"{clean}@%"))
                | (User.email.ilike(f"%{clean}%"))
                | (User.full_name.ilike(f"%{clean}%"))
            )
            .order_by(User.is_active.desc(), User.created_at.desc())
        )
        return self.db.scalars(stmt).first()

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
