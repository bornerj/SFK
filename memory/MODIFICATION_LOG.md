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
- `kernel/BOOTSTRAP.md`, `kernel/RULES.md` e `kernel/index.toml` atualizados para:
  - classify the repository as NEW PROJECT when there are no plans, no decisions, and no real history in `MODIFICATION_LOG`;
  - ignore `kernel/project.toml` and `kernel/SYSTEM.md` as validation sources when the project is new;
  - require `docs/project/PROJECT_OVERVIEW.md` and `docs/project/REQUIREMENTS.md` to match the structure from `../Rifa`.
- `docs/project/PROJECT_OVERVIEW.md` and `docs/project/REQUIREMENTS.md` reformatted to mirror the `Rifa` sections, including `FR-XXX`, `NFR-XXX`, and `AC-XXX` identifiers.
- `docs/project/SCOPE.md` and `docs/project/SETUP.md` created with the same `##` section structure used in `../Rifa/docs/project/`.
- `docs/project/SCOPE.md` and `docs/project/SETUP.md` converted to English to keep consistency with SFK's own files.
- Explicit rule added: SFK kernel/template files stay in English; project-generated documents may follow the language declared in `kernel/project.toml`.

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
