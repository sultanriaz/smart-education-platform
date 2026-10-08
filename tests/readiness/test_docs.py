from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_go_live_documents_exist():
    required = [
        "PRODUCTION_READINESS_PLAN.md",
        "GO_NO_GO_PROCESS.md",
        "GO_LIVE_RUNBOOK.md",
        "MIGRATION_PRODUCTION_RUNBOOK.md",
        "ROLLBACK_AND_ABORT_CRITERIA.md",
        "OPERATIONS_OWNERSHIP.md",
        "INCIDENT_RESPONSE_HANDOFF.md",
        "PRODUCTION_SECRETS_DNS_TLS.md",
        "DR_RTO_RPO_DECISION.md",
        "SPRINT_27_HANDOFF.md",
    ]
    for name in required:
        assert (ROOT / name).exists(), name
