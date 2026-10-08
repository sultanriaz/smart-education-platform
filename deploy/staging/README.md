# Staging Deployment Adapter

Sprint 22 consumes the repository's actual Compose topology through `STAGING_COMPOSE_FILES`; it does not invent a second deployment architecture. After Codex reconciliation, Compose services should reference digest-pinned variables emitted by `render-release-env.py`, for example `image: ${IDENTITY_SERVICE_IMAGE:?release image required}`. Never use `latest`.

The runner validates the manifest, performs an approved backup hook, pulls images, upgrades only migration-bearing services, deploys, checks the Gateway health URL, and records current/previous manifests. Database downgrade is never automatic.
