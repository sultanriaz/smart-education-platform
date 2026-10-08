# Sprint 22 Artifact Retention

Short-lived CI artifacts such as JUnit reports may retain 14–30 days. GitHub Releases are the durable release record and contain the release manifest/checksum. Image SBOM/provenance/signatures remain attached to registry artifacts.

Do not archive `.env` files, access tokens, database backups, private keys, or staging secrets as generic CI artifacts. Database backup retention is an operational/deployment concern and must use approved protected storage.
