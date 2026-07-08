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
updated      = ""                     # YYYY-MM-DD of last session
active_plan  = ""                     # e.g. "PLAN-0003" or "" if none
phase        = ""                     # short phrase for the current step
status       = "idle"                 # in-progress | paused | blocked | idle
branch       = ""                     # working branch
blockers     = []                     # e.g. ["waiting DECISION-004"]
next_action  = ""                     # the very next concrete step
```

**Where am I:** <one or two lines of plain-language context for a returning human>

---

## Modules

<!-- Available states: stable | in-progress | blocked | planned | deprecated -->
<!-- Format: | Module | State | Updated | Notes | -->

| Module | State | Updated | Notes |
|--------|-------|---------|-------|

---

## Technical Debt

<!-- Severity: critical | medium | low -->

| Area | Debt | Severity |
|------|------|----------|

---

## Recent Activity

<!-- Log of completed tasks. Summarize entries older than 30 days. -->
<!-- Format: - YYYY-MM-DD: [what was done] (PLAN-XXXX or point-in-time) -->
