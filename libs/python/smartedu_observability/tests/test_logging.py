import json
import logging

from smartedu_observability.context import clear_request_context, set_request_context
from smartedu_observability.logging import JsonFormatter


def test_json_formatter_redacts_sensitive_fields_and_adds_context():
    set_request_context(request_id="req-1", correlation_id="corr-1")
    try:
        record = logging.LogRecord(
            "test",
            logging.INFO,
            __file__,
            1,
            "hello",
            (),
            None,
        )
        record.structured = {
            "user_id": "u1",
            "password": "secret-password",
            "headers": {
                "Authorization": "Bearer hidden",
                "X-Request-ID": "req-1",
            },
        }
        formatter = JsonFormatter(
            service_name="academic-service",
            environment="test",
            service_version="1",
        )
        payload = json.loads(formatter.format(record))

        assert payload["service"] == "academic-service"
        assert payload["request_id"] == "req-1"
        assert payload["correlation_id"] == "corr-1"
        assert payload["fields"]["user_id"] == "u1"
        assert payload["fields"]["password"] == "[REDACTED]"
        assert payload["fields"]["headers"]["Authorization"] == "[REDACTED]"
    finally:
        clear_request_context()
