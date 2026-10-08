from __future__ import annotations

from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from app.schemas.admin import ServiceRegistryCreate


@pytest.mark.parametrize(
    "url",
    [
        "http://169.254.169.254",
        "https://untrusted.example.edu",
        "http://user:password@identity-service:8000",
        "http://identity-service:8000?override=1",
    ],
)
def test_registry_rejects_untrusted_origins(url):
    with pytest.raises(ValidationError):
        ServiceRegistryCreate(service_name="identity-service", base_url=url)


@dataclass
class Response:
    status_code: int


class FakeClient:
    def __init__(self, status=200):
        self.status = status

    def get(self, url, timeout):
        return Response(status_code=self.status)


def test_service_registry_and_health(platform):
    platform.upsert_service(
        ServiceRegistryCreate(
            service_name="identity-service",
            base_url="http://identity-service:8000",
            critical=True,
        )
    )
    rows = platform.check_services(FakeClient(200))
    assert len(rows) == 1
    assert rows[0].status == "HEALTHY"
    assert rows[0].health_ok is True
    assert rows[0].ready_ok is True


def test_degraded_service(platform):
    platform.upsert_service(
        ServiceRegistryCreate(
            service_name="academic-service",
            base_url="http://academic-service:8000",
        )
    )
    rows = platform.check_services(FakeClient(503))
    assert rows[0].status == "DEGRADED"
