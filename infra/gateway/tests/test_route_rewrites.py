from __future__ import annotations

import re
from pathlib import Path

TEMPLATE = (
    Path(__file__).resolve().parents[1] / "templates" / "default.conf.template"
).read_text(encoding="utf-8")


def test_service_rewrites_preserve_api_v1():
    namespaces = [
        "identity",
        "academic",
        "attendance",
        "scheduling",
        "notifications",
        "facilities",
        "learning",
        "assessments",
        "reporting",
        "platform",
    ]
    for namespace in namespaces:
        expected = rf"rewrite ^/api/v1/{namespace}/(.*)$ /api/v1/$1 break;"
        assert expected in TEMPLATE


def test_gateway_health_is_not_proxied():
    health_block = re.search(r"location = /health \{.*?\n    \}", TEMPLATE, re.S)
    assert health_block
    assert "proxy_pass" not in health_block.group(0)
