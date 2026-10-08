from app.main import app


def test_openapi_contains_health():
    schema = app.openapi()
    assert "/health" in schema["paths"]
    assert "/api/v1/dashboard/overview" in schema["paths"]
