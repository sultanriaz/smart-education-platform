# Browser E2E

Install once:

```powershell
cd .\tests\e2e
npm install
npx playwright install chromium
```

Configure:

```text
SMARTEDU_FRONTEND_URL=http://localhost:3000

SMARTEDU_E2E_STUDENT_EMAIL=...
SMARTEDU_E2E_STUDENT_PASSWORD=...

SMARTEDU_E2E_TEACHER_EMAIL=...
SMARTEDU_E2E_TEACHER_PASSWORD=...

SMARTEDU_E2E_ADMIN_EMAIL=...
SMARTEDU_E2E_ADMIN_PASSWORD=...
```

Run:

```powershell
npm test
```

The three accounts must be dedicated QA accounts, not real production users.

The package intentionally keeps credentials outside source control.
