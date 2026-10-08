from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_workflow_yaml_parses():
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_stabilization_workflow_is_read_only_by_design():
    text = (
        ROOT / ".github" / "workflows" / "production-stabilization.yml"
    ).read_text(encoding="utf-8").casefold()

    forbidden = [
        "kubectl apply",
        "kubectl delete",
        "helm upgrade",
        "rollout restart",
        "alembic upgrade",
        "alembic downgrade",
    ]
    for token in forbidden:
        assert token not in text

    assert "production_read_only" in text
