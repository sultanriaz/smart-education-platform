"""Attendance owner-service SQLite workflow for 55 Students; not PostgreSQL race E2E."""
from __future__ import annotations
import sys,uuid
from datetime import date
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for lib in (root/'libs/python').iterdir():
    if lib.is_dir():sys.path.insert(0,str(lib))
sys.path.insert(0,str(root/'services/attendance-service'))
from sqlalchemy import create_engine,select,func
from sqlalchemy.orm import Session
from app.db.base import Base
from app.domain.models import AttendanceRecord,AttendanceSession,SessionStatus
from app.schemas.attendance import SessionCreate,BulkMark,Mark,AttendanceStatus
from app.security.jwt import Principal
from app.services.attendance import AttendanceService
from app.core.config import Settings
from app.clients.academic import AcademicSection
section_id=uuid.uuid4();students=[uuid.uuid4() for _ in range(55)]
class AcademicFixture:
    def get_section(self,sid,token):
        assert sid==section_id
        return AcademicSection(id=sid,course_id=uuid.uuid4(),semester_id=uuid.uuid4(),is_active=True)
    def validate_student_enrollment(self,sid,uid,token):
        assert sid==section_id and uid in students
    def get_section_roster(self,sid,token):
        return set(students)
    def validate_teacher_assignment(self,*args): return True
actor=Principal(user_id=uuid.uuid4(),roles=frozenset({'admin'}),access_token='fixture')
engine=create_engine('sqlite+pysqlite:///:memory:');Base.metadata.create_all(engine)
with Session(engine,expire_on_commit=False) as db:
    svc=AttendanceService(db,AcademicFixture(),Settings.model_construct(ENVIRONMENT='test',VERIFY_SCHEDULE_OCCURRENCES=False))
    item=svc.create_session(actor,SessionCreate(section_id=section_id,session_date=date(2026,10,5)))
    first=svc.bulk_mark(actor,item.id,BulkMark(records=[Mark(student_user_id=s,status=AttendanceStatus.PRESENT) for s in students[:21]]))
    assert len(first)==21
    rest=svc.bulk_mark(actor,item.id,BulkMark(records=[Mark(student_user_id=s,status=AttendanceStatus.ABSENT) for s in students[21:]]))
    assert len(rest)==34
    assert db.scalar(select(func.count(AttendanceRecord.id)))==55
    svc.finalize(actor,item.id)
    assert db.get(AttendanceSession,item.id).status==SessionStatus.FINALIZED
    print('PASS Attendance owner SQLite: 55 users→partial save 21→remaining 34→finalize; 55 persisted')
