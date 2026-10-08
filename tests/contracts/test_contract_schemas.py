from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parent


def test_all_json_schemas_are_valid_draft_2020_12():
    schemas = sorted(ROOT.glob("*.schema.json"))
    assert schemas
    for path in schemas:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_error_envelope_rejects_success_payload():
    schema = json.loads(
        (ROOT / "error-envelope.schema.json").read_text(encoding="utf-8")
    )
    errors = list(
        Draft202012Validator(schema).iter_errors({"status": "ok"})
    )
    assert errors


def test_event_envelope_requires_correlation_id():
    schema = json.loads(
        (ROOT / "event-envelope.schema.json").read_text(encoding="utf-8")
    )
    payload = {
        "event_id": "11111111-1111-1111-1111-111111111111",
        "event_type": "assessment.attempt.graded",
        "event_version": 1,
        "source": "assessment-service",
        "occurred_at": "2026-10-07T00:00:00Z",
        "data": {},
        "metadata": {},
    }
    errors = list(Draft202012Validator(schema).iter_errors(payload))
    assert any(error.validator == "required" for error in errors)
