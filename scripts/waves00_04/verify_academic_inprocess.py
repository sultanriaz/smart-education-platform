"""Academic owner-service SQLite integration smoke; external Identity not included."""
from __future__ import annotations
import sys,uuid
from datetime import date
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for lib in (root/'libs/python').iterdir():
    if lib.is_dir(): sys.path.insert(0,str(lib))
sys.path.insert(0,str(root/'services/academic-service'))
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.domain.models import Department, Program, AcademicYear, Semester, Course, Section,StudentAcademicProfile, TeacherAcademicProfile,Enrollment,EnrollmentStatus,TeacherAssignment,OutboxEvent
from app.schemas.academic import DepartmentWrite,ProgramWrite,AcademicYearWrite,SemesterWrite,CourseWrite,SectionWrite,StudentProfileWrite,TeacherProfileWrite
from app.services.academic import AcademicService
engine=create_engine('sqlite+pysqlite:///:memory:')
Base.metadata.create_all(engine)
with sessionmaker(bind=engine,expire_on_commit=False)() as db:
    svc=AcademicService(db)
    d=svc.create(Department,DepartmentWrite(code='CS',name='Computer Science'))
    p=svc.create(Program,ProgramWrite(code='BSCS',name='BSCS',department_id=d.id,duration_semesters=8))
    y=svc.create(AcademicYear,AcademicYearWrite(code='2026',name='Academic Year',starts_on=date(2026,8,1),ends_on=date(2027,6,30)))
    sem=svc.create(Semester,SemesterWrite(academic_year_id=y.id,number=1,name='Fall',starts_on=date(2026,8,10),ends_on=date(2026,12,31)))
    c=svc.create(Course,CourseWrite(program_id=p.id,code='CSE101',title='Intro to Computing',credits=3,semester_number=1))
    section=svc.create(Section,SectionWrite(course_id=c.id,semester_id=sem.id,code='A',capacity=55))
    st=svc.create(StudentAcademicProfile,StudentProfileWrite(external_user_id=uuid.uuid4(),student_number='CIIT-001',program_id=p.id,admission_year_id=y.id,current_semester=1))
    tch=svc.create(TeacherAcademicProfile,TeacherProfileWrite(external_user_id=uuid.uuid4(),employee_number='T-1',department_id=d.id,designation='Lecturer'))
    enrolled=svc.enroll(st.id,section.id)
    assigned=svc.assign(tch.id,section.id)
    assert db.scalar(select(Enrollment).where(Enrollment.id==enrolled.id)) is not None
    assert db.scalar(select(TeacherAssignment).where(TeacherAssignment.id==assigned.id)) is not None
    svc.delete(Enrollment,enrolled.id)
    after=db.get(Enrollment,enrolled.id)
    assert after is not None and after.status == EnrollmentStatus.DROPPED,(after, after.status if after else None)
    assert db.scalar(select(OutboxEvent).where(OutboxEvent.event_type=='academic.enrollment_dropped')) is not None
    print('PASS Academic owner SQLite: department→program→year→term→course→section→student/teacher→enroll/assign→soft-withdraw+event')
