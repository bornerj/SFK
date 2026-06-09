#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SFK -- Structured Framework Kit
================================
Update an existing project with the latest SFK kernel files.

Usage:
    python sfk_updater.py <target> [--yes] [--dry-run]

What is updated:
  - All .md files inside kernel/
  - kernel/scripts/    (all scripts)
  - kernel/agents/     (all agent definitions)
  - kernel/skills/     (all skills)
  - kernel/workflows/  (all workflows)
  - kernel/index.toml
  - memory/WORKFLOW_MEMORY_PLAYBOOK.md
  - memory/logs/SESSION-AUDIT-CHECKLIST.md  (framework-owned, always latest)
  - Root config files: .clauderules, CLAUDE.md, .windsurfrules, .gitignore, .cursor/

What is added only when MISSING (never overwrites existing content):
  - kernel/project.toml          (blank template — fill in your project identity)
  - memory/progress.md           (blank template)
  - memory/logs/DRIFT-RULES.md   (blank template — add project-specific rules)
  - memory/logs/BUILD-HISTORY.md (blank template)

What is NEVER touched:
  - kernel/project.toml      (if already present — filled by the user)
  - kernel/SYSTEM.md         (filled by the user)
  - kernel/mcp_config.json   (filled by the user)
  - memory/                  (operational memory, except framework-owned items above)
  - docs/                    (product documentation)

Deprecated files detected (reported, never deleted automatically):
  - kernel/AUDIT_CHECKLIST.md    → moved to memory/logs/SESSION-AUDIT-CHECKLIST.md
  - kernel/AUDITOR_MODE.md       → merged into SESSION-AUDIT-CHECKLIST
  - kernel/DRIFT_RULES.md        → moved to memory/logs/DRIFT-RULES.md
  - kernel/SKILLS_MANIFEST.md    → replaced by kernel/ARCHITECTURE.md
  - kernel/RULES-TEMPLATE.md     → removed in v1.1.0
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Files inside kernel/ that belong to the user — never overwrite
PROTECTED_KERNEL_FILES: set[str] = {
    "project.toml",
    "SYSTEM.md",
    "mcp_config.json",
}

# kernel/ sub-directories that are fully synced by adding/updating source files
KERNEL_SYNC_DIRS: list[str] = ["scripts", "agents", "skills", "workflows"]

# Root-level extra config items to sync (files or directories)
EXTRA_CONFIG_ITEMS: list[str] = [".clauderules", "CLAUDE.md", ".windsurfrules", ".gitignore", ".cursor"]

# Memory items that belong to the framework and are always synced to latest
EXTRA_MEMORY_ITEMS: list[str] = [
    "WORKFLOW_MEMORY_PLAYBOOK.md",
    "logs/SESSION-AUDIT-CHECKLIST.md",
]

# Memory/kernel items added from _blueprint/ only when MISSING — never overwritten
# These use the clean blueprint templates, not SFK's own filled-in versions
BLUEPRINT_NEW_ONLY_ITEMS: list[tuple[str, str]] = [
    # (source relative to _blueprint/, destination relative to target/)
    ("memory/progress.md",           "memory/progress.md"),
    ("memory/logs/DRIFT-RULES.md",   "memory/logs/DRIFT-RULES.md"),
    ("memory/logs/BUILD-HISTORY.md", "memory/logs/BUILD-HISTORY.md"),
]

# kernel/project.toml: add from SFK template if missing; skip if exists (user-owned)
KERNEL_NEW_ONLY_CONFIGS: list[str] = ["project.toml"]

# Deprecated kernel files — reported to the user but never deleted automatically
DEPRECATED_KERNEL_FILES: dict[str, str] = {
    "AUDIT_CHECKLIST.md":   "moved to memory/logs/SESSION-AUDIT-CHECKLIST.md (v1.1.0)",
    "AUDITOR_MODE.md":      "merged into memory/logs/SESSION-AUDIT-CHECKLIST.md (v1.1.0)",
    "DRIFT_RULES.md":       "moved to memory/logs/DRIFT-RULES.md (v1.1.0)",
    "SKILLS_MANIFEST.md":   "replaced by kernel/ARCHITECTURE.md (v1.1.0)",
    "RULES-TEMPLATE.md":    "removed in v1.1.0",
    "OLD_RULES_deprecated.md": "legacy file — safe to delete",
}

# Directories inside the target project that are NEVER touched by the main sync
SKIP_TARGET_DIRS: set[str] = {"memory", "docs", ".git"}

# Ignore patterns when walking source trees
IGNORE_NAMES: set[str] = {
    ".git", ".idea", ".vscode", ".shared", "_blueprint",
    "__pycache__", "node_modules", ".next", "dist", "build",
}
IGNORE_SUFFIXES: set[str] = {".pyc", ".pyo", ".tmp"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class SyncItem(NamedTuple):
    src: Path
    dst: Path
    is_new: bool
    content_changed: bool
    is_first_time: bool = False  # True for new-only items on old projects


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def should_ignore(path: Path) -> bool:
    if path.name in IGNORE_NAMES:
        return True
    if path.suffix.lower() in IGNORE_SUFFIXES:
        return True
    return False


def collect_kernel_md_files(kernel_src: Path) -> list[tuple[Path, Path]]:
    """Return (src, rel_to_kernel) pairs for every .md file directly in kernel/."""
    pairs: list[tuple[Path, Path]] = []
    for f in kernel_src.iterdir():
        if f.is_file() and f.suffix.lower() == ".md" and not should_ignore(f):
            pairs.append((f, Path(f.name)))
    return pairs


def collect_dir_files(src_dir: Path) -> list[tuple[Path, Path]]:
    """Recursively collect all files under src_dir as (abs_src, rel_from_src_dir)."""
    pairs: list[tuple[Path, Path]] = []
    for f in src_dir.rglob("*"):
        if f.is_file() and not should_ignore(f):
            pairs.append((f, f.relative_to(src_dir)))
    return pairs


def build_sync_plan(sfk_root: Path, target: Path) -> list[SyncItem]:
    """Compare source files against target and return the full sync plan."""
    items: list[SyncItem] = []
    kernel_src = sfk_root / "kernel"
    kernel_dst = target / "kernel"
    blueprint = sfk_root / "_blueprint"

    # 1. Kernel .md files (top-level only, skip protected)
    for src, rel in collect_kernel_md_files(kernel_src):
        if rel.name in PROTECTED_KERNEL_FILES:
            continue
        dst = kernel_dst / rel
        is_new = not dst.exists()
        changed = False if is_new else not filecmp.cmp(src, dst, shallow=False)
        if is_new or changed:
            items.append(SyncItem(src, dst, is_new, changed))

    # 2. kernel/index.toml
    toml_src = kernel_src / "index.toml"
    toml_dst = kernel_dst / "index.toml"
    if toml_src.exists():
        is_new = not toml_dst.exists()
        changed = False if is_new else not filecmp.cmp(toml_src, toml_dst, shallow=False)
        if is_new or changed:
            items.append(SyncItem(toml_src, toml_dst, is_new, changed))

    # 3. Selected kernel directories (add/update all source files)
    for rel_dir in KERNEL_SYNC_DIRS:
        src_dir = kernel_src / rel_dir
        dst_dir = kernel_dst / rel_dir
        if not src_dir.exists():
            continue
        for src, rel in collect_dir_files(src_dir):
            dst = dst_dir / rel
            is_new = not dst.exists()
            changed = False if is_new else not filecmp.cmp(src, dst, shallow=False)
            if is_new or changed:
                items.append(SyncItem(src, dst, is_new, changed))

    # 4. Root-level config items
    for item_name in EXTRA_CONFIG_ITEMS:
        src_item = sfk_root / item_name
        dst_item = target / item_name
        if not src_item.exists():
            continue
        if src_item.is_file():
            is_new = not dst_item.exists()
            changed = False if is_new else not filecmp.cmp(src_item, dst_item, shallow=False)
            if is_new or changed:
                items.append(SyncItem(src_item, dst_item, is_new, changed))
        elif src_item.is_dir():
            for src, rel in collect_dir_files(src_item):
                dst = dst_item / rel
                is_new = not dst.exists()
                changed = False if is_new else not filecmp.cmp(src, dst, shallow=False)
                if is_new or changed:
                    items.append(SyncItem(src, dst, is_new, changed))

    # 5. Framework-owned memory items (always synced to latest)
    memory_src = sfk_root / "memory"
    memory_dst = target / "memory"
    for item_name in EXTRA_MEMORY_ITEMS:
        src_item = memory_src / item_name
        dst_item = memory_dst / item_name
        if not src_item.exists():
            continue
        is_new = not dst_item.exists()
        changed = False if is_new else not filecmp.cmp(src_item, dst_item, shallow=False)
        if is_new or changed:
            items.append(SyncItem(src_item, dst_item, is_new, changed))

    # 6. kernel/project.toml — add from template if missing; skip if present (user-owned)
    for config_name in KERNEL_NEW_ONLY_CONFIGS:
        src_item = kernel_src / config_name
        dst_item = kernel_dst / config_name
        if src_item.exists() and not dst_item.exists():
            items.append(SyncItem(src_item, dst_item, is_new=True, content_changed=False, is_first_time=True))

    # 7. Blueprint new-only items — add clean templates if missing; never overwrite
    if blueprint.exists():
        for src_rel, dst_rel in BLUEPRINT_NEW_ONLY_ITEMS:
            src_item = blueprint / src_rel
            dst_item = target / dst_rel
            if src_item.exists() and not dst_item.exists():
                items.append(SyncItem(src_item, dst_item, is_new=True, content_changed=False, is_first_time=True))

    return items


def find_deprecated_files(target: Path) -> dict[Path, str]:
    """Return deprecated kernel files found in the target project."""
    kernel_dst = target / "kernel"
    found: dict[Path, str] = {}
    for name, reason in DEPRECATED_KERNEL_FILES.items():
        path = kernel_dst / name
        if path.exists():
            found[path] = reason
    return found


def print_plan(items: list[SyncItem], sfk_root: Path, target: Path) -> None:
    if not items:
        print("  (nothing to update — project is already up to date)")
        return

    regular = [i for i in items if not i.is_first_time]
    first_time = [i for i in items if i.is_first_time]

    new_files = [i for i in regular if i.is_new]
    changed_files = [i for i in regular if not i.is_new]

    if new_files:
        print(f"\n  NEW ({len(new_files)} files):")
        for item in new_files:
            print(f"    + {item.dst.relative_to(target)}")
    if changed_files:
        print(f"\n  UPDATED ({len(changed_files)} files):")
        for item in changed_files:
            print(f"    ~ {item.dst.relative_to(target)}")
    if first_time:
        print(f"\n  FIRST-TIME SETUP ({len(first_time)} files — added only because missing):")
        for item in first_time:
            note = "  ← fill in your project identity" if "project.toml" in str(item.dst) else ""
            print(f"    + {item.dst.relative_to(target)}{note}")


def print_deprecated_warning(deprecated: dict[Path, str], target: Path) -> None:
    if not deprecated:
        return
    print(f"\n  DEPRECATED ({len(deprecated)} files — manual cleanup recommended):")
    for path, reason in deprecated.items():
        print(f"    ! {path.relative_to(target)}")
        print(f"        {reason}")


def apply_sync(items: list[SyncItem]) -> int:
    applied = 0
    for item in items:
        item.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item.src, item.dst)
        applied += 1
    return applied


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_sfk_project(target: Path) -> None:
    """Raise if the target doesn't look like an SFK-scaffolded project."""
    sentinel = target / "kernel" / "BOOTSTRAP.md"
    if not sentinel.exists():
        raise RuntimeError(
            f"'{target}' does not appear to be an SFK project "
            f"(missing kernel/BOOTSTRAP.md). "
            f"Use new-project to create a project first."
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update an existing SFK project with the latest kernel files from this template.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        help="Path to the existing SFK project directory to update.",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt and apply changes immediately.",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be changed without writing anything.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sfk_root = Path(__file__).resolve().parents[1]
    target = Path(args.target).resolve()

    print()
    print("SFK — Update Project")
    print(f"  Template : {sfk_root}")
    print(f"  Target   : {target}")
    print()

    try:
        validate_sfk_project(target)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Build plan
    print("Scanning for changes...")
    items = build_sync_plan(sfk_root, target)
    deprecated = find_deprecated_files(target)

    # Show plan
    print_plan(items, sfk_root, target)
    print_deprecated_warning(deprecated, target)

    if not items and not deprecated:
        return 0

    if args.dry_run:
        print("\n[dry-run] No files were written.")
        return 0

    if not items:
        print("\nNothing to update. Review the deprecated files above and delete them manually.")
        return 0

    # Confirm
    if not args.yes:
        print()
        answer = input("Apply these changes? [y/N] ").strip().lower()
        if answer not in {"y", "yes", "s", "sim"}:
            print("Cancelled.")
            return 0

    # Apply
    applied = apply_sync(items)
    print(f"\n✅  {applied} file(s) updated successfully.")
    print("   Protected (skipped): kernel/project.toml (if present), kernel/SYSTEM.md, kernel/mcp_config.json")
    print("   Skipped dirs       : memory/ (except framework-owned items), docs/")

    if deprecated:
        print()
        print("⚠️   Deprecated files found — review and delete manually:")
        for path, reason in deprecated.items():
            print(f"      {path.relative_to(target)}  ({reason})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
