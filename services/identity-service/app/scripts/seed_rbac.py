from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.entities.role import Permission, Role
from app.domain.entities.user import User
from app.security.password import hash_password

PERMISSIONS = {
    'academic.records.read': 'List and inspect academic records',
    'academic.records.write': 'Manage academic records and manual reconciliations',
    'attendance.records.manage': 'Manage attendance sessions and records',
    'assessment.authoring.manage': 'Author assessments within ownership restrictions',
    'assessment.grading.manage': 'Grade assessment submissions',
    'assessment.reviews.read': 'Read teacher assessment reviews within ownership restrictions',
    'learning.resources.manage': 'Manage learning resources within ownership restrictions',
    'learning.categories.manage': 'Manage learning categories',
    'notification.admin.manage': 'Manage notification administration',
    'notification.announcements.manage': 'Publish teacher announcements',
    'reporting.reports.read': 'Read institution-wide reporting',
    'reporting.snapshots.write': 'Create reporting snapshots',
    'platform.admin.manage': 'Manage platform administration',

    "identity.users.read": "Read user accounts",
    "identity.users.write": "Create and update user accounts",
    "identity.roles.read": "Read roles and permissions",
    "identity.roles.write": "Manage roles and permissions",
    "scheduling.schedules.manage": "Manage all schedules and publish timetables",
    "facility.facilities.manage": "Manage facilities and equipment",
    "facility.bookings.review": "Review and list facility bookings",
    "facility.blocks.manage": "Manage facility availability blocks",

    "finance.fees.read": "Read fee structures",
    "finance.fees.manage": "Manage fee structures and components",
    "finance.scholarships.read": "Read scholarships and awards",
    "finance.scholarships.manage": "Manage scholarships and grant awards",
    "finance.accounts.read": "Read student financial accounts",
    "finance.invoices.read": "Read student fee invoices",
    "finance.invoices.manage": "Generate and manage student invoices and penalties",
    "finance.payments.read": "Read payment transactions and receipts",
    "finance.payments.manage": "Record and manage payments",
    "finance.refunds.read": "Read refund requests",
    "finance.refunds.manage": "Request and process fee refunds",
    "finance.refunds.approve": "Approve student fee refund decisions",
    "finance.reconciliation.read": "Read bank reconciliation batches",
    "finance.reconciliation.manage": "Perform bank reconciliation matching",
    "finance.accounting.read": "Read chart of accounts and general ledger",
    "finance.accounting.manage": "Manage chart of accounts and journal entries",
    "finance.reports.read": "Read institutional finance reports",
    "finance.portal.read": "Student financial portal self-service",

    "payroll.profiles.read": "Read employee payroll profiles",
    "payroll.profiles.manage": "Manage employee payroll profiles",
    "payroll.structures.read": "Read employee salary structures",
    "payroll.structures.manage": "Manage employee salary structures and components",
    "payroll.periods.read": "Read payroll periods",
    "payroll.periods.manage": "Manage payroll periods",
    "payroll.runs.read": "Read payroll calculation runs",
    "payroll.runs.manage": "Calculate and review monthly payroll runs",
    "payroll.runs.approve": "Approve monthly payroll runs",
    "payroll.disbursement.read": "Read salary disbursement batches",
    "payroll.disbursement.manage": "Execute salary disbursements",
    "payroll.payslips.read": "Read all employee payslips",
    "payroll.my.payslips": "Read own employee payslips",
    "payroll.reports.read": "Read payroll reports",
}

ROLE_PERMISSIONS = {
    "student": ["finance.portal.read"],
    "teacher": ["payroll.my.payslips"],
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
