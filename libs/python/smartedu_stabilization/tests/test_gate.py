from datetime import UTC, datetime

from smartedu_stabilization import (
    CheckpointResult,
    FollowUp,
    StabilizationApproval,
    StabilizationCheckpoint,
    StabilizationIssue,
    StabilizationRun,
    evaluate_stabilization,
)


def checkpoints():
    return [
        StabilizationCheckpoint(
            id="STAB-A-001",
            category="A",
            title="A",
            owner_role="TechnicalLead",
            evidence_required=["a"],
            source_refs=["Sprint27"],
        ),
        StabilizationCheckpoint(
            id="STAB-B-001",
            category="B",
            title="B",
            owner_role="OperationsOwner",
            evidence_required=["b"],
            source_refs=["Sprint21"],
        ),
    ]


def policy():
    return {
        "max_open_issues": {
            "SEV1": 0,
            "SEV2": 0,
            "SEV3": 0,
            "SEV4": 999,
        },
        "require_all_high_followups_closed": True,
        "required_approval_roles": [
            "TechnicalLead",
            "OperationsOwner",
            "SecurityOwner",
            "ProductOwner",
            "ProjectSupervisor",
        ],
        "allowed_dispositions": [
            "STABLE",
            "STABLE_WITH_FOLLOWUPS",
        ],
    }


def approvals(now):
    return [
        StabilizationApproval(
            role=role,
            approver=role,
            approved_at=now,
            decision="APPROVE",
        )
        for role in policy()["required_approval_roles"]
    ]


def clean_run():
    now = datetime.now(UTC)
    return StabilizationRun(
        run_id="stab-1",
        launch_id="launch-1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        production_url="https://prod.example.invalid",
        started_at=now,
        completed_at=now,
        disposition="STABLE",
        checkpoints=[
            CheckpointResult(
                checkpoint_id=item.id,
                status="PASS",
                observed_by="tester",
                observed_at=now,
            )
            for item in checkpoints()
        ],
        approvals=approvals(now),
    )


def test_clean_stabilization_passes():
    result = evaluate_stabilization(
        checkpoints=checkpoints(),
        run=clean_run(),
        policy=policy(),
    )
    assert result.passed
    assert result.mandatory_passed == 2


def test_open_sev2_blocks_closure():
    run = clean_run()
    run.issues.append(
        StabilizationIssue(
            id="ISS-2",
            severity="SEV2",
            title="Major issue",
            status="MONITORING",
            owner="ops",
            opened_at=datetime.now(UTC),
            mitigation="Investigating",
        )
    )
    result = evaluate_stabilization(
        checkpoints=checkpoints(),
        run=run,
        policy=policy(),
    )
    assert not result.passed
    assert any("SEV2" in reason for reason in result.reasons)


def test_open_high_followup_blocks_closure():
    run = clean_run()
    run.followups.append(
        FollowUp(
            id="F-1",
            title="High follow-up",
            owner="tech",
            severity="HIGH",
            status="OPEN",
        )
    )
    result = evaluate_stabilization(
        checkpoints=checkpoints(),
        run=run,
        policy=policy(),
    )
    assert not result.passed
    assert any("HIGH follow-ups" in reason for reason in result.reasons)
