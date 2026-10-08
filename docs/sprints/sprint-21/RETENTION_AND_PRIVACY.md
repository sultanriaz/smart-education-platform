# Sprint 21 Telemetry Retention and Privacy

Telemetry can contain personal or operational data even when the business
database is properly secured.

## Logs

Bundled local Loki retention:

```text
7 days
```

Production retention must be explicitly approved.

Reduce retention when logs contain educational identifiers that are not needed
for operations.

## Traces

Bundled local Tempo retention:

```text
48 hours
```

Traces are primarily for short-term diagnosis.

Longer production retention should be justified by operational need and cost.

## Metrics

Bundled local Prometheus retention:

```text
35 days
```

This preserves enough history for the rolling 30-day availability SLO while
leaving a small comparison margin.

Metrics should avoid personal identifiers, so longer retention is generally less
privacy-sensitive than logs/traces.

## Data minimization

Never use high-cardinality identifiers as metric labels.

Avoid recording:

```text
email addresses
passwords
JWTs
assessment answer bodies
complete uploaded-resource content
private notification bodies
```

in telemetry.

## Incident exports

Incident artifact bundles should be reviewed before sharing.

Do not export environment dumps because they commonly contain secrets.
