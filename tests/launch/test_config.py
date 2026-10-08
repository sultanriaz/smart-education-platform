from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_component_catalog_has_twelve_components():
    payload = yaml.safe_load(
        (ROOT / "config" / "launch" / "components.yaml").read_text(
            encoding="utf-8"
        )
    )
    components = payload["components"]
    assert len(components) == 12
    names = {item["component"] for item in components}
    assert {
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
        "frontend",
        "api-gateway",
    } == names


def test_only_backend_components_have_migration_commands():
    payload = yaml.safe_load(
        (ROOT / "config" / "launch" / "components.yaml").read_text(
            encoding="utf-8"
        )
    )
    by_name = {item["component"]: item for item in payload["components"]}
    assert by_name["frontend"]["migration"] is False
    assert by_name["api-gateway"]["migration"] is False
    for name, item in by_name.items():
        if name not in {"frontend", "api-gateway"}:
            assert item["migration"] is True
            assert item["migration_command"]


def test_launch_policy_forbids_database_downgrade():
    payload = yaml.safe_load(
        (ROOT / "config" / "launch" / "policy.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert payload["rollback_database_downgrade_allowed"] is False
    assert payload["require_backup_before_migrations"] is True
    assert payload["require_all_migrations_complete_before_rollout"] is True
