# Progress — Resume Panel & Module State

> **Read this file FIRST when returning to the project.** The Resume Panel below
> answers "where did I stop and what is next" in a few tokens, so you don't have
> to re-investigate the repo. Complements `memory/MODIFICATION_LOG.md` (full
> chronological history).

---

## Resume Panel

<!-- The AI MUST update this block at the end of every working session. -->
<!-- Keep it small: names and short phrases only, never long prose. -->

```toml
updated      = "2026-07-07"
active_plan  = "PLAN-0001"
phase        = "Phase 4 done (Layer-1 dedup + Operating Card + pre-commit hook) — ready to commit"
status       = "in-progress"          # in-progress | paused | blocked | idle
branch       = "refactor/engine-project-separation"
blockers     = []                     # e.g. ["waiting DECISION-004"]
next_action  = "Commit Phase 4, then Phase 5: rework sfk_updater.py to migrate legacy kernel/ projects"
```

**Where am I:** Executing the engine/project separation refactor (PLAN-0001).
Phases 0–3 committed. Phase 4 complete (D4 enforcement): `OPERATING_CARD.md` always-loaded
digest, `.sfk/kernel/hooks/pre-commit` blocks significant commits missing a memory record,
Layer-1 dedup (NEW/EXISTING classification single-sourced to BOOTSTRAP Step 0; doc-heading
rules single-sourced to RULES §11; SOUL trimmed to persona). Next: commit Phase 4, then
Phase 5 (updater). Nothing blocked.

---

## Modules

<!-- Available states: stable | in-progress | blocked | planned | deprecated -->
<!-- Format: | Module | State | Updated | Notes | -->

| Module              | State       | Updated    | Notes                                                        |
|---------------------|-------------|------------|--------------------------------------------------------------|
| Architecture (SFK)  | in-progress | 2026-07-07 | Engine isolated in `.sfk/`; config promoted to root (PLAN-0001) |
| Audit Protocol      | stable      | 2026-04-06 | Moved into `memory/logs/` with routing support               |
| Template Memory     | stable      | 2026-04-20 | PR, plan, and decision files converted into reusable examples |
| Publication Flow    | stable      | 2026-04-20 | Kernel requires PR descriptions and versions framework templates |

<!-- Example filled in:
| Authentication      | stable      | 2026-03-20 | JWT + refresh token implemented               |
| Billing (Stripe)    | in-progress | 2026-03-25 | Webhook and portal working; retry pending     |
| Push Notifications  | blocked     | 2026-03-18 | Blocked by infra decision (DECISION-004)      |
-->

---

## Technical Debt

<!-- Severity: critical | medium | low -->

| Area | Debt | Severity |
|------|------|----------|
|      |      |          |

<!-- Example filled in:
| Auth     | Refresh token without rotation — replay-vulnerable | critical |
| Database | Missing index on `orders.user_id`                  | medium   |
-->

---

## Recent Activity

<!-- Log of completed tasks. Summarize entries older than 30 days. -->
<!-- Format: - YYYY-MM-DD: [what was done] (PLAN-XXXX or point-in-time) -->

- 2026-07-07: PLAN-0001 Phases 0–2 — engine isolated into `.sfk/`, tooling into `bin/` (in-progress)
- 2026-04-06: Core SFK consolidated (`sfk.toml` expanded, `docs/config` cleaned up, audit assets relocated) (DONE)
- 2026-04-20: SFK memory and templates converted into versioned reusable examples (point-in-time)

<!-- Example filled in:
- 2026-03-25: Implemented CSV export in Dashboard (PLAN-0012 DONE)
- 2026-03-20: JWT authentication with refresh token completed (PLAN-0010 DONE)
-->
