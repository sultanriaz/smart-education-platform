from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
SERVICES = {f"{service}-service" for service in (
    "identity", "academic", "attendance", "scheduling", "notification",
    "facility", "learning", "assessment", "reporting", "platform",
)}


def test_worker_manifests_match_service_secrets_and_images():
    for environment in ("staging", "production"):
        directory = ROOT / "deploy" / "kubernetes" / environment
        kustomization = yaml.safe_load((directory / "kustomization.yaml").read_text())
        for name in SERVICES:
            path = directory / "workers" / f"{name}.yaml"
            assert f"workers/{name}.yaml" in kustomization["resources"]
            worker = yaml.safe_load(path.read_text())
            api = yaml.safe_load((directory / "deployments" / f"{name}.yaml").read_text())
            worker_pod = worker["spec"]["template"]["spec"]
            wc = worker_pod["containers"][0]
            ac = api["spec"]["template"]["spec"]["containers"][0]
            assert wc["image"] == ac["image"]
            assert wc["envFrom"] == ac["envFrom"]
            assert wc["command"] == ["python", "-m", "app.event_worker"]
            assert wc["securityContext"]["readOnlyRootFilesystem"]
            assert worker_pod["automountServiceAccountToken"] is False
            assert worker_pod["terminationGracePeriodSeconds"] >= 30
            assert worker["spec"]["replicas"] == 1
            assert worker_pod["serviceAccountName"] == name


def test_frontend_read_only_startup_contract_and_public_origins():
    scripts = ROOT / "apps" / "frontend" / "docker"
    runtime = (scripts / "40-runtime-config.sh").read_text()
    headers = (scripts / "45-security-headers.sh").read_text()
    nginx = (scripts / "nginx.conf").read_text()
    assert "cat > /tmp/runtime-config.js" in runtime
    assert "cat > /tmp/security-headers.conf" in headers
    assert "alias /tmp/runtime-config.js;" in nginx
    assert "include /tmp/security-headers.conf;" in nginx
    assert "/usr/share/nginx/html/runtime-config.js" not in runtime
    for environment in ("staging", "production"):
        directory = ROOT / "deploy" / "kubernetes" / environment
        cm = yaml.safe_load((directory / "configmap.yaml").read_text())["data"]
        assert cm["API_BASE_URL"].startswith("https://")
        assert cm["JWT_ISSUER"].startswith("https://")
        assert cm["JWT_ISSUER"] == cm["PUBLIC_BASE_URL"]
        assert cm["REFRESH_COOKIE_SECURE"] == "true"
        assert cm["STORAGE_BACKEND"] == "s3"
        secrets_text = (directory / "secrets.example.yaml").read_text()
        assert "JWT_KEY_ID: REPLACE_WITH_ACTIVE_SIGNING_KEY_ID" in secrets_text
        assert cm["STORAGE_BACKEND"] == "s3"
        identity = yaml.safe_load((directory / "deployments" / "identity-service.yaml").read_text())
        c = identity["spec"]["template"]["spec"]["containers"][0]
        assert any(e["name"] == "JWT_PRIVATE_KEY_FILE" for e in c["env"])
        assert any(v["name"] == "jwt-signing-key" for v in c["volumeMounts"])
        assert "identity-service-signing-key" in (directory / "signing-key.example.yaml").read_text()
