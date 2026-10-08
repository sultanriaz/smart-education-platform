from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_observability_yaml_files_parse():
    files = sorted((ROOT / "infra" / "observability").rglob("*.yml"))
    assert files
    for path in files:
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_grafana_dashboards_parse_and_have_unique_uids():
    paths = sorted(
        (ROOT / "infra" / "observability" / "grafana" / "dashboards").glob("*.json")
    )
    assert paths
    uids = []
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["title"]
        uids.append(document["uid"])
    assert len(uids) == len(set(uids))


def test_alerts_have_runbooks_and_severity():
    rules = yaml.safe_load(
        (
            ROOT
            / "infra"
            / "observability"
            / "prometheus"
            / "rules"
            / "alerts.yml"
        ).read_text(encoding="utf-8")
    )

    alerts = [
        rule
        for group in rules["groups"]
        for rule in group["rules"]
        if "alert" in rule
    ]
    assert alerts
    for alert in alerts:
        assert alert["labels"]["severity"] in {"warning", "critical"}
        assert alert["annotations"]["runbook"].startswith("RUNBOOKS.md#")


def test_prometheus_scrapes_all_ten_services():
    config = yaml.safe_load(
        (
            ROOT
            / "infra"
            / "observability"
            / "prometheus"
            / "prometheus.yml"
        ).read_text(encoding="utf-8")
    )
    job = next(item for item in config["scrape_configs"] if item["job_name"] == "smartedu-services")
    targets = [
        target
        for block in job["static_configs"]
        for target in block["targets"]
    ]
    expected = {
        "identity-service:8000",
        "academic-service:8000",
        "attendance-service:8000",
        "scheduling-service:8000",
        "notification-service:8000",
        "facility-service:8000",
        "learning-service:8000",
        "assessment-service:8000",
        "reporting-service:8000",
        "platform-service:8000",
    }
    assert set(targets) == expected
