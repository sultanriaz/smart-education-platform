"""Isolated HTTP+SQLite scheduling lifecycle smoke; NOT distributed PostgreSQL E2E."""
from __future__ import annotations
import os, sys, uuid
from pathlib import Path
os.environ['ENVIRONMENT']='test'
os.environ['OBSERVABILITY_ENABLED']='false'
os.environ['DATABASE_URL']='sqlite+pysqlite:///:memory:'
root=Path(__file__).resolve().parents[2]
for lib in (root/'libs/python').iterdir():
    if lib.is_dir():sys.path.insert(0,str(lib))
sys.path.insert(0,str(root/'services/scheduling-service'))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.clients.academic import AcademicSection, get_academic_client
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.security.auth import Principal, get_current_principal

section=uuid.uuid4();teacher=uuid.uuid4(); admin=uuid.uuid4(); course=uuid.uuid4(); semester=uuid.uuid4(); room=uuid.uuid4()
class AcademicFixture:
    def get_section(self, section_id, token):
        assert section_id==section
        return AcademicSection(id=section,course_id=course,semester_id=semester)
    def validate_teacher_assignment(self, teacher_user_id, section_id, token):
        return teacher_user_id==teacher and section_id==section
    def validate_student_enrollment(self,*args):return False
    def list_student_section_ids(self,*args):return []
engine=create_engine('sqlite+pysqlite:///:memory:',connect_args={'check_same_thread':False},poolclass=StaticPool)
Base.metadata.create_all(engine)
Factory=sessionmaker(bind=engine,expire_on_commit=False)
with Factory() as session:
    app.dependency_overrides[get_db]=lambda:session
    app.dependency_overrides[get_current_principal]=lambda:Principal(admin,frozenset({'admin'}),'fixture-jwt')
    app.dependency_overrides[get_academic_client]=lambda:AcademicFixture()
    with TestClient(app) as client:
        payload=dict(section_id=str(section),teacher_user_id=str(teacher),room_id=str(room),weekday=0, starts_at='09:00:00', ends_at='10:00:00',effective_from='2026-10-05',effective_to='2026-12-28',timezone_name='Asia/Karachi',publish=False)
        r=client.post('/api/v1/schedules',json=payload)
        assert r.status_code==201,(r.status_code,r.text)
        item=r.json();assert item['status']=='DRAFT',item
        sid=item['id']
        # Updating the draft before publication is a supported feature.
        patch=client.patch(f'/api/v1/schedules/{sid}',json={'ends_at':'10:30:00'})
        assert patch.status_code==200,patch.text
        pub=client.post(f'/api/v1/schedules/{sid}/publish')
        assert pub.status_code==200,pub.text
        assert pub.json()['status']=='ACTIVE'
        again=client.post(f'/api/v1/schedules/{sid}/publish')
        assert again.status_code==200
        h=client.get(f'/api/v1/schedules/{sid}/history')
        assert h.status_code==200 and len(h.json())>=3,h.text
        print('PASS Scheduling HTTP + SQLite: draft→edit→publish→repeat idempotently→audit history')
    app.dependency_overrides.clear()
