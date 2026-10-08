from datetime import UTC, datetime

from smartedu_uat import (
    ScenarioResult,
    Signoff,
    UATDefect,
    UATPolicy,
    UATRun,
    UATScenario,
    evaluate_gate,
)


def scenarios():
    return [
        UATScenario(
            id="UAT-STU-001",
            role="Student",
            title="Login",
            domain="Identity",
            priority="P0",
            execution="manual",
            steps=["Login"],
            expected_results=["Success"],
            requirement_refs=["REQ-A"],
        ),
        UATScenario(
            id="UAT-STU-002",
            role="Student",
            title="View",
            domain="Academic",
            priority="P1",
            execution="manual",
            steps=["View"],
            expected_results=["Success"],
            requirement_refs=["REQ-B"],
        ),
    ]


def policy():
    return UATPolicy(
        minimum_pass_rate_percent=95,
        require_all_p0_pass=True,
        require_all_p1_pass=True,
        max_open_blocker=0,
        max_open_critical=0,
        max_open_major=0,
        required_signoff_roles=[
            "StudentRepresentative",
            "TeacherRepresentative",
            "AdminRepresentative",
            "ProductOwner",
            "ProjectSupervisor",
        ],
    )


def full_signoffs():
    now = datetime.now(UTC)
    return [
        Signoff(role=role, signer=role, decision="APPROVE", signed_at=now)
        for role in [
            "StudentRepresentative",
            "TeacherRepresentative",
            "AdminRepresentative",
            "ProductOwner",
            "ProjectSupervisor",
        ]
    ]


def test_gate_passes_complete_clean_run():
    now = datetime.now(UTC)
    run = UATRun(
        run_id="r1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        staging_url="https://staging.example.org",
        started_at=now,
        completed_at=now,
        results=[
            ScenarioResult(
                scenario_id=item.id,
                status="PASS",
                executed_by="tester",
                executed_at=now,
            )
            for item in scenarios()
        ],
        signoffs=full_signoffs(),
    )

    result = evaluate_gate(scenarios=scenarios(), run=run, policy=policy())
    assert result.passed
    assert result.pass_rate_percent == 100.0


def test_gate_rejects_open_major_and_failed_p0():
    now = datetime.now(UTC)
    run = UATRun(
        run_id="r1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        staging_url="https://staging.example.org",
        started_at=now,
        completed_at=now,
        results=[
            ScenarioResult(
                scenario_id="UAT-STU-001",
                status="FAIL",
                executed_by="tester",
                executed_at=now,
            ),
            ScenarioResult(
                scenario_id="UAT-STU-002",
                status="PASS",
                executed_by="tester",
                executed_at=now,
            ),
        ],
        defects=[
            UATDefect(
                id="UAT-D-1",
                scenario_id="UAT-STU-001",
                severity="MAJOR",
                title="Login workflow issue",
                status="OPEN",
            )
        ],
        signoffs=full_signoffs(),
    )

    result = evaluate_gate(scenarios=scenarios(), run=run, policy=policy())
    assert not result.passed
    assert any("P0 scenarios not PASS" in reason for reason in result.reasons)
    assert any("open MAJOR defects" in reason for reason in result.reasons)
