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
