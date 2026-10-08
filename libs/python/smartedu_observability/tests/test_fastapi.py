from fastapi import FastAPI
from fastapi.testclient import TestClient

from smartedu_observability.install import install_observability
from smartedu_observability.settings import ObservabilitySettings


def make_app():
    app = FastAPI()

    @app.get("/items/{item_id}")
    def item(item_id: str):
        return {"id": item_id}

    runtime = install_observability(
        app,
        settings=ObservabilitySettings(
            SERVICE_NAME="test-service",
            ENVIRONMENT="test",
            SERVICE_VERSION="1",
            TRACING_ENABLED=False,
            JSON_LOGS=False,
        ),
    )
    return app, runtime


def test_request_ids_are_returned_and_metrics_use_route_template():
    app, _runtime = make_app()
    client = TestClient(app)

    response = client.get(
        "/items/12345",
        headers={"X-Correlation-ID": "corr-1"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert response.headers["X-Correlation-ID"] == "corr-1"

    metrics = client.get("/metrics").text
    assert 'route="/items/{item_id}"' in metrics
    assert 'route="/items/12345"' not in metrics


def test_invalid_incoming_ids_are_replaced():
    app, _runtime = make_app()
    response = TestClient(app).get(
        "/items/1",
        headers={
            "X-Request-ID": 'bad"\\nvalue',
            "X-Correlation-ID": "ok-correlation",
        },
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != 'bad"\\nvalue'
    assert response.headers["X-Correlation-ID"] == "ok-correlation"
