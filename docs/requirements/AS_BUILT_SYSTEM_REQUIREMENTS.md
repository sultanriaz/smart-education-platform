# Draft as-built system requirements

Updated 2026-10-08. Engineering draft; not an approved SRS or stakeholder signoff.

The latest user directive supersedes the outdated original SRS. Sources of truth: directive, available sprint packages/instructions, consolidated contracts/business rules, then documented quality targets. No final approved SRS was supplied; engineering proceeds without inventing institutional policy or approval.

Ten independent FastAPI services own their schemas: Identity, Academic, Attendance, Scheduling, Notification, Facility, Learning, Assessment, Reporting, and Platform. Cross-service communication uses authenticated HTTP and durable domain events. React/TypeScript provides Student, Teacher, and Admin workspaces through Nginx. Infrastructure includes PostgreSQL, authenticated Redis, RabbitMQ, private S3-compatible storage, background workers, and telemetry/deployment tooling.

Implementation and verification are separate. See [functional requirements](FUNCTIONAL_REQUIREMENTS.md), [quality requirements](NON_FUNCTIONAL_REQUIREMENTS.md), and [traceability](REQUIREMENTS_TRACEABILITY.md). Code presence does not establish successful runtime integration.

Local QA uses generated secrets, isolated Docker volumes/network, and explicitly labelled demo data seeded through service APIs. It does not represent production deployment or real institutional data.

Ten owner schemas were migrated to their Alembic heads. Real local verification covers role authentication, relationships, attendance summaries/finalization restrictions, recurrence, notes/private files, assessment grading/resume, booking conflicts, announcements/SMTP recovery, broker projections and durable jobs. [Delivery evidence and remaining limits](../integration/FINAL_DELIVERY_REPORT.md) distinguish unit, live, browser, load and external results. Proposed improvements and unverified features are recorded in [known limitations](../integration/KNOWN_LIMITATIONS.md).

Unresolved decisions: institutional registration/verification policy; representative approved 500-user workload/hardware; availability measurement window; formal RTO/RPO; production secrets/DNS/TLS; institutional UAT/accessibility acceptance. These remain pending while reversible integration work proceeds.
