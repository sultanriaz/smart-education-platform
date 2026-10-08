# DNS, TLS, and Edge Security

## DNS

Production requires an institution-approved public hostname, for example:

```text
smartedu.university.example
```

The generated source uses:

```text
smartedu.example.edu
```

only as a placeholder. `preflight-production.py --strict` rejects that
placeholder.

Point the final DNS record to the production load balancer.

## TLS

TLS terminates at the production Ingress/load-balancer boundary.

Required:

```text
valid publicly trusted certificate
automatic renewal or managed certificate lifecycle
HTTP -> HTTPS redirect
TLS 1.2 minimum
TLS 1.3 preferred
```

The application Ingress references:

```text
smartedu-tls
```

An optional cert-manager example is included but is not applied automatically.

## HSTS

Sprint 18 HSTS should be enabled only after HTTPS and domain ownership are fully
validated.

Do not preload an incorrect domain.

## Firewall / security groups

Provider firewall rules should enforce:

```text
Internet -> load balancer: 443/80 only
load balancer -> cluster ingress: provider-required private path
cluster -> PostgreSQL: database port only
cluster -> Redis: Redis TLS/private port only
cluster -> RabbitMQ: broker TLS/private port only
cluster -> object storage: HTTPS
operations/VPN -> observability/admin endpoints
```

Avoid source range `0.0.0.0/0` on databases, message brokers, Redis, or admin
interfaces.
