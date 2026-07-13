#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFK -- Structured Framework Kit
================================
Update an existing SFK project to the latest engine, migrate legacy projects
(root `kernel/` layout) to the current `.sfk/` layout, and bootstrap SFK onto a
project that has none yet.

Usage:
    python sfk_updater.py <target> [--yes] [--dry-run] [--no-backup]

Layouts detected:
  - CURRENT : target has `.sfk/kernel/BOOTSTRAP.md`  → engine sync only.
  - LEGACY  : target has `kernel/BOOTSTRAP.md` (no `.sfk/`) → migrate, then sync.
  - NONE    : neither → bootstrap install (add SFK to an existing project).

Migration (LEGACY → CURRENT), applied before syncing:
  - `kernel/`            → `.sfk/kernel/`
  - `kernel/project.toml`→ `sfk.toml`  (root; user-owned content preserved)
  - `kernel/SYSTEM.md`   → `SYSTEM.md` (root; user-owned content preserved)
  A timestamped backup archive of the target is created first (unless --no-backup).

Bootstrap (NONE → CURRENT), strictly additive — never overwrites a file that
already exists in the target: installs the `.sfk/` engine, blank `sfk.toml`/
`SYSTEM.md`, blank starter `memory/`/`docs/`/`db/` skeleton (never this repo's
own real plans/decisions/PR descriptions — only the `XXXX`/`XXX` template files,
via `jb_kit_turbo.is_own_delivery_history`), IDE config, gitattributes and hooks.

Engine sync (CURRENT/LEGACY): every path listed in `.sfk/MANIFEST` is overwritten
with the latest version. The MANIFEST is the single ownership map — anything not
in it (sfk.toml, SYSTEM.md, .sfk/kernel/mcp_config.json, memory/, docs/, db/,
product code) is NEVER touched. Also synced: root IDE config (.clauderules,
CLAUDE.md, .windsurfrules, .gitignore, .cursor/), framework-owned memory items,
and clean blueprint templates added only when missing.

`.gitattributes` gets the `.sfk` vendor rule appended if absent (all layouts).
Git hooks are (re)installed via core.hooksPath (all layouts).
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from jb_kit_turbo import (  # sibling module in bin/lib/
    blank_debug_history,
    blank_modification_log,
    is_own_delivery_history,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Root-level IDE/config items to sync (files or directories), outside .sfk/.
EXTRA_CONFIG_ITEMS: list[str] = [".clauderules", "CLAUDE.md", ".windsurfrules", ".gitignore", ".cursor"]

# Framework-owned memory items — always synced to latest.
EXTRA_MEMORY_ITEMS: list[str] = [
    "WORKFLOW_MEMORY_PLAYBOOK.md",
    "logs/SESSION-AUDIT-CHECKLIST.md",
]

# Clean blueprint templates added only when MISSING — never overwritten.
# (source relative to _blueprint/, destination relative to target/)
BLUEPRINT_NEW_ONLY_ITEMS: list[tuple[str, str]] = [
    ("memory/progress.md",           "memory/progress.md"),
    ("memory/logs/DRIFT-RULES.md",   "memory/logs/DRIFT-RULES.md"),
    ("memory/logs/BUILD-HISTORY.md", "memory/logs/BUILD-HISTORY.md"),
]

# Deprecated files — reported to the user, never deleted automatically.
# Keys are paths relative to the target project (current-layout aware).
DEPRECATED_FILES: dict[str, str] = {
    ".sfk/kernel/AUDIT_CHECKLIST.md":  "moved to memory/logs/SESSION-AUDIT-CHECKLIST.md",
    ".sfk/kernel/AUDITOR_MODE.md":     "merged into memory/logs/SESSION-AUDIT-CHECKLIST.md",
    ".sfk/kernel/DRIFT_RULES.md":      "moved to memory/logs/DRIFT-RULES.md",
    ".sfk/kernel/SKILLS_MANIFEST.md":  "replaced by .sfk/kernel/ARCHITECTURE.md",
    ".sfk/kernel/RULES-TEMPLATE.md":   "removed in v1.1.0",
    "docs/evolutive_changes/EVOLUTION_MEMORY.md":
        "removed — fold its content into memory/MODIFICATION_LOG.md (tag ##evolution)",
    "docs/config/INTEGRATIONS.md":
        "replaced by sfk.toml [[integrations]] + docs/integrations/<service>.md",
    "docs/config/DEPLOY_ENV_REFERENCE.md":
        "replaced by sfk.toml [hosting.*]/[environments.*] + docs/deploy/",
}

# Post-migration guidance printed once after a legacy migration.
MIGRATION_NOTES: list[str] = [
    "Config moved to root: fill/keep `sfk.toml` and `SYSTEM.md` there (not under .sfk/).",
    "Add a Resume Panel block to memory/progress.md (see _blueprint template) for fast returns.",
    "If docs/evolutive_changes/EVOLUTION_MEMORY.md exists, fold it into MODIFICATION_LOG (##evolution) and delete it.",
    "Move any docs/config integration/deploy notes into docs/integrations/ and docs/deploy/.",
    "Run your first AI session so it re-reads .sfk/kernel/BOOTSTRAP.md under the new layout.",
]

IGNORE_NAMES: set[str] = {
    ".git", ".idea", ".vscode", ".shared", "_blueprint",
    "__pycache__", "node_modules", ".next", "dist", "build",
}
IGNORE_SUFFIXES: set[str] = {".pyc", ".pyo", ".tmp"}

GITATTRIBUTES_RULE = "/.sfk/** linguist-vendored"
HOOKS_PATH = ".sfk/kernel/hooks"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class SyncItem(NamedTuple):
    src: Path
    dst: Path
    is_new: bool
    content_changed: bool
    is_first_time: bool = False  # new-only template added because it was missing


class Move(NamedTuple):
    src: Path
    dst: Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def should_ignore(path: Path) -> bool:
    return path.name in IGNORE_NAMES or path.suffix.lower() in IGNORE_SUFFIXES


def collect_dir_files(src_dir: Path) -> list[tuple[Path, Path]]:
    """Recursively collect files under src_dir as (abs_src, rel_from_src_dir)."""
    return [
        (f, f.relative_to(src_dir))
        for f in src_dir.rglob("*")
        if f.is_file() and not should_ignore(f)
    ]


def detect_layout(target: Path) -> str:
    if (target / ".sfk" / "kernel" / "BOOTSTRAP.md").exists():
        return "current"
    if (target / "kernel" / "BOOTSTRAP.md").exists():
        return "legacy"
    return "none"


def read_manifest(sfk_root: Path) -> list[str]:
    """Return engine-owned path entries from .sfk/MANIFEST (files and dirs)."""
    manifest = sfk_root / ".sfk" / "MANIFEST"
    entries: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.append(line)
    return entries


# ---------------------------------------------------------------------------
# Migration (legacy -> current)
# ---------------------------------------------------------------------------

def plan_migration(target: Path) -> list[Move]:
    moves: list[Move] = []
    if (target / "kernel").exists() and not (target / ".sfk" / "kernel").exists():
        moves.append(Move(target / "kernel", target / ".sfk" / "kernel"))
    # After the kernel move, config lands under .sfk/kernel/ — promote to root.
    if not (target / "sfk.toml").exists():
        moves.append(Move(target / ".sfk" / "kernel" / "project.toml", target / "sfk.toml"))
    if not (target / "SYSTEM.md").exists():
        moves.append(Move(target / ".sfk" / "kernel" / "SYSTEM.md", target / "SYSTEM.md"))
    return moves


def apply_migration(moves: list[Move], target: Path) -> None:
    for mv in moves:
        # kernel dir move happens first; config sources exist only afterwards.
        if not mv.src.exists():
            continue
        mv.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(mv.src), str(mv.dst))


def backup_target(target: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = target.parent / f"{target.name}-sfk-backup-{ts}.tar.gz"

    def _filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
        parts = set(Path(info.name).parts)
        if parts & IGNORE_NAMES - {"_blueprint"}:  # keep engine, drop heavy/vcs dirs
            return None
        return info

    with tarfile.open(archive, "w:gz") as tar:
        tar.add(target, arcname=target.name, filter=_filter)
    return archive


# ---------------------------------------------------------------------------
# Sync plan
# ---------------------------------------------------------------------------

def _diff_item(src: Path, dst: Path, first_time: bool = False) -> SyncItem | None:
    is_new = not dst.exists()
    changed = False if is_new else not filecmp.cmp(src, dst, shallow=False)
    if is_new or changed:
        return SyncItem(src, dst, is_new, changed, is_first_time=first_time)
    return None


def build_manifest_items(sfk_root: Path, target: Path) -> list[SyncItem]:
    """Engine files/dirs, driven by `.sfk/MANIFEST` (always latest)."""
    items: list[SyncItem] = []
    for entry in read_manifest(sfk_root):
        src = sfk_root / entry
        dst = target / entry
        if entry.endswith("/"):
            if not src.exists():
                continue
            for f, rel in collect_dir_files(src):
                item = _diff_item(f, dst / rel)
                if item:
                    items.append(item)
        else:
            if src.exists():
                item = _diff_item(src, dst)
                if item:
                    items.append(item)
    return items


def collect_new_only(src_dir: Path, dst_dir: Path, skip=None) -> list[SyncItem]:
    """Per-file additive copy: only files missing at the destination, never a diff/overwrite."""
    items: list[SyncItem] = []
    for f, rel in collect_dir_files(src_dir):
        if skip and skip(f.name):
            continue
        dst = dst_dir / rel
        if not dst.exists():
            items.append(SyncItem(f, dst, True, False, is_first_time=True))
    return items


def build_sync_plan(sfk_root: Path, target: Path) -> list[SyncItem]:
    items: list[SyncItem] = build_manifest_items(sfk_root, target)

    # 2. Root-level IDE/config items.
    for name in EXTRA_CONFIG_ITEMS:
        src_item = sfk_root / name
        dst_item = target / name
        if not src_item.exists():
            continue
        if src_item.is_file():
            item = _diff_item(src_item, dst_item)
            if item:
                items.append(item)
        else:
            for f, rel in collect_dir_files(src_item):
                item = _diff_item(f, dst_item / rel)
                if item:
                    items.append(item)

    # 3. Framework-owned memory items (always latest).
    for name in EXTRA_MEMORY_ITEMS:
        src_item = sfk_root / "memory" / name
        if src_item.exists():
            item = _diff_item(src_item, target / "memory" / name)
            if item:
                items.append(item)

    # 4. Clean blueprint templates — added only when missing.
    blueprint = sfk_root / "_blueprint"
    if blueprint.exists():
        for src_rel, dst_rel in BLUEPRINT_NEW_ONLY_ITEMS:
            src_item = blueprint / src_rel
            dst_item = target / dst_rel
            if src_item.exists() and not dst_item.exists():
                items.append(SyncItem(src_item, dst_item, True, False, is_first_time=True))

    return items


# Root-level dirs whose already-blank templates are safe to copy verbatim from the
# SFK repo (unlike memory/MODIFICATION_LOG.md / DEBUG-HISTORY.md, nothing here holds
# this repo's own real project history).
BOOTSTRAP_TEMPLATE_DIRS: list[str] = [
    "docs/project", "docs/integrations", "docs/deploy",
    "db/migrations", "db/seeds",
]

BOOTSTRAP_NOTES: list[str] = [
    "First-time install: sfk.toml and SYSTEM.md were added as blank templates — fill them in before the first AI session.",
    "memory/MODIFICATION_LOG.md and memory/logs/DEBUG-HISTORY.md start blank — nothing from your project's history was touched.",
    "Files that already existed in your project were never overwritten — only missing SFK files were added.",
    "Run your first AI session so it re-reads .sfk/kernel/BOOTSTRAP.md under the new layout.",
]


def build_bootstrap_items(sfk_root: Path, target: Path) -> list[SyncItem]:
    """Layout NONE plan: install SFK into an existing project. Strictly additive —
    every item here is skipped if the destination already exists."""
    items: list[SyncItem] = build_manifest_items(sfk_root, target)

    # Root config — doesn't exist yet for a "none" project.
    sfk_toml_src = sfk_root / "sfk.toml"
    if sfk_toml_src.exists() and not (target / "sfk.toml").exists():
        items.append(SyncItem(sfk_toml_src, target / "sfk.toml", True, False, is_first_time=True))
    system_md_src = sfk_root / "_blueprint" / "SYSTEM.md"
    if system_md_src.exists() and not (target / "SYSTEM.md").exists():
        items.append(SyncItem(system_md_src, target / "SYSTEM.md", True, False, is_first_time=True))

    # Root-level IDE/config items — new-only here (unlike CURRENT/LEGACY sync above,
    # a first bootstrap must never clobber a .gitignore/CLAUDE.md the project already has).
    for name in EXTRA_CONFIG_ITEMS:
        src_item = sfk_root / name
        if not src_item.exists():
            continue
        if src_item.is_file():
            dst_item = target / name
            if not dst_item.exists():
                items.append(SyncItem(src_item, dst_item, True, False, is_first_time=True))
        else:
            items += collect_new_only(src_item, target / name)

    # Framework-owned memory items (WORKFLOW_MEMORY_PLAYBOOK.md, SESSION-AUDIT-CHECKLIST.md).
    for name in EXTRA_MEMORY_ITEMS:
        src_item = sfk_root / "memory" / name
        if src_item.exists() and not (target / "memory" / name).exists():
            items.append(SyncItem(src_item, target / "memory" / name, True, False, is_first_time=True))

    # Blank blueprint templates (progress.md, DRIFT-RULES.md, BUILD-HISTORY.md).
    blueprint = sfk_root / "_blueprint"
    if blueprint.exists():
        for src_rel, dst_rel in BLUEPRINT_NEW_ONLY_ITEMS:
            src_item = blueprint / src_rel
            dst_item = target / dst_rel
            if src_item.exists() and not dst_item.exists():
                items.append(SyncItem(src_item, dst_item, True, False, is_first_time=True))

    # docs/, db/ — already-blank templates in this repo, safe direct copy.
    for rel_dir in BOOTSTRAP_TEMPLATE_DIRS:
        src_dir = sfk_root / rel_dir
        if src_dir.exists():
            items += collect_new_only(src_dir, target / rel_dir)

    # memory/plans, memory/decisions — template files only, never this repo's real
    # delivered plans/decisions.
    for rel_dir in ("memory/plans", "memory/decisions"):
        src_dir = sfk_root / rel_dir
        if src_dir.exists():
            items += collect_new_only(src_dir, target / rel_dir, skip=is_own_delivery_history)

    # memory/*-DESCRIPTION.md at root — template only (PR-XXXX-DESCRIPTION.md).
    for f in sorted(sfk_root.glob("memory/*-DESCRIPTION.md")):
        if is_own_delivery_history(f.name):
            continue
        dst = target / "memory" / f.name
        if not dst.exists():
            items.append(SyncItem(f, dst, True, False, is_first_time=True))

    return items


def build_bootstrap_generated_content(target: Path) -> list[tuple[Path, str]]:
    """Files that must NOT be copied verbatim from this repo (they hold this repo's
    own real history) — generated blank instead, new-only."""
    today = datetime.now().strftime("%Y-%m-%d")
    pairs: list[tuple[Path, str]] = []
    mod_log = target / "memory" / "MODIFICATION_LOG.md"
    if not mod_log.exists():
        pairs.append((mod_log, blank_modification_log(today)))
    debug_hist = target / "memory" / "logs" / "DEBUG-HISTORY.md"
    if not debug_hist.exists():
        pairs.append((debug_hist, blank_debug_history()))
    return pairs


def apply_generated(pairs: list[tuple[Path, str]]) -> int:
    for dst, content in pairs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
    return len(pairs)


def find_deprecated_files(target: Path) -> dict[Path, str]:
    found: dict[Path, str] = {}
    for rel, reason in DEPRECATED_FILES.items():
        path = target / rel
        if path.exists():
            found[path] = reason
    return found


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_sync(items: list[SyncItem]) -> int:
    for item in items:
        item.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item.src, item.dst)
    return len(items)


def ensure_gitattributes(target: Path, dry_run: bool) -> str | None:
    """Ensure the .sfk vendor rule is present. Returns a human note or None."""
    ga = target / ".gitattributes"
    if ga.exists():
        if GITATTRIBUTES_RULE in ga.read_text(encoding="utf-8"):
            return None
        if not dry_run:
            with ga.open("a", encoding="utf-8") as fh:
                fh.write(f"\n{GITATTRIBUTES_RULE}\n")
        return "appended .sfk vendor rule to existing .gitattributes"
    if not dry_run:
        ga.write_text(f"{GITATTRIBUTES_RULE}\n", encoding="utf-8")
    return "created .gitattributes with .sfk vendor rule"


def install_hooks(target: Path, dry_run: bool) -> str | None:
    hook = target / HOOKS_PATH / "pre-commit"
    if not hook.exists():
        return None
    if not dry_run:
        hook.chmod(0o755)
        subprocess.run(
            ["git", "config", "core.hooksPath", HOOKS_PATH],
            cwd=target, check=False,
        )
    return f"pre-commit hook enabled (core.hooksPath = {HOOKS_PATH})"


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_plan(items: list[SyncItem], target: Path) -> None:
    if not items:
        print("  (engine already up to date)")
        return
    regular = [i for i in items if not i.is_first_time]
    first_time = [i for i in items if i.is_first_time]
    new_files = [i for i in regular if i.is_new]
    changed = [i for i in regular if not i.is_new]

    if new_files:
        print(f"\n  NEW ({len(new_files)}):")
        for i in new_files:
            print(f"    + {i.dst.relative_to(target)}")
    if changed:
        print(f"\n  UPDATED ({len(changed)}):")
        for i in changed:
            print(f"    ~ {i.dst.relative_to(target)}")
    if first_time:
        print(f"\n  FIRST-TIME (added only because missing) ({len(first_time)}):")
        for i in first_time:
            print(f"    + {i.dst.relative_to(target)}")


def print_deprecated(deprecated: dict[Path, str], target: Path) -> None:
    if not deprecated:
        return
    print(f"\n  DEPRECATED ({len(deprecated)} — manual cleanup recommended):")
    for path, reason in deprecated.items():
        print(f"    ! {path.relative_to(target)}\n        {reason}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update/migrate an existing SFK project to the latest engine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("target", help="Path to the existing SFK project directory.")
    parser.add_argument("--yes", "-y", action="store_true", help="Apply without confirmation.")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview only; write nothing.")
    parser.add_argument("--no-backup", action="store_true", help="Skip the pre-migration backup archive.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sfk_root = Path(__file__).resolve().parents[2]
    target = Path(args.target).resolve()

    print(f"\nSFK — Update Project\n  Template : {sfk_root}\n  Target   : {target}\n")

    layout = detect_layout(target)
    bootstrap = layout == "none"

    migration = plan_migration(target) if layout == "legacy" else []

    if layout == "legacy":
        print("Detected LEGACY layout — migration required:")
        for mv in migration:
            print(f"    {mv.src.relative_to(target)}  ->  {mv.dst.relative_to(target)}")
    elif layout == "current":
        print("Detected CURRENT layout (.sfk/).")
    else:
        print(
            "Detected NONE layout — first-time install (bootstrap).\n"
            "  Nothing pre-existing in the target is overwritten; only missing SFK files are added."
        )

    # Migration is destructive-ish (moves): confirm and back up before doing it.
    if migration:
        if args.dry_run:
            print("\n[dry-run] Migration moves shown above would run first.")
        else:
            if not args.yes:
                ans = input("\nMigrate this project to the .sfk/ layout? [y/N] ").strip().lower()
                if ans not in {"y", "yes", "s", "sim"}:
                    print("Cancelled.")
                    return 0
            if not args.no_backup:
                print("Creating backup archive...")
                archive = backup_target(target)
                print(f"  backup: {archive}")
            apply_migration(migration, target)
            print("  migration applied.")

    # After migration the target is in current layout; build the sync plan.
    build_target = target
    if migration and args.dry_run:
        # Cannot really inspect post-migration files without moving; report engine
        # additions conceptually. We still diff against current (pre-move) paths that
        # exist, so at minimum new engine files (.sfk/VERSION, OPERATING_CARD, hooks)
        # will show as NEW.
        pass

    print("\nScanning engine for changes...")
    if bootstrap:
        items = build_bootstrap_items(sfk_root, build_target)
        generated = build_bootstrap_generated_content(build_target)
    else:
        items = build_sync_plan(sfk_root, build_target)
        generated = []
    deprecated = find_deprecated_files(build_target)

    print_plan(items, build_target)
    if generated:
        print(f"\n  GENERATED (blank starter, not copied from this repo) ({len(generated)}):")
        for dst, _ in generated:
            print(f"    + {dst.relative_to(build_target)}")
    print_deprecated(deprecated, build_target)

    if args.dry_run:
        # Preview .gitattributes/hook actions without applying.
        ga_note = ensure_gitattributes(build_target, dry_run=True)
        hook_note = install_hooks(build_target, dry_run=True)
        for note in (ga_note, hook_note):
            if note:
                print(f"  · {note}")
        print("\n[dry-run] No files were written.")
        return 0

    if not items and not generated and not deprecated and not migration:
        print("\nNothing to do — project is already current.")
        return 0

    if (items or generated) and not args.yes:
        ans = input("\nApply engine sync? [y/N] ").strip().lower()
        if ans not in {"y", "yes", "s", "sim"}:
            print("Cancelled (migration, if any, was already applied).")
            return 0

    applied = apply_sync(items) if items else 0
    applied += apply_generated(generated) if generated else 0
    ga_note = ensure_gitattributes(build_target, dry_run=False)
    hook_note = install_hooks(build_target, dry_run=False)

    print(f"\n✅  {applied} engine file(s) synced.")
    for note in (ga_note, hook_note):
        if note:
            print(f"    · {note}")
    if bootstrap:
        print("    Never overwritten: any file that already existed in your project.")
    else:
        print("    Never touched: sfk.toml, SYSTEM.md, .sfk/kernel/mcp_config.json, memory/, docs/, db/")

    if bootstrap:
        print("\n📌  Bootstrap notes:")
        for note in BOOTSTRAP_NOTES:
            print(f"    - {note}")

    if migration:
        print("\n📌  Post-migration notes:")
        for note in MIGRATION_NOTES:
            print(f"    - {note}")

    if deprecated:
        print("\n⚠️   Deprecated files found — review and delete manually:")
        for path, reason in deprecated.items():
            print(f"      {path.relative_to(build_target)}  ({reason})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
