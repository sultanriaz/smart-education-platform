# Sprint 22 Release Strategy

Releases use immutable SemVer tags `vMAJOR.MINOR.PATCH`. Every release builds all deployable components from the exact tagged commit. Images receive human-readable release/SHA tags, but deployments consume only digest references from `release-manifest.json`.

Every release image must have an SBOM, build provenance, vulnerability gate, and keyless Sigstore/Cosign signature. The GitHub Release stores the signed-image manifest and checksum. `latest` is prohibited.

A release tag must point to a commit already contained in `main`. If a release candidate fails, fix forward in source and issue a new tag rather than moving an existing tag.
