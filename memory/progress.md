# Progress — Current Module State

> Current state of the project. Updated after each completed task.
> Complements `memory/MODIFICATION_LOG.md` (chronological history).
> This file answers the question: **"What is ready right now?"**

---

## Modules

<!-- Available states: stable | in-progress | blocked | planned | deprecated -->
<!-- Update this file whenever a PLAN-XXXX is marked as DONE -->

| Architecture (SFK) | stable | 2026-04-06 | Technical dictionary expanded and docs/config cleaned up |
| Audit Protocol     | stable | 2026-04-06 | Moved into `memory/logs/` with routing support |
| Template Memory    | stable | 2026-04-20 | PR, plan, and decision files converted into reusable examples |
| Publication Flow   | stable | 2026-04-20 | Kernel now requires PR descriptions and versions framework templates |

<!-- Example filled in:
| Module              | State       | Updated    | Notes                                         |
|---------------------|-------------|------------|-----------------------------------------------|
| Authentication      | stable      | 2026-03-20 | JWT + refresh token implemented               |
| Dashboard           | stable      | 2026-03-22 | Filters, pagination, and CSV export           |
| Billing (Stripe)    | in-progress | 2026-03-25 | Webhook and portal working; retry pending     |
| PDF Reports         | planned     | —          | Waiting for approved design                   |
| Push Notifications  | blocked     | 2026-03-18 | Blocked by infra decision (DECISION-004)      |
| API v1 (legacy)     | deprecated  | 2026-02-28 | Replaced by v2 in March                       |
-->

---

## Technical Debt

<!-- Severity: critical | medium | low -->

| Area | Debt | Severity |
|------|------|----------|
|      |      |          |

<!-- Example filled in:
| Area          | Debt                                             | Severity |
|---------------|--------------------------------------------------|----------|
| Auth          | Refresh token without rotation — replay-vulnerable | critical |
| Database      | Missing index on `orders.user_id`               | medium   |
| Frontend      | 12 components without explicit TypeScript types  | low      |
| Tests         | Billing services without error coverage          | medium   |
-->

---

## Recent Activity

<!-- Log of completed tasks. Summarize entries older than 30 days. -->
<!-- Format: - YYYY-MM-DD: [what was done] (PLAN-XXXX or point-in-time) -->

- 2026-04-06: Core SFK consolidated (`project.toml` expanded, `docs/config` cleaned up, audit assets relocated) (DONE)
- 2026-04-20: SFK memory and templates converted into versioned reusable examples (point-in-time)
- 2026-04-20: Publication rules updated with `memory/PR-XXXX-DESCRIPTION.md` and template versioning (point-in-time)

<!-- Example filled in:
- 2026-03-25: Implemented CSV export in Dashboard (PLAN-0012 DONE)
- 2026-03-22: Fixed pagination bug in the contract listing (point-in-time, ERR-0008)
- 2026-03-20: JWT authentication with refresh token completed (PLAN-0010 DONE)
- 2026-03-14: Initial project setup — base stack and infrastructure (PLAN-0001 DONE)
-->
