# Destiny — Internal Preview Deployment Decision

> Decision date: 2026-09-16  
> Status: approved for an internal, non-public preview only. This is not a
> production hosting decision.

## Decision

Use **Render** for the first internal preview:

1. one static site for the Vite web client;
2. one FastAPI web service for the calculation API;
3. no database, account system, analytics identifier, or stored birth input in
   this phase.

The client receives the API URL through `VITE_API_BASE`. The API deployment
sets `DESTINY_ALLOWED_ORIGINS` to that static site's exact HTTPS origin. No
wildcard origin is permitted.

## Why this is the initial recommendation

- Render explicitly supports Python web services and static sites, so the
  existing Vite client and FastAPI API can be deployed without adding a second
  host or a serverless adaptation.
- A single provider keeps the first preview's environment variables, service
  logs, TLS, and rollback workflow simple.
- The current API is stateless; it does not need a database or persistent disk
  for the calculator preview.

## Boundary and user experience

Render's free web services are suitable for testing and preview, not a
production application. They spin down after 15 minutes without inbound
traffic and can take about a minute to start on the next request. The preview
UI must therefore show a neutral loading state and never imply the calculator
failed while the API is waking up.

The preview must remain unlisted or access-limited until the public release
checklist is approved. Do not collect birth data in analytics, feedback forms,
or logs beyond the minimum transient request handling required for calculation.

## Before public launch

1. Move the API to an appropriate paid compute plan so idle spin-down is not a
   user-facing behavior.
2. Select and connect the final custom domain; then replace the preview origin
   in `DESTINY_ALLOWED_ORIGINS` with its exact HTTPS origin.
3. Add a privacy notice, retention policy, and a consent-aware feedback CTA
   before accepting any user-provided birth information outside a calculation
   request.
4. Run a browser end-to-end review against the deployed frontend and API,
   including known-time, date-only, and solar-term-boundary paths.

## Sources checked

- [Render: Deploy for Free](https://render.com/docs/free) — Python web-service
  support, free-instance limits, and idle spin-down behavior.
- [Render: Services and Service Types](https://render.com/docs/service-types)
  — web-service and static-site suitability.
- [Render: Pricing](https://render.com/pricing) — current paid-compute
  transition path.

## Alternatives not selected now

- Vercel is strong for a static Vite client, but its Hobby plan is restricted
  to non-commercial personal use. It is therefore not the default recommendation
  for a future commercial Destiny service.
- Railway supports FastAPI deployment, but using it would still require a
  separate static-client decision or a different combined deployment shape.
