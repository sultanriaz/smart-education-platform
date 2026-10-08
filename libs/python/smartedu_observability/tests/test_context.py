from smartedu_observability.context import (
    clear_request_context,
    get_correlation_id,
    get_request_id,
    set_request_context,
)


def test_request_context_defaults_correlation_to_request_id():
    context = set_request_context(request_id="req-1")
    try:
        assert context.request_id == "req-1"
        assert context.correlation_id == "req-1"
        assert get_request_id() == "req-1"
        assert get_correlation_id() == "req-1"
    finally:
        clear_request_context()


def test_request_context_generates_ids():
    context = set_request_context()
    try:
        assert context.request_id
        assert context.correlation_id
    finally:
        clear_request_context()
