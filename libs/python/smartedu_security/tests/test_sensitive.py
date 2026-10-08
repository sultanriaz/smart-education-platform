from smartedu_security import (
    decrypt_sensitive_json,
    encrypt_sensitive_json,
    generate_encryption_key,
)


def test_sensitive_payload_round_trip_and_ciphertext_hides_token():
    key = generate_encryption_key()
    payload = {
        "email": "student@example.edu",
        "token": "very-secret-reset-token",
    }

    encrypted = encrypt_sensitive_json(
        payload,
        key=key,
        purpose="identity.password_reset.requested",
    )

    assert "very-secret-reset-token" not in encrypted
    assert (
        decrypt_sensitive_json(
            encrypted,
            key=key,
            purpose="identity.password_reset.requested",
        )
        == payload
    )
