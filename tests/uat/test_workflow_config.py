from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_workflows_parse():
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_uat_policy_requires_all_five_signoff_roles():
    policy = yaml.safe_load(
        (ROOT / "config" / "uat" / "policy.yaml").read_text(encoding="utf-8")
    )
    assert len(policy["required_signoff_roles"]) == 5
