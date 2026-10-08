from datetime import UTC, datetime

from smartedu_readiness import (
    Approval,
    CheckResult,
    ReadinessCheck,
    ReadinessPolicy,
    ReadinessRisk,
    ReadinessRun,
    evaluate_readiness,
)


def checks():
    return [
        ReadinessCheck(
            id="PR-REL-001",
            category="Release",
            title="Release verified",
            owner_role="TechnicalLead",
            evidence_required=["manifest"],
            source_refs=["Sprint22"],
        ),
        ReadinessCheck(
            id="PR-SEC-001",
            category="Security",
            title="Security verified",
            owner_role="SecurityOwner",
            evidence_required=["report"],
            source_refs=["Sprint18"],
        ),
    ]


def policy():
    return ReadinessPolicy(
        required_approval_roles=[
            "TechnicalLead",
            "OperationsOwner",
            "SecurityOwner",
            "ProductOwner",
            "ProjectSupervisor",
        ]
    )


def approvals(now):
    return [
        Approval(
            role=role,
            approver=role,
            decision="APPROVE",
            approved_at=now,
        )
        for role in policy().required_approval_roles
    ]


def test_clean_completed_go_run_passes():
    now = datetime.now(UTC)
    run = ReadinessRun(
        run_id="r1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        production_url="https://prod.example.invalid",
        started_at=now,
        completed_at=now,
        final_decision="GO",
        checks=[
            CheckResult(
                check_id=item.id,
                status="PASS",
                verified_by="tester",
                verified_at=now,
            )
            for item in checks()
        ],
        approvals=approvals(now),
    )
    gate = evaluate_readiness(checks=checks(), run=run, policy=policy())
    assert gate.passed
    assert gate.mandatory_passed == 2


def test_open_high_risk_fails_gate():
    now = datetime.now(UTC)
    run = ReadinessRun(
        run_id="r1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        production_url="https://prod.example.invalid",
        started_at=now,
        completed_at=now,
        final_decision="GO",
        checks=[
            CheckResult(
                check_id=item.id,
                status="PASS",
                verified_by="tester",
                verified_at=now,
            )
            for item in checks()
        ],
        approvals=approvals(now),
        risks=[
            ReadinessRisk(
                id="R-1",
                title="Capacity gap",
                severity="HIGH",
                status="OPEN",
                owner="ops",
                mitigation="Scale before launch",
            )
        ],
    )
    gate = evaluate_readiness(checks=checks(), run=run, policy=policy())
    assert not gate.passed
    assert any("open HIGH risks" in reason for reason in gate.reasons)


def test_no_go_fails_gate():
    now = datetime.now(UTC)
    run = ReadinessRun(
        run_id="r1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        production_url="https://prod.example.invalid",
        started_at=now,
        completed_at=now,
        final_decision="NO_GO",
        checks=[
            CheckResult(
                check_id=item.id,
                status="PASS",
                verified_by="tester",
                verified_at=now,
            )
            for item in checks()
        ],
        approvals=approvals(now),
    )
    gate = evaluate_readiness(checks=checks(), run=run, policy=policy())
    assert not gate.passed
    assert "final readiness decision is NO_GO" in gate.reasons
