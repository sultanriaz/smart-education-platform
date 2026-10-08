from pathlib import Path

import yaml

from smartedu_uat import load_scenarios

ROOT = Path(__file__).resolve().parents[2]


def test_formal_catalog_has_40_scenarios():
    scenarios = load_scenarios(ROOT / "config" / "uat" / "scenarios")
    assert len(scenarios) == 40
    by_role = {}
    for scenario in scenarios:
        by_role[scenario.role] = by_role.get(scenario.role, 0) + 1
    assert by_role == {
        "Student": 10,
        "Teacher": 10,
        "Admin": 10,
        "CrossRole": 10,
    }


def test_every_requirement_has_uat_coverage():
    requirements = yaml.safe_load(
        (ROOT / "config" / "uat" / "requirements.yaml").read_text(encoding="utf-8")
    )["requirements"]
    scenarios = load_scenarios(ROOT / "config" / "uat" / "scenarios")
    referenced = {
        ref
        for scenario in scenarios
        for ref in scenario.requirement_refs
    }
    assert {item["id"] for item in requirements} <= referenced


def test_default_gate_has_zero_blocker_critical_major_tolerance():
    policy = yaml.safe_load(
        (ROOT / "config" / "uat" / "policy.yaml").read_text(encoding="utf-8")
    )
    assert policy["max_open_blocker"] == 0
    assert policy["max_open_critical"] == 0
    assert policy["max_open_major"] == 0
    assert policy["require_all_p0_pass"] is True
    assert policy["require_all_p1_pass"] is True
