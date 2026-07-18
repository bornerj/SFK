# Modification Log

This log tracks relevant changes in the SFK framework and also serves as a reference example for how to record change history in projects that adopt this structure.

---

## 2026-07-17 — SESSION AUDIT — PASS
| Item | Result |
|---|---|
| Decision Integrity | PASS — `DECISION-001` (skillspector audit, prior session) unrelated and unaffected; no structural/auth/schema/API change this session |
| State Integrity | PASS — `PLAN-0001`–`PLAN-0004` already `DONE`; `PLAN-0005` closed `DONE` this session with a filled Git Record; scope respected (explicit out-of-scope list honored) |
| Operational Memory | PASS — every change recorded in this log in real time, including the mid-session `LangSwitch` follow-up; plan closed with real progress, not placeholders |
| Debug Memory | PASS, with a note — the `LangSwitch` visibility report was investigated (introspection found the widget mapped/viewable/correctly positioned, no confirmed reproducible defect) and hardened rather than logged as a `DEBUG-HISTORY` entry, since no SYMPTOM→ROOT_CAUSE was actually confirmed; full reasoning kept in this log instead |
| Technical Validation | PASS, same noted caveat as prior sessions — no formal lint/test-suite tool configured for this repo's Python tooling; validation was `py_compile` + live-`DISPLAY` functional checks (geometry/cutoff, language-switch retranslation + input preservation, persistence round-trip, widget introspection, full real dry-run flow) |
| Regression Risk | PASS — no sensitive area touched (auth/payment/scheduling/external integration); change confined to the GUI presentation layer; `ProcessRunner`/subprocess wiring and the wrapped scripts untouched; no prior debug-history entry in this area |
| Git Governance | PASS — files reviewed and summarized before commit; Conventional Commits message; Git Record of Delivery filled (`PLAN-0005` §7) with real hash/push range; commit and push both explicitly authorized by the user in the same instruction |

Session summary: delivered `PLAN-0005` — SFK Launcher GUI compact layout (window
880x620→760x580, fonts and cards shrunk so all 5 Home cards fit without manual
resizing) + a full PT/EN language switch (`bin/lib/gui_i18n.py`, in-place
retranslation, persisted preference), including a post-test follow-up making the
`LangSwitch` a visible bordered chip after the user found the first version easy to
miss testing via the real Zorin desktop shortcut. 1 commit, pushed to `origin/main`
(`57c1f35..f0085d6`). Nothing pending, nothing blocked.

Full checklist copy: `memory/logs/AUDIT_CHECKLIST_2026-07-17-PASS.md`.

## 2026-07-17 — PLAN-0005 (SFK Launcher GUI: compact layout + PT/EN language switch) — PLAN COMPLETE
- User-reported problem: `bin/sfk_gui.py`'s default window (`880x620`) cut off the last Home card ("Checar um projeto") — cards were `92px` tall and required manual resizing to see. Also requested a PT/EN language toggle, top-right, visible on every screen, plus overall smaller fonts/window.
- **F1 — i18n foundation:** new `bin/lib/gui_i18n.py` — `STRINGS` dict (PT/EN, one key per UI string: titles, buttons, checkboxes, console/error messages, `messagebox` dialogs), `Lang` singleton (`t()`/`load()`/`save()`/`on_change()`/`set()`), preference persisted to `Path.home() / ".sfk_launcher_lang"` (outside the repo — user-level GUI preference, not project state).
- **F2 — compact layout:** `Theme.SPACE_*` (32/24/16/8/4 → 24/18/12/6/3), `Fonts` sizes (title 22→18, h1 15→13, h2 12→11, body 11→10, small 9→8, mono 10→9), `ActionCard` height 92→72 with re-tuned text offsets, `App.geometry`/`minsize` 880x620/720x520 → 760x580/680x480.
- **F3 — language switch + retranslation:** `LangSwitch` widget (PT/EN, top-right, placed directly on the root window so it survives `tkraise()` between views) toggles `Lang.current`. Chose **retranslate in-place** over rebuilding views on switch — every static-text widget across `Header`, `PathPicker`, `ResultBanner`, and all 6 views (`HomeView`, `CheckProjectView`, `NewProjectView`, `UpdateProjectView` ×2 routes, `SkillsView`) now keeps a `self.xxx` reference and each view implements `retranslate()`, so a language switch mid-task never discards a typed path/name/checkbox state.
- Validated (`/tmp/.../validate_gui.py`, `/tmp/.../validate_gui_flow.py`, not committed — scratch scripts): `py_compile` clean; real `App` instantiated against a live `DISPLAY` — all 5 Home cards fit inside the new window height (last card bottom=414px vs 580px window, no cutoff); language switch retranslates every checked view without losing a simulated typed path; preference file round-trips (`Lang.set("en")` → file contains `en` → fresh `Lang.load()` reads it back); full existing dry-run flow (`CheckProjectView` → `sfk_updater.py --dry-run` against this repo) still completes successfully end-to-end through the refactored wiring — no regression in the untouched business logic.
- No screenshot tool available in this environment to eyeball the result visually — validation relied on programmatic geometry/text assertions instead (see above); font sizes chosen are still standard readable UI sizes (10pt body / 8pt small), not extreme shrinks.
- **Follow-up (same day, pre-commit):** user tested the real build via the Zorin desktop shortcut — smaller fonts confirmed, but didn't spot the `LangSwitch`. Introspection (`winfo_ismapped`/`winfo_viewable`/geometry — no screenshot tool in this environment, see above) confirmed the widget was in fact mapped, viewable, and correctly positioned at the top-right corner within window bounds; most likely low visual salience (8pt plain gray/teal text, no border, blending into the background) rather than a real absence. Redesigned `LangSwitch` as a bordered chip (`Theme.CARD_BG` background + `Theme.CARD_BORDER` outline, `Fonts.body_bold` instead of `Fonts.small`) so it reads as a clickable control at a glance; also added a defensive `self._lang_switch.lift()` in `App.show()` on every view switch, closing any residual doubt about z-order stacking across window managers. Re-validated: `py_compile` clean, full `validate_gui.py` suite still passes.

## 2026-07-17 — DECISION-001: skillspector false-positive audit (7 flagged skills cleared) (point-in-time)
- User received a third-party security scan report ("skillspector", NVIDIA) flagging 178 skills as ≠ SEGURO. Of the SFK's 57 skills, 7 matched by name: `mcp-builder`, `mobile-design`, `performance-profiling`, `red-team-tactics`, `systematic-debugging`, `ui-ux-pro-max`, `deployment-procedures`.
- Manually investigated every finding for all 7 skills against the actual files/lines in `.sfk/kernel/skills/`: confirmed real content, grepped for genuinely dangerous patterns (`subprocess`, `os.environ`, `eval`/`exec`, `shell=True`, credential-file reads, network calls), and cross-checked each report's cited evidence line-by-line.
- Result: **zero real risk in all 7 skills.** Root causes identified: (1) two skills (`mcp-builder`, `systematic-debugging`) — scanner analyzed a different/fuller upstream version; cited files don't exist in the SFK's vendored copy; (2) `mobile-design`, `deployment-procedures` — security-advice prose ("use Keychain", checklist items) misread as the vulnerability itself; (3) `ui-ux-pro-max` — scanner systematically confused "Don't"/"Code Bad" examples in a Do/Don't reference dataset with the skill's actual behavior; (4) `red-team-tactics` — educational pentest-checklist table row misread as real command execution; (5) `performance-profiling` — a `subprocess.run` call already using the safe list-args pattern (no `shell=True`) flagged anyway.
- Recorded as `memory/decisions/DECISION-001.md` (Status: ACTIVE) — includes the reusable verification methodology and the recurring false-positive patterns, so future skillspector-style reports on SFK skills don't require re-deriving this from scratch.
- No code changed; all 7 skills remain installed, unrestricted.

---

## 2026-07-13 — SESSION CLOSURE — PASS
| Item | Result |
|---|---|
| Decision Integrity | PASS — no ACTIVE `DECISION-*` exists in this repo; nothing contradicted; no structural/auth/schema/API change occurred this session |
| State Integrity | PASS — `PLAN-0001`, `PLAN-0002`, `PLAN-0003`, `PLAN-0004` all `DONE`; no open plan; scope respected in all (out-of-scope items explicitly deferred, not silently done) |
| Operational Memory | PASS — every change recorded in this log in real time; both plans updated with real phase progress and closed with a filled Git Record |
| Debug Memory | PASS — 3 bugs fixed this session, all recorded in `memory/logs/DEBUG-HISTORY.md` (ERR-0001, ERR-0002, ERR-0003), full ID/SYMPTOM/ROOT_CAUSE/ACTION/CONTEXT template |
| Technical Validation | PASS, with a noted caveat — no formal lint/test-suite tool is configured for this repo's Python tooling (`bin/lib/*.py`); validation was `py_compile` (syntax) + functional fixture testing (dry-run, apply, byte-identical diffs on pre-existing files, LEGACY/CURRENT regression, dry-run against the user's real reported project) — same methodology already established in this repo's prior sessions (`PLAN-0001`/`PLAN-0002`), not a gap introduced here |
| Regression Risk | PASS — no sensitive area touched (auth/payment/scheduling/external integration); change is scaffolder/updater tooling only; fixture-based functional coverage exists for the changed paths; no unresolved prior debug-history entry could resurface (these are the first entries in the file) |
| Git Governance | PASS — files reviewed and summarized before every commit; Conventional Commits messages; Git Record of Delivery filled for `PLAN-0002`/`PLAN-0003`/`PLAN-0004` including push hashes; every commit and every push explicitly authorized by the user, separately |

Session summary: fixed the user-reported bug (SFK Launcher "Adicionar SFK a projeto
existente" failing on genuinely SFK-less projects — `PLAN-0003`), a collateral leak
found while investigating it (`PLAN-0004`, new-project scaffolder copying this repo's
own real plans/PRs), and a follow-up doc correction (`_blueprint/SYSTEM.md` stale
`kernel/` references, ERR-0003). 4 commits, all pushed to `origin/main`
(`a0377d5..f8b2abe`). Nothing pending, nothing blocked.

Full checklist copy: `memory/logs/AUDIT_CHECKLIST_2026-07-13-PASS.md`.

## 2026-07-13 — _blueprint/SYSTEM.md: fix stale pre-.sfk/ layout references (point-in-time) ##bug
- `_blueprint/SYSTEM.md` (the blank `SYSTEM.md` handed to every new/bootstrapped project — user-requested follow-up to `PLAN-0003`'s closing notes) still referenced the pre-v1.3.0 layout: `kernel/RULES.md`, `kernel/SYSTEM-TEMPLATE.md`, `kernel/sfk.toml` (the last one doubly wrong — `sfk.toml` lives at the project root, never under `kernel/`). Corrected to `.sfk/kernel/RULES.md`, `.sfk/kernel/SYSTEM-TEMPLATE.md`, `sfk.toml`. This repo's own root `SYSTEM.md` was already correct; only the `_blueprint/` starter was stale. Recorded as `memory/logs/DEBUG-HISTORY.md` ERR-0003.
- Single file, no behavior change, below the plan threshold — point-in-time execution per Anti-Scope-Drift.

## 2026-07-13 — PLAN-0004 F1–F3 (scaffolder: stop leaking real delivery history) ##bug
- Bug reported by the user: SFK Launcher "Adicionar SFK a projeto existente" failed with "not an SFK project" on a project that genuinely has no SFK yet — investigation traced the root cause to `sfk_updater.py` never having a real bootstrap path for layout `none` (tracked as `PLAN-0003`). While investigating, found a related but separate leak in the *new-project* scaffolder and confirmed scope with the user: only the framework (`.sfk/` + blank `memory/`/`docs/`/`db/` skeleton) should ever propagate to a project — never this repo's own real plans/PRs.
- `bin/lib/jb_kit_turbo.py`: added `REAL_HISTORY_PATTERN` (`^(PLAN|DECISION|PR)-\d+`) + `is_own_delivery_history()`, wired into `should_ignore()` (shared by `ignore_filter`/`copytree` and `apply_blueprint_overrides`). Template files (`PLAN-XXXX-...`, `DECISION-XXX.md`, `PR-XXXX-...`) are unaffected; files with a real sequence number are now skipped during scaffolding, self-applying to any future `PLAN-000N` without touching the filter again.
- Validated: `py_compile` clean; scaffolded a fresh fixture in a temp dir — `memory/plans/` now contains only `PLAN-XXXX-DONE-subject.md` (previously also had real `PLAN-0001`/`PLAN-0002`/`PLAN-0003`), `memory/decisions/` only `DECISION-XXX.md`, `memory/` root only `PR-XXXX-DESCRIPTION.md` (previously also `PR-0001-DESCRIPTION.md`); `.sfk/`, `docs/`, `db/`, and the 6 already-blanked starter files (`MODIFICATION_LOG.md`, `DEBUG-HISTORY.md`, `progress.md`, `DRIFT-RULES.md`, `BUILD-HISTORY.md`, `SYSTEM.md`) confirmed unchanged — no regression. Recorded as `memory/logs/DEBUG-HISTORY.md` ERR-0001.
- Next: `PLAN-0003` (updater bootstrap for layout `none`) imports `is_own_delivery_history()` from this file — implementation in progress.

## 2026-07-13 — PLAN-0003 (sfk_updater.py: bootstrap install for layout `none`) — PLAN COMPLETE ##bug
- Fixes the actual bug the user reported: SFK Launcher GUI "➕ Adicionar o SFK a um projeto que já existe" errored with "not an SFK project" on a real project that genuinely has no SFK — the exact case that button exists for. Root cause and fix detail: `memory/logs/DEBUG-HISTORY.md` ERR-0002.
- `bin/lib/sfk_updater.py`: `detect_layout("none")` no longer aborts. New `build_bootstrap_items()` (strictly additive — every item skipped if the destination already exists), `build_bootstrap_generated_content()` + `apply_generated()` (blank `MODIFICATION_LOG.md`/`DEBUG-HISTORY.md` via `jb_kit_turbo`, never this repo's own real ones), `collect_new_only()` helper, `BOOTSTRAP_TEMPLATE_DIRS`/`BOOTSTRAP_NOTES`. `build_manifest_items()` extracted from `build_sync_plan()` as a pure refactor (no behavior change) so both the CURRENT/LEGACY sync path and the new bootstrap path share it. `main()` branches on `bootstrap` instead of erroring; CURRENT/LEGACY code paths and their output are otherwise untouched. Docstring updated to describe the new NONE→bootstrap path instead of "aborts".
- Depends on `PLAN-0004`'s `jb_kit_turbo.is_own_delivery_history()` (memory/plans, memory/decisions, memory/PR-*-DESCRIPTION.md filtered the same way as the scaffolder) and new `blank_modification_log()`/`blank_debug_history()` (extracted from `jb_kit_turbo.reset_starter_docs()`, no behavior change to the new-project scaffolder).
- `USAGE.md` §3 and `sfk_gui.py::UpdateProjectView` needed **no changes** — §3 already documented this exact "install only if missing" behavior (the docs described the promised feature; the code just never delivered it until now), and the GUI's success/error handling is generic on the script's exit code.
- Validated: `py_compile` clean on both files. Fixture with pre-existing `README.md`/`app.py`/custom `.gitignore` (with a project-specific rule) — dry-run showed a clean additive-only plan (no `.gitignore` in it since it already existed), apply installed `.sfk/`, `sfk.toml`, `SYSTEM.md`, `memory/docs/db` skeleton, confirmed `README.md`/`app.py`/`.gitignore` byte-identical (md5) before/after, `.gitignore`'s custom rule intact; `memory/plans/`/`memory/decisions/`/`memory/` root only contained template files (`PLAN-XXXX-DONE-subject.md`, `DECISION-XXX.md`, `PR-XXXX-DESCRIPTION.md`), never this repo's real PLAN-0001/0002/0003/PR-0001. Regression: LEGACY fixture (`kernel/` layout with real `project.toml`/`SYSTEM.md` content) migrated correctly, content preserved byte-for-byte, product code untouched; CURRENT-layout re-run (dry-run) on the just-bootstrapped fixture produced sensible output unaffected by the refactor. Dry-run against the user's actual reported project path (`antigravity-awesome-skills/reports/dashboard`) confirmed the fix — clean bootstrap plan instead of the original error; not applied for real (out of this plan's scope — read-only confirmation only, per the approved checklist).
- Known side-effect flagged, not fixed here (pre-existing CURRENT-layout behavior, unrelated to this plan): re-running "Update" on an already-bootstrapped project will fully sync `EXTRA_CONFIG_ITEMS` (including `.gitignore`), which can overwrite a project's own `.gitignore` rules on a later update — same behavior that already existed for any CURRENT-layout project, not introduced by this fix. Also noted: `_blueprint/SYSTEM.md` (used by both the scaffolder and this bootstrap path) has one stale reference to `kernel/RULES.md` instead of `.sfk/kernel/RULES.md` — pre-existing content issue, one line, not fixed here (out of scope).

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

## 2026-07-08 — PLAN-0002 Phase 6 (docs & memory) — PLAN COMPLETE
- `USAGE.md`: new §0 "Prefer clicking? Use the SFK Launcher (GUI)" — how to run it (`python3 bin/sfk_gui.py` or double-click launchers), what it covers (maps to §2–§6), and the Tkinter dependency note. Added a GUI row to the quick command reference table.
- `README.md`: added a "🖱️ Prefer clicking?" pointer near the top; directory tree updated with `bin/sfk_gui.py`, `bin/sfk-launcher.sh`, `bin/sfk-launcher.bat`.
- `INSTRUCTIONS.md`: added a GUI row to the reference table.
- `memory/plans/PLAN-0002-SFK-LAUNCHER-GUI-STANDALONE.md`: marked **DONE**, Git Record filled with all 6 phase commit hashes (`d1521bd`…`fbfbc8f`), approval checklist checked off.
- `memory/progress.md`: Resume Panel updated to reflect PLAN-0002 shipped; Modules table gained a "SFK Launcher (GUI)" row; Recent Activity updated.
- **PLAN-0002 complete** (F1–F6). All commits are on `main` directly (single-phase-per-commit pace, no separate branch this time); push to `origin` remains a separate pending authorization.

## 2026-07-08 — PLAN-0002 Phase 5 (SFK Launcher — ergonomics & robustness)
- Friendly missing-Tkinter handling: `import tkinter` moved into a `try/except ModuleNotFoundError` at the top of `bin/sfk_gui.py`, printing distro-specific install commands (apt/dnf/pacman/brew) instead of a raw traceback.
- App icon generated procedurally (no external asset, no PIL): `build_icon_image()` draws 3 stacked bars (teal background + cream/console-accent bars) echoing the app's own 3-zone architecture diagram; wired into the window via `iconphoto`. Maintainer command `python3 bin/sfk_gui.py --export-icon [path]` regenerates the static asset; committed `bin/sfk-launcher.png` (64x64).
- Double-click launchers: `bin/sfk-launcher.sh` (Linux/macOS, detects python3/python, `--install-desktop` writes a validated `.desktop` entry to `~/.local/share/applications/` with absolute paths) and `bin/sfk-launcher.bat` (Windows, prefers `pythonw` to avoid a console flash).
- Validated: `py_compile` clean; icon exported and visually inspected (64x64 PNG, correct motif); full regression — all 6 views still render after the import restructuring; `sfk-launcher.sh` launched the real GUI; `--install-desktop` generated a `.desktop` file that passed `desktop-file-validate`.

## 2026-07-08 — PLAN-0002 Phase 4 (SFK Launcher — Skills panel)
- `.sfk/kernel/scripts/import_skill.py` (engine maintenance edit): added `--force` (skip the interactive overwrite `input()` prompt — was the blocker preventing non-interactive/GUI use), changed `import_skill()` to return `bool`, and the CLI now exits with the correct code (`0`/`1`) instead of always `0`. CLI behavior unchanged when `--force` is omitted.
- New `SkillsView`: import a new skill (folder picker + `import_skill.py --force`, with a confirmation dialog only when the skill name already exists — avoids duplicating a name silently), a shortcut to the existing Update/Add flow for syncing a project's skills (skills are engine files, synced via `.sfk/MANIFEST` like everything else — no separate mechanism needed), and a live list of skills already installed in this SFK (refreshed via a new `BaseView.on_show()` hook called from `App.show()`).
- Validated: `py_compile` clean on both files; direct CLI test of `import_skill.py --force` (new import, overwrite, missing-path error) confirms correct exit codes; full GUI test — all 6 views render, skills list shows 57 entries on load, importing a new skill succeeds and appends to the list, re-importing the same skill triggers the confirmation dialog (simulated) and overwrites without duplicating the list entry. Test residue cleaned up; `git status` confirmed no stray files.

## 2026-07-08 — PLAN-0002 Phase 3 (SFK Launcher — Add/Update panel)
- New `UpdateProjectView` wraps `bin/lib/sfk_updater.py`, reused for both "Adicionar o SFK a um projeto existente" and "Atualizar o SFK de um projeto" (same underlying action, different header copy). "Pré-visualizar (dry-run)" is the primary action; "Aplicar" is a same-path-preview-gated, confirmation-required (`messagebox.askyesno`) secondary action styled with the danger color. Checkbox to skip the automatic backup (`--no-backup`), unchecked by default.
- Safety guard: Apply refuses to run (shows an inline error banner, no confirmation dialog even shown) unless a dry-run preview already succeeded for the exact same path in this session; changing the path hides any stale banner.
- Transparency-by-design: detected layout, migration plan, and the backup archive path are shown via the real console output (no fragile output-parsing needed) — the updater already prints all of this.
- Validated: `py_compile` clean; all 6 views render headless; apply-without-preview guard confirmed to block before reaching the confirmation dialog; **full end-to-end migration** on a legacy fixture (root `kernel/` layout, same shape as the real VetSystem project) through the GUI — preview detected LEGACY layout, `_last_previewed_target` set, simulated confirmation (`messagebox.askyesno` monkeypatched to True for the automated test), apply executed the real migration: `.sfk/kernel` created, legacy `kernel/` removed, `sfk.toml`/`SYSTEM.md` promoted to root, timestamped backup `.tar.gz` created, success banner shown.

## 2026-07-08 — PLAN-0002 Phase 2 (SFK Launcher — New Project panel)
- `NewProjectView` wired to the real scaffolder (`bin/lib/jb_kit_turbo.py`): folder-picker for the parent directory + project-name field (sanitized: no path separators, no `.`/`..`), checkboxes for `--init-git` (default on) and `--force`; inline pre-flight validation blocks running against a non-empty target unless `--force` is checked.
- New reusable `ResultBanner` widget (success/error strip + "Abrir pasta" action) and `open_folder()` cross-platform helper (Windows/macOS/Linux); fixed a real Tkinter `pack()` ordering bug — the banner must be packed with `before=<anchor widget>` since `pack()` order follows call order, not creation order.
- Validated: `py_compile` clean; headless render of all views; unit tests of the 4 validation branches (empty folder / empty name / slash in name / valid); **end-to-end run through the real threaded pipeline** — created an actual project on disk (`sfk.toml`, `SYSTEM.md`, `.sfk/kernel`, `.git` with `core.hooksPath` auto-enabled via `--init-git`), success banner shown; confirmed the non-empty-folder guard blocks without `--force` and allows with it.

## 2026-07-08 — PLAN-0002 Phase 1 (SFK Launcher GUI — skeleton)
- Started `PLAN-0002` (standalone Tkinter GUI launcher for SFK), approved by the user (design, phases, name "SFK Launcher").
- Applied `@frontend-specialist` + skill `frontend-design`: sober high-contrast theme (warm off-white + deep-teal accent, avoiding dark/neon/purple clichés), OS-native font fallback chain (zero-install, no bundled fonts), card-based Home screen as the differentiation anchor, dark console panel as the one deliberate high-contrast surface.
- New `bin/sfk_gui.py` (stdlib-only, no pip deps): `Theme`/`Fonts`, threaded `ProcessRunner` (subprocess + queue, non-blocking UI), reusable widgets (`ActionCard` canvas-drawn rounded card, `PrimaryButton`/`SecondaryButton`, `PathPicker` with disk-browse dialog, `ConsolePanel` live read-only console, `Header`), `HomeView` with 5 self-explanatory action cards, fully functional `CheckProjectView` (wraps `sfk_updater.py --dry-run`), `ComingSoonView` stubs for New Project/Add-existing/Update/Skills (land in later phases).
- Dev environment note: Tkinter was not installed on this machine; user authorized and ran `sudo apt install python3-tk` (reversible, stdlib companion package).
- Fixed a real bug found in testing: `App._register` collided with Tkinter's internal `Misc._register` (used by `wm_protocol`) — renamed to `_add_view`.
- Validated: `py_compile` clean; headless smoke test rendered all 6 views without exception; end-to-end test ran `CheckProjectView` against a real scaffolded fixture through the actual threaded runner — console streamed real `sfk_updater.py` output, exit code 0 captured, **zero files modified** (dry-run safety confirmed with a fresh timestamp marker). No visual screenshot possible (no screenshot tool in this Wayland session) — validated functionally instead.

## 2026-07-07 — README.md aligned to v1.3.0 + skill count fix
- README "Create a new project" commands were stale (root `.\new-project.ps1`, `bash new-project.sh`, `python tools/jb_kit_turbo.py`) → corrected to `bin\new-project.ps1` / `bash bin/new-project.sh`; added USAGE.md pointer. The directory-tree block was already correct (Phase 3).
- Fixed wrong clone URL `github.com/Jeiel/sfk` → `github.com/bornerj/SFK` (matches origin).
- Skill count drift (pre-existing): actual count is **57**, docs said 56. Updated README, CLAUDE.md, and scaffolder QUICKSTART text to 57. Agents (20) and workflows (11) verified correct.

## 2026-07-07 — INSTRUCTIONS.md aligned to v1.3.0 layout
- Follow-up: the F1/F3 seds only rewrote literal paths in `INSTRUCTIONS.md`; structural/prose refs were still stale. Fixed manually:
  - Layer diagram redrawn as 3 zones (engine `.sfk/` read-only · project config at root `sfk.toml`/`SYSTEM.md` · project state `memory/ docs/ db/`), added OPERATING_CARD/hooks/VERSION/MANIFEST.
  - Scaffolder section: `bin/new-project.sh` + `bin\new-project.ps1` (was root `.\new-project.ps1`); corrected the "what it copies" list (`.sfk/`, root config, `db/`; dropped bogus `.agent/`); noted hook auto-enable on `--init-git`.
  - Close-session example: audit result recorded in MODIFICATION_LOG (per rule f8dffdf), not a separate AUDIT file; closes on PASS only.
  - Reference table: added `USAGE.md`, `OPERATING_CARD.md`, updater rows.

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
