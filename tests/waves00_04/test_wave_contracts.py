"""Focused Wave 00–04 regressions runnable without a live database.

These are NOT substitutes for PostgreSQL concurrency or multi-service tests.
"""
from __future__ import annotations
import ast
import importlib.util
import sys
from pathlib import Path
from uuid import uuid4
import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_python(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_invalid_scheduling_timezone_rejected():
    from pydantic import ValidationError
    from datetime import date, time
    mod = load_python("services/scheduling-service/app/schemas/schedule.py", "wave04_schedule_schema")
    data = dict(section_id=uuid4(), weekday=3, starts_at=time(9), ends_at=time(10),
                effective_from=date(2026, 10, 1), effective_to=date(2026, 10, 31))
    with pytest.raises(ValidationError):
        mod.ScheduleCreate(**data, timezone_name="Imaginary/Invalid")
    assert mod.ScheduleCreate(**data, timezone_name="Asia/Karachi", publish=False).publish is False


def test_trimmed_blank_identity_names_rejected():
    from pydantic import ValidationError
    mod=load_python("services/identity-service/app/schemas/user.py","wave04_identity_schema")
    with pytest.raises(ValidationError):
        mod.UserSelfUpdate(full_name="  ")
    assert mod.UserSelfUpdate(full_name="  Ali Example ").full_name == "Ali Example"


def test_identity_auth_version_migration_present():
    p=ROOT/"services/identity-service/migrations/versions/0004_auth_version.py"
    assert p.is_file()
    contents=p.read_text(encoding="utf-8")
    assert '"auth_version"' in contents
    assert "0003_identity_event_runtime" in contents


def test_enrollment_delete_preserves_record_and_event():
    text=(ROOT/"services/academic-service/app/services/academic.py").read_text()
    assert "self.set_enrollment_status(record_id, EnrollmentStatus.DROPPED)" in text
    assert '"academic.enrollment_dropped"' in text


def test_search_authorization_fails_closed():
    text=(ROOT/"services/platform-service/app/services/platform_service.py").read_text()
    assert "not user_id or str(user_id) not in (owner | permitted)" in text
    assert "self.repo.search_documents(query, document_type, source_service, 200, offset)" in text


def test_attendance_roster_and_record_paging():
    text=(ROOT/"apps/frontend/src/features/teacher/teacher-api.ts").read_text()
    assert "offset=${offset}" in text
    assert "Roster exceeds the configured safe pagination limit" in text
    page=(ROOT/"apps/frontend/src/pages/teacher/TeacherClassesAttendancePage.tsx").read_text()
    assert "new Map(" in page
    assert "roster.data.map" in page


def test_admin_attendance_route_and_controls():
    router=(ROOT/"apps/frontend/src/app/AppRouter.tsx").read_text()
    page=(ROOT/"apps/frontend/src/pages/admin/AdminAttendancePage.tsx").read_text()
    assert 'path="admin/attendance"' in router
    assert "/reopen" in page and "/cancel" in page and "/history" in page


def test_audit_redaction_nested_metadata():
    path=ROOT/"services/platform-service/app/services/event_ingestion_service.py"
    node=ast.parse(path.read_text(encoding="utf-8"))
    defs=[n for n in node.body if isinstance(n, ast.FunctionDef) and n.name=="redact_audit_metadata"]
    assert len(defs)==1
    names=ast.Assign(targets=[ast.Name(id="_SENSITIVE_FIELDS", ctx=ast.Store())], value=ast.Set(elts=[ast.Constant(value="password"),ast.Constant(value="token")]))
    namespace={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[names, defs[0]],type_ignores=[])),"<redact>","exec"),namespace)
    result=namespace["redact_audit_metadata"]({"metadata": {"password": "dummy", "nested": [{"token": "dummy"}]},"ok":"fine"})
    assert result["metadata"]["password"]=="[REDACTED]"
    assert result["metadata"]["nested"][0]["token"]=="[REDACTED]"
    assert result["ok"]=="fine"


def test_prod_middleware_registered_in_services():
    services="academic attendance scheduling notification facility learning assessment reporting platform".split()
    for svc in services:
        main=ROOT/f"services/{svc}-service/app/main.py"
        text=main.read_text(encoding="utf-8")
        assert "LiveAccessMiddleware" in text, svc


def test_refresh_propagates_auth_version():
    text=(ROOT/"services/identity-service/app/services/auth_service.py").read_text()
    assert text.count("self._issue_pair(user.id, [role.name for role in user.roles], user.auth_version)") == 2


def test_admin_section_form_uses_code_field():
    page=(ROOT/"apps/frontend/src/pages/admin/AdminAcademicPage.tsx").read_text()
    assert 'label="Section code"' in page
    assert 'setSectionForm((f) => ({ ...f, code: e.target.value }))' in page
    assert 'setSectionForm((f) => ({ ...f, name: e.target.value }))' not in page


def test_admin_owner_profile_identifiers_used_in_normalizer():
    text=(ROOT/"apps/frontend/src/features/admin/normalizers.ts").read_text()
    assert 'studentUserId: s(r.student_profile_id ??' in text
    assert 'teacherUserId: s(r.teacher_profile_id ??' in text


def test_schedule_model_and_migration_accept_drafts():
    model=(ROOT/"services/scheduling-service/app/domain/models.py").read_text()
    migration=(ROOT/"services/scheduling-service/migrations/versions/0004_schedule_draft_state.py").read_text()
    assert "status IN ('DRAFT', 'ACTIVE', 'CANCELLED')" in model
    assert "status IN ('DRAFT', 'ACTIVE', 'CANCELLED')" in migration
    assert 'down_revision = "0003_scheduling_event_runtime"' in migration
