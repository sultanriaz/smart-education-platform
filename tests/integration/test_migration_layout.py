from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SERVICES = (
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
)


@pytest.mark.architecture
@pytest.mark.parametrize("service", SERVICES)
def test_each_service_has_own_alembic_configuration(service):
    service_root = ROOT / "services" / service
    if not service_root.exists():
        pytest.skip(f"{service} not present")
    assert (service_root / "alembic.ini").exists(), f"{service} has no alembic.ini"


@pytest.mark.architecture
def test_no_root_shared_alembic_history():
    assert not (ROOT / "alembic.ini").exists(), (
        "A root-wide Alembic history would weaken database-per-service ownership"
    )
