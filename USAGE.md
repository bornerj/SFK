# SFK — Usage Guide (v1.3.0)

**Structured Framework Kit** — a persistent memory and governance layer for
AI-assisted development. AI-agnostic (Claude Code, Cursor, Windsurf, Codex).

This guide answers the six operational questions:
1. [How SFK works now / how to use it](#1-how-sfk-works-now)
2. [Starting a brand-new project](#2-starting-a-brand-new-project)
3. [Adding SFK to an existing project](#3-adding-sfk-to-an-existing-project)
4. [Updating SFK to a new version](#4-updating-sfk-in-a-project)
5. [Updating skills](#5-updating-skills)
6. [Adding a new skill](#6-adding-a-new-skill)

Prefer clicking over typing commands? See [§0 — SFK Launcher (GUI)](#0-prefer-clicking-use-the-sfk-launcher-gui).

---

## 0. Prefer clicking? Use the SFK Launcher (GUI)

`bin/sfk_gui.py` is a **zero-install desktop app** (pure Python standard library —
no `pip install`, nothing beyond Python itself) that wraps §2–§6 below in a
window with buttons and folder-browse dialogs. You never type a path or a flag.

Run it:
```bash
python3 bin/sfk_gui.py
```
Or double-click:
- **Linux/macOS**: `bin/sfk-launcher.sh` — run `bash bin/sfk-launcher.sh --install-desktop`
  once to add "SFK Launcher" to your applications menu.
- **Windows**: `bin/sfk-launcher.bat`

What it offers, one card per action: **criar um projeto novo** (§2), **adicionar o
SFK a um projeto existente** (§3), **atualizar/migrar** (§4), **skills** — importar
ou atualizar (§5–§6), and **checar um projeto** (read-only preview). It is a thin
shell over the exact same scripts described below — same guarantees (dry-run
first, automatic backup before migrating, never touches your product code, apply
requires confirmation) — just with buttons instead of typed commands.

Requires Tkinter, which ships with Python on most systems. If it's missing, the
app prints the exact install command for your OS (e.g. `sudo apt install python3-tk`
on Debian/Ubuntu/Zorin) instead of crashing.

---

## 1. How SFK works now

Since **v1.3.0**, everything lives in one of three clearly separated zones:

| Zone | Location | Who owns it | Ships to projects? |
|------|----------|-------------|--------------------|
| **A. Engine** (framework) | `.sfk/` | SFK — **read-only** | Yes (as `.sfk/`) |
| **B. Project state** | `sfk.toml`, `SYSTEM.md`, `memory/`, `docs/`, `db/` (all at root) | You + AI, per project | Yes (as clean templates) |
| **C. Maintainer tooling** | `bin/` | SFK maintainer | **No** — never |

```
your-project/
├── .sfk/                    ← ENGINE (don't edit; updated by the updater)
│   ├── VERSION  · MANIFEST
│   └── kernel/  (BOOTSTRAP, RULES, SOUL, OPERATING_CARD, index.toml,
│                 agents/, skills/, workflows/, scripts/, hooks/)
├── sfk.toml                 ← project identity, stack, hosting, [[integrations]], [db]
├── SYSTEM.md                ← technical/engineering standards
├── memory/                  ← the project's "brain"
│   ├── progress.md          ← Resume Panel (read first on returning)
│   ├── MODIFICATION_LOG.md  ← chronological change history
│   ├── plans/  decisions/  logs/
├── docs/                    ← project docs (project/, integrations/, deploy/)
├── db/                      ← migrations/  seeds/
└── (your product code)
```

### The session contract
Every AI session begins by reading **`.sfk/kernel/BOOTSTRAP.md`**, which:
1. Classifies the repo as NEW or EXISTING project.
2. Loads Layer 0 (always): `OPERATING_CARD.md` → `SOUL.md` → `RULES.md` → `sfk.toml` → `SYSTEM.md`.
3. Loads Layer 1 selectively by task type (via `index.toml`).
4. Routes the request to the right agent/skill.
5. Returns a readback confirmation.

**To start any session**, open your AI tool in the project folder and send:
```
Read .sfk/kernel/BOOTSTRAP.md and give me your confirmation readback.
```

### What keeps the AI honest (D4)
- **Operating Card** (`.sfk/kernel/OPERATING_CARD.md`) — a ≤20-line digest of the
  non-negotiables, loaded first every session.
- **pre-commit hook** (`.sfk/kernel/hooks/pre-commit`) — **blocks** any commit with a
  significant change (code / product docs / DB migration) unless
  `memory/MODIFICATION_LOG.md` is updated in the same commit. Escape:
  `git commit --no-verify`.

---

## 2. Starting a brand-new project

Use the scaffolder from the SFK repo. It creates a clean project with the engine
installed and project-state files as **empty templates** (SFK's own filled-in data
never leaks in).

```bash
# from inside the SFK repo
bash bin/new-project.sh /path/to/my-new-project --project-name "My App" --init-git
```
- `--init-git` initializes git **and auto-enables the pre-commit hook** (recommended).
- Omit the target to launch an interactive wizard.

Then, in the new project (a `QUICKSTART.md` is generated to walk you through):

1. **Fill `sfk.toml`** — project identity, stack, hosting, `[environments.*]`
   (variable **names** only, never secrets), `[[integrations]]`, `[db]`.
2. **Fill `SYSTEM.md`** — language/stack, code style, error handling, architecture
   (use `.sfk/kernel/SYSTEM-TEMPLATE.md` as a guide).
3. Fill `docs/project/` — `PROJECT_OVERVIEW.md`, `REQUIREMENTS.md`, `SCOPE.md`, `SETUP.md`.
4. If you did **not** use `--init-git`: after `git init`, run
   `bash .sfk/kernel/hooks/install.sh` to enable the hook.
5. Start your first AI session with the BOOTSTRAP command above — the AI detects a
   NEW project and guides the Day-1 onboarding.

---

## 3. Adding SFK to an existing project

You want SFK's engine and memory system layered onto a codebase that already exists.
Use the **updater** — it installs the engine without touching your product code.

```bash
# 1) ALWAYS preview first (writes nothing)
bash bin/update-project.sh /path/to/existing-project --dry-run

# 2) Apply
bash bin/update-project.sh /path/to/existing-project
```

What it does:
- Installs `.sfk/` (engine), `sfk.toml` + `SYSTEM.md` (if missing), the `memory/`,
  `docs/`, `db/` templates (only when missing), IDE config, the `.gitattributes`
  vendor rule, and enables the pre-commit hook.
- **Never touches** your product code, or your existing `sfk.toml`/`SYSTEM.md`/
  `memory/`/`docs/` content.

Then fill in `sfk.toml` and `SYSTEM.md` to describe the existing stack, and run a
first AI session so the AI reads BOOTSTRAP under the new layout.

> The same updater **migrates legacy SFK projects** (old root-`kernel/` layout, pre-1.3.0)
> to the `.sfk/` layout automatically — see §4.

---

## 4. Updating SFK in a project

When a new SFK version ships, pull the latest SFK repo, then point the updater at
your project. It syncs **only engine-owned files** (everything listed in
`.sfk/MANIFEST`); your project state is left alone.

```bash
# preview
bash bin/update-project.sh /path/to/project --dry-run

# apply (prompts for confirmation)
bash bin/update-project.sh /path/to/project

# non-interactive
bash bin/update-project.sh /path/to/project --yes
```

Behavior:
- **Engine files** (kernel, agents, skills, workflows, scripts, hooks, Operating Card,
  VERSION, MANIFEST) → refreshed to the latest version.
- **Never touched**: `sfk.toml`, `SYSTEM.md`, `.sfk/kernel/mcp_config.json`, `memory/`,
  `docs/`, `db/`, product code.
- **Added only when missing**: clean templates (`progress.md`, `DRIFT-RULES.md`,
  `BUILD-HISTORY.md`).
- **Deprecated files** are reported (never auto-deleted).

**Migrating a legacy (pre-1.3.0) project:** if the updater detects the old root-`kernel/`
layout, it automatically migrates it — `kernel/` → `.sfk/kernel/`, `project.toml` →
`sfk.toml`, `SYSTEM.md` → root — after creating a **timestamped `.tar.gz` backup** next
to the project. Use `--no-backup` to skip the backup (not recommended). Always run
`--dry-run` first and, for important repos, test on a copy.

---

## 5. Updating skills

Skills live in `.sfk/kernel/skills/<skill-name>/` and are **engine-owned** — they are
listed in `.sfk/MANIFEST`, so the updater refreshes them to the latest version like any
other engine file.

**To roll out new skill versions to a project**, update the SFK repo's
`.sfk/kernel/skills/` first (see §6 for editing/importing), then run the updater:
```bash
bash bin/update-project.sh /path/to/project        # syncs skills/ to latest
```

**To change a skill's content in the SFK repo itself**, edit its
`.sfk/kernel/skills/<name>/SKILL.md` (and supporting files). Because skills are engine
files, edit them **in the SFK repo** (the source of truth), not inside a scaffolded
project — a project edit would be overwritten on the next update.

> An agent only loads the skills listed in its own `skills:` frontmatter, so after
> adding/renaming a skill, make sure the relevant agent in `.sfk/kernel/agents/`
> references it, and keep `.sfk/kernel/ARCHITECTURE.md` (the inventory) in sync.

---

## 6. Adding a new skill

Use the importer script — it copies a skill folder into the kernel and wires up the
Cursor bridge automatically.

```bash
# from inside the SFK repo (or a project that has .sfk/)
python3 .sfk/kernel/scripts/import_skill.py /path/to/my-skill-folder
# or run with no argument for interactive mode (drag the folder in)
python3 .sfk/kernel/scripts/import_skill.py
```

The folder name becomes the skill name. The importer:
- copies the folder to `.sfk/kernel/skills/<name>/`,
- mirrors `SKILL.md` into `.cursor/rules/<name>.md` (Cursor bridge).

A skill folder should contain a **`SKILL.md`** describing the domain knowledge
(the AI reads it via the referencing agent's frontmatter). After importing:
1. Reference the skill in the relevant agent under `.sfk/kernel/agents/*.md`
   (`skills:` frontmatter) so it actually gets loaded for matching tasks.
2. Add it to the inventory in `.sfk/kernel/ARCHITECTURE.md`.
3. Add it in the **SFK repo** so it propagates to projects via the updater (§5).

`.clauderules` and `.windsurfrules` already point at `.sfk/kernel/skills/`, so
Claude Code and Windsurf pick up new skills automatically.

---

## Quick command reference

| Goal | Command |
|------|---------|
| **Prefer a GUI?** | `python3 bin/sfk_gui.py` (or double-click `bin/sfk-launcher.sh` / `.bat`) |
| New project | `bash bin/new-project.sh <target> --project-name "Name" --init-git` |
| Add SFK to existing project | `bash bin/update-project.sh <target> --dry-run` then without `--dry-run` |
| Update SFK / migrate legacy | `bash bin/update-project.sh <target>` (auto-backs up on migration) |
| Enable hook manually | `bash .sfk/kernel/hooks/install.sh` |
| Import a skill | `python3 .sfk/kernel/scripts/import_skill.py <folder>` |
| Start an AI session | Send: `Read .sfk/kernel/BOOTSTRAP.md and give me your confirmation readback.` |
| Bypass hook once | `git commit --no-verify` |
