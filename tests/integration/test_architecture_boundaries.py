from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_ROOT = REPO_ROOT / "services"

SERVICE_NAMES = (
    "identity-service",
    "academic-service",
    "attendance-service",
    "scheduling-service",
    "notification-service",
    "facility-service",
    "learning-service",
    "assessment-service",
    "reporting-service",
    "platform-service",
)


def python_sources(service: str):
    root = SERVICES_ROOT / service
    if not root.exists():
        return []
    return [
        path
        for path in root.rglob("*.py")
        if ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and "tests" not in path.parts
    ]


@pytest.mark.architecture
@pytest.mark.parametrize("service", SERVICE_NAMES)
def test_service_does_not_import_another_service_package(service):
    sources = python_sources(service)
    if not sources:
        pytest.skip(f"{service} not present in this checkout")

    others = [name for name in SERVICE_NAMES if name != service]
    offenders = []

    for path in sources:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for other in others:
            package_like = other.replace("-service", "").replace("-", "_")
            patterns = [
                rf"from\s+services\.{re.escape(package_like)}\b",
                rf"import\s+services\.{re.escape(package_like)}\b",
                rf"from\s+{re.escape(package_like)}\.app\b",
            ]
            if any(re.search(pattern, text) for pattern in patterns):
                offenders.append(f"{path.relative_to(REPO_ROOT)} -> {other}")

    assert not offenders, "Cross-service Python imports found:\n" + "\n".join(offenders)


@pytest.mark.architecture
def test_frontend_does_not_reference_private_service_ports():
    frontend = REPO_ROOT / "apps" / "frontend" / "src"
    if not frontend.exists():
        pytest.skip("frontend not present")

    offenders = []
    for path in frontend.rglob("*"):
        if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for port in range(8001, 8011):
            if f":{port}" in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{port}")

    assert not offenders, (
        "Frontend must use API Gateway only; direct service ports found:\n"
        + "\n".join(offenders)
    )
