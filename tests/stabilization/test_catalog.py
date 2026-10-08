from pathlib import Path

from smartedu_stabilization import load_checkpoints, load_policy

ROOT = Path(__file__).resolve().parents[2]


def test_stabilization_catalog_has_49_mandatory_checkpoints():
    checkpoints = load_checkpoints(
        ROOT / "config" / "stabilization" / "checkpoints.yaml"
    )
    assert len(checkpoints) == 49
    assert all(item.mandatory for item in checkpoints)


def test_catalog_covers_major_operational_domains():
    checkpoints = load_checkpoints(
        ROOT / "config" / "stabilization" / "checkpoints.yaml"
    )
    categories = {item.category for item in checkpoints}
    assert {
        "Launch",
        "Edge",
        "Services",
        "Performance",
        "Database",
        "Redis",
        "Messaging",
        "Observability",
        "Security",
        "Identity",
        "Roles",
        "DataIntegrity",
        "Support",
        "Change",
        "Recovery",
        "Operations",
        "Closure",
    } <= categories


def test_default_policy_requires_zero_sev1_sev2_sev3():
    policy = load_policy(
        ROOT / "config" / "stabilization" / "policy.yaml"
    )
    assert policy["max_open_issues"]["SEV1"] == 0
    assert policy["max_open_issues"]["SEV2"] == 0
    assert policy["max_open_issues"]["SEV3"] == 0
    assert policy["require_all_high_followups_closed"] is True
    assert len(policy["required_approval_roles"]) == 5
