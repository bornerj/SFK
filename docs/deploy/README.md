# Deploy — Runbook & Environments

Human-facing deploy runbook. The **structured source of truth** for hosting and
environments is `sfk.toml` (`[hosting.*]` and `[environments.*]`); this folder holds
the step-by-step "how".

## What goes here
- `<provider>.md` — one runbook per hosting target (e.g. `vercel.md`, `railway.md`),
  with build settings, deploy steps, rollbacks, and the env var **names** each needs.
- Migration/cutover notes when moving providers.

## Rules
- **Names, not values.** Never store secrets, tokens, keys or connection strings here.
- Env var *names* are declared in `sfk.toml -> [environments.*]`; this folder explains
  how to set them on each platform.
- A provider change (e.g. Railway → Fly.io) is recorded as a `DECISION-XXX` so the
  timeline of hosting moves stays traceable.
