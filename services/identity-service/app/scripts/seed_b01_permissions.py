"""Add B01 permissions without replacing existing built-in or custom-role grants.

This is intentionally NOT the general bootstrap/demo seeder.
"""
from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain.entities.role import Permission, Role
from app.scripts.seed_rbac import PERMISSIONS


def main() -> None:
    with SessionLocal() as db:
        try:
            permission_map = {}
            for code, description in PERMISSIONS.items():
                row = db.scalar(select(Permission).where(Permission.code == code))
                if row is None:
                    row = Permission(code=code, description=description)
                    db.add(row)
                    db.flush()
                permission_map[code] = row
            admin = db.scalar(select(Role).where(Role.name == "admin"))
            if admin is not None:
                current = {entry.code: entry for entry in admin.permissions}
                current.update(permission_map)
                admin.permissions = list(current.values())
            db.commit()
            print(f"PASS: {len(permission_map)} known permission codes present; existing role grants preserved.")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()
