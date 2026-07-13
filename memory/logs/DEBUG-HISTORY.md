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
