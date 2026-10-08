from __future__ import annotations

from dataclasses import dataclass

from .models import LaunchRecord

REQUIRED_PHASES = (
    "preflight",
    "backup",
    "migrations",
    "application-rollout",
    "public-smoke",
    "role-smoke",
    "event-smoke",
    "observability",
)


@dataclass(frozen=True, slots=True)
class LaunchGate:
    passed: bool
    reasons: list[str]


def evaluate_launch(record: LaunchRecord) -> LaunchGate:
    reasons: list[str] = []
    phases = {item.name: item for item in record.phases}

    for name in REQUIRED_PHASES:
        phase = phases.get(name)
        if not phase:
            reasons.append(f"required phase missing: {name}")
        elif phase.status != "PASS":
            reasons.append(f"required phase not PASS: {name}={phase.status}")

    open_sev1 = [
        incident.id
        for incident in record.incidents
        if incident.severity == "SEV1" and incident.status != "CLOSED"
    ]
    if open_sev1:
        reasons.append(f"open SEV1 incidents: {open_sev1}")

    if record.completed_at is None:
        reasons.append("launch record is not completed")

    if record.outcome != "SUCCEEDED":
        reasons.append(f"launch outcome is not SUCCEEDED: {record.outcome}")

    return LaunchGate(passed=not reasons, reasons=reasons)
