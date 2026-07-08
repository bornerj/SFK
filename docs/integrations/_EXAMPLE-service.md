# <Service Name> (e.g. Stripe Checkout)

> Runbook template. Copy to `docs/integrations/<service>.md` and fill in.
> Values are NEVER stored here — only names. Secrets live in `.env` / secret manager.

## Overview
- Purpose: <what this service does for the product>
- Mode: sandbox | production (how to tell them apart)
- Owner / account: <team or account name, not credentials>

## Auth model
- Auth type: API key | OAuth2 | HMAC signature | ...
- Environment variable **names** (values in `.env`):
  - `SERVICE_ENABLED`
  - `SERVICE_API_KEY`
  - `SERVICE_WEBHOOK_SECRET`

## Endpoints (our side)
- `POST /api/.../checkout-session`
- `POST /api/.../webhook`

## Webhooks
- Inbound events handled: <list>
- Signature validation: <how>
- Idempotency: <how duplicates are handled>

## Gotchas
- <rate limits, retry behavior, sandbox quirks, known failures>

## Related
- Deploy env: `docs/deploy/`
- Decision (if provider was chosen/changed): `memory/decisions/DECISION-XXX.md`
