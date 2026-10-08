from __future__ import annotations

import os
from pathlib import Path

import httpx
import pytest
import yaml

MATRIX = yaml.safe_load(
    Path(__file__).with_name("authorization-matrix.yaml").read_text(encoding="utf-8")
)
GATEWAY_URL = os.getenv("SMARTEDU_GATEWAY_URL", "").rstrip("/")

TOKENS = {
    "student": os.getenv("SMARTEDU_STUDENT_TOKEN"),
    "teacher": os.getenv("SMARTEDU_TEACHER_TOKEN"),
    "admin": os.getenv("SMARTEDU_ADMIN_TOKEN"),
}


def expected_statuses(value):
    return value if isinstance(value, list) else [value]


@pytest.mark.live
@pytest.mark.skipif(not GATEWAY_URL, reason="SMARTEDU_GATEWAY_URL is not configured")
@pytest.mark.parametrize("rule", MATRIX["rules"], ids=lambda row: row["name"])
@pytest.mark.parametrize("principal", MATRIX["principals"])
def test_authorization_matrix(rule, principal):
    headers = {}
    if principal != "anonymous":
        token = TOKENS.get(principal)
        if not token:
            pytest.skip(f"{principal} token is not configured")
        headers["Authorization"] = f"Bearer {token}"

    body = {}
    with httpx.Client(timeout=10.0) as client:
        response = client.request(
            rule["method"],
            GATEWAY_URL + rule["path"],
            headers=headers,
            json=body if rule["method"] != "GET" else None,
        )

    assert response.status_code in expected_statuses(rule[principal]), (
        f"{rule['name']} for {principal}: got {response.status_code}, "
        f"expected {rule[principal]}"
    )
