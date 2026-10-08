# Production Launch Evidence Policy

## Evidence root

Recommended:

```text
launch/evidence/<launch-id>/
  preflight/
  backup/
  migrations/
  rollout/
  smoke/
  monitoring/
  incidents/
```

## Evidence examples

```text
release manifest checksum/signature references
rendered bundle verification output
backup/PITR identifier
migration Job status/log references
rollout status
production-safe smoke reports
monitoring snapshots
alert screenshots/exports
incident timeline
```

## Never archive

```text
passwords
JWTs
cookies
private keys
database URLs with passwords
Redis/RabbitMQ credentials
S3 secret keys
Kubernetes Secret manifests containing values
kubeconfig
full environment-variable dumps
real user personal data
```

## Hash index

Generate:

```powershell
python .\scripts\generate-launch-evidence-index.py `
    --root .\launch\evidence `
    --output .\launch\PRODUCTION_LAUNCH_EVIDENCE_INDEX.json
```

## Immutability

Evidence should identify:

```text
launch ID
release tag
commit SHA
time
operator/job
```

Do not overwrite failure evidence after recovery. Add new evidence showing the
subsequent state.
