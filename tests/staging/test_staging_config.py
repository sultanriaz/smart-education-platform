from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_staging_topology_has_twelve_multi_replica_workloads():
    payload = yaml.safe_load(
        (ROOT / "config" / "staging" / "staging-topology.yaml").read_text(
            encoding="utf-8"
        )
    )
    workloads = payload["workload_overrides"]
    assert len(workloads) == 12
    assert all(item["replicas"] >= 2 for item in workloads)
    assert all(item["min_replicas"] >= 2 for item in workloads)


def test_staging_dependencies_are_declared():
    payload = yaml.safe_load(
        (ROOT / "config" / "staging" / "dependencies.yaml").read_text(
            encoding="utf-8"
        )
    )
    names = {item["name"] for item in payload["dependencies"]}
    assert {
        "postgresql",
        "redis-cache",
        "redis-durable",
        "rabbitmq",
        "object-storage",
        "email-provider",
        "observability",
    } == names


def test_acceptance_contains_role_e2e_and_recovery():
    payload = yaml.safe_load(
        (ROOT / "config" / "staging" / "staging-acceptance.yaml").read_text(
            encoding="utf-8"
        )
    )
    checks = set(payload["required_checks"])
    assert {"student_e2e", "teacher_e2e", "admin_e2e"} <= checks
    assert {"backup_restore_rehearsal", "pod_failure_drill"} <= checks
