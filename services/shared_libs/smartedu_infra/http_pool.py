"""Bounded per-origin HTTP connections, with credentials supplied per request."""

from __future__ import annotations

import atexit
from http.cookiejar import DefaultCookiePolicy
from threading import Lock
from urllib.parse import urlsplit

import httpx


class NoCookies(DefaultCookiePolicy):
    def set_ok(self, cookie, request):
        return False


_clients: dict[str, httpx.Client] = {}
_lock = Lock()


def shared_http_client(base_url: str) -> httpx.Client:
    url = urlsplit(base_url)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ValueError("Invalid service URL")
    origin = f"{url.scheme}://{url.netloc}"
    with _lock:
        if origin not in _clients:
            if len(_clients) >= 16:
                raise RuntimeError("Service HTTP origin limit reached")
            client = httpx.Client(
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                timeout=httpx.Timeout(5, connect=3, pool=2),
                follow_redirects=False,
            )
            client.cookies.jar.set_policy(NoCookies())
            _clients[origin] = client
        return _clients[origin]


def close_http_clients():
    with _lock:
        for client in _clients.values():
            client.close()
        _clients.clear()


atexit.register(close_http_clients)
