# Sprint 22 Supply-Chain Security

Release controls:

```text
least-privilege GitHub workflow permissions
pinned major action versions under dependency review
Trivy HIGH/CRITICAL image/filesystem gates
Bandit / pip-audit / npm audit from existing security workflows
SBOM generation during image build
SLSA-style build provenance through GitHub attestation
keyless Cosign signatures via GitHub OIDC
immutable digest deployment
release-manifest checksum
no registry passwords stored for GHCR release builds
```

Self-hosted staging runners should be dedicated, patched, non-public, and must not execute untrusted pull-request code. Deployment environments hold operational secrets; build jobs should not receive staging/production secrets.
