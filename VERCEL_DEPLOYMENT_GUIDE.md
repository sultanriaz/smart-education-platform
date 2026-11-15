# SmartEdu Platform — Vercel Deployment Guide

This guide explains how to deploy the **SmartEdu Web Application** to [Vercel](https://vercel.com).

---

## 1. Quick Overview

The repository is pre-configured with:
- Root [`vercel.json`](file:///c:/black_paper/Projects/smart-education-platform/vercel.json) and [`package.json`](file:///c:/black_paper/Projects/smart-education-platform/package.json) for 1-click root deployment.
- Subfolder [`apps/frontend/vercel.json`](file:///c:/black_paper/Projects/smart-education-platform/apps/frontend/vercel.json) in case you set the root directory to `apps/frontend`.
- Dynamic API Base URL resolution in [`apps/frontend/src/lib/runtime-config.ts`](file:///c:/black_paper/Projects/smart-education-platform/apps/frontend/src/lib/runtime-config.ts) supporting cloud environments and `VITE_API_BASE_URL`.
- Complete SPA route rewrites (`/(.*) -> /index.html`) so refreshing routes like `/app/admin`, `/app/teacher`, and `/app/student` never returns 404.

---

## 2. Option A: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub / GitLab / Bitbucket**.
2. Go to [https://vercel.com/new](https://vercel.com/new).
3. Import your `smart-education-platform` repository.
4. Vercel will automatically detect the configuration from `vercel.json`:
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm --prefix apps/frontend run build`
   - **Output Directory**: `apps/frontend/dist`
   - **Install Command**: `npm --prefix apps/frontend install`
5. *(Optional)* Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: The URL of your live API Gateway or backend (e.g. `https://api.yourdomain.com`).
   - If left empty, it will default to same-origin relative URLs (`/api/v1/...`).
6. Click **Deploy**.

---

## 3. Option B: Deploy via Vercel CLI

You can deploy directly from your local terminal using `npx vercel`:

### Step 1: Login to Vercel
```bash
npx vercel login
```

### Step 2: Deploy to Preview
```bash
npx vercel
```
Follow the interactive prompts (accept the defaults detected from `vercel.json`).

### Step 3: Deploy to Production
```bash
npx vercel --prod
```

---

## 4. Connecting to Your Live Backend API

When deploying to Vercel, the frontend connects to your API Gateway.

### Setting the Backend URL:
In the Vercel Project Settings under **Environment Variables**:
| Variable Name | Example Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://api.smartedu.edu.pk` | Full HTTPS URL of your deployed API Gateway / backend |

> **Note on CORS:** Ensure your production backend allows your Vercel deployment domain (e.g. `https://your-project.vercel.app`) in its `CORS_ORIGINS` setting.

---

## 5. Verification Checklist After Deployment

- [ ] Visit your Vercel URL (e.g. `https://your-app.vercel.app`).
- [ ] Direct page refresh on `/login` or `/app/admin` loads correctly (proves SPA rewrites work).
- [ ] Log in with the demo administrator credentials.
- [ ] Static assets (`/assets/*`) are cached with long TTL immutable headers.
- [ ] Check developer console to ensure no Mixed Content (HTTP vs HTTPS) warnings appear.
