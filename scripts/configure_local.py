"""Generate private, isolated local-demo configuration without touching user .env files."""
from __future__ import annotations

import base64
import json
import secrets
from pathlib import Path

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".integration/runtime"
NAMES = ["identity", "academic", "attendance", "scheduling", "notification", "facility", "learning", "assessment", "reporting", "platform"]


def write_env(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n", encoding="utf-8")


def main():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    secret_file = RUNTIME / "secrets.json"
    if secret_file.exists():
        values = json.loads(secret_file.read_text())
    else:
        values = {key: secrets.token_urlsafe(32) for key in ["POSTGRES_SUPERUSER_PASSWORD", "RABBITMQ_PASSWORD", "MINIO_ROOT_PASSWORD", "LEARNING_S3_SECRET", "PLATFORM_S3_SECRET", "REPORTING_S3_SECRET", "INTERNAL_EVENT_TOKEN", "SECURITY_TOKEN_PEPPER", "DEMO_PASSWORD"] + [f"{name.upper()}_DB_PASSWORD" for name in NAMES]}
        values["SECURITY_NOTIFICATION_ENCRYPTION_KEY"] = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        values["DEMO_PASSWORD"] = "Demo!" + secrets.token_urlsafe(18) + "7aZ"
        secret_file.write_text(json.dumps(values, indent=2))
    for key in ("REDIS_CACHE_PASSWORD", "REDIS_DURABLE_PASSWORD", "TEACHER_PASSWORD", "STUDENT_PASSWORD"):
        if key not in values:
            values[key] = "Q7!" + secrets.token_urlsafe(32) + "aZ"
    secret_file.write_text(json.dumps(values, indent=2))
    for kind in ("cache", "durable"):
        original = (ROOT / f"infra/redis/{kind}.conf").read_text()
        (RUNTIME / f"redis-{kind}.conf").write_text(original + f"\nrequirepass {values[f'REDIS_{kind.upper()}_PASSWORD']}\n")
    keypath = RUNTIME / "identity-private.pem"
    if not keypath.exists():
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        keypath.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    public_keys = {}
    for name in NAMES:
        private = RUNTIME / f"{name}-internal-private.pem"
        if not private.exists():
            key = ed25519.Ed25519PrivateKey.generate()
            private.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        key = serialization.load_pem_private_key(private.read_bytes(), password=None)
        public_keys[f"{name}-service"] = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    infra = {**values, "POSTGRES_HOST_PORT": "55432", "REDIS_CACHE_HOST_PORT": "56379", "REDIS_DURABLE_HOST_PORT": "56380", "RABBITMQ_USER": "smartedu", "RABBITMQ_AMQP_HOST_PORT": "55672", "RABBITMQ_MANAGEMENT_HOST_PORT": "55673", "MINIO_ROOT_USER": "smartedu", "MINIO_API_HOST_PORT": "59000", "MINIO_CONSOLE_HOST_PORT": "59001"}
    write_env(RUNTIME / "infrastructure.env", infra)
    for index, name in enumerate(NAMES, 1):
        common = {
            "ENVIRONMENT": "development", "DATABASE_URL": f"postgresql+psycopg://{name}_svc:{values[f'{name.upper()}_DB_PASSWORD']}@127.0.0.1:55432/{name}_db",
            "JWT_ISSUER": "http://localhost:8001", "JWT_ACCESS_AUDIENCE": "smart-education-api", "JWT_AUDIENCE": "smart-education-api", "JWT_JWKS_URL": "http://127.0.0.1:8001/.well-known/jwks.json",
            "JWT_PRIVATE_KEY_FILE": str(keypath).replace("\\", "/"), "JWT_KEY_ID": "identity-local-integration-1", "JWT_PREVIOUS_PUBLIC_KEYS": "{}",
            "CORS_ORIGINS": '["http://localhost:5173","http://localhost:3000"]', "TRUSTED_HOSTS": "localhost,127.0.0.1,host.docker.internal",
            "TRACING_ENABLED": "false", "DB_POOL_SIZE": "5", "DB_MAX_OVERFLOW": "5", "DB_POOL_TIMEOUT_SECONDS": "5", "DB_STATEMENT_TIMEOUT_MS": "10000",
            "IDEMPOTENCY_REDIS_URL": f"redis://:{values['REDIS_DURABLE_PASSWORD']}@127.0.0.1:56380/1", "AUTH_SECURITY_REDIS_URL": f"redis://:{values['REDIS_DURABLE_PASSWORD']}@127.0.0.1:56380/2",
            "CELERY_BROKER_URL": f"redis://:{values['REDIS_DURABLE_PASSWORD']}@127.0.0.1:56380/3", "CELERY_RESULT_BACKEND": f"redis://:{values['REDIS_DURABLE_PASSWORD']}@127.0.0.1:56380/4",
            "REDIS_CACHE_URL": f"redis://:{values['REDIS_CACHE_PASSWORD']}@127.0.0.1:56379/0", "REDIS_DURABLE_URL": f"redis://:{values['REDIS_DURABLE_PASSWORD']}@127.0.0.1:56380/0",
            "RABBITMQ_URL": f"amqp://smartedu:{values['RABBITMQ_PASSWORD']}@127.0.0.1:55672/smartedu",
            "ACADEMIC_SERVICE_BASE_URL": "http://127.0.0.1:8002", "IDENTITY_SERVICE_BASE_URL": "http://127.0.0.1:8001", "NOTIFICATION_SERVICE_BASE_URL": "http://127.0.0.1:8005",
            "INTERNAL_EVENT_TOKEN": values["INTERNAL_EVENT_TOKEN"], "INTERNAL_SERVICE_TOKEN": values["INTERNAL_EVENT_TOKEN"], "SERVICE_INTERNAL_TOKEN": values["INTERNAL_EVENT_TOKEN"], "NOTIFICATION_INTERNAL_EVENT_TOKEN": values["INTERNAL_EVENT_TOKEN"],
            "INTERNAL_SERVICE_PRIVATE_KEY_FILE": str(RUNTIME / f"{name}-internal-private.pem").replace("\\", "/"), "TRUSTED_INTERNAL_PUBLIC_KEYS_JSON": "'" + json.dumps(public_keys) + "'",
            "SECURITY_TOKEN_PEPPER": values["SECURITY_TOKEN_PEPPER"], "SECURITY_NOTIFICATION_ENCRYPTION_KEY": values["SECURITY_NOTIFICATION_ENCRYPTION_KEY"], "FRONTEND_PUBLIC_URL": "http://localhost:5173",
            "STORAGE_BACKEND": "s3", "S3_ENDPOINT_URL": "http://127.0.0.1:59000", "S3_BUCKET": "learning-resources", "S3_ACCESS_KEY": "learning_svc", "S3_SECRET_KEY": values["LEARNING_S3_SECRET"],
            "EMAIL_PROVIDER": "smtp", "SMTP_HOST": "127.0.0.1", "SMTP_PORT": "11025",
            "BOOTSTRAP_ADMIN_EMAIL": "admin@demo.example.edu", "BOOTSTRAP_ADMIN_PASSWORD": values["DEMO_PASSWORD"], "BOOTSTRAP_ADMIN_NAME": "Demo Administrator",
        }
        write_env(RUNTIME / f"{name}-service.env", common)
    # Isolate this project's Docker names/volumes from unrelated running projects.
    compose = yaml.safe_load((ROOT / "docker-compose.infrastructure.yml").read_text())
    compose["name"] = "smartedu-local"
    for service in compose["services"].values():
        service.pop("container_name", None)
        if "ports" in service:
            service["ports"] = ["127.0.0.1:" + item for item in service["ports"]]
    compose["networks"]["smartedu-backend"]["name"] = "smartedu-local-backend"
    for kind in ("cache", "durable"):
        redis = compose["services"][f"redis-{kind}"]
        redis["environment"] = {"REDISCLI_AUTH": "${REDIS_" + kind.upper() + "_PASSWORD:?Redis password is required}"}
        redis["volumes"] = [item for item in redis["volumes"] if "redis.conf" not in item] + [f"./.integration/runtime/redis-{kind}.conf:/usr/local/etc/redis/redis.conf:ro"]
    compose["services"]["minio"].pop("image")
    compose["services"]["minio"]["build"] = {"context": "./infra/minio"}
    compose["services"]["minio-bootstrap"].pop("image")
    compose["services"]["minio-bootstrap"]["build"] = {"context": "./infra/minio", "dockerfile": "Dockerfile.mc"}
    compose["services"]["mailpit"] = {"image": "axllent/mailpit:latest", "ports": ["127.0.0.1:18025:8025", "127.0.0.1:11025:1025"], "networks": ["smartedu-backend"]}
    gateway = yaml.safe_load((ROOT / "docker-compose.gateway.yml").read_text())["services"]["api-gateway"]
    gateway["networks"] = ["smartedu-backend"]
    gateway["extra_hosts"] = ["host.docker.internal:host-gateway"]
    gateway["ports"] = ["127.0.0.1:18080:8080"]
    gateway["environment"]["LOCAL_NATIVE_UPSTREAMS"] = "true"
    gateway["environment"] = {**gateway["environment"], **{f"{name.upper()}_UPSTREAM": f"host.docker.internal:{8000+i}" for i,name in enumerate(NAMES, 1)}}
    compose["services"]["api-gateway"] = gateway
    (ROOT / "docker-compose.local.yml").write_text(yaml.safe_dump(compose, sort_keys=False))
    print("Local configuration generated under ignored .integration/runtime. Existing service .env files preserved.")


if __name__ == "__main__":
    main()
