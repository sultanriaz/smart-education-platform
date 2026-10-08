from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_production_topology_has_twelve_ha_workloads():
    payload = yaml.safe_load(
        (
            ROOT / "config" / "deployment" / "production-topology.yaml"
        ).read_text(encoding="utf-8")
    )
    workloads = payload["workloads"]
    assert len(workloads) == 12
    assert all(item["replicas"] >= 2 for item in workloads)
    assert all(item["min_replicas"] >= 2 for item in workloads)
    assert all(item["max_replicas"] >= item["replicas"] for item in workloads)


def test_stateful_production_dependencies_are_private_and_ha():
    payload = yaml.safe_load(
        (
            ROOT / "config" / "deployment" / "production-topology.yaml"
        ).read_text(encoding="utf-8")
    )
    dependencies = payload["external_dependencies"]
    stateful = {
        "postgresql",
        "redis-cache",
        "redis-durable",
        "rabbitmq",
        "object-storage",
    }
    selected = [item for item in dependencies if item["kind"] in stateful]
    assert selected
    assert all(item["private_network_only"] for item in selected)
    assert all(item["highly_available"] for item in selected)
