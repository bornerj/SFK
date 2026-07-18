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
updated      = "2026-07-17"
active_plan  = "PLAN-0005 DONE — implemented and validated, uncommitted"
phase        = "idle — SFK Launcher GUI: compact layout + PT/EN language switch shipped"
status       = "idle"                 # in-progress | paused | blocked | idle
branch       = "main"
blockers     = []
next_action  = "None pending. Awaiting user's commit approval for PLAN-0005 (bin/sfk_gui.py, bin/lib/gui_i18n.py, memory/*)."
```

**Where am I:** User reported the SFK Launcher GUI (`bin/sfk_gui.py`) window was too
big — the last Home card ("Checar um projeto") was cut off, requiring a manual resize
— and asked for a PT/EN language toggle, top-right, visible on every screen, with
smaller fonts overall. Delivered as `PLAN-0005`: new `bin/lib/gui_i18n.py` (PT/EN
string dict + `Lang` singleton, preference persisted to
`~/.sfk_launcher_lang`); `Theme`/`Fonts`/`ActionCard` shrunk and `App.geometry`
recalculated (760x580, was 880x620) so all 5 Home cards fit without resizing;
`LangSwitch` widget added top-right on the root window; every static-text widget
across `Header`, `PathPicker`, `ResultBanner` and all 6 views now retranslates
in-place on language switch (no rebuild, no loss of typed input). Validated with a
live `DISPLAY`: card-fit geometry check, language-switch + persistence round-trip,
and a full real dry-run flow through `sfk_updater.py` — all passed. Nothing blocked.
Previous session's bug-fix work (`PLAN-0002/0003/0004`) is already committed and
pushed to `origin/main`; this plan's changes are implemented and validated but not
yet committed — awaiting the user's explicit commit authorization.

---

## Modules

<!-- Available states: stable | in-progress | blocked | planned | deprecated -->
<!-- Format: | Module | State | Updated | Notes | -->

| Module              | State       | Updated    | Notes                                                        |
|---------------------|-------------|------------|--------------------------------------------------------------|
| Architecture (SFK)  | stable      | 2026-07-07 | Engine isolated in `.sfk/`; config promoted to root (PLAN-0001, v1.3.0) |
| SFK Launcher (GUI)  | stable      | 2026-07-17 | `bin/sfk_gui.py` — zero-install Tkinter app; compact layout + PT/EN language switch (`bin/lib/gui_i18n.py`, PLAN-0005) |
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

- 2026-07-17: PLAN-0005 — SFK Launcher GUI compact layout + PT/EN language switch (`bin/lib/gui_i18n.py` new, `bin/sfk_gui.py` retranslation wiring) (implemented & validated, uncommitted)
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
