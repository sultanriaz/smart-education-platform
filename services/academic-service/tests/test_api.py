from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.models import Section
from app.schemas.academic import SectionWrite
from app.services.academic import AcademicService


def test_full_admin_workflow(client):
    def create(path, payload):
        response = client.post(f"/api/v1/{path}", json=payload)
        assert response.status_code == 201, response.text
        record = response.json()
        assert record["id"] and record["created_at"] and record["updated_at"]
        return record

    department = create("departments", {"code": "CS", "name": "Computer Science"})
    program = create(
        "programs",
        {
            "code": "BSCS",
            "name": "BSCS",
            "duration_semesters": 8,
            "department_id": department["id"],
        },
    )
    year = create(
        "academic-years",
        {"code": "2026", "name": "2026/27", "starts_on": "2026-08-01", "ends_on": "2027-07-31"},
    )
    semester = create(
        "semesters",
        {
            "academic_year_id": year["id"],
            "number": 1,
            "name": "Fall",
            "starts_on": "2026-08-15",
            "ends_on": "2026-12-31",
        },
    )
    course = create(
        "courses",
        {
            "program_id": program["id"],
            "code": "CS101",
            "title": "Computing",
            "credits": 3,
            "semester_number": 1,
        },
    )
    section = create(
        "sections",
        {"course_id": course["id"], "semester_id": semester["id"], "code": "A", "capacity": 20},
    )
    student = create(
        "student-profiles",
        {
            "external_user_id": str(uuid4()),
            "student_number": "S1",
            "program_id": program["id"],
            "admission_year_id": year["id"],
            "current_semester": 1,
        },
    )
    teacher = create(
        "teacher-profiles",
        {
            "external_user_id": str(uuid4()),
            "employee_number": "T1",
            "department_id": department["id"],
            "designation": "Lecturer",
        },
    )
    enrollment = create(
        "enrollments", {"student_profile_id": student["id"], "section_id": section["id"]}
    )
    assignment = create(
        "teacher-assignments", {"teacher_profile_id": teacher["id"], "section_id": section["id"]}
    )
    roster = client.get(f"/api/v1/sections/{section['id']}/roster").json()
    assert roster["total"] == 1
    assert roster["students"][0]["external_user_id"] == student["external_user_id"]
    assert (
        client.patch(
            f"/api/v1/enrollments/{enrollment['id']}", json={"status": "dropped"}
        ).status_code
        == 200
    )
    assert client.get(f"/api/v1/sections/{section['id']}/roster").json()["total"] == 0
    assert (
        client.patch(
            f"/api/v1/teacher-assignments/{assignment['id']}", json={"is_active": False}
        ).status_code
        == 200
    )
    for path, record in [
        ("enrollments", enrollment),
        ("teacher-assignments", assignment),
        ("sections", section),
        ("student-profiles", student),
        ("teacher-profiles", teacher),
        ("courses", course),
        ("semesters", semester),
        ("programs", program),
        ("academic-years", year),
        ("departments", department),
    ]:
        assert client.get(f"/api/v1/{path}/{record['id']}").status_code == 200
        assert len(client.get(f"/api/v1/{path}").json()) == 1
        if path == "enrollments":
            assert client.delete(f"/api/v1/{path}/{record['id']}").status_code == 204
            historical = client.get(f"/api/v1/{path}/{record['id']}")
            assert historical.status_code == 200
            assert historical.json()["status"] == "dropped"
            assert client.get(f"/api/v1/sections/{section['id']}/roster").json()["total"] == 0
        elif path in ("teacher-assignments", "teacher-profiles"):
            assert client.delete(f"/api/v1/{path}/{record['id']}").status_code == 204
            assert client.get(f"/api/v1/{path}/{record['id']}").status_code == 404
        else:
            # Preserve parents referenced by retained enrollment history.
            assert client.get(f"/api/v1/{path}/{record['id']}").status_code == 200


@pytest.mark.parametrize(
    ("path", "attribute", "changes"),
    [
        ("departments", "department", {"name": "School of Computing"}),
        ("programs", "program", {"name": "Computer Science Degree"}),
        ("academic-years", "year", {"name": "Academic Year 2026"}),
        ("semesters", "semester", {"name": "Autumn"}),
        ("courses", "course", {"title": "Introduction to Computing"}),
        ("sections", "section", {"capacity": 30}),
        ("student-profiles", "students", {"current_semester": 2}),
        ("teacher-profiles", "teacher", {"designation": "Professor"}),
    ],
)
def test_admin_replace(client, academic, path, attribute, changes):
    record = getattr(academic, attribute)
    if attribute == "students":
        record = record[0]
    endpoint = f"/api/v1/{path}/{record.id}"
    payload = client.get(endpoint).json()
    for key in ("id", "created_at", "updated_at"):
        payload.pop(key)
    payload.update(changes)
    response = client.put(endpoint, json=payload)
    assert response.status_code == 200, response.text
    assert all(response.json()[key] == value for key, value in changes.items())


def test_teacher_reads_only_assigned_resources(client, token, academic, db):
    service = AcademicService(db)
    enrollment = service.enroll(academic.students[0].id, academic.section.id)
    assignment = service.assign(academic.teacher.id, academic.section.id)
    other_section = service.create(
        Section,
        SectionWrite(
            course_id=academic.course.id,
            semester_id=academic.semester.id,
            code="B",
            capacity=10,
        ),
    )
    client.headers["Authorization"] = (
        f"Bearer {token(subject=academic.teacher.external_user_id, roles=['teacher'])}"
    )
    for path in ("departments", "programs", "academic-years", "semesters", "courses"):
        assert client.get(f"/api/v1/{path}").status_code == 200
    assert client.get("/api/v1/teacher-profiles/me").json()["id"] == str(academic.teacher.id)
    assert client.get("/api/v1/sections").json()[0]["id"] == str(academic.section.id)
    assert len(client.get("/api/v1/sections").json()) == 1
    assert client.get(f"/api/v1/sections/{academic.section.id}").status_code == 200
    roster = client.get(f"/api/v1/sections/{academic.section.id}/roster").json()
    assert roster["students"][0]["enrollment_id"] == str(enrollment.id)
    assert client.get(f"/api/v1/sections/{other_section.id}").status_code == 403
    assert client.get(f"/api/v1/sections/{other_section.id}/roster").status_code == 403
    assert client.get("/api/v1/teacher-assignments").json()[0]["id"] == str(assignment.id)
    assert client.get(f"/api/v1/teacher-assignments/{assignment.id}").status_code == 200
    for path in ("student-profiles", "teacher-profiles", "enrollments"):
        assert client.get(f"/api/v1/{path}").status_code == 403
    for path, record_id in (
        ("student-profiles", academic.students[0].id),
        ("teacher-profiles", academic.teacher.id),
        ("enrollments", enrollment.id),
    ):
        assert client.get(f"/api/v1/{path}/{record_id}").status_code == 403
    service.set_assignment_active(assignment.id, False)
    assert client.get(f"/api/v1/sections/{academic.section.id}/roster").status_code == 403
    assert client.get("/api/v1/sections").json() == []
    assert client.get("/api/v1/teacher-assignments").json() == []


@pytest.mark.parametrize(
    "path",
    [
        "departments",
        "programs",
        "academic-years",
        "semesters",
        "courses",
        "sections",
        "student-profiles",
        "teacher-profiles",
        "enrollments",
        "teacher-assignments",
    ],
)
def test_teacher_cannot_mutate(client, token, path):
    client.headers["Authorization"] = f"Bearer {token(roles=['teacher'])}"
    assert client.post(f"/api/v1/{path}", json={}).status_code == 403
    assert client.put(f"/api/v1/{path}/{uuid4()}", json={}).status_code in (403, 405)
    assert client.delete(f"/api/v1/{path}/{uuid4()}").status_code == 403


def test_teacher_cannot_change_enrollment_or_assignment(client, token):
    client.headers["Authorization"] = f"Bearer {token(roles=['teacher'])}"
    for path, payload in (
        ("enrollments", {"status": "dropped"}),
        ("teacher-assignments", {"is_active": False}),
    ):
        assert client.patch(f"/api/v1/{path}/{uuid4()}", json=payload).status_code == 403


def test_teacher_cannot_read_another_assignment(client, token, academic, db):
    assignment = AcademicService(db).assign(academic.teacher.id, academic.section.id)
    client.headers["Authorization"] = f"Bearer {token(roles=['teacher'])}"
    assert client.get(f"/api/v1/teacher-assignments/{assignment.id}").status_code == 404
    assert client.get(f"/api/v1/sections/{academic.section.id}/roster").status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"code": "", "name": "Valid"},
        {"code": "CS", "name": "   "},
        {"code": "CS", "name": "Valid", "unexpected": 1},
    ],
)
def test_invalid_catalog_input(client, payload):
    assert client.post("/api/v1/departments", json=payload).status_code == 422


def test_invalid_dates_and_missing_parent(client):
    assert (
        client.post(
            "/api/v1/academic-years",
            json={
                "code": "BAD",
                "name": "Bad",
                "starts_on": "2027-01-01",
                "ends_on": "2026-01-01",
            },
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/programs",
            json={
                "department_id": str(uuid4()),
                "code": "MISSING",
                "name": "Missing",
                "duration_semesters": 8,
            },
        ).status_code
        == 404
    )


def test_pagination_and_duplicate_conflicts(client, academic):
    assert len(client.get("/api/v1/student-profiles?limit=1&offset=1").json()) == 1
    assert client.get("/api/v1/departments?limit=101").status_code == 422
    assert client.get("/api/v1/departments?offset=-1").status_code == 422
    assert (
        client.post("/api/v1/departments", json={"code": "CS", "name": "Duplicate"}).status_code
        == 409
    )
    assert client.get("/api/v1/departments").status_code == 200
    assert client.delete(f"/api/v1/departments/{academic.department.id}").status_code == 409


def test_roster_pagination_and_filtering(client, academic, db):
    service = AcademicService(db)
    for student in academic.students[:2]:
        service.enroll(student.id, academic.section.id)
    roster = client.get(f"/api/v1/sections/{academic.section.id}/roster?limit=1&offset=1").json()
    assert roster["total"] == 2
    assert roster["limit"] == 1 and roster["offset"] == 1
    assert [row["student_number"] for row in roster["students"]] == ["2026-002"]
    assert (
        len(client.get(f"/api/v1/enrollments?student_profile_id={academic.students[0].id}").json())
        == 1
    )
