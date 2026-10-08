from datetime import UTC, datetime

from smartedu_security import (
    constant_time_token_match,
    issue_one_time_token,
)


def test_one_time_token_is_hashed_and_expires():
    now = datetime(2026, 10, 7, tzinfo=UTC)
    token = issue_one_time_token(
        ttl_seconds=1800,
        pepper="pepper",
        now=now,
    )

    assert token.plaintext
    assert token.plaintext not in token.digest
    assert token.expires_at.isoformat() == "2026-10-07T00:30:00+00:00"
    assert constant_time_token_match(
        token.plaintext,
        token.digest,
        pepper="pepper",
    )
    assert not constant_time_token_match(
        token.plaintext + "x",
        token.digest,
        pepper="pepper",
    )
