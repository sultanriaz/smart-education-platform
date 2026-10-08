import pytest

from smartedu_security import PasswordPolicyError, validate_password


def test_strong_password_passes():
    validate_password(
        "T!gerRiver2026",
        email="student@example.edu",
        full_name="Student Example",
    )


@pytest.mark.parametrize(
    "password",
    [
        "shortA1!",
        "alllowercase123!",
        "ALLUPPERCASE123!",
        "NoDigitsHere!",
        "NoSymbols1234",
        "student@exampleA1!",
    ],
)
def test_weak_passwords_fail(password):
    with pytest.raises(PasswordPolicyError):
        validate_password(
            password,
            email="student@example.edu",
            full_name="Student Example",
        )
