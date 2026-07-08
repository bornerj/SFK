# Integrations — External Interfaces (single fixed location)

This folder is the **single home for every external interface** the project talks to:
WhatsApp, Stripe, PayPal, SendGrid, internal/partner APIs, OAuth providers, etc.

## How it works (two parts)

1. **Index — `sfk.toml -> [[integrations]]`**
   One block per service, machine-readable. Names/identifiers only, never secrets.

2. **Runbook — `docs/integrations/<service>.md`**
   One human file per service: auth model, endpoints, webhooks, sandbox vs prod,
   env var **names**, and gotchas. See `_EXAMPLE-service.md` for the shape.

## Rules

- One file per service, named after the service (`stripe.md`, `whatsapp-zapi.md`).
- **Never store secret values** — only variable names. Values live in `.env`
  (git-ignored) or the platform's secret manager.
- When adding/removing a service, update **both** the `sfk.toml` index and this folder.
- Provider swaps (e.g. Stripe → PayPal) are recorded as a `DECISION-XXX`.
