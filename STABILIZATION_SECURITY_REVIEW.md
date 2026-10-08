# Post-Launch Security Review

Sprint 28 does not replace Sprint 18 security hardening.

It checks whether production operation introduced a security regression.

## Review

Check:

```text
failed/suspicious authentication trends
admin/audit events
unexpected authorization denials or bypass reports
public surface drift
secret leakage alerts
container/runtime alerts
production operator access
upload/security alerts
JWT/JWKS errors
```

## Secrets

Review launch/stabilization evidence and logs for accidental exposure of:

```text
passwords
JWTs
cookies
private keys
DB credentials
Redis/RabbitMQ credentials
object-storage keys
kubeconfig
```

If exposure is suspected:

```text
restrict access
rotate affected credential
preserve incident evidence
assess impact
record a security issue/incident
```

## Public surface drift

Confirm only the intended edge remains public.

A temporary troubleshooting exposure must not silently become permanent.

## Security hotfixes

Security hotfixes are new immutable releases.

They must retain:

```text
build/sign/SBOM/provenance
focused security regression
protected production deployment
rollback/backup/migration guardrails
```

Severity determines urgency, not whether release controls disappear.
