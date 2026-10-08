from smartedu_observability.events import inject_trace_context


def test_trace_context_injection_preserves_existing_event_metadata():
    metadata = inject_trace_context({"schema_version": "1", "source": "test"})
    assert metadata["schema_version"] == "1"
    assert metadata["source"] == "test"
