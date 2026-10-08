from pathlib import Path

import yaml

from smartedu_readiness import load_checks, load_policy

ROOT = Path(__file__).resolve().parents[2]


def test_readiness_catalog_is_comprehensive():
    checks = load_checks(ROOT / "config" / "readiness" / "checks.yaml")
    assert len(checks) >= 50
    assert all(check.mandatory for check in checks)

    categories = {check.category for check in checks}
    assert {
        "Release",
        "UAT",
        "Infrastructure",
        "Data",
        "Security",
        "Performance",
        "Reliability",
        "Operations",
        "Change",
        "DisasterRecovery",
        "Communications",
        "FinalGate",
    } <= categories


def test_default_policy_is_strict():
    policy = load_policy(ROOT / "config" / "readiness" / "policy.yaml")
    assert policy.require_all_mandatory_pass is True
    assert policy.allow_mandatory_waiver is False
    assert policy.max_open_blocker == 0
    assert policy.max_open_critical == 0
    assert policy.max_open_high == 0
    assert len(policy.required_approval_roles) == 5


def test_every_check_has_owner_evidence_and_source():
    checks = load_checks(ROOT / "config" / "readiness" / "checks.yaml")
    for check in checks:
        assert check.owner_role
        assert check.evidence_required
        assert check.source_refs
