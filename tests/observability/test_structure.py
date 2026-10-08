from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SERVICES = {
    "identity-service",
    "academic-service",
    "attendance-service",
    "scheduling-service",
    "notification-service",
    "facility-service",
    "learning-service",
    "assessment-service",
    "reporting-service",
    "platform-service",
}


def test_all_ten_services_have_sprint21_bridge():
    found = {
        path.parent.parent.name
        for path in (ROOT / "services").glob("*-service/app/sprint21.py")
    }
    assert found == SERVICES


def test_runbook_anchors_exist_for_all_prometheus_alerts():
    import yaml

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
    runbooks = (ROOT / "RUNBOOKS.md").read_text(encoding="utf-8").casefold()

    for group in rules["groups"]:
        for rule in group["rules"]:
            if "alert" not in rule:
                continue
            reference = rule["annotations"]["runbook"]
            anchor = reference.split("#", 1)[1]
            heading = "## " + rule["alert"]
            assert heading.casefold() in runbooks, (
                f"{rule['alert']} points to missing runbook section #{anchor}"
            )


def test_public_gateway_observability_snippets_do_not_log_auth_headers():
    text = (
        ROOT / "infra" / "gateway" / "sprint21-http-context.conf"
    ).read_text(encoding="utf-8").casefold()
    assert "$http_authorization" not in text
    assert "$http_cookie" not in text
