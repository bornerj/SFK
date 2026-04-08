#!/usr/bin/env python3
"""
SFK — Structured Framework Kit
==============================
Scaffold a new project using this repository as a blueprint.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


BLUEPRINT_DIRS = ["kernel", "memory", "docs"]
EXTRA_CONFIG_FILES = [".cursor", ".clauderules", ".windsurfrules", ".gitignore"]

IGNORE_NAMES = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
}
IGNORE_SUFFIXES = {".pyc", ".pyo", ".tmp"}
EXAMPLE_DOCS = {
    Path("docs/project/PROJECT_OVERVIEW_EXAMPLE.md"),
    Path("docs/project/REQUIREMENTS_EXAMPLE.md"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new project skeleton from the SFK blueprint."
    )
    parser.add_argument("target", help="Target directory where the new project will be created.")
    parser.add_argument(
        "--project-name",
        help="Project name for generated starter docs (default: target folder name).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing non-empty target directory.",
    )
    parser.add_argument(
        "--init-git",
        action="store_true",
        help="Run git init in the target directory after scaffolding.",
    )
    parser.add_argument(
        "--keep-examples",
        action="store_true",
        help="Keep *_EXAMPLE.md files under docs/project.",
    )
    return parser.parse_args()


def should_ignore(name: str, full_path: Path) -> bool:
    if name in IGNORE_NAMES:
        return True
    if full_path.suffix.lower() in IGNORE_SUFFIXES:
        return True
    return False


def ignore_filter(current_dir: str, names: list[str]) -> list[str]:
    ignored: list[str] = []
    base = Path(current_dir)
    for name in names:
        full_path = base / name
        if should_ignore(name, full_path):
            ignored.append(name)
    return ignored


def validate_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()) and not force:
        raise RuntimeError(
            f"Target '{target}' is not empty. Use --force to allow writing into it."
        )


def copy_blueprint(template_root: Path, target: Path, force: bool) -> None:
    target.mkdir(parents=True, exist_ok=True)
    
    # Copy core directories
    for rel_dir in BLUEPRINT_DIRS:
        src_dir = template_root / rel_dir
        if not src_dir.exists():
            raise RuntimeError(f"Missing blueprint directory: {src_dir}")
        dst_dir = target / rel_dir
        shutil.copytree(
            src_dir,
            dst_dir,
            ignore=ignore_filter,
            dirs_exist_ok=force,
        )

    # Copy extra config files/dirs if they exist
    for rel_item in EXTRA_CONFIG_FILES:
        src_item = template_root / rel_item
        if src_item.exists():
            dst_item = target / rel_item
            if src_item.is_dir():
                shutil.copytree(
                    src_item,
                    dst_item,
                    ignore=ignore_filter,
                    dirs_exist_ok=force,
                )
            else:
                shutil.copyfile(src_item, dst_item)



def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def reset_starter_docs(target: Path, project_name: str, keep_examples: bool) -> None:
    today = date.today().isoformat()

    overview = f"""# Project Overview

## Summary
- Project: {project_name}
- Created: {today}
- Status: Planning

## Problem Statement
- Define the business problem this product solves.

## Target Users
- Primary users:
- Secondary users:

## Scope
- In scope:
- Out of scope:

## Technical Direction (Initial)
- Frontend:
- Backend:
- Database:
- Infrastructure:

## Milestones
- M1:
- M2:
- M3:
"""

    requirements = f"""# Requirements

Last updated: {today}

## Functional Requirements
- [ ] FR-001:
- [ ] FR-002:
- [ ] FR-003:

## Non-Functional Requirements
- [ ] NFR-001 Performance:
- [ ] NFR-002 Security:
- [ ] NFR-003 Reliability:

## Constraints
- Budget:
- Timeline:
- Integrations:

## Acceptance Criteria
- [ ] AC-001:
- [ ] AC-002:
"""

    modification_log = f"""# Modification Log

Start date: {today}

Use this file for macro operational tracking, according to:
- `kernel/RULES.md`
- `memory/WORKFLOW_MEMORY_PLAYBOOK.md`
"""

    debug_history = """# Debug History

Use semantic IDs:
- ERR-0001
- ERR-0002

Template:
# ID: ERR-000X: Short semantic title
SINTOMA:
CAUSA_RAIZ:
ACAO:
CONTEXTO:
"""

    write_text(target / "docs/project/PROJECT_OVERVIEW.md", overview)
    write_text(target / "docs/project/REQUIREMENTS.md", requirements)
    write_text(target / "memory/MODIFICATION_LOG.md", modification_log)
    write_text(target / "memory/logs/DEBUG-HISTORY.md", debug_history)

    (target / "memory/plans").mkdir(parents=True, exist_ok=True)
    (target / "memory/decisions").mkdir(parents=True, exist_ok=True)

    if not keep_examples:
        for rel in EXAMPLE_DOCS:
            path = target / rel
            if path.exists():
                path.unlink()


def maybe_init_git(target: Path, init_git: bool) -> None:
    if not init_git:
        return
    # Use -b main to ensure modern branch naming standards
    subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True)



def print_next_steps(target: Path) -> None:
    print("")
    print("SFK scaffold created successfully.")
    print(f"Path: {target}")
    print("")
    print("Next steps:")
    print(f"1) cd \"{target}\"")
    print("2) Open your coding assistant in this folder")
    print("3) Start session with: execute kernel/BOOTSTRAP.md")
    print("4) Run: brainstorming -> tool-evaluator -> plan-writing")


def main() -> int:
    args = parse_args()
    template_root = Path(__file__).resolve().parents[1]
    target = Path(args.target).resolve()
    project_name = args.project_name or target.name

    try:
        validate_target(target, args.force)
        copy_blueprint(template_root, target, force=args.force)
        reset_starter_docs(target, project_name, keep_examples=args.keep_examples)
        maybe_init_git(target, args.init_git)
        print_next_steps(target)
        return 0
    except Exception as exc:  # pragma: no cover - CLI top-level handler
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
