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
updated      = "2026-07-13"
active_plan  = "PLAN-0004 DONE (uncommitted); PLAN-0003 DONE (uncommitted)"
phase        = "Bug fix implemented & validated: 'Adicionar SFK a projeto existente' now works on real no-SFK projects"
status       = "in-progress"          # in-progress | paused | blocked | idle
branch       = "main"
blockers     = []
next_action  = "Present consolidated pre-commit review for PLAN-0003 + PLAN-0004, get commit authorization (then a separate push authorization)."
```

**Where am I:** Bug reported via SFK Launcher GUI: "Adicionar SFK a projeto existente"
errored with "not an SFK project" on a genuinely SFK-less project — root cause was
`sfk_updater.py` never implementing a real path for layout `none` (only `current`/
`legacy`). Two plans, both implemented and validated (not yet committed):
`PLAN-0004` (collateral finding, confirmed by the user — the new-project scaffolder
was leaking this repo's own real `PLAN-0001/0002/0003`/`PR-0001-DESCRIPTION.md` into
scaffolded projects; fixed via `jb_kit_turbo.is_own_delivery_history()`) and
`PLAN-0003` (the reported bug — updater bootstrap install for layout `none`,
strictly additive; depends on `PLAN-0004`'s filter + two extracted blank-template
generators). Both regression-tested (CURRENT/LEGACY unaffected) and validated
against the user's actual reported project path via dry-run. See
`memory/logs/DEBUG-HISTORY.md` ERR-0001/ERR-0002 for full detail. PLAN-0001/PLAN-0002
(engine separation + SFK Launcher GUI) remain shipped underneath, `main` still
pending push authorization from before.

---

## Modules

<!-- Available states: stable | in-progress | blocked | planned | deprecated -->
<!-- Format: | Module | State | Updated | Notes | -->

| Module              | State       | Updated    | Notes                                                        |
|---------------------|-------------|------------|--------------------------------------------------------------|
| Architecture (SFK)  | stable      | 2026-07-07 | Engine isolated in `.sfk/`; config promoted to root (PLAN-0001, v1.3.0) |
| SFK Launcher (GUI)  | stable      | 2026-07-08 | `bin/sfk_gui.py` — zero-install Tkinter app over scaffolder/updater/skill-importer (PLAN-0002) |
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

- 2026-07-13: PLAN-0003 F1–F5 — `sfk_updater.py` bootstrap install for layout `none` (ERR-0002); fixes "Adicionar SFK a projeto existente" on real no-SFK projects (implemented & validated, uncommitted)
- 2026-07-13: PLAN-0004 F1–F4 — scaffolder (`jb_kit_turbo.py`) stops copying this repo's real PLAN/PR files into new projects (ERR-0001) (implemented & validated, uncommitted)
- 2026-07-08: PLAN-0002 F1–F6 — SFK Launcher GUI (`bin/sfk_gui.py`) shipped: New Project, Add/Update with legacy migration, Skills, Check-project, icon, double-click launchers (DONE)
- 2026-07-07: PLAN-0001 F0–F5 + release — engine/project separation, SFK v1.3.0 shipped and pushed (DONE)
- 2026-04-06: Core SFK consolidated (`sfk.toml` expanded, `docs/config` cleaned up, audit assets relocated) (DONE)
- 2026-04-20: SFK memory and templates converted into versioned reusable examples (point-in-time)

<!-- Example filled in:
- 2026-03-25: Implemented CSV export in Dashboard (PLAN-0012 DONE)
- 2026-03-20: JWT authentication with refresh token completed (PLAN-0010 DONE)
-->
