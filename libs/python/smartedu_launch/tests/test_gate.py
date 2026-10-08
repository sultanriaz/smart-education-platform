from datetime import UTC, datetime

from smartedu_launch import (
    LaunchIncident,
    LaunchRecord,
    PhaseRecord,
    evaluate_launch,
)

REQUIRED = [
    "preflight",
    "backup",
    "migrations",
    "application-rollout",
    "public-smoke",
    "role-smoke",
    "event-smoke",
    "observability",
]


def complete_record():
    now = datetime.now(UTC)
    return LaunchRecord(
        launch_id="launch-1",
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        production_url="https://prod.example.invalid",
        kube_context="prod",
        started_at=now,
        completed_at=now,
        readiness_run_id="readiness-1",
        backup_reference="backup-1",
        outcome="SUCCEEDED",
        phases=[
            PhaseRecord(
                name=name,
                status="PASS",
                started_at=now,
                completed_at=now,
                operator="tester",
            )
            for name in REQUIRED
        ],
    )


def test_complete_successful_launch_passes_gate():
    gate = evaluate_launch(complete_record())
    assert gate.passed


def test_missing_required_phase_fails_gate():
    record = complete_record()
    record.phases = [phase for phase in record.phases if phase.name != "event-smoke"]
    gate = evaluate_launch(record)
    assert not gate.passed
    assert any("event-smoke" in reason for reason in gate.reasons)


def test_open_sev1_incident_fails_gate():
    record = complete_record()
    record.incidents.append(
        LaunchIncident(
            id="INC-1",
            severity="SEV1",
            summary="Critical outage",
            opened_at=datetime.now(UTC),
            status="OPEN",
        )
    )
    gate = evaluate_launch(record)
    assert not gate.passed
    assert any("SEV1" in reason for reason in gate.reasons)
