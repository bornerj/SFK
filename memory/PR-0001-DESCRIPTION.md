# Version reusable memory templates and publication rules

## Objective

Version the reusable memory templates in the repository and align the kernel publication flow so SFK can be used more clearly as a development framework.

## What Was Done

### Product and Flow

- turned the old project-specific memory examples into reusable templates for PR descriptions, plans, and decisions
- made framework memory and project docs versionable so GitHub users can consume the templates directly from the repository
- aligned the publication flow so publishable deliveries require a PR description artifact

### Technical

- updated `.gitignore` to stop excluding framework templates under `memory/` and `docs/project/`
- extended `kernel/BOOTSTRAP.md`, `kernel/RULES.md`, `kernel/SOUL.md`, and `kernel/index.toml` with publication and new-project classification rules
- normalized the new memory artifacts and changelog/progress entries to English

### Memory and Governance

- added reusable templates:
  - `memory/PR-XXXX-DESCRIPTION.md`
  - `memory/plans/PLAN-XXXX-DONE-subject.md`
  - `memory/decisions/DECISION-XXX.md`
- updated `memory/MODIFICATION_LOG.md` and `memory/progress.md` to reflect the framework-level changes
- created this publishable PR description artifact for the current delivery

## Main Files

### Code

- `.gitignore`
- `kernel/BOOTSTRAP.md`
- `kernel/RULES.md`
- `kernel/SOUL.md`
- `kernel/index.toml`

### Memory and Documentation

- `memory/MODIFICATION_LOG.md`
- `memory/progress.md`
- `memory/PR-0001-DESCRIPTION.md`
- `memory/PR-XXXX-DESCRIPTION.md`
- `memory/plans/PLAN-XXXX-DONE-subject.md`
- `memory/decisions/DECISION-XXX.md`
- `docs/project/PROJECT_OVERVIEW.md`

## Validation

- reviewed local diff against `origin/main`
- verified `main` and `origin/main` matched before packaging local changes
- verified publishable files and templates were normalized to English

## Notes

- this delivery intentionally versions framework templates that were previously ignored, so the repo can act as a clearer source of truth for GitHub users
- no code tests were run because the change set is documentation and governance focused
