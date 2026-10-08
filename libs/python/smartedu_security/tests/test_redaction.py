from smartedu_security import redact_mapping


def test_sensitive_log_fields_are_redacted_recursively():
    value = {
        "email": "student@example.edu",
        "password": "secret",
        "headers": {
            "Authorization": "Bearer abc",
            "X-Request-ID": "r1",
        },
        "event": {
            "encrypted_payload": "ciphertext",
        },
    }

    redacted = redact_mapping(value)

    assert redacted["email"] == "student@example.edu"
    assert redacted["password"] == "[REDACTED]"
    assert redacted["headers"]["Authorization"] == "[REDACTED]"
    assert redacted["headers"]["X-Request-ID"] == "r1"
    assert redacted["event"]["encrypted_payload"] == "[REDACTED]"
