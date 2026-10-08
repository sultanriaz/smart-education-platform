# As-built architecture

The React/TypeScript frontend calls the Nginx gateway's service namespaces. Identity owns users, roles and cookie sessions. Academic owns enrollment and teaching relationships; dependent services call its authenticated contracts rather than reading its database.

| Owner | Owned data / key responsibilities | Local API |
|---|---|---:|
| Identity | Users, roles, refresh/security tokens, audit and encrypted recovery outbox | 8001 |
| Academic | Curriculum, profiles, sections, enrollment, assignments and bounded owner data jobs | 8002 |
| Attendance | Sessions, records, corrections, finalization and outbox | 8003 |
| Scheduling | Recurrence, occurrences, conflicts, history and outbox | 8004 |
| Notification | Inbox, recipients, preferences, campaigns, templates and delivery attempts | 8005 |
| Facility | Facilities, equipment, bookings, blocks and external reservations | 8006 |
| Learning | Targeted resources, versions, downloads, recommendations and private objects | 8007 |
| Assessment | Banks, questions, quizzes, assignments, attempts, answers, grading and outbox | 8008 |
| Reporting | Owned event inbox/projections, snapshots and export audit | 8009 |
| Platform | Support, registry, health checks, settings, feature flags, jobs, audit and search | 8010 |

Public prefixes are `/api/v1/identity`, `/academic`, `/attendance`, `/scheduling`, `/notifications`, `/facilities`, `/learning`, `/assessments`, `/reporting` and `/platform` under the gateway. Downstream internal paths are blocked there. Each API exposes `/health` and `/ready` directly; readiness includes its own current Alembic migration revision.

Eight domain outboxes publish committed events through owned worker processes. RabbitMQ uses durable queues and publisher confirmations. Notification, Reporting and Platform maintain deduplicating owned inboxes/projections. Retry attempts and backoff are persisted; exhausted messages are quarantined or moved to dead-letter queues for operator review. SMTP delivery is at least once across a crash after delivery and before acknowledgement.

PostgreSQL provides separate service databases/roles. Redis cache and durable state are isolated and authenticated. MinIO buckets are private and credentials have owner-specific policies. Generated local secrets, keys and process records stay under ignored `.integration/runtime`. The active deployment does not use the retained empty `apps/backend` scaffold.

Telemetry, deployment, readiness, UAT and release libraries/catalogs are integrated and pass their applicable local suites. Real collector pipelines, external CI, Kubernetes rollouts, staging acceptance and production operations remain separately verifiable activities.
