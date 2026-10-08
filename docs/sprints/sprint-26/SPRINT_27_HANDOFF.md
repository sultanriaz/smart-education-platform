# Sprint 26 → Sprint 27 Handoff

Sprint 27 may deploy production only after the Sprint 26 gate passes.

Handoff package must contain:

```text
exact release-manifest.json
release checksum/signature/provenance evidence
rendered production deployment bundle
readiness run JSON
production readiness report
evidence index with SHA-256 hashes
GO/GO_WITH_CONDITIONS decision
risk register
migration plan
rollback/abort criteria
launch communications plan
operations/support ownership
```

## Immutable handoff

Record:

```text
release tag
commit SHA
12 image digests
```

Sprint 27 must verify these values before any production change.

If they differ, deployment stops and the candidate returns to staging/UAT/
readiness review as appropriate.

## Sprint 27 responsibilities

Sprint 27 owns:

```text
actual production deployment execution
production migrations
launch smoke verification
real-time monitoring
abort/rollback execution if needed
launch evidence
```

Sprint 26 does not claim those actions have happened.
