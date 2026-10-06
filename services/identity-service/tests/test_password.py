from app.security.password import hash_password, verify_password


def test_password_hashing_round_trip():
    password = "StrongPassword123!"
    encoded = hash_password(password)
    assert encoded != password
    assert verify_password(password, encoded)
    assert not verify_password("wrong-password", encoded)
