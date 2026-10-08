from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.transaction import transaction
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.roles = RoleRepository(db)

    def create(self, payload: RoleCreate):
        with transaction(self.db, conflict_message="Role already exists."):
            if self.roles.get_by_name(payload.name):
                raise ConflictError("Role already exists.")
            permissions = []
            for code in payload.permissions:
                permission = self.roles.get_permission(code)
                if permission is None:
                    raise NotFoundError(f"Permission '{code}' does not exist.")
                permissions.append(permission)
            return self.roles.create_role(
                name=payload.name,
                description=payload.description,
                permissions=permissions,
            )
