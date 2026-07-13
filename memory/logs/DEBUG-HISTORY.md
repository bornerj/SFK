# Debug History 

# ID: ERR-0001: Scaffolder leaked SFK's own real delivery history into new projects ##bug
SYMPTOM: `bin/lib/jb_kit_turbo.py` (new-project scaffolder) copied this repository's
real `memory/plans/PLAN-0001-*.md`, `PLAN-0002-*.md`, `PLAN-0003-*.md`, and
`memory/PR-0001-DESCRIPTION.md` into every freshly scaffolded project — discovered as
a collateral finding while investigating the `sfk_updater.py` bootstrap bug (PLAN-0003),
confirmed by the user as unwanted.
ROOT_CAUSE: `copy_blueprint()` does a wholesale `shutil.copytree()` of `memory/` (and
`docs/`, `db/`, `.sfk/`) from the SFK repo root; the `ignore_filter` only excluded VCS/
build noise (`.git`, `node_modules`, `.pyc`, etc.), never distinguished a template file
(`PLAN-XXXX-...`, `DECISION-XXX.md`, `PR-XXXX-...`) from this repo's own numbered
delivery history (`PLAN-0001`, `PR-0001`).
ACTION: Added `REAL_HISTORY_PATTERN = re.compile(r"^(PLAN|DECISION|PR)-\d+")` and
`is_own_delivery_history()` in `bin/lib/jb_kit_turbo.py`, wired into `should_ignore()`
(shared by `ignore_filter` for `copytree` and `apply_blueprint_overrides`). A file is a
template when its sequence number is the literal placeholder (`XXXX`/`XXX`); it is real
history when it has an actual number — auto-applies to any future `PLAN-000N` without
touching the filter again. Verified with a scaffolded fixture: `memory/plans/` only
`PLAN-XXXX-DONE-subject.md`, `memory/decisions/` only `DECISION-XXX.md`, `memory/` root
only `PR-XXXX-DESCRIPTION.md`; `.sfk/`, `docs/`, `db/` and the 6 already-blanked files
unaffected (regression-clean).
CONTEXT: `memory/plans/PLAN-0004-SCAFFOLDER-REAL-HISTORY-LEAK.md`.

# ID: ERR-0002: "Adicionar SFK a projeto existente" failed on projects with no SFK at all ##bug
SYMPTOM: User reported, via the SFK Launcher GUI, that clicking "➕ Adicionar o SFK a
um projeto que já existe" on a real, genuinely SFK-less project produced
`ERROR: '<path>' is not an SFK project (no .sfk/kernel/BOOTSTRAP.md or
kernel/BOOTSTRAP.md).` — exactly the scenario the button exists for.
ROOT_CAUSE: `bin/lib/sfk_updater.py::detect_layout()` correctly classifies a project
with neither `.sfk/kernel/BOOTSTRAP.md` nor `kernel/BOOTSTRAP.md` as layout `"none"`,
but `main()` treated `"none"` as a fatal abort (`return 1`) — a leftover guard from
before the "add to existing project" GUI flow existed. The updater only ever
implemented two real code paths (`current` sync, `legacy` migration); `none` was
never actually built out despite `sfk_gui.py::UpdateProjectView` and `USAGE.md` §3
already documenting/promising the bootstrap behavior.
ACTION: Added a real bootstrap path for layout `none` in `sfk_updater.py`
(`build_bootstrap_items()`, `build_bootstrap_generated_content()`, `apply_generated()`),
strictly additive — every item is skipped if the destination already exists, so a
project's pre-existing files (`.gitignore`, `CLAUDE.md`, code, etc.) are never
overwritten. Installs `.sfk/` (MANIFEST-driven, already additive when nothing
exists), blank `sfk.toml`/`SYSTEM.md`, blank `memory/`/`docs/`/`db/` skeleton (via
`jb_kit_turbo.is_own_delivery_history()` from `PLAN-0004` — never this repo's own
real plans/decisions/PRs), and generates blank `MODIFICATION_LOG.md`/
`DEBUG-HISTORY.md` (`jb_kit_turbo.blank_modification_log()`/`blank_debug_history()`)
instead of copying this repo's real ones. `main()` now branches on `bootstrap`
instead of aborting; `CURRENT`/`LEGACY` code paths untouched (`build_sync_plan()`
kept as-is, only had `build_manifest_items()` extracted from it as a pure
refactor for reuse).
CONTEXT: `memory/plans/PLAN-0003-UPDATER-BOOTSTRAP-NONE-LAYOUT.md`. Validated: dry-run
+ apply on a fixture with pre-existing `README.md`/`app.py`/custom `.gitignore` (all
confirmed byte-identical after apply); LEGACY and CURRENT layouts regression-tested
(byte-identical migration content, no plan changes); dry-run against the user's
actual reported project path confirmed the fix (clean additive plan instead of the
error).

# ID: ERR-0003: _blueprint/SYSTEM.md pointed to the pre-.sfk/ legacy layout ##bug
SYMPTOM: Flagged as a side-finding while validating `PLAN-0003` (the bootstrap path
copies `_blueprint/SYSTEM.md` into a project's `SYSTEM.md` on first install, same as
the new-project scaffolder already did). The file itself still referenced the old
root-`kernel/` layout from before the v1.3.0 `.sfk/` restructuring (`PLAN-0001`).
ROOT_CAUSE: `_blueprint/SYSTEM.md` was never updated when `PLAN-0001` moved the engine
to `.sfk/kernel/` and promoted `sfk.toml` to the project root. It still said
`kernel/RULES.md`, `kernel/SYSTEM-TEMPLATE.md`, and `kernel/sfk.toml` — the last one
doubly wrong, since `sfk.toml` lives at the project root, never under `kernel/` at all.
This repo's own root `SYSTEM.md` was already correct; only the `_blueprint/` starter
template was stale.
ACTION: Corrected all three references in `_blueprint/SYSTEM.md` to
`.sfk/kernel/RULES.md`, `.sfk/kernel/SYSTEM-TEMPLATE.md`, and `sfk.toml`. No other
`kernel/`-without-`.sfk/` references remained in the file (verified by grep). Both
consumers of this template — the new-project scaffolder (`jb_kit_turbo.py`
`apply_blueprint_overrides()`) and the `PLAN-0003` bootstrap path — now hand out a
correct `SYSTEM.md` on first install.
CONTEXT: Noted but not fixed in `PLAN-0003`'s closing `MODIFICATION_LOG.md` entry
(2026-07-13); fixed here as a point-in-time correction (single file, no behavior
change, below the plan threshold).
