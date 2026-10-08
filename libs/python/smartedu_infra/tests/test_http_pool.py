import httpx

from smartedu_infra import http_pool


def test_pool_reuses_connections_without_reusing_credentials_or_cookies(monkeypatch):
    original = httpx.Client
    seen = []

    def handler(request):
        seen.append((request.headers.get("authorization"), request.headers.get("cookie")))
        return httpx.Response(200, headers={"Set-Cookie": "credential=private; Path=/"})

    monkeypatch.setattr(
        http_pool.httpx,
        "Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    http_pool.close_http_clients()
    try:
        client = http_pool.shared_http_client("https://academic.example.edu")
        assert client is http_pool.shared_http_client("https://academic.example.edu/other")
        client.get("https://academic.example.edu/check", headers={"Authorization": "Bearer first"})
        client.get("https://academic.example.edu/check", headers={"Authorization": "Bearer second"})
        assert seen == [("Bearer first", None), ("Bearer second", None)]
    finally:
        http_pool.close_http_clients()
