# Sprint 8 Integration — Assessment Service

Extract this package into the Smart Education Platform repository root.

Expected additions:

- `services/assessment-service`
- `docker-compose.assessment.yml`
- `.github/workflows/assessment-service-ci.yml`

## Required contract reconciliation

Before declaring Sprint 8 integrated, inspect the real repository and adapt:

1. Identity Service JWKS URL, issuer, audience, role claim and token type.
2. Academic Service routes used for:
   - section lookup
   - teacher assignment validation
   - student enrollment validation
3. Notification Service internal event envelope and internal token header.
4. Repository-wide Docker network/service names.
5. Existing error-envelope conventions.

Do not query `identity_db` or `academic_db` directly.

## Required integrated smoke flow

Teacher:
1. create bank
2. create MCQ + short-text question
3. create quiz
4. attach questions
5. publish
6. assign to a section

Student:
7. start attempt
8. answer both questions
9. submit
10. verify objective score is auto-calculated

Teacher:
11. manually grade short-text response
12. verify final score/percentage/pass result
13. verify transactional outbox contains graded event

Then verify Notification integration using the actual Sprint 5 event contract.

## Ports

- Assessment API: 8008
- Assessment PostgreSQL host port: 5441
