# Sprint 22 CI/CD Architecture

```text
PR / push
   -> change planner
   -> per-service tests + frontend/gateway tests
   -> container build + vulnerability scan
   -> security/observability/quality gates

SemVer tag on main
   -> rebuild all 12 deployable images from exact tag commit
   -> SBOM + provenance
   -> push GHCR
   -> keyless sign immutable digest
   -> release-manifest.json + checksum
   -> GitHub Release

Approved staging deployment
   -> self-hosted staging runner
   -> download manifest
   -> checksum + signature verification
   -> pre-migration backup
   -> service-owned migrations
   -> digest-pinned Compose deployment
   -> health/live smoke
```

Build runners never need staging database credentials. Deployment secrets are scoped to the protected GitHub Environment and self-hosted staging runner.
