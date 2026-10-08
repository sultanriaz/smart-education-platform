# Merge decisions

Original tracked work retained in the Git bundle. Every replaced file also has a staged pre-overlay backup. Source ZIPs preserved.

Root sprint instructions and verification reports are stored under `docs/sprints/sprint-NN/`; reports are historical package evidence, not results of this integration.

## Overlapping files

- Sprint 12: `apps/frontend/.gitignore` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/.env.example` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/README.md` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/tsconfig.app.json` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/tsconfig.node.json` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/eslint.config.js` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/Dockerfile` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/index.html` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/package.json` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/vite.config.ts` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/src/index.css` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/src/main.tsx` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 12: `apps/frontend/src/lib/api-client.ts` â€” Sprint 18 retains Sprint 16 stable idempotency retries and Sprint 13 downloads; adopts HttpOnly refresh.
- Sprint 12: `.github/workflows/frontend-ci.yml` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 13: `apps/frontend/src/lib/api-client.ts` â€” Sprint 18 retains Sprint 16 stable idempotency retries and Sprint 13 downloads; adopts HttpOnly refresh.
- Sprint 13: `apps/frontend/src/app/AppRouter.tsx` â€” Sprint 18 retains all Student/Teacher/Admin routes from Sprint 15 and adds recovery routes.
- Sprint 13: `services/assessment-service/app/api/v1/router.py` â€” Sprint 14 includes both Sprint 13 student_read and teacher_read routers.
- Sprint 14: `apps/frontend/src/app/AppRouter.tsx` â€” Sprint 18 retains all Student/Teacher/Admin routes from Sprint 15 and adds recovery routes.
- Sprint 14: `apps/frontend/src/components/layout/navigation.ts` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 14: `apps/frontend/src/pages/student/StudentAssessmentAttemptPage.tsx` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 14: `services/notification-service/app/clients/academic.py` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 14: `services/notification-service/app/api/v1/router.py` â€” Sprint 14 retains prior routes and adds teacher announcements.
- Sprint 14: `services/assessment-service/app/api/v1/router.py` â€” Sprint 14 includes both Sprint 13 student_read and teacher_read routers.
- Sprint 14: `services/assessment-service/app/api/v1/endpoints/grading.py` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 14: `services/assessment-service/app/api/v1/endpoints/authoring.py` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 15: `apps/frontend/src/app/AppRouter.tsx` â€” Sprint 18 retains all Student/Teacher/Admin routes from Sprint 15 and adds recovery routes.
- Sprint 15: `apps/frontend/src/components/layout/navigation.ts` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 16: `infra/gateway/nginx.conf` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 16: `infra/gateway/templates/default.conf.template` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 16: `infra/gateway/snippets/proxy_common.conf` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 16: `apps/frontend/src/lib/api-client.ts` â€” Sprint 18 retains Sprint 16 stable idempotency retries and Sprint 13 downloads; adopts HttpOnly refresh.
- Sprint 18: `docker-compose.infrastructure.yml` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `.env.infrastructure.example` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `docker-compose.gateway.yml` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `docker-compose.frontend.yml` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `infra/gateway/templates/default.conf.template` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/Dockerfile` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/docker/nginx.conf` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/src/lib/token-store.ts` â€” Remove browser refresh-token persistence; keep access tokens in memory.
- Sprint 18: `apps/frontend/src/lib/token-store.test.ts` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/src/lib/api-client.ts` â€” Sprint 18 retains Sprint 16 stable idempotency retries and Sprint 13 downloads; adopts HttpOnly refresh.
- Sprint 18: `apps/frontend/src/pages/RegisterPage.tsx` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/src/pages/LoginPage.tsx` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/src/app/AppRouter.tsx` â€” Sprint 18 retains all Student/Teacher/Admin routes from Sprint 15 and adds recovery routes.
- Sprint 18: `apps/frontend/src/features/auth/AuthContext.tsx` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 18: `apps/frontend/src/features/auth/auth-api.ts` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.
- Sprint 27: `scripts/verify-production-bundle.py` â€” Chronological extension retained with before/after diff; regressions verified in local suites; external operational execution remains environment dependent.

Legacy `apps/backend` scaffold retained for recovery, excluded from the active distributed runtime. Ten service databases remain separately owned.

Complete per-file provenance: `.integration/merge-manifest.json`. Consolidation diff: `.integration/merge-diffs.patch`.
