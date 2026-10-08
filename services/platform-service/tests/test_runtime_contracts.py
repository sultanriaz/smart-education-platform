from fastapi.testclient import TestClient

from app.main import app


def test_platform_health_has_service_context_and_trusted_host_validation():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers["X-Service-Name"] == "platform-service"
        assert response.headers["X-Request-ID"]
        assert client.get("/health", headers={"Host": "untrusted.example.edu"}).status_code == 400


def test_platform_contract_middleware_is_installed():
    middleware = {item.cls.__name__ for item in app.user_middleware}
    assert {
        "IdempotencyMiddleware",
        "RequestContextMiddleware",
        "TrustedHostMiddleware",
    } <= middleware
