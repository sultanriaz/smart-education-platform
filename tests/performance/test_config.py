from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parent


def test_load_profiles_include_srs_500_and_soak():
    payload = yaml.safe_load(
        (ROOT / "config" / "load-profiles.yaml").read_text(encoding="utf-8")
    )
    profiles = {item["name"]: item for item in payload["profiles"]}
    assert profiles["srs-500"]["users"] >= 500
    assert profiles["srs-500"]["duration_seconds"] >= 600
    assert profiles["soak-250"]["duration_seconds"] >= 1800


def test_srs_performance_budgets_are_encoded():
    payload = yaml.safe_load(
        (ROOT / "config" / "performance-budgets.yaml").read_text(encoding="utf-8")
    )
    budgets = {item["name"]: item for item in payload["budgets"]}
    assert payload["defaults"]["p95_ms"] == 3000
    assert budgets["attendance-write"]["p95_ms"] == 2000
    assert budgets["attendance-read"]["p95_ms"] == 2000
    assert budgets["notifications"]["p95_ms"] == 5000
    assert payload["acceptance"]["minimum_concurrent_users"] >= 500


def test_workload_mix_weights_sum_to_100():
    payload = yaml.safe_load(
        (ROOT / "config" / "workload-mix.yaml").read_text(encoding="utf-8")
    )
    assert sum(payload["roles"].values()) == 100
    assert sum(payload["student_actions"].values()) == 100
    assert sum(payload["teacher_actions"].values()) == 100
    assert sum(payload["admin_actions"].values()) == 100


def test_scaling_candidate_has_all_core_services():
    payload = json.loads(
        (ROOT / "config" / "scaling-candidates.json").read_text(encoding="utf-8")
    )
    candidate = payload["candidate"]
    for service in [
        "identity-service",
        "academic-service",
        "attendance-service",
        "scheduling-service",
        "facility-service",
        "learning-service",
        "assessment-service",
        "reporting-service",
        "platform-service",
    ]:
        assert service in candidate
