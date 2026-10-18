"""Bounded bulk contracts for authorized Platform administration jobs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError
from smartedu_contracts import internal_auth_dependency

from app.api.dependencies import Limit, Offset, Service
from app.domain import models
from app.schemas import academic
from app.services.transaction import transaction
from app.sprint16 import internal_token_verifier

router = APIRouter(prefix="/internal", tags=["Internal data jobs"])
Export = Annotated[
    object,
    Depends(
        internal_auth_dependency(
            internal_token_verifier(),
            audience="academic-service",
            required_scopes=("academic:data:export",),
        )
    ),
]
Import = Annotated[
    object,
    Depends(
        internal_auth_dependency(
            internal_token_verifier(),
            audience="academic-service",
            required_scopes=("academic:data:import",),
        )
    ),
]
RESOURCES = {
    "departments": (models.Department, academic.DepartmentWrite, academic.DepartmentRead),
    "programs": (models.Program, academic.ProgramWrite, academic.ProgramRead),
    "academic-years": (models.AcademicYear, academic.AcademicYearWrite, academic.AcademicYearRead),
    "semesters": (models.Semester, academic.SemesterWrite, academic.SemesterRead),
    "courses": (models.Course, academic.CourseWrite, academic.CourseRead),
    "sections": (models.Section, academic.SectionWrite, academic.SectionRead),
    "students": (
        models.StudentAcademicProfile,
        academic.StudentProfileWrite,
        academic.StudentProfileRead,
    ),
    "teachers": (
        models.TeacherAcademicProfile,
        academic.TeacherProfileWrite,
        academic.TeacherProfileRead,
    ),
}


class ImportBatch(BaseModel):
    items: list[dict] = Field(min_length=1, max_length=100)


def resource_contract(resource):
    if resource not in RESOURCES:
        raise HTTPException(404, "No bulk contract for this resource; use its owner API")
    return RESOURCES[resource]


def only_platform(principal):
    if principal.service_name != "platform-service":
        raise HTTPException(403, "Only Platform may execute administration data jobs")


@router.get("/exports/{resource}")
def export_data(
    resource: str, service: Service, principal: Export, limit: Limit = 100, offset: Offset = 0
):
    only_platform(principal)
    if resource == "enrollments":
        model, output = models.Enrollment, academic.EnrollmentRead
        rows = service.list(model, limit=limit, offset=offset)
        return {"items": [output.model_validate(row).model_dump(mode="json") for row in rows], "limit": limit, "offset": offset}
    model, _, output = resource_contract(resource)
    rows = service.list(model, limit=limit, offset=offset)
    return {
        "items": [output.model_validate(row).model_dump(mode="json") for row in rows],
        "limit": limit,
        "offset": offset,
    }


def import_rows(service, resource, items, *, dry_run=False):
    model, schema, output = resource_contract(resource)
    try:
        payloads = [schema.model_validate(item) for item in items]
    except ValidationError as exc:
        raise HTTPException(422, "Import row does not match the resource input schema") from exc
    if dry_run:
        # Validate semantic references and duplicate request rows, without mutation.
        seen = set()
        from json import dumps
        for row in payloads:
            values = row.model_dump()
            digest = dumps(values, default=str, sort_keys=True)
            if digest in seen:
                raise HTTPException(422, "Duplicate import row")
            seen.add(digest)
            service._validate(model, values)
        return {"dry_run": True, "valid_rows": len(payloads), "errors": [], "imported": 0}
    rows = []
    with transaction(service.db):
        for payload in payloads:
            values = payload.model_dump()
            service._validate(model, values)
            rows.append(service.repo.add(model(**values)))
    return {
        "items": [output.model_validate(row).model_dump(mode="json") for row in rows],
        "imported": len(rows),
    }


@router.post("/imports/{resource}")
def import_data(resource: str, payload: ImportBatch, service: Service, principal: Import, dry_run: bool = Query(default=False)):
    only_platform(principal)
    if resource == "enrollments":
        if len(payload.items) == 0 or len(payload.items) > 100:
            raise HTTPException(422, "Enrollment batch must contain 1-100 rows")
        try:
            rows = [academic.EnrollmentCreate.model_validate(item) for item in payload.items]
        except ValidationError as exc:
            raise HTTPException(422, "Invalid enrollment row") from exc
        sections = {row.section_id for row in rows}
        students = [row.student_profile_id for row in rows]
        if len(sections) != 1 or len(set(students)) != len(students):
            raise HTTPException(422, "One distinct section with distinct students required")
        section_id = next(iter(sections))
        if dry_run:
            section = service.get(models.Section, section_id)
            if service.repo.enrollment_count(section_id) + len(students) > section.capacity:
                raise HTTPException(409, "Enrollment batch exceeds section capacity")
            for student_id in students:
                student = service.get(models.StudentAcademicProfile, student_id)
                service._validate_enrollment(student, section)
            return {"dry_run": True, "valid_rows": len(rows), "errors": [], "imported": 0}
        created = service.bulk_enroll(section_id, students)
        return {"imported": len(created), "items": [{"id": str(row.id)} for row in created]}
    return import_rows(service, resource, payload.items, dry_run=dry_run)
