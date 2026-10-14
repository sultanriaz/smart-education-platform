"""B04: trust Identity-owned eligibility, not Academic's stale active bit."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

import httpx
import pytest

from app.api.dependencies import get_identity_accounts
from app.core.exceptions import ConflictError, DomainError
from app.domain.models import Enrollment, EnrollmentStatus, StudentAcademicProfile, TeacherAssignment
from app.services.academic import AcademicService
from app.services.identity_accounts import IdentityAccountClient


class SignedTestIssuer:
    def __init__(self):
        self.issued = []

    def issue(self, **kwargs):
        self.issued.append(kwargs)
        return "fake-signed-service-token"


@pytest.fixture
def owner():
    state = {}
    calls = []
    signer = SignedTestIssuer()

    def serve(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.headers["Authorization"] == "Bearer fake-signed-service-token"
        uid = request.url.path.rsplit("/", 1)[-1]
        data = state.get(uid)
        if data == "down":
            return httpx.Response(503)
        if data is None:
            return httpx.Response(404)
        return httpx.Response(200, json={"id": uid, "is_active": data[0], "roles": data[1], "auth_version": data[2]})

    checker = IdentityAccountClient(
        "http://identity.internal:8000", signer=signer, transport=httpx.MockTransport(serve)
    )
    return SimpleNamespace(state=state, signer=signer, calls=calls, checker=checker)


def test_owner_client_checks_missing_wrong_role_inactive_reactivation_and_outage(owner):
    uid = uuid4()
    with pytest.raises(ConflictError, match="does not exist"):
        owner.checker.require_eligible(uid, "student")
    owner.state[str(uid)] = (True, ["teacher"], 1)
    with pytest.raises(ConflictError, match="active student"):
        owner.checker.require_eligible(uid, "student")
    owner.state[str(uid)] = (False, ["student"], 2)
    with pytest.raises(ConflictError, match="active student"):
        owner.checker.require_eligible(uid, "student")
    owner.state[str(uid)] = (True, ["student"], 3)
    assert owner.checker.require_eligible(uid, "student").auth_version == 3
    owner.state[str(uid)] = "down"
    with pytest.raises(DomainError) as error:
        owner.checker.require_eligible(uid, "student")
    assert error.value.status_code == 503
    assert all(x == {"audience": "identity-service", "scopes": ("identity:academic:read",)} for x in owner.signer.issued)
    assert all("/api/v1/internal/users/academic-accounts/" in req.url.path for req in owner.calls)


def test_invalid_owner_response_fails_closed(owner):
    uid = uuid4()
    owner.state[str(uid)] = (True, ["student"], 1)
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"id": str(uuid4()), "roles": ["student"], "is_active": True, "auth_version": 1}))
    owner.checker.transport = transport
    with pytest.raises(DomainError) as error:
        owner.checker.require_eligible(uid, "student")
    assert error.value.status_code == 503


def test_public_api_checks_identity_at_profile_creation(client, academic, owner):
    # Already seeded academic profiles stay; new links require authoritative owner state.
    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    uid = uuid4()
    body = {
        "external_user_id": str(uid),
        "student_number": "S-new",
        "program_id": str(academic.program.id),
        "admission_year_id": str(academic.year.id),
        "current_semester": 1,
    }
    url = "/api/v1/student-profiles"
    assert client.post(url, json=body).status_code == 409
    owner.state[str(uid)] = (True, ["teacher"], 0)
    assert client.post(url, json=body).status_code == 409
    owner.state[str(uid)] = (True, ["student"], 0)
    response = client.post(url, json=body)
    assert response.status_code == 201, response.text
    assert response.json()["external_user_id"] == str(uid)

    teacher_uid = uuid4()
    teacher_body = {
        "external_user_id": str(teacher_uid),
        "employee_number": "T-new",
        "department_id": str(academic.department.id),
        "designation": "Lecturer",
    }
    owner.state[str(teacher_uid)] = (False, ["teacher"], 2)
    assert client.post("/api/v1/teacher-profiles", json=teacher_body).status_code == 409
    owner.state[str(teacher_uid)] = (True, ["teacher"], 3)
    assert client.post("/api/v1/teacher-profiles", json=teacher_body).status_code == 201


def test_existing_profiles_cannot_start_new_relationships_after_identity_change(client, academic, owner, db):
    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    student = academic.students[0]
    teacher = academic.teacher
    owner.state[str(student.external_user_id)] = (False, ["student"], 2)
    owner.state[str(teacher.external_user_id)] = (True, ["student"], 3)
    enrollment_count = db.query(Enrollment).count()
    assignment_count = db.query(TeacherAssignment).count()

    enroll_url = "/api/v1/enrollments"
    enroll = {"student_profile_id": str(student.id), "section_id": str(academic.section.id)}
    assert client.post(enroll_url, json=enroll).status_code == 409
    assignment_url = "/api/v1/teacher-assignments"
    assignment = {"teacher_profile_id": str(teacher.id), "section_id": str(academic.section.id)}
    assert client.post(assignment_url, json=assignment).status_code == 409
    assert db.query(Enrollment).count() == enrollment_count
    assert db.query(TeacherAssignment).count() == assignment_count

    owner.state[str(student.external_user_id)] = (True, ["student"], 4)
    owner.state[str(teacher.external_user_id)] = (True, ["teacher"], 4)
    assert client.post(enroll_url, json=enroll).status_code == 201
    assert client.post(assignment_url, json=assignment).status_code == 201
    assert db.query(Enrollment).filter(Enrollment.status == EnrollmentStatus.ENROLLED).count() == 1


def test_reactivation_requires_current_identity_state(client, academic, owner):
    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    student = academic.students[2]
    body = {
        "external_user_id": str(student.external_user_id),
        "student_number": student.student_number,
        "program_id": str(student.program_id),
        "admission_year_id": str(student.admission_year_id),
        "current_semester": student.current_semester,
        "is_active": False,
    }
    url = f"/api/v1/student-profiles/{student.id}"
    assert client.put(url, json=body).status_code == 200
    body["is_active"] = True
    owner.state[str(student.external_user_id)] = (False, ["student"], 2)
    assert client.put(url, json=body).status_code == 409
    owner.state[str(student.external_user_id)] = (True, ["student"], 3)
    assert client.put(url, json=body).status_code == 200


def test_admin_reconciliation_disables_invalid_profiles_and_keeps_enrollment_history(client, academic, owner, db):
    from app.domain.models import OutboxEvent, TeacherAcademicProfile

    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    student = academic.students[0]
    teacher = academic.teacher
    owner.state[str(student.external_user_id)] = (True, ["student"], 0)
    owner.state[str(teacher.external_user_id)] = (True, ["teacher"], 0)
    enroll = client.post(
        "/api/v1/enrollments",
        json={"student_profile_id": str(student.id), "section_id": str(academic.section.id)},
    )
    assignment = client.post(
        "/api/v1/teacher-assignments",
        json={"teacher_profile_id": str(teacher.id), "section_id": str(academic.section.id)},
    )
    assert enroll.status_code == 201, enroll.text
    assert assignment.status_code == 201, assignment.text
    before = db.query(OutboxEvent).count()

    owner.state[str(student.external_user_id)] = (False, ["student"], 1)
    owner.state[str(teacher.external_user_id)] = (True, ["student"], 2)
    student_url = f"/api/v1/identity-reconciliation/{student.external_user_id}"
    teacher_url = f"/api/v1/identity-reconciliation/{teacher.external_user_id}"
    response = client.post(student_url)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "student_profiles_disabled": 1, "teacher_profiles_disabled": 0,
        "enrollments_dropped": 1, "assignments_disabled": 0,
    }
    response = client.post(teacher_url)
    assert response.status_code == 200, response.text
    assert response.json() == {
        "student_profiles_disabled": 0, "teacher_profiles_disabled": 1,
        "enrollments_dropped": 0, "assignments_disabled": 1,
    }
    db.expire_all()
    assert db.get(StudentAcademicProfile, student.id).is_active is False
    assert db.get(TeacherAcademicProfile, teacher.id).is_active is False
    assert db.get(Enrollment, UUID(enroll.json()["id"])).status == EnrollmentStatus.DROPPED
    assert db.get(TeacherAssignment, UUID(assignment.json()["id"])).is_active is False
    assert db.query(OutboxEvent).count() == before + 1
    assert client.get(f"/api/v1/enrollments/{enroll.json()['id']}").status_code == 200
    assert client.post(student_url).json()["enrollments_dropped"] == 0
    assert client.post(teacher_url).json()["assignments_disabled"] == 0
    assert db.query(OutboxEvent).count() == before + 1


def test_admin_reconciliation_preserves_valid_accounts(client, academic, owner, db):
    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    student = academic.students[0]
    owner.state[str(student.external_user_id)] = (True, ["student"], 7)
    response = client.post(f"/api/v1/identity-reconciliation/{student.external_user_id}")
    assert response.status_code == 200
    assert all(count == 0 for count in response.json().values())
    db.expire_all()
    assert db.get(StudentAcademicProfile, student.id).is_active is True


def test_reconciliation_denies_non_admin(client, academic, owner, token):
    client.app.dependency_overrides[get_identity_accounts] = lambda: owner.checker
    client.headers["Authorization"] = f"Bearer {token(roles=['student'])}"
    response = client.post(f"/api/v1/identity-reconciliation/{academic.students[0].external_user_id}")
    assert response.status_code == 403
    assert owner.calls == []
