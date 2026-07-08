# Modification Log

This log tracks relevant changes in the SFK framework and also serves as a reference example for how to record change history in projects that adopt this structure.

---

**Examples of how to record entries in the LOG**
## 2026-03-08 22:45 (Approx)
- Plan PLAN-0005: START AND END.
- Added Mass Creation screen (`MassCreator.tsx`).
- Added new navigation button to the Sidebar.
- Updated routing in `App.tsx` for correct display with pinned Header bar.
- Refactored `/api/upload` endpoint in `server.py` to use MD5 hash of file content, deduplicating identical uploads.

##
- Plan PLAN-0001 completed and consolidated in the first commit (git init).

## 2026-03-06 21:00 (Approx)
- Plan PLAN-0002: START AND END of the application.
- Recorded DECISION-001.md in /memory/decisions approving SQLite persistence and Latte palette.
- Backend: `is_favorite` column inserted in local database via Python script, `server.py` updated (`PromptModel` and `sqlite3` queries).
- Frontend: `is_favorite` coupled to the typed `Prompt` interface. Implemented `toggleFavorite` function interacting with the API via LocalState Update.
- Visual: Removed cool tones (slate) and inserted custom Latte palette in `tailwind.config.js` (foam/crema/roast/etc). Applied conversion across app classes.
- Consolidated final Git commit detailing architectural and visual changes.
- `PLAN-0002-FAVORITOS-THEME-LATTE.md` moved to DONE state.

**End Examples**

---



## Modification Log Start
## 2026-04-06 03:15 (Approx)
- SFK architectural consolidation:
  - `kernel/project.toml`: promoted to a full technical dictionary (hosting, stack layers, design, env vars by platform, integrations).
  - `docs/config/` cleanup: removed INTEGRATIONS, DEPLOY_ENV, and MODULES_CATALOG; moved BUILD_NOTES to `memory/logs/BUILD-HISTORY.md`.
  - Protocol relocation: moved AUDIT_CHECKLIST, DRIFT_RULES, and AUDITOR_MODE into `memory/logs/` and merged them.
  - Routing update: `kernel/index.toml` now includes an `[on_audit]` section for selective protocol loading.
  - Template reset: `PROJECT_OVERVIEW.md` and `REQUIREMENTS.md` reset to template placeholders.
  - General sync: README.md, INSTRUCTIONS.md, and WORKFLOW_MEMORY_PLAYBOOK.md aligned with the new structure.

## 2026-04-14 00:00 (Approx)
- Bootstrap and documentation rules reinforced to distinguish a new project from an existing project.
- `kernel/BOOTSTRAP.md`, `kernel/RULES.md` and `kernel/index.toml` updated to:
  - classify the repository as NEW PROJECT when there are no plans, no decisions, and no real history in `MODIFICATION_LOG`;
  - ignore `kernel/project.toml` and `kernel/SYSTEM.md` as validation sources when the project is new;
  - require `docs/project/PROJECT_OVERVIEW.md` and `docs/project/REQUIREMENTS.md` to match the structure from `../Rifa`.
- `docs/project/PROJECT_OVERVIEW.md` and `docs/project/REQUIREMENTS.md` reformatted to mirror the `Rifa` sections, including `FR-XXX`, `NFR-XXX`, and `AC-XXX` identifiers.
- `docs/project/SCOPE.md` and `docs/project/SETUP.md` created with the same `##` section structure used in `../Rifa/docs/project/`.
- `docs/project/SCOPE.md` and `docs/project/SETUP.md` converted to English to keep consistency with SFK's own files.
- Explicit rule added: SFK kernel/template files stay in English; project-generated documents may follow the language declared in `kernel/project.toml`.

## 2026-06-09
- SFK v1.2.0 — Blueprint separation and new project onboarding:
  - `_blueprint/` created: clean templates that override SFK's own data during scaffold (SYSTEM.md, progress.md, BUILD-HISTORY.md, DRIFT-RULES.md, EVOLUTION_MEMORY.md).
  - `tools/jb_kit_turbo.py`: added `apply_blueprint_overrides()` + `write_quickstart()` to scaffold pipeline.
  - `kernel/BOOTSTRAP.md`: added Step 0a — NEW PROJECT Day 1 Onboarding Protocol.
  - `CHANGELOG.md`: v1.2.0 entry added.

## 2026-04-20 00:00 (Approx)
- SFK example memory refined for framework use:
  - `memory/PR-0001-DESCRIPTION.md` replaced by `memory/PR-XXXX-DESCRIPTION.md` as a reusable template.
  - `memory/plans/PLAN-0001-DONE-rifa-web-platform.md` replaced by `memory/plans/PLAN-XXXX-DONE-subject.md` as a generic completed-plan example.
  - concrete files in `memory/decisions/` replaced by `memory/decisions/DECISION-XXX.md` as the decision template.
  - old examples tied to a specific project removed to avoid confusion between real history and framework templates.
- `memory/MODIFICATION_LOG.md` kept as SFK's real log while also serving as a format reference for projects that adopt this structure.
- Publication and versioning rules adjusted for the framework itself:
  - `.gitignore` updated to allow versioning templates and examples in `memory/` and `docs/project/`.
  - `kernel/BOOTSTRAP.md` reinforced to consider `memory/PR-XXXX-DESCRIPTION.md` during release, publish, deploy, and final review sessions.
  - `kernel/RULES.md` expanded with the PR description kernel for publishable deliveries, including mandatory use, minimum content, and closure rules.
  - `kernel/SOUL.md` updated to keep the PR description aligned with the real diff, the final commit, and the project's default language.
  - `kernel/index.toml` synchronized with the project classification rules, mandatory documentation, and template governance.

## 2026-07-07 — PLAN-0001 Phase 0 (no-risk fixes)
- Started structural refactor `PLAN-0001` (engine/project/tooling separation) on branch `refactor/engine-project-separation`. Restore points created: physical tarball `SFK-backup-20260707-203040.tar.gz` + git tag `sfk-pre-refactor-20260707-203040` (`main` untouched).
- `kernel/RULES.md`: added Fundamental Principle #10 — **File Boundary Law** (Engine / Project state / Maintainer tooling categories; engine is read-only; never mix categories).
- `kernel/RULES.md §12.3`: fixed broken reference `kernel/AUDIT_CHECKLIST.md` → `memory/logs/SESSION-AUDIT-CHECKLIST.md`.
- Pending (next phases): F1 move `kernel/`→`.sfk/kernel/` + path rewrite; F2 tooling→`bin/`; F3 config/memory (sfk.toml, progress.md board, integrations, db migrations, deploy/env); F4 Layer-1 dedup + operating card + pre-commit hook; F5 migrate existing projects via updater.

## 2026-07-07 — PLAN-0001 Phase 1 (engine moved to .sfk/)
- `kernel/` → `.sfk/kernel/` via `git mv` (244 files). Root no longer has loose engine files.
- Path rewrite `kernel/` → `.sfk/kernel/` across engine files + root pointers (`CLAUDE.md`, `.clauderules`, `.windsurfrules`, `INSTRUCTIONS.md`, `README.md`, `CONTRIBUTING.md`) + `memory/WORKFLOW_MEMORY_PLAYBOOK.md`. History/tooling/blueprint/cursor left untouched.
- Added `.sfk/VERSION` (1.3.0-dev, provisional) and `.sfk/MANIFEST` (engine ownership map for the updater).
- Added `.gitattributes`: `/.sfk/** linguist-vendored`. Added `.claude/` to `.gitignore`.
- Validated: `.sfk/kernel/BOOTSTRAP.md` exists, root `kernel/` gone, IDE pointers updated, no stray active `kernel/` refs, no `.sfk/.sfk/` duplication.
- Deferred: `project.toml`/`SYSTEM.md` still under `.sfk/kernel/` (move to root as `sfk.toml`/`SYSTEM.md` in F3); tooling path logic (`tools/`, `import_skill.py` parents[]) in F2.

## 2026-07-07 — PLAN-0001 pushed to origin (SHIPPED)
- Push authorized by the user. `git push origin main` → `875735a..9236fce`. `main` and `origin/main` are in sync. SFK v1.3.0 is published. PLAN-0001 fully closed.

## 2026-07-07 — PLAN-0001 merged to main + usage documentation
- Merged `refactor/engine-project-separation` → `main` (`--no-ff`, merge commit `5dd6b66`). Local only — **not pushed** (awaiting push authorization). `main` is 9 commits ahead of `origin/main`.
- Added `USAGE.md` — v1.3.0 usage guide covering: how SFK works, new project, adding SFK to an existing project, updating SFK, updating skills, adding a skill, plus a command reference.
- `bin/update-project.sh`: added `--no-backup` passthrough (wrapper now matches the updater's flags).

## 2026-07-07 — PLAN-0001 Release closure v1.3.0 + Session Audit
- `.sfk/VERSION`: `1.3.0-dev` → `1.3.0`. `CHANGELOG.md`: added `[1.3.0]` entry summarizing the engine/project separation.
- **Session Audit (SESSION-AUDIT-CHECKLIST) — Status: PASS.**
  1. Decision Integrity: no ACTIVE DECISION contradicted; architectural direction captured in PLAN-0001 + RULES (File Boundary Law).
  2. State Integrity: PLAN-0001 marked DONE; all 6 phases reflected; scope (6 points + D1–D4) fully respected.
  3. Operational Memory: every phase recorded here; PLAN updated with commit hashes and closed.
  4. Debug Memory: no product bug fixed this session — N/A.
  5. Technical Validation: `py_compile` (updater), functional hook tests (block/pass/`--no-verify`), scaffold tests (F3/F4), legacy migration fixture + idempotent re-run. No SFK product test suite; no secrets/console noise introduced.
  6. Regression Risk: sensitive area = updater (could harm existing projects) — mitigated by COPY-fixture test, auto-backup, report-only deletes, never-touch list.
  7. Git Governance: per-phase reviews done; Conventional-Commit messages; Git Record filled (F0 `6debf51`…F5 `670059d`); **push/merge NOT yet authorized (pending second explicit approval)**.
- Result: PASS for commit stage. Merge `refactor/engine-project-separation` → `main` and any push remain gated on the user's separate authorization.

## 2026-07-07 — PLAN-0001 Phase 5 (updater reworked for .sfk/ migration) — PLAN COMPLETE
- Rewrote `bin/lib/sfk_updater.py` for the new architecture:
  - **Layout detection**: CURRENT (`.sfk/kernel/BOOTSTRAP.md`) vs LEGACY (`kernel/BOOTSTRAP.md`) vs NONE.
  - **Legacy migration** (auto, before sync): `kernel/`→`.sfk/kernel/`, `kernel/project.toml`→`sfk.toml`, `kernel/SYSTEM.md`→`SYSTEM.md` (user content preserved). Timestamped `tar.gz` backup created first (skip with `--no-backup`).
  - **Engine sync driven by `.sfk/MANIFEST`** (single ownership map) — everything listed is refreshed to latest; anything not listed (`sfk.toml`, `SYSTEM.md`, `mcp_config.json`, `memory/`, `docs/`, `db/`, product code) is never touched.
  - Installs hooks (`core.hooksPath`), appends the `.sfk` rule to `.gitattributes` (non-destructive), syncs root IDE config + framework memory items, adds clean blueprint templates only when missing.
  - Deprecated list updated for the new layout (EVOLUTION_MEMORY, docs/config/*) — reported, never deleted. Post-migration guidance printed.
- Validated on a legacy fixture (COPY): migration moved kernel→.sfk, promoted config to root with content intact, installed VERSION/MANIFEST/hooks, activated `core.hooksPath`, appended gitattributes rule, created backup, reported EVOLUTION_MEMORY as deprecated. Idempotent re-run detected CURRENT and did nothing. `py_compile` clean.
- **PLAN-0001 complete** (F0–F5). Remaining closure (separate step): VERSION 1.3.0-dev→1.3.0, CHANGELOG, session audit, merge `refactor/engine-project-separation`→`main`.

## 2026-07-07 — PLAN-0001 Phase 4 (D4 enforcement + Layer-1 dedup) ##evolution
- **D4 — deterministic rule enforcement** so the AI can't silently drift from the memory discipline:
  - `.sfk/kernel/OPERATING_CARD.md` — new ≤20-line always-loaded digest of non-negotiables (plan/decision/debug/db/integration/modification-log/git-dual-approval/boundaries). Wired into Layer 0 (`BOOTSTRAP.md` + `index.toml [always]`, loaded first).
  - `.sfk/kernel/hooks/pre-commit` — BLOCKS commits with a significant change (source code / product docs / DB migration) unless `memory/MODIFICATION_LOG.md` is updated in the same commit; DB migrations/seeds also require `memory/logs/BUILD-HISTORY.md`. Escape: `git commit --no-verify`. Installer `.sfk/kernel/hooks/install.sh` (sets `core.hooksPath`).
  - Scaffolder auto-enables the hook on `--init-git`; QUICKSTART/next-steps updated; MANIFEST lists the new engine files.
  - New rule `RULES.md §9.6` documents the enforcement pair.
- **Layer-1 deduplication** (single source of truth per rule):
  - NEW vs EXISTING PROJECT classification: canonical in `BOOTSTRAP.md` Step 0; `RULES.md §9.2/§11` and `index.toml [bootstrap_project_state]` now point to it instead of restating.
  - Document-heading governance: canonical in `RULES.md §11`; `BOOTSTRAP.md` "Documentation Bootstrap Rules" now points to it.
  - `SOUL.md` "Context Management" trimmed to persona/behavior — defers memory mechanics to the Operating Card + RULES §9.
- Dogfooded: installed the hook on the SFK repo itself (`core.hooksPath = .sfk/kernel/hooks`).
- Validated in a fresh `--init-git` scaffold: Operating Card present, hook executable and installed, index loads it; functional test — significant-without-log BLOCKED, significant+log PASSES, `--no-verify` bypasses.

## 2026-07-07 — PLAN-0001 Phase 3 (project config to root + D1/D2/D3 structures) ##evolution
- **Config promoted to root** (Category B — project state, no longer buried in the engine):
  - `.sfk/kernel/project.toml` → `sfk.toml` (root); `.sfk/kernel/SYSTEM.md` → `SYSTEM.md` (root).
  - References rewritten across engine + root pointers + memory docs (word-boundary sed preserved `pyproject.toml`). Excluded `bin/lib/sfk_updater.py` (F5).
  - `_blueprint/.sfk/kernel/SYSTEM.md` → `_blueprint/SYSTEM.md`; scaffolder `EXTRA_CONFIG_FILES` now ships `sfk.toml`/`SYSTEM.md` from root.
- **D1 — Resume Panel:** `memory/progress.md` redefined with a minimal TOML front-block (updated/active_plan/phase/status/branch/blockers/next_action) + "Where am I" line, so returning to a project costs near-zero tokens. Clean template mirrored in `_blueprint/memory/progress.md`.
- **D2 — External interfaces single location:** `docs/integrations/` (README + `_EXAMPLE-service.md`) as per-service runbooks; `sfk.toml [[integrations]]` gains `runbook` pointer. Deploy runbook home `docs/deploy/`.
- **D3 — DB lifecycle single location:** `db/migrations/` + `db/seeds/` (sequential, append-only, never renumber) with convention READMEs; `sfk.toml [db]` section (engine, paths, ledger); application ledger = `memory/logs/BUILD-HISTORY.md`. `db` added to scaffolder `BLUEPRINT_DIRS`.
- **EVOLUTION_MEMORY removed** (req #4): deleted `docs/evolutive_changes/EVOLUTION_MEMORY.md` (root + `_blueprint`); technical evolution now consolidated into `memory/MODIFICATION_LOG.md` with tag `##evolution`. Rules updated in `RULES.md §9.1/§11` and `WORKFLOW_MEMORY_PLAYBOOK.md`.
- Removed stray `docs/config/INTEGRATIONS.md` (leaked JLR_Beauty draft — framework contamination). Added "names not values" rule to `RULES.md §11`. README directory tree rewritten to the new layout.
- Validated: fresh scaffold in temp → `sfk.toml`/`SYSTEM.md` at root, `db/`+`docs/integrations/`+`docs/deploy/` propagate, `progress.md` clean Resume Panel, no `EVOLUTION_MEMORY`/`.sfk/kernel/{project.toml,SYSTEM.md}` refs remain.

## 2026-07-07 — PLAN-0001 Phase 2 (tooling consolidated into bin/)
- `tools/` → `bin/lib/` (`jb_kit_turbo.py`, `sfk_updater.py`), `tools/README.md` → `bin/README.md`.
- Root wrappers → `bin/` (`new-project.{sh,ps1}`, `update-project.{sh,ps1}`); wrapper paths updated `tools/` → `lib/`.
- `_blueprint/kernel/` → `_blueprint/.sfk/kernel/` so blueprint overrides land at the new engine path.
- `bin/lib/jb_kit_turbo.py`: `template_root` parents[1]→[2]; `BLUEPRINT_DIRS` `kernel`→`.sfk`; added `.gitattributes` to `EXTRA_CONFIG_FILES`; QUICKSTART text refs `kernel/`→`.sfk/kernel/`.
- `.sfk/kernel/scripts/import_skill.py`: fixed `PROJECT_ROOT` (parents[3]) and `SKILLS_DIR` (`.sfk/kernel/skills`) — the sed missed this (Python path-join form).
- `bin/lib/sfk_updater.py`: fixed `__file__` parents; added PHASE-5 warning (its layout logic still targets legacy `kernel/`).
- Root cleanup: removed `null`, `.codex`, and stale `*.log` files.
- Validated: scaffolded a fresh project in a temp dir → `.sfk/` isolated, root clean, `memory/`+`docs/` at root, `.gitattributes` propagated, QUICKSTART points to `.sfk/kernel/`.
