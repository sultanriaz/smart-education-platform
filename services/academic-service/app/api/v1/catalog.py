from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Admin, Limit, Offset, Service, Staff
from app.domain.models import AcademicYear, Course, Department, Program, Semester
from app.schemas.academic import (
    AcademicYearRead,
    AcademicYearWrite,
    CourseRead,
    CourseWrite,
    DepartmentRead,
    DepartmentWrite,
    ProgramRead,
    ProgramWrite,
    SemesterRead,
    SemesterWrite,
)

router = APIRouter(tags=["catalog"])


@router.get("/departments", response_model=list[DepartmentRead])
def list_departments(
    service: Service, _principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[DepartmentRead]:
    return [
        DepartmentRead.model_validate(row)
        for row in service.list(Department, limit=limit, offset=offset)
    ]


@router.post("/departments", response_model=DepartmentRead, status_code=201)
def create_departments(payload: DepartmentWrite, service: Service, _admin: Admin) -> DepartmentRead:
    return DepartmentRead.model_validate(service.create(Department, payload))


@router.get("/departments/{record_id}", response_model=DepartmentRead)
def get_departments(record_id: UUID, service: Service, _principal: Staff) -> DepartmentRead:
    return DepartmentRead.model_validate(service.get(Department, record_id))


@router.put("/departments/{record_id}", response_model=DepartmentRead)
def replace_departments(
    record_id: UUID, payload: DepartmentWrite, service: Service, _admin: Admin
) -> DepartmentRead:
    return DepartmentRead.model_validate(service.replace(Department, record_id, payload))


@router.delete("/departments/{record_id}", status_code=204)
def delete_departments(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Department, record_id)
    return Response(status_code=204)


@router.get("/programs", response_model=list[ProgramRead])
def list_programs(
    service: Service, _principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[ProgramRead]:
    return [
        ProgramRead.model_validate(row) for row in service.list(Program, limit=limit, offset=offset)
    ]


@router.post("/programs", response_model=ProgramRead, status_code=201)
def create_programs(payload: ProgramWrite, service: Service, _admin: Admin) -> ProgramRead:
    return ProgramRead.model_validate(service.create(Program, payload))


@router.get("/programs/{record_id}", response_model=ProgramRead)
def get_programs(record_id: UUID, service: Service, _principal: Staff) -> ProgramRead:
    return ProgramRead.model_validate(service.get(Program, record_id))


@router.put("/programs/{record_id}", response_model=ProgramRead)
def replace_programs(
    record_id: UUID, payload: ProgramWrite, service: Service, _admin: Admin
) -> ProgramRead:
    return ProgramRead.model_validate(service.replace(Program, record_id, payload))


@router.delete("/programs/{record_id}", status_code=204)
def delete_programs(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Program, record_id)
    return Response(status_code=204)


@router.get("/academic-years", response_model=list[AcademicYearRead])
def list_academic_years(
    service: Service, _principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[AcademicYearRead]:
    return [
        AcademicYearRead.model_validate(row)
        for row in service.list(AcademicYear, limit=limit, offset=offset)
    ]


@router.post("/academic-years", response_model=AcademicYearRead, status_code=201)
def create_academic_years(
    payload: AcademicYearWrite, service: Service, _admin: Admin
) -> AcademicYearRead:
    return AcademicYearRead.model_validate(service.create(AcademicYear, payload))


@router.get("/academic-years/{record_id}", response_model=AcademicYearRead)
def get_academic_years(record_id: UUID, service: Service, _principal: Staff) -> AcademicYearRead:
    return AcademicYearRead.model_validate(service.get(AcademicYear, record_id))


@router.put("/academic-years/{record_id}", response_model=AcademicYearRead)
def replace_academic_years(
    record_id: UUID, payload: AcademicYearWrite, service: Service, _admin: Admin
) -> AcademicYearRead:
    return AcademicYearRead.model_validate(service.replace(AcademicYear, record_id, payload))


@router.delete("/academic-years/{record_id}", status_code=204)
def delete_academic_years(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(AcademicYear, record_id)
    return Response(status_code=204)


@router.get("/semesters", response_model=list[SemesterRead])
def list_semesters(
    service: Service, _principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[SemesterRead]:
    return [
        SemesterRead.model_validate(row)
        for row in service.list(Semester, limit=limit, offset=offset)
    ]


@router.post("/semesters", response_model=SemesterRead, status_code=201)
def create_semesters(payload: SemesterWrite, service: Service, _admin: Admin) -> SemesterRead:
    return SemesterRead.model_validate(service.create(Semester, payload))


@router.get("/semesters/{record_id}", response_model=SemesterRead)
def get_semesters(record_id: UUID, service: Service, _principal: Staff) -> SemesterRead:
    return SemesterRead.model_validate(service.get(Semester, record_id))


@router.put("/semesters/{record_id}", response_model=SemesterRead)
def replace_semesters(
    record_id: UUID, payload: SemesterWrite, service: Service, _admin: Admin
) -> SemesterRead:
    return SemesterRead.model_validate(service.replace(Semester, record_id, payload))


@router.delete("/semesters/{record_id}", status_code=204)
def delete_semesters(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Semester, record_id)
    return Response(status_code=204)


@router.get("/courses", response_model=list[CourseRead])
def list_courses(
    service: Service, _principal: Staff, limit: Limit = 50, offset: Offset = 0
) -> list[CourseRead]:
    return [
        CourseRead.model_validate(row) for row in service.list(Course, limit=limit, offset=offset)
    ]


@router.post("/courses", response_model=CourseRead, status_code=201)
def create_courses(payload: CourseWrite, service: Service, _admin: Admin) -> CourseRead:
    return CourseRead.model_validate(service.create(Course, payload))


@router.get("/courses/{record_id}", response_model=CourseRead)
def get_courses(record_id: UUID, service: Service, _principal: Staff) -> CourseRead:
    return CourseRead.model_validate(service.get(Course, record_id))


@router.put("/courses/{record_id}", response_model=CourseRead)
def replace_courses(
    record_id: UUID, payload: CourseWrite, service: Service, _admin: Admin
) -> CourseRead:
    return CourseRead.model_validate(service.replace(Course, record_id, payload))


@router.delete("/courses/{record_id}", status_code=204)
def delete_courses(record_id: UUID, service: Service, _admin: Admin) -> Response:
    service.delete(Course, record_id)
    return Response(status_code=204)
