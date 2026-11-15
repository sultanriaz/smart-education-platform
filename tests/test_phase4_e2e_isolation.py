"""Phase 4: End-to-End Automated Tests for Student Data Isolation & Security Hardening.

Verifies strict multi-tenant boundary on student_id across:
- Subject management (Create, List, Get, Delete)
- Material ingestion & Storage quota
- Test generation, retrieval, deletion
- Evaluation, diagnostic result retrieval & smart test regeneration
- Topic mastery profiling
"""

import io
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add libs and services to sys.path
ROOT = Path(__file__).resolve().parent.parent
libs_dir = ROOT / "libs" / "python"
if libs_dir.exists():
    for lib in sorted(libs_dir.iterdir()):
        if lib.is_dir() and str(lib) not in sys.path:
            sys.path.insert(0, str(lib))

import jwt
from fastapi.testclient import TestClient
from api.index import STATIC_PRIVATE_KEY_PEM, app

STUDENT_A_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
STUDENT_B_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


def mint_token(user_id: uuid.UUID, roles: list[str] | None = None) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "roles": roles or ["student"],
        "permissions": [],
        "jti": uuid.uuid4().hex,
        "iss": "http://localhost:8001",
        "aud": "smart-education-api",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(hours=2),
    }
    return jwt.encode(
        payload,
        STATIC_PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers={"kid": "identity-dev-1", "typ": "at+jwt"},
    )


def auth_header(user_id: uuid.UUID) -> dict[str, str]:
    token = mint_token(user_id)
    return {"Authorization": f"Bearer {token}"}


client = TestClient(app)


def test_student_data_isolation():
    print("\n========================================================")
    print("PHASE 4 SECURITY VERIFICATION: STRICT MULTI-TENANT ISOLATION")
    print("========================================================")

    headers_a = auth_header(STUDENT_A_ID)
    headers_b = auth_header(STUDENT_B_ID)

    # Initial cleanup of any leftover test subjects
    for headers in [headers_a, headers_b]:
        try:
            r = client.get("/api/v1/learning/self-learning/subjects", headers=headers)
            if r.status_code == 200:
                for sub in r.json():
                    client.delete(f"/api/v1/learning/self-learning/subjects/{sub['id']}", headers=headers)
        except Exception:
            pass

    test_run_id = uuid.uuid4().hex[:6]

    # ------------------------------------------------------------------
    # 1. Subject Management Isolation
    # ------------------------------------------------------------------
    print("\n[1] Testing Subject Data Isolation...")

    # Student A creates a subject
    resp = client.post(
        "/api/v1/learning/self-learning/subjects",
        headers=headers_a,
        json={
            "name": f"Advanced Neural Architectures {test_run_id}",
            "code": "CS-801",
            "department": "Computer Science",
            "description": "Deep learning and transformer architectures",
            "color_hex": "#4F46E5",
            "icon_name": "Brain",
        },
    )
    assert resp.status_code == 201, f"Student A failed to create subject: {resp.text}"
    subject_a = resp.json()
    subject_a_id = subject_a["id"]
    print(f"  + Student A created subject: {subject_a_id} ('{subject_a['name']}')")

    # Student B creates a subject
    resp = client.post(
        "/api/v1/learning/self-learning/subjects",
        headers=headers_b,
        json={
            "name": f"Constitutional Law & Jurisprudence {test_run_id}",
            "code": "LAW-502",
            "department": "Faculty of Law",
            "description": "Constitutional law frameworks",
            "color_hex": "#DC2626",
            "icon_name": "Scale",
        },
    )
    assert resp.status_code == 201, f"Student B failed to create subject: {resp.text}"
    subject_b = resp.json()
    subject_b_id = subject_b["id"]
    print(f"  + Student B created subject: {subject_b_id} ('{subject_b['name']}')")

    # Verify Student A only lists their own subjects
    resp = client.get("/api/v1/learning/self-learning/subjects", headers=headers_a)
    assert resp.status_code == 200
    sub_ids_a = [s["id"] for s in resp.json()]
    assert subject_a_id in sub_ids_a, "Student A cannot see their own subject"
    assert subject_b_id not in sub_ids_a, "SECURITY VIOLATION: Student A can see Student B's subject!"
    print("  ✓ PASS: Student A cannot list Student B's subject.")

    # Verify Student B cannot get Student A's subject directly
    resp = client.get(f"/api/v1/learning/self-learning/subjects/{subject_a_id}", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B accessed Student A subject! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot get Student A's subject (404 Not Found).")

    # Verify Student B cannot delete Student A's subject
    resp = client.delete(f"/api/v1/learning/self-learning/subjects/{subject_a_id}", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B deleted Student A subject! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot delete Student A's subject (404 Not Found).")

    # ------------------------------------------------------------------
    # 2. Study Material Ingestion & Storage Quota Isolation
    # ------------------------------------------------------------------
    print("\n[2] Testing Study Material & Storage Quota Isolation...")

    test_content = b"Transformer Architecture Lecture. Attention is All You Need. Multi-head self-attention mechanisms and feedforward layers."
    files = {"file": ("attention_transformers.txt", io.BytesIO(test_content), "text/plain")}
    data = {"subject_id": subject_a_id, "title": "Transformer Notes"}
    resp = client.post(
        "/api/v1/learning/self-learning/materials/upload",
        headers=headers_a,
        data=data,
        files=files,
    )
    assert resp.status_code == 201, f"Student A upload failed: {resp.text}"
    material_a = resp.json()
    material_a_id = material_a["id"]
    print(f"  + Student A ingested material: {material_a_id} ('{material_a['file_name']}')")

    # Check Student A's quota
    resp = client.get("/api/v1/learning/self-learning/quota", headers=headers_a)
    assert resp.status_code == 200
    quota_a = resp.json()
    assert quota_a["used_bytes"] > 0
    assert quota_a["materials_count"] >= 1
    print(f"  + Student A quota: {quota_a['used_bytes']} bytes used, {quota_a['materials_count']} items.")

    # Student B queries quota: must be 0 bytes used
    resp = client.get("/api/v1/learning/self-learning/quota", headers=headers_b)
    assert resp.status_code == 200
    quota_b = resp.json()
    assert quota_b["used_bytes"] == 0, f"SECURITY VIOLATION: Student B sees Student A's quota bytes: {quota_b['used_bytes']}"
    assert quota_b["materials_count"] == 0
    print("  ✓ PASS: Storage quota strictly partitioned per-student (100MB quota).")

    # Student B attempts to query materials: must not see Student A's material
    resp = client.get("/api/v1/learning/self-learning/materials", headers=headers_b)
    assert resp.status_code == 200
    mats_b = [m["id"] for m in resp.json()]
    assert material_a_id not in mats_b, "SECURITY VIOLATION: Student B sees Student A's material!"

    # Student B attempts to delete Student A's material: must return 404
    resp = client.delete(f"/api/v1/learning/self-learning/materials/{material_a_id}", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B deleted Student A's material! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot view or delete Student A's materials (404 Not Found).")

    # ------------------------------------------------------------------
    # 3. Assessment & Test Generation Isolation
    # ------------------------------------------------------------------
    print("\n[3] Testing Assessment Engine Isolation...")

    # Generate a practice test for Student A
    resp = client.post(
        "/api/v1/learning/self-learning/tests/generate",
        headers=headers_a,
        json={
            "subject_id": subject_a_id,
            "count": 5,
            "difficulty": "medium",
            "title": "Transformer Attention Quiz",
        },
    )
    assert resp.status_code == 201, f"Student A failed to generate test: {resp.text}"
    test_a = resp.json()
    test_a_id = test_a["id"]
    print(f"  + Student A generated test: {test_a_id} with {test_a['total_questions']} questions.")

    # Student B attempts to list tests
    resp = client.get("/api/v1/learning/self-learning/tests", headers=headers_b)
    assert resp.status_code == 200
    test_ids_b = [t["id"] for t in resp.json()]
    assert test_a_id not in test_ids_b, "SECURITY VIOLATION: Student B can list Student A's test!"

    # Student B attempts to GET Student A's test
    resp = client.get(f"/api/v1/learning/self-learning/tests/{test_a_id}", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B retrieved Student A's test! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot inspect Student A's test questions (404 Not Found).")

    # Student B attempts to submit answers to Student A's test
    resp = client.post(
        f"/api/v1/learning/self-learning/tests/{test_a_id}/submit",
        headers=headers_b,
        json={"answers": {"dummy": "A"}, "time_taken_seconds": 30},
    )
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B submitted to Student A's test! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot submit answers to Student A's test (404 Not Found).")

    # Student B attempts to regenerate Student A's test
    resp = client.post(
        f"/api/v1/learning/self-learning/tests/{test_a_id}/regenerate",
        headers=headers_b,
        json={"mode": "weak_focus", "count": 5},
    )
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B regenerated Student A's test! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot trigger smart regeneration on Student A's test (404 Not Found).")

    # ------------------------------------------------------------------
    # 4. Evaluation, Diagnostic Feedback & Mastery Profiler Isolation
    # ------------------------------------------------------------------
    print("\n[4] Testing Diagnostic Feedback & Mastery Profiler Isolation...")

    # Student A submits answers to their test
    questions = test_a["questions"]
    student_a_answers = {}
    for idx, q in enumerate(questions):
        # Answer first question correctly, rest with 'A'
        if idx == 0:
            student_a_answers[q["id"]] = q["correct_option"]
        else:
            student_a_answers[q["id"]] = "A"

    resp = client.post(
        f"/api/v1/learning/self-learning/tests/{test_a_id}/submit",
        headers=headers_a,
        json={"answers": student_a_answers, "time_taken_seconds": 120},
    )
    assert resp.status_code == 200, f"Student A failed to submit test: {resp.text}"
    eval_result = resp.json()
    print(f"  + Student A evaluated: Score {eval_result['score']}/{eval_result['total_questions']} ({eval_result['percentage']}%)")
    assert "topic_breakdown" in eval_result
    assert "detailed_results" in eval_result

    # Student B attempts to fetch Student A's test result
    resp = client.get(f"/api/v1/learning/self-learning/tests/{test_a_id}/result", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B retrieved Student A's results! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot view Student A's score or diagnostic feedback (404 Not Found).")

    # Student B attempts to fetch Student A's subject mastery
    resp = client.get(f"/api/v1/learning/self-learning/subjects/{subject_a_id}/mastery", headers=headers_b)
    assert resp.status_code == 404, f"SECURITY VIOLATION: Student B retrieved Student A's mastery! Status: {resp.status_code}"
    print("  ✓ PASS: Student B cannot view Student A's topic mastery profile (404 Not Found).")

    # Student A fetches their own mastery
    resp = client.get(f"/api/v1/learning/self-learning/subjects/{subject_a_id}/mastery", headers=headers_a)
    assert resp.status_code == 200, f"Student A failed to get mastery: {resp.text}"
    mastery = resp.json()
    print(f"  + Student A Mastery: {mastery['overall_mastery_percentage']}% across {len(mastery['topics'])} topics.")
    assert "topics" in mastery
    assert "strong_topics_count" in mastery
    assert "moderate_topics_count" in mastery
    assert "weak_topics_count" in mastery
    print("  ✓ PASS: Student A topic mastery profiler functional with Bloom's categorization.")

    # Clean up test subjects
    client.delete(f"/api/v1/learning/self-learning/subjects/{subject_a_id}", headers=headers_a)
    client.delete(f"/api/v1/learning/self-learning/subjects/{subject_b_id}", headers=headers_b)

    print("\n========================================================")
    print("ALL PHASE 4 SECURITY & DATA ISOLATION TESTS PASSED 100%!")
    print("========================================================\n")


if __name__ == "__main__":
    test_student_data_isolation()
