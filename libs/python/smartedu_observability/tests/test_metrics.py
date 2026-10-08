from datetime import UTC, datetime, timedelta

from smartedu_observability.metrics import Metrics


def test_metrics_exposition_contains_build_and_outbox_metrics():
    metrics = Metrics(
        service_name="assessment-service",
        service_version="test",
        environment="test",
    )
    metrics.set_outbox(
        pending=3,
        oldest_created_at=datetime.now(UTC) - timedelta(seconds=5),
    )
    output = metrics.exposition().decode()

    assert "smartedu_build_info" in output
    assert 'service="assessment-service"' in output
    assert "smartedu_outbox_pending" in output
    assert "smartedu_outbox_oldest_age_seconds" in output


def test_event_lag_metrics_accept_timezone_aware_timestamp():
    metrics = Metrics(service_name="reporting-service")
    metrics.observe_event(
        event_type="attendance.recorded",
        outcome="success",
        occurred_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    output = metrics.exposition().decode()
    assert "smartedu_events_processed_total" in output
    assert "smartedu_event_processing_lag_seconds" in output
