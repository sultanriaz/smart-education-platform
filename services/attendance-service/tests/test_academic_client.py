from __future__ import annotations

import json
from uuid import uuid4

import httpx
import pytest

from app.clients.academic import HttpAcademicClient
from app.core.config import Settings
from app.core.exceptions import DependencyUnavailable, ForbiddenError, NotFoundError


def adapter(handler, **settings):
    return HttpAcademicClient(
        Settings(_env_file=None, **settings), httpx.Client(transport=httpx.MockTransport(handler))
    )


def test_forwarded_token_and_section_contract():
    section_id, course_id, semester_id = uuid4(), uuid4(), uuid4()
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "id": str(section_id),
                "course_id": str(course_id),
                "semester_id": str(semester_id),
                "is_active": True,
            },
        )

    client = adapter(handle)
    section = client.get_section(section_id, "verified-token")
    client.validate_teacher_assignment(section_id, "verified-token")
    assert section.course_id == course_id
    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer verified-token"
    assert str(requests[0].url) == f"http://localhost:8002/api/v1/sections/{section_id}"


@pytest.mark.parametrize(
    ("status", "exception"),
    [
        (404, NotFoundError),
        (401, ForbiddenError),
        (403, ForbiddenError),
        (500, DependencyUnavailable),
        (503, DependencyUnavailable),
        (302, DependencyUnavailable),
    ],
)
def test_academic_status_mapping(status, exception):
    client = adapter(lambda request: httpx.Response(status))
    with pytest.raises(exception):
        client.get_section(uuid4(), "token")


@pytest.mark.parametrize("failure", [httpx.ConnectError, httpx.ReadTimeout, httpx.PoolTimeout])
def test_academic_network_failures(failure):
    def handle(request):
        raise failure("offline")

    with pytest.raises(DependencyUnavailable):
        adapter(handle).get_section(uuid4(), "token")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"id": "not-uuid"},
        {
            "id": str(uuid4()),
            "course_id": str(uuid4()),
            "semester_id": str(uuid4()),
            "is_active": True,
        },
    ],
)
def test_malformed_or_mismatched_section(payload):
    with pytest.raises(DependencyUnavailable):
        adapter(lambda request: httpx.Response(200, json=payload)).get_section(uuid4(), "token")


def test_malformed_json():
    with pytest.raises(DependencyUnavailable):
        adapter(lambda request: httpx.Response(200, content=b"not-json")).get_section(
            uuid4(), "token"
        )


def test_roster_all_pages_enrollment_and_request_cache():
    section_id = uuid4()
    students = [uuid4() for _ in range(101)]
    calls = []

    def handle(request):
        calls.append(request)
        offset = int(request.url.params["offset"])
        return httpx.Response(
            200,
            json={
                "section_id": str(section_id),
                "total": len(students),
                "limit": 100,
                "offset": offset,
                "students": [
                    {"external_user_id": str(student)}
                    for student in students[offset : offset + 100]
                ],
            },
        )

    client = adapter(handle)
    assert client.get_section_roster(section_id, "token") == set(students)
    client.validate_student_enrollment(section_id, students[-1], "token")
    assert len(calls) == 2
    with pytest.raises(ForbiddenError):
        client.validate_student_enrollment(section_id, uuid4(), "token")


@pytest.mark.parametrize(
    "change", ["mismatched_section", "incomplete", "duplicate", "bad_offset", "changed_total"]
)
def test_invalid_roster_pagination_fails_closed(change):
    section_id = uuid4()
    student = uuid4()

    def handle(request):
        offset = int(request.url.params["offset"])
        payload = {
            "section_id": str(section_id),
            "total": 1,
            "limit": 100,
            "offset": offset,
            "students": [{"external_user_id": str(student)}],
        }
        if change == "mismatched_section":
            payload["section_id"] = str(uuid4())
        elif change == "incomplete":
            payload["students"] = []
        elif change == "duplicate":
            payload["total"] = 2
            payload["students"] *= 2
        elif change == "bad_offset":
            payload["offset"] = 42
        else:
            payload["total"] = 101 if offset == 0 else 102
            payload["students"] = [
                {"external_user_id": str(uuid4())} for _ in range(100 if offset == 0 else 1)
            ]
        return httpx.Response(200, content=json.dumps(payload).encode())

    with pytest.raises(DependencyUnavailable):
        adapter(handle).get_section_roster(section_id, "token")


def test_section_lists_follow_pagination():
    sections = [
        {
            "id": str(uuid4()),
            "course_id": str(uuid4()),
            "semester_id": str(uuid4()),
            "is_active": True,
        }
        for _ in range(101)
    ]

    def handle(request):
        offset = int(request.url.params["offset"])
        return httpx.Response(200, json=sections[offset : offset + 100])

    client = adapter(handle)
    assert len(client.assigned_sections("token")) == 101
    limited = adapter(handle, ACADEMIC_SERVICE_MAX_PAGES=1)
    with pytest.raises(DependencyUnavailable):
        limited.assigned_sections("token")
