"""Bounded bulk contracts for authorized Platform administration jobs."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
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
    model, _, output = resource_contract(resource)
    rows = service.list(model, limit=limit, offset=offset)
    return {
        "items": [output.model_validate(row).model_dump(mode="json") for row in rows],
        "limit": limit,
        "offset": offset,
    }


def import_rows(service, resource, items):
    model, schema, output = resource_contract(resource)
    try:
        payloads = [schema.model_validate(item) for item in items]
    except ValidationError as exc:
        raise HTTPException(422, "Import row does not match the resource input schema") from exc
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
def import_data(resource: str, payload: ImportBatch, service: Service, principal: Import):
    only_platform(principal)
    return import_rows(service, resource, payload.items)
