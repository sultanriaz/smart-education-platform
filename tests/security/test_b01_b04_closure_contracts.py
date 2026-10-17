"""Fail on permission drift or missing durable Identity lifecycle wiring."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[2]


def text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_all_extended_grants_declared_in_identity_seed():
    tree = ast.parse(text("services/identity-service/app/scripts/seed_rbac.py"))
    permissions = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "PERMISSIONS" for t in n.targets))
    codes = {key.value for key in permissions.keys}
    expected = {
        "academic.records.read", "academic.records.write", "attendance.records.manage",
        "assessment.authoring.manage", "assessment.grading.manage", "assessment.reviews.read",
        "learning.resources.manage", "learning.categories.manage", "notification.admin.manage",
        "notification.announcements.manage", "reporting.reports.read", "reporting.snapshots.write",
        "platform.admin.manage",
    }
    assert expected.issubset(codes)
    assert len(codes) == len(set(codes))


def test_scope_authorization_present_in_each_of_seven_domains():
    required = {
        "academic": ("app/security/dependencies.py", "live_permission"),
        "attendance": ("app/security/dependencies.py", "live_permission"),
        "assessment": ("app/security/auth.py", "live_permission"),
        "learning": ("app/security/auth.py", "live_permission"),
        "notification": ("app/security/authorization.py", "live_permission"),
        "reporting": ("app/security/auth.py", "live_permission"),
        "platform": ("app/security/auth.py", "live_permission"),
    }
    for name, (path, symbol) in required.items():
        source = text(f"services/{name}-service/{path}")
        assert symbol in source, f"Missing fail-closed scope verification in {name}"
        ast.parse(source)


def test_identity_event_is_transactional_and_academic_consumes():
    user = text("services/identity-service/app/services/user_service.py")
    assert 'event_type="identity.account_eligibility_changed"' in user
    assert "self._eligibility_event(user)" in user
    runtime = text("libs/python/smartedu_infra/smartedu_infra/runtime.py")
    assert '"academic-service": ("identity.account_eligibility_changed",)' in runtime
    worker = text("services/academic-service/app/event_worker.py")
    assert "IdentityEligibilityInbox" in worker and "handler=handle_identity_eligibility" in worker


def test_reactivation_never_undoes_manual_academic_disablement():
    models = text("services/academic-service/app/domain/models.py")
    migration = text("services/academic-service/migrations/versions/0004_identity_lifecycle_inbox.py")
    service = text("services/academic-service/app/services/academic.py")
    assert models.count("identity_suspended: Mapped[bool]") == 2
    assert 'for table in ("student_academic_profiles", "teacher_academic_profiles")' in migration
    assert 'student.identity_suspended' in service
    assert 'teacher.identity_suspended' in service


def test_academic_read_scope_does_not_imply_write_admin():
    source = (ROOT / "services/academic-service/app/security/jwt.py").read_text()
    assert '"academic.records.write" in self.permissions' in source
    assert 'bool(self.permissions & {"academic.records.read", "academic.records.write"})' not in source
