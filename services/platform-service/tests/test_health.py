from app.main import app


def test_openapi_core_paths():
    schema = app.openapi()
    paths = schema["paths"]
    assert "/health" in paths
    assert "/ready" in paths
    assert "/api/v1/search" in paths
    assert "/api/v1/support/tickets" in paths
    assert "/api/v1/internal/events" in paths
