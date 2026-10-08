from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_launch_documents_exist():
    required = [
        "PRODUCTION_DEPLOYMENT_EXECUTION.md",
        "POST_DEPLOYMENT_VALIDATION.md",
        "PRODUCTION_LAUNCH_MONITORING.md",
        "PRODUCTION_ROLLBACK_RUNBOOK.md",
        "LAUNCH_EVIDENCE_POLICY.md",
        "SPRINT_28_HANDOFF.md",
    ]
    for name in required:
        assert (ROOT / name).exists(), name


def test_production_scripts_have_explicit_confirmation_tokens():
    deploy = (ROOT / "scripts" / "deploy-production-k8s.ps1").read_text(
        encoding="utf-8"
    )
    rollback = (ROOT / "scripts" / "rollback-production-app.ps1").read_text(
        encoding="utf-8"
    )
    assert "PRODUCTION_DEPLOY" in deploy
    assert "PRODUCTION_ROLLBACK" in rollback
    assert "SCHEMA_COMPATIBLE" in rollback
