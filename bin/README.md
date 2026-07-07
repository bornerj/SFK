# SFK — Scaffolding Tool

Creates a new project from the SFK template, copying:

- `kernel/`
- `memory/`
- `docs/`

## Usage

**Linux/macOS:**
```bash
# Interactive wizard (recommended)
bash new-project.sh

# Direct mode
python tools/jb_kit_turbo.py /path/to/new-project --project-name MyProject --init-git
```

**Windows (PowerShell):**
```powershell
# Interactive wizard (recommended)
.\new-project.ps1

# Direct mode
.\new-project.ps1 "C:\projects\MyProject" -ProjectName "MyProject" -InitGit
```

## Options

| Option | Description |
|---|---|
| `--project-name "Name"` | Name used in generated starter docs |
| `--force` | Allow writing into an existing non-empty directory |
| `--init-git` | Run `git init` in the target directory |
| `--keep-examples` | Keep `*_EXAMPLE.md` files in `docs/project/` |

## What it does

1. Copies `kernel/`, `memory/`, `docs/` to the target directory
2. Generates fresh `PROJECT_OVERVIEW.md` and `REQUIREMENTS.md` with today's date
3. Resets `MODIFICATION_LOG.md` and `DEBUG-HISTORY.md`
4. Creates `memory/plans/` and `memory/decisions/` directories
5. Runs `git init` (if `--init-git` is set)
