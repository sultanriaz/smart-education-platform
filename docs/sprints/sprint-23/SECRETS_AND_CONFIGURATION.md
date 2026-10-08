# Secrets and Configuration

## Principles

Production configuration separates:

```text
non-secret runtime configuration
secret runtime configuration
release identity
```

Non-secret values belong in ConfigMaps or deployment settings.

Secrets belong in the approved secret manager and are materialized into
Kubernetes Secrets at deployment time.

Release identity comes from the Sprint 22 immutable release manifest.

## Per-service secrets

Each workload references:

```text
<component>-secrets
```

This prevents one shared Kubernetes Secret from becoming a platform-wide blast
radius.

The included `secrets.example.yaml` is not part of `kustomization.yaml`.

Do not apply the example file unchanged.

## Required reconciliation

Codex must inspect every real service settings class and create the exact secret
key set for that service.

Examples include:

```text
DATABASE_URL
RABBITMQ_URL
REDIS_DURABLE_URL
S3 credentials
SMTP/provider credentials
JWT/JWKS trust settings where secret
internal service tokens
security-event encryption key
password-reset pepper
```

Do not create unused shared secrets "just in case."

## Secret manager

Preferred production patterns:

```text
cloud secret manager + workload identity
external-secrets operator
sealed delivery from CI into Kubernetes Secret
```

The provider-specific choice is deferred to the actual deployment environment.

Whatever mechanism is selected must provide:

```text
auditability
rotation
least privilege
no plaintext Git storage
no secrets in container image layers
no secrets in CI artifacts/logs
```

## Rotation

Rotation plans are required for:

```text
database passwords
RabbitMQ credentials
Redis credentials
S3 keys
email provider credentials
internal service tokens
security-event encryption keys
JWT signing keys
```

Where possible, use overlapping credentials/keys during rotation so availability
is not lost.

## GitHub Actions

Production/staging CI should use environment-scoped secrets and short-lived
federated credentials where supported.

Do not give pull-request jobs production deployment credentials.
