# Production Secrets, DNS, and TLS Readiness

## Secrets

Production secrets must come from the approved secret manager/runtime injection
mechanism.

Verify per service:

```text
DB credentials
internal service token where used
RabbitMQ credentials
Redis credentials
object-storage credentials
email-provider credentials
Identity signing/verification keys
reset/security peppers and encryption keys
```

Application pods should receive only the credentials they require.

## Secret rotation

Before launch, document rotation for:

```text
JWT signing keys
DB credentials
broker credentials
Redis credentials
object-storage credentials
email credentials
internal tokens
```

Prefer overlap/dual-key rotation where supported.

## DNS

Verify the real production hostname:

```text
resolves to intended production edge
has expected TTL
does not point to staging
has an owner and change procedure
```

## TLS

Verify:

```text
certificate hostname
trusted chain
minimum TLS version per policy
renewal mechanism
expiry alert
HTTP -> HTTPS redirect
```

## Public exposure

Public:

```text
HTTPS frontend/API entry point
```

Private:

```text
domain service ports
PostgreSQL
Redis
RabbitMQ
object-storage admin/control plane
Prometheus/Grafana/Loki/Tempo unless explicitly protected
Kubernetes API
```
