from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_all_generated_workflows_parse():
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_readiness_workflow_does_not_deploy_production():
    path = ROOT / ".github" / "workflows" / "production-readiness.yml"
    text = path.read_text(encoding="utf-8").casefold()
    forbidden = [
        "kubectl apply",
        "helm upgrade",
        "docker compose up",
    ]
    for token in forbidden:
        assert token not in text
