# Sprint 22 — CI/CD Engineering

Sprint 22 turns the repository into a controlled build/release/promotion pipeline without changing the distributed service architecture.

## What is included

- `smartedu-cicd` shared package for component planning, SemVer/tag checks, immutable release manifests, and image-ref rendering.
- Change-aware CI for ten FastAPI services, React frontend, and Nginx Gateway.
- Reusable Python-service and container-validation workflows.
- Container vulnerability scanning for changed components.
- SemVer release workflow that rebuilds all 12 deployable images from the exact tagged commit.
- GHCR push using immutable digests.
- SBOM and build provenance generation.
- Keyless Sigstore/Cosign image signing through GitHub OIDC.
- GitHub provenance attestations.
- GitHub Release assets containing `release-manifest.json` and checksums.
- Protected staging deployment using a self-hosted staging runner.
- Signature/checksum verification before deployment.
- Migration-aware release manifests and staging migration gate.
- Forward-only/default migration and rollback policy.
- Application-image rollback workflow requiring explicit schema compatibility confirmation.
- Supply-chain, branch-protection, artifact-retention, and self-hosted-runner guidance.

## Deployable release components

```text
identity-service
academic-service
attendance-service
scheduling-service
notification-service
facility-service
learning-service
assessment-service
reporting-service
platform-service
frontend
api-gateway
```

A release always includes all 12 images so one release manifest completely describes an application version.

## Immutable release model

Human-friendly tags exist for navigation, but deployment uses only:

```text
ghcr.io/<owner>/smartedu-<component>@sha256:<digest>
```

`latest` is prohibited.

## Main workflows

```text
.github/workflows/ci.yml
.github/workflows/reusable-python-service.yml
.github/workflows/reusable-container-check.yml
.github/workflows/release.yml
.github/workflows/staging-deploy.yml
.github/workflows/staging-rollback.yml
.github/workflows/supply-chain.yml
```

## Release flow

```text
Pull request
  -> affected-component plan
  -> tests / lint / frontend / Gateway
  -> container build + Trivy
  -> security/quality gates

vX.Y.Z tag on main
  -> build all images
  -> SBOM + provenance
  -> push GHCR
  -> keyless Cosign sign
  -> GitHub attestation
  -> release-manifest.json
  -> GitHub Release

Approved staging promotion
  -> download manifest
  -> checksum/signature verify
  -> backup hook
  -> migrations
  -> digest-pinned deployment
  -> health/live smoke
```

Production deployment is intentionally not finalized here because Sprint 23 owns deployment architecture and later sprints own production readiness/deployment.
