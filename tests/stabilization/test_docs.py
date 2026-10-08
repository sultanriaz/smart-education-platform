from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_closure_documents_exist():
    required = [
        "PRODUCTION_STABILIZATION_PLAN.md",
        "STABILIZATION_SLO_REVIEW.md",
        "STABILIZATION_MESSAGING_DATA.md",
        "STABILIZATION_SECURITY_REVIEW.md",
        "STABILIZATION_INCIDENT_TRIAGE.md",
        "HOTFIX_PROCESS.md",
        "SUPPORT_OPERATIONS_HANDOFF.md",
        "FYP_OPERATIONAL_CLOSURE.md",
    ]
    for name in required:
        assert (ROOT / name).exists(), name
