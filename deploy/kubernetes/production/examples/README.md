# Production Examples

Files in this directory are **not** referenced by `kustomization.yaml`.

They require environment-specific reconciliation before use.

- `cert-manager-certificate.example.yaml` requires the real public DNS name and
  approved `ClusterIssuer`.
- `strict-egress.example.yaml` demonstrates the start of a default-deny egress
  model. It intentionally omits the provider-specific PostgreSQL, Redis,
  RabbitMQ, object-storage, email-provider, and observability destination
  CIDRs/endpoints.

Do not enable default-deny egress until every required dependency has an
explicit tested rule. A partially configured egress policy can make healthy
services appear unavailable.
