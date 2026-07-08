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
updated      = "2026-07-08"
active_plan  = "PLAN-0002 DONE — SFK Launcher GUI complete, committed to main"
phase        = "Shipped: SFK Launcher (bin/sfk_gui.py), F1-F6"
status       = "idle"                 # in-progress | paused | blocked | idle
branch       = "main"
blockers     = []
next_action  = "Push main to origin (pending authorization). Optional: migrate the real VetSystem project via the GUI's Update panel."
```

**Where am I:** PLAN-0002 (SFK Launcher, a zero-install Tkinter GUI over the
scaffolder/updater/skill-importer) is fully shipped — all 6 phases committed to
`main` (not yet pushed). Covers: New Project, Add/Update (with legacy migration,
tested against the real VetSystem project's shape), Skills (import + list),
Check-project preview, procedural icon, double-click launchers (`.sh`/`.bat`),
friendly missing-Tkinter handling. `USAGE.md` and `README.md` updated with a
GUI entry point. PLAN-0001 (engine/project separation, v1.3.0, shipped and
pushed earlier) remains underneath it. Nothing blocked.

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

- 2026-07-08: PLAN-0002 F1–F6 — SFK Launcher GUI (`bin/sfk_gui.py`) shipped: New Project, Add/Update with legacy migration, Skills, Check-project, icon, double-click launchers (DONE)
- 2026-07-07: PLAN-0001 F0–F5 + release — engine/project separation, SFK v1.3.0 shipped and pushed (DONE)
- 2026-04-06: Core SFK consolidated (`sfk.toml` expanded, `docs/config` cleaned up, audit assets relocated) (DONE)
- 2026-04-20: SFK memory and templates converted into versioned reusable examples (point-in-time)

<!-- Example filled in:
- 2026-03-25: Implemented CSV export in Dashboard (PLAN-0012 DONE)
- 2026-03-20: JWT authentication with refresh token completed (PLAN-0010 DONE)
-->
