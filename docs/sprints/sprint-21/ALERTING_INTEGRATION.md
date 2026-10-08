# Sprint 21 Alerting Integration

The bundled Alertmanager configuration intentionally has local no-op receivers.

This prevents generated development code from silently sending platform
telemetry to an external party.

## Staging / production

Replace the receivers with the institution's approved channel, for example:

```text
email
Slack
Microsoft Teams via supported bridge
PagerDuty/Opsgenie or equivalent incident system
```

Keep credentials in deployment secret storage.

Do not commit:

```text
webhook URLs
SMTP passwords
PagerDuty routing keys
bot tokens
```

## Routing

Recommended minimum routing:

```text
warning  -> engineering/operations channel
critical -> urgent incident channel + responsible owner
```

Group by:

```text
alertname
service
severity
```

to avoid notification storms.

## Testing

Before production:

1. route alerts to a staging receiver
2. intentionally stop one QA service
3. verify `SmartEduServiceDown` fires
4. verify Alertmanager groups the alert
5. verify the destination receives it
6. restore the service
7. verify a resolved notification if the chosen receiver supports it

Also test a synthetic high-error/latency alert.

Do not test production alerting by causing a real user outage.
