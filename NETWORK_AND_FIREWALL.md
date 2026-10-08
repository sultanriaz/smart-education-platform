# Network and Firewall Architecture

## Public boundary

Allow Internet ingress only to the production load balancer:

```text
TCP 443  required
TCP 80   optional redirect to HTTPS
```

Do not expose:

```text
FastAPI service ports
PostgreSQL 5432
Redis 6379
RabbitMQ 5672/15672/15692
MinIO/S3 administration
Prometheus
Grafana
Loki
Tempo
OTel Collector
Kubernetes API
```

to the public Internet.

## Cluster ingress

Ingress routes:

```text
/      -> frontend:8080
/api   -> api-gateway:8080
```

The application namespace has a default-deny ingress NetworkPolicy.

Internal application pods can communicate within the namespace because service
contracts require controlled service-to-service HTTP calls.

Ingress-controller traffic is allowed only to frontend/API Gateway.

## Egress

Sprint 23 does not enable global default-deny egress automatically because the
required destination CIDRs differ by deployment provider.

`examples/strict-egress.example.yaml` provides the starting pattern.

Before production go-live, add explicit egress for:

```text
cluster DNS
private PostgreSQL endpoint
private Redis endpoints
private RabbitMQ endpoint
object-storage endpoint
approved email provider
OTel/observability endpoint
identity/JWKS internal calls where applicable
```

Then enable default-deny egress and run the complete Sprint 19 E2E suite.

## Network ownership

Network policy supplements service authentication; it does not replace it.

JWT, internal service tokens, RBAC, event authorization, and database ownership
remain authoritative.
