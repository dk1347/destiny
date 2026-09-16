# Destiny — Render Internal Preview Runbook

> Scope: an internal, unlisted preview. Do not use this runbook for a public
> release until the conditions in `29_INTERNAL_PREVIEW_DEPLOYMENT_DECISION.md`
> are complete.

## Preconditions

- The GitHub repository branch to deploy is `fix/v3-data-integrity`.
- Keep the preview URL only with trusted testers. No account, database, or
  feedback form is part of this deployment.
- The `GET /healthz` endpoint must return HTTP 200 before testing the client.

## 1. Create the API web service

In Render, create a **Web Service** from the GitHub repository with these
values:

| Setting | Value |
| --- | --- |
| Branch | `fix/v3-data-integrity` |
| Runtime | Python |
| Root directory | repository root (leave blank) |
| Build command | `pip install ".[api]"` |
| Start command | `uvicorn destiny_saju.api:app --host 0.0.0.0 --port $PORT` |
| Health check path | `/healthz` |
| Compute plan | Free, for internal preview only |
| Auto-deploy | Off until the first browser review passes |

Do **not** add a wildcard CORS origin. At creation time, either leave
`DESTINY_ALLOWED_ORIGINS` absent (the API remains local-origin-only) or set it
only after the static site's exact HTTPS URL is known.

After the first deploy, open `<API URL>/healthz`. It must return:

```json
{"status":"ok","service":"destiny-saju"}
```

## 2. Create the static web client

Create a **Static Site** from the same repository:

| Setting | Value |
| --- | --- |
| Branch | `fix/v3-data-integrity` |
| Root directory | `web` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |
| Auto-deploy | Off until the first browser review passes |

Render gives the static site an HTTPS `onrender.com` URL. Copy that exact
origin (scheme plus hostname, without a trailing slash).

## 3. Bind the two services explicitly

In the API service, set:

```text
DESTINY_ALLOWED_ORIGINS=<exact static-site HTTPS origin>
```

Redeploy the API. In the static site's build environment, set:

```text
VITE_API_BASE=<exact API HTTPS URL>
```

Redeploy the static site. `VITE_API_BASE` is bundled into browser JavaScript,
so changing it requires a new static build. Neither variable is a secret, but
they must still be entered exactly: no wildcard origin and no extra path in
`DESTINY_ALLOWED_ORIGINS`.

## 4. Internal browser acceptance check

From the static-site URL, verify all of the following:

1. Known date and time produces four pillars.
2. Date-only input produces three pillars and an unknown-time notice.
3. A date-only solar-term boundary asks for birth time; it does not guess.
4. Switching “알아요/몰라요” removes any previous result before recalculation.
5. The annual-cycle card appears only after known-time calculation.
6. Browser network traffic uses only the configured API HTTPS URL; no CORS
   error appears.
7. A cold API start shows the existing loading state rather than an invented
   calculation error.

If any check fails, keep the preview unshared, capture the non-sensitive error
code, and fix it on the branch before enabling automatic deployments.

## Sources checked

- [Render first deployment guide](https://render.com/docs/your-first-deploy)
- [Render health checks](https://render.com/docs/health-checks)
- [Render monorepo support](https://render.com/docs/monorepo-support)
- [Render static sites](https://render.com/docs/static-sites)
