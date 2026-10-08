import httpx
import pytest

from smartedu_testkit import SequenceTransport


@pytest.mark.asyncio
async def test_sequence_transport_is_deterministic():
    transport = SequenceTransport([503, 200])
    async with httpx.AsyncClient(transport=transport) as client:
        first = await client.get("http://service.test/")
        second = await client.get("http://service.test/")
    assert first.status_code == 503
    assert second.status_code == 200
    assert transport.calls == 2
