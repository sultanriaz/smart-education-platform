"""Seed labelled demo fixtures through the gateway, never another service's DB.

Only the generated, isolated local environment is supported. Credentials and
fixture IDs are retained under ignored .integration/runtime for repeatable QA.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from local_stack import ROOT, RUNTIME, environment

BASE = "http://localhost:18080"


def main():
    secrets = json.loads((RUNTIME / "secrets.json").read_text())
    subprocess.run([sys.executable, "-m", "app.scripts.repair_local_demo"], cwd=ROOT / "services/identity-service", env=environment("identity"), check=True)
    subprocess.run([sys.executable, "-m", "app.scripts.seed_rbac"], cwd=ROOT / "services/identity-service", env=environment("identity"), check=True)
    client = httpx.Client(base_url=BASE, timeout=20, headers={"Origin": "http://localhost:5173"})
    fixture_file = RUNTIME / "demo-fixtures.json"
    fixtures = json.loads(fixture_file.read_text()) if fixture_file.exists() else {}

    def request(method, service, path, payload=None, token=None):
        public_name = {"assessment": "assessments", "notification": "notifications", "facility": "facilities"}.get(service, service)
        response = client.request(method, f"/api/v1/{public_name}/{path}", json=payload,
                                  headers={"Authorization": f"Bearer {token}"} if token else {})
        if response.status_code >= 400:
            # Credentials and response bodies are not written to terminal logs.
            raise RuntimeError(f"Demo operation {method} {service}/{path}: HTTP {response.status_code}; request {response.headers.get('X-Request-ID')}")
        return response.json() if response.status_code != 204 else None

    def login(role):
        password = secrets["DEMO_PASSWORD"] if role == "admin" else secrets[f"{role.upper()}_PASSWORD"]
        return request("POST", "identity", "auth/login", {"email": f"{role}@demo.example.edu", "password": password})["access_token"]

    tokens = {"admin": login("admin")}

    def create(key, service, path, payload, role="admin"):
        if key not in fixtures:
            fixtures[key] = request("POST", service, path, payload, tokens[role])
            fixture_file.write_text(json.dumps(fixtures, indent=2), encoding="utf-8")
            print(f"Created demo fixture: {key}", flush=True)
        return fixtures[key]

    for role, name in (("teacher", "Demo Teacher"), ("student", "Demo Student")):
        create(role, "identity", "users", {"email": f"{role}@demo.example.edu", "full_name": name, "password": secrets[f"{role.upper()}_PASSWORD"], "role": role})
        tokens[role] = login(role)
    department = create("department", "academic", "departments", {"code": "DEMO-CS", "name": "Demo · Computer Science"})
    program = create("program", "academic", "programs", {"department_id": department["id"], "code": "DEMO-BSCS", "name": "Demo · BS Computer Science", "duration_semesters": 8})
    year = create("year", "academic", "academic-years", {"code": "DEMO-2026", "name": "Demo · Academic Year 2026", "starts_on": "2026-01-01", "ends_on": "2026-12-31"})
    semester = create("semester", "academic", "semesters", {"academic_year_id": year["id"], "number": 1, "name": "Demo · Autumn 2026", "starts_on": "2026-08-01", "ends_on": "2026-12-20"})
    course = create("course", "academic", "courses", {"program_id": program["id"], "code": "DEMO-CS101", "title": "Demo · Distributed Systems", "credits": 3, "semester_number": 1})
    section = create("section", "academic", "sections", {"course_id": course["id"], "semester_id": semester["id"], "code": "DEMO-A", "capacity": 40})
    student = create("student-profile", "academic", "student-profiles", {"external_user_id": fixtures["student"]["id"], "student_number": "DEMO-SP26-001", "program_id": program["id"], "admission_year_id": year["id"], "current_semester": 1})
    teacher = create("teacher-profile", "academic", "teacher-profiles", {"external_user_id": fixtures["teacher"]["id"], "employee_number": "DEMO-T001", "department_id": department["id"], "designation": "Demo Lecturer"})
    create("enrollment", "academic", "enrollments", {"student_profile_id": student["id"], "section_id": section["id"]})
    create("teacher-assignment", "academic", "teacher-assignments", {"teacher_profile_id": teacher["id"], "section_id": section["id"]})
    create("schedule", "scheduling", "schedules", {"section_id": section["id"], "teacher_user_id": fixtures["teacher"]["id"], "weekday": 3, "starts_at": "09:00:00", "ends_at": "10:00:00", "effective_from": "2026-08-01", "effective_to": "2026-12-20", "timezone_name": "Asia/Karachi"})
    for index, status in enumerate(("PRESENT", "PRESENT", "ABSENT", "LATE", "PRESENT")):
        date = f"2026-10-{index+1:02}"
        session = create(f"attendance-{date}", "attendance", "sessions", {"section_id": section["id"], "session_date": date, "starts_at": "09:00:00", "ends_at": "10:00:00"}, "teacher")
        current = request("GET", "attendance", f"sessions/{session['id']}", token=tokens["teacher"])
        if current["status"] == "OPEN":
            request("PUT", "attendance", f"sessions/{session['id']}/records", {"records": [{"student_user_id": fixtures["student"]["id"], "status": status}]}, tokens["teacher"])
            request("POST", "attendance", f"sessions/{session['id']}/finalize", {}, tokens["teacher"])
    create("facility", "facility", "facilities", {"code": "DEMO-LAB", "name": "Demo · Innovation Lab", "kind": "LAB", "capacity": 30, "building": "Demo Block", "description": "Explicit demonstration fixture."})
    now = datetime.now(timezone.utc)
    create("booking", "facility", "bookings", {"facility_id": fixtures["facility"]["id"], "purpose": "Demo study group", "attendees": 4, "starts_at": (now+timedelta(days=1)).isoformat(), "ends_at": (now+timedelta(days=1,hours=1)).isoformat()}, "student")
    resource = create("resource", "learning", "resources", {"title": "Demo · Your distributed systems toolkit", "resource_type": "NOTE", "description": "A labelled demo resource for end-to-end verification.", "targets": [{"target_type": "SECTION", "target_id": section["id"]}], "tags": ["demo", "systems"]}, "teacher")
    create("resource-version", "learning", f"resources/{resource['id']}/versions", {"text_content": "Demo lesson: independent services own their data and communicate through contracts and durable events."}, "teacher")
    request("POST", "learning", f"resources/{resource['id']}/publish", {}, tokens["teacher"])
    bank = create("bank", "assessment", "banks", {"name": "Demo · Systems fundamentals", "course_id": course["id"]}, "teacher")
    question = create("question", "assessment", "questions", {"bank_id": bank["id"], "question_type": "MCQ_SINGLE", "prompt": "Which mechanism reliably publishes committed domain events?", "choices": [{"text": "Transactional outbox", "is_correct": True}, {"text": "Browser storage", "is_correct": False}], "points": 5}, "teacher")
    quiz = create("quiz", "assessment", "quizzes", {"title": "Demo · Systems knowledge check", "course_id": course["id"], "duration_minutes": 15}, "teacher")
    create("quiz-question", "assessment", f"quizzes/{quiz['id']}/questions", {"question_id": question["id"], "position": 0}, "teacher")
    request("POST", "assessment", f"quizzes/{quiz['id']}/publish", {}, tokens["teacher"])
    create("assessment-assignment", "assessment", f"quizzes/{quiz['id']}/assignments", {"section_id": section["id"], "opens_at": (now-timedelta(days=1)).isoformat(), "due_at": (now+timedelta(days=30)).isoformat(), "attempt_limit": 5}, "teacher")
    create("announcement", "notification", "teacher/announcements", {"section_id": section["id"], "title": "Demo · Welcome to your workspace", "body": "Your timetable, attendance, resources, and assessments are connected. This is a labelled demonstration announcement."}, "teacher")
    create("support-ticket", "platform", "support/tickets", {"subject": "Demo · Workspace feedback", "description": "This labelled support ticket verifies the service-owned help workflow."}, "student")
    client.close()
    print("Local demo fixtures ready. Credentials remain in .integration/runtime/secrets.json.")


if __name__ == "__main__":
    main()
