import pytest

from smartedu_security import MalwareScanError, parse_clamav_response


def test_clamav_ok_response():
    result = parse_clamav_response("stream: OK")
    assert result.clean is True
    assert result.signature is None


def test_clamav_found_response():
    result = parse_clamav_response("stream: Eicar-Test-Signature FOUND")
    assert result.clean is False
    assert result.signature == "Eicar-Test-Signature"


def test_clamav_unexpected_response_fails_closed():
    with pytest.raises(MalwareScanError):
        parse_clamav_response("stream: UNKNOWN")
