from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.role import Permission, Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).options(selectinload(Role.permissions)).where(Role.name == name.lower())
        return self.db.scalar(stmt)

    def list_roles(self) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.name)
        return list(self.db.scalars(stmt).unique().all())

    def list_permissions(self) -> list[Permission]:
        return list(self.db.scalars(select(Permission).order_by(Permission.code)).all())

    def get_permission(self, code: str) -> Permission | None:
        return self.db.scalar(select(Permission).where(Permission.code == code))

    def create_role(
        self, *, name: str, description: str | None, permissions: list[Permission]
    ) -> Role:
        role = Role(name=name.lower(), description=description, permissions=permissions)
        self.db.add(role)
        self.db.flush()
        self.db.refresh(role)
        return self.get_by_name(role.name)
