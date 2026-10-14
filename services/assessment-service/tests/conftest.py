from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.services.assessment_service import AssessmentService


class FakeAcademic:
    def get_section(self, section_id, token=None):
        return {"id": str(section_id), "course_id": str(self.course_id)}

    def validate_teacher_assignment(self, teacher_user_id, section_id, token=None):
        return True

    def validate_student_enrollment(self, student_user_id, section_id, token=None):
        return True


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    s = Session()
    try:
        yield s
    finally:
        s.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def service(db, ids):
    academic = FakeAcademic()
    academic.course_id = ids["course"]
    return AssessmentService(db, academic)


@pytest.fixture()
def ids():
    return {
        "teacher": uuid.uuid4(),
        "student": uuid.uuid4(),
        "course": uuid.uuid4(),
        "section": uuid.uuid4(),
    }
