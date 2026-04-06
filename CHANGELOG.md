# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [1.1.0] - 2026-04-06

### Changed

#### `kernel/project.toml` - Promoted to Technical Dictionary
- Expanded from identity/stack shorthand to **complete project dictionary**
- New sections: `[hosting.frontend/backend/database]` - multi-server breakdown with URL + provider + service
- New sections: `[stack.runtime/frontend/backend/database/package_manager]` - full stack with versions, separated by layer
- `[design]` expanded: added `framework`, `framework_version`, `build_command`, `component_library`, `icon_library`
- `[environments]` restructured: now `[environments.<platform>]` - env vars grouped by server/platform (Railway, Vercel, etc.)
- New section: `[[integrations]]` - one block per active third-party API (name, purpose, docs, env_vars)
- New section: `[tools.dev.*]` - local dev tools (e.g. ngrok) with purpose, who_calls, setup, note
- Rule established: all answers to "where is this hosted?", "which versions?", "which vars on which server?", "what integrations?" belong here

#### `kernel/TESTING_GUIDE.md` - New (moved + rewritten)
- Moved from `docs/config/TESTING_GUIDE.md` to `kernel/`
- Fully rewritten as **universal testing directives** - no project-specific content
- Covers: test pyramid, environments, seed strategy, mandatory test categories, standard script names, observability
- Stack-specific tooling remains in `kernel/SYSTEM.md`

#### Operational Protocols — Moved to `memory/logs/`
- `kernel/AUDIT_CHECKLIST.md` + `kernel/AUDITOR_MODE.md` → `memory/logs/SESSION-AUDIT-CHECKLIST.md` (merged)
- `kernel/DRIFT_RULES.md` → `memory/logs/DRIFT-RULES.md`
- `kernel/index.toml` updated with `[on_audit]` routing for automated context loading.

### Removed

- `docs/config/` (entire folder) — specific project configs absorbed into `project.toml`.
- `kernel/SKILLS_MANIFEST.md` + `kernel/README_AGENT.md` — redundant info.
- `kernel/RULES-TEMPLATE.md` — out of context; rules are in `RULES.md`.
- `docs/project/*_EXAMPLE.md` — redundant.

### Reset (Clear Templates)

- `docs/project/PROJECT_OVERVIEW.md` — reset to fill-in placeholders.
- `docs/project/REQUIREMENTS.md` — reset to fill-in placeholders.

---

## [1.0.0] - 2026-04-02

### Added

#### Core Kernel
- `kernel/BOOTSTRAP.md` v0.6 - session entry point with LAYER 0/1 loading protocol
- `kernel/RULES.md` - sovereign governance with 16 sections: state machine, RAG+STAR engine, anti-scope-drift, anti-failure checkpoints, memory system, Git dual-approval, Socratic Gate
- `kernel/SOUL.md` - portable AI behavior contract (identity, communication, delivery, restrictions)
- `kernel/project.toml` - project identity, stack, URLs, design tokens and env vars
- `kernel/index.toml` - declarative session router (15 task-type triggers   file mappings)
- `kernel/SYSTEM.md` + `kernel/SYSTEM-TEMPLATE.md` - technical contract and guide
- `kernel/RULES-TEMPLATE.md` - stack-agnostic rules template
- `kernel/AUDIT_CHECKLIST.md` + `kernel/AUDITOR_MODE.md` - session auditing
- `kernel/DRIFT_RULES.md` - scope drift detection rules
- `kernel/SKILLS_MANIFEST.md` - skill index

#### Agents (20)
- `orchestrator`, `project-planner`, `frontend-specialist`, `backend-specialist`
- `database-architect`, `mobile-developer`, `game-developer`, `devops-engineer`
- `security-auditor`, `penetration-tester`, `test-engineer`, `debugger`
- `performance-optimizer`, `seo-specialist`, `documentation-writer`
- `product-manager`, `product-owner`, `qa-automation-engineer`
- `code-archaeologist`, `explorer-agent`

#### Skills (56)
- **Frontend & UI**: `web-design-guidelines`, `tailwind-patterns`, `frontend-design`, `engineering-frontend-developer`, `nextjs-react-expert`, `architect-ux`, `3d-web-experience`, `design-orchestration`, `mobile-design`
- **Backend & API**: `api-patterns`, `engineering-backend-architect`, `nodejs-best-practices`, `python-patterns`, `rust-pro`, `mcp-builder`
- **Database**: `database-design`
- **Cloud & Infra**: `deployment-procedures`, `fullstack-docker-deploy`, `server-management`, `bash-linux`, `powershell-windows`, `supabase-automation`
- **Testing & Quality**: `testing-patterns`, `webapp-testing`, `tdd-workflow`, `code-review-checklist`, `lint-and-validate`, `systematic-debugging`, `systematic-debugging-awesome`, `performance-profiling`, `kaizen`, `ai-governance-audit`
- **Security**: `vulnerability-scanner`, `red-team-tactics`, `ux-legal-review`
- **Architecture & Planning**: `app-builder`, `architecture`, `plan-writing`, `brainstorming`, `intelligent-routing`, `parallel-agents`, `agents-orchestrator`, `behavioral-modes`, `project-manager-senior`
- **Game**: `game-development`
- **SEO & Growth**: `seo-fundamentals`, `geo-fundamentals`
- **Documentation & Strategy**: `documentation-templates`, `technical-writer`, `executive-summary-generator`, `tool-evaluator`
- **Other**: `clean-code`, `i18n-localization`, `legal-domain-modeling`, `rag-chunking-legal`, `nextjs-supabase-auth`

#### Workflows (11)
- `/brainstorm`, `/create`, `/debug`, `/deploy`, `/enhance`
- `/orchestrate`, `/plan`, `/preview`, `/status`, `/test`, `/ui-ux-pro-max`

#### Scripts (5)
- `kernel/scripts/checklist.py` - priority-based validation (Security   Lint   Schema   Tests   UX   SEO)
- `kernel/scripts/verify_all.py` - full verification suite + Lighthouse + Playwright E2E
- `kernel/scripts/auto_preview.py` - start/stop local preview server
- `kernel/scripts/session_manager.py` - project status and stack detection
- `kernel/scripts/import_skill.py" - skill import utility

#### Memory System
- `memory/MODIFICATION_LOG.md` - macro operational log
- `memory/progress.md" - module state snapshot
- `memory/WORKFLOW_MEMORY_PLAYBOOK.md` - complete memory system guide
- `memory/plans/`, `memory/decisions/`, `memory/logs/` - structured persistence directories

#### Tooling & IDE Integration
- `new-project.ps1` + `tools/jb_kit_turbo.py" - project scaffolding wizard (interactive + direct modes)
- `.clauderules` - Claude Code integration
- `.windsurfrules` - Windsurf integration
- `.cursor/rules/` - Cursor integration (56 rule files)

#### Documentation
- `README.md" - public-facing project overview
- `INSTRUCTIONS.md" - full usage guide with 5 practical examples
- `kernel/README.md" - kernel structure and precedence hierarchy
- `kernel/ARCHITECTURE.md" - all agents, skills, workflows and scripts
- `LICENSE` - MIT License
- `CHANGELOG.md" - this file
- `CONTRIBUTING.md" - contribution guidelines
- `.gitignore` - standard ignore rules

---

[1.0.0]: https://github.com/Jeiel/sfk/releases/tag/v1.0.0
