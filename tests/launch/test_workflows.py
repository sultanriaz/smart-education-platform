from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_launch_workflows_parse():
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_production_deploy_is_manual_and_protected():
    payload = yaml.safe_load(
        (
            ROOT / ".github" / "workflows" / "production-deploy.yml"
        ).read_text(encoding="utf-8")
    )
    assert "workflow_dispatch" in payload[True] if True in payload else "workflow_dispatch" in payload.get("on", {})
    job = payload["jobs"]["deploy"]
    assert job["environment"] == "production"
    assert job["runs-on"] == ["self-hosted", "production"]


def test_rollback_workflow_does_not_run_db_downgrade():
    text = (
        ROOT / ".github" / "workflows" / "production-rollback.yml"
    ).read_text(encoding="utf-8").casefold()
    assert "alembic downgrade" not in text
