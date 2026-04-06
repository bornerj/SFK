# SFK — Structured Framework Kit

> **SFK is a multi-tenant orchestration layer that provides memory, rules, and procedures as a service, decoupling AI intelligence from execution logic.**

---

## What is it

SFK is a project template that turns any AI assistant into a **structured development partner**. It does not depend on any specific AI — it works with Gemini, Claude, ChatGPT, or any model that reads text files.

The core idea: instead of explaining the project rules to the AI in every conversation, SFK encodes those rules into files that the AI reads automatically. The result is an assistant that:

- Knows the project identity, stack, and URLs from the very first prompt
- Knows how to behave, what to ask, and when to stop
- Records decisions, bugs, and changes in persistent memory
- Uses specialist agents and domain skills on demand

---

## How It Works

SFK operates in three layers:

```
┌───────────────────────────────────────────────────────────┐
│  CONTROL AND CAPABILITIES LAYER  (kernel/)                 │
│  project.toml · SOUL.md · RULES.md · index.toml            │
│  BOOTSTRAP.md · ARCHITECTURE.md                            │
│  agents/ · skills/ · workflows/ · rules/ · scripts/        │
└────────────────┬───────────────────────────────────────────┘
                 │ persists to
┌────────────────▼────────────────────┐
│  MEMORY LAYER  (memory/)            │  ← Everything that happened is recorded
│  MODIFICATION_LOG · plans/ · debug  │
│  decisions/ · progress.md           │
└─────────────────────────────────────┘
```

### Session Flow

1. The AI reads `kernel/BOOTSTRAP.md` → loads identity, rules, and behavior (LAYER 0)
2. Consults `kernel/index.toml` → loads only the files relevant to the task type (LAYER 1)
3. Checks `memory/progress.md` → snapshot of the current module state
4. Checks `memory/plans/` → resumes an active plan if any exists
5. Classifies the request → selects agent and skills → executes
6. Records the result in `memory/MODIFICATION_LOG.md` or the active plan

---

## How to Use

### 1. Create a new project from the template

SFK includes a PowerShell script that copies the framework and initializes the project:

```powershell
# Interactive mode (wizard) — recommended for first use
.\new-project.ps1

# Direct mode with parameters
.\new-project.ps1 -Target "C:\projects\my-project" -ProjectName "MyProject" -InitGit
```

**Available parameters:**

| Parameter | Description |
|---|---|
| `-Target` | Destination folder for the new project |
| `-ProjectName` | Project name (default: folder name) |
| `-InitGit` | Automatically runs `git init` |
| `-KeepExamples` | Keeps `*_EXAMPLE.md` files in `docs/project/` |
| `-Force` | Allows writing to a non-empty folder |
| `-Interactive` | Forces wizard mode even with parameters defined |

**What the script does automatically:**
- Copies `.agent/`, `kernel/`, `memory/`, `docs/` to the destination
- Generates `docs/project/PROJECT_OVERVIEW.md` and `REQUIREMENTS.md` with the current date
- Resets `memory/MODIFICATION_LOG.md` and `memory/logs/DEBUG-HISTORY.md`
- Creates `memory/plans/` and `memory/decisions/` folders
- Runs `git init` (if `-InitGit` is active)

### 2. Fill in the project identity

Edit `kernel/project.toml` — the **complete technical dictionary** of your project:

```toml
[project]
name        = "MyProject"
description = "SaaS task management for remote teams"
type        = "web-app"

[hosting.frontend]
provider = "Vercel"
url      = "https://myapp.vercel.app"

[hosting.backend]
provider = "Railway"
url      = "https://api.myapp.up.railway.app"

[stack.frontend]
framework = "Vite + React"
version   = "React 18 / Vite 5"
styling   = "TailwindCSS 3.4.17"

[stack.backend]
framework = "Express"
orm       = "Prisma"
language  = "TypeScript (strict) — Node.js 20+ ESM"

[environments.railway]
vars = ["DATABASE_URL", "JWT_SECRET", "APP_API_URL", "APP_WEB_URL"]

[environments.vercel]
vars = ["VITE_API_URL", "VITE_WEB_URL"]
```

### 3. Define the project's technical rules

Use `kernel/SYSTEM-TEMPLATE.md` as a guide and save as `kernel/SYSTEM.md`:

```markdown
## Language and Stack
- TypeScript with strict mode
- Next.js 14 App Router
- Prisma with PostgreSQL

## Code Style
- Use Server components by default
- Client Components only when necessary (hooks, events)
```

### 4. Start the AI with BOOTSTRAP

In the first message of every session:

```
Read kernel/BOOTSTRAP.md and give me your confirmation readback.
```

From there, the AI operates within the project's rules without needing re-explanation.

---

## Usage Examples

### Example 1 — Start Session

**Prompt:**
```
Read kernel/BOOTSTRAP.md and confirm the current project state.
```

**What the AI does:**
- Reads `project.toml` → knows it's a TypeScript web-app
- Reads `SOUL.md` → adopts direct, no-preamble behavior
- Reads `RULES.md` → knows it needs approval before commit/push
- Checks `memory/plans/` → finds PLAN-0003 in progress
- Returns readback: current state, active plan, next steps

---

### Example 2 — New Feature

**Prompt:**
```
I need an email notification system when a contract is signed.
```

**What the AI does:**
1. Passes through the **Socratic Gate** → asks: email provider? HTML or text template? retry on failure?
2. Classifies as **COMPLEX CODE** → creates `memory/plans/PLAN-0004-EMAIL-NOTIFICATIONS.md`
3. Waits for explicit approval
4. On execution: activates `@backend-specialist` + skills `api-patterns` + `nodejs-best-practices`
5. On completion: updates `memory/MODIFICATION_LOG.md` and `memory/progress.md`

---

### Example 3 — Bug Fix

**Prompt:**
```
Login fails silently on Safari mobile.
```

**What the AI does:**
1. Classifies as **BUG** → consults `memory/logs/DEBUG-HISTORY.md` first
2. Activates `@debugger` + skill `systematic-debugging`
3. Applies RAG methodology: searches similar implementations, analyzes boundaries
4. On fix: records `ERR-000X` in `DEBUG-HISTORY.md` with SYMPTOM/ROOT_CAUSE/ACTION
5. Does not close without recording

---

### Example 4 — Use Slash Commands

SFK includes 11 ready-to-use workflows:

```
/brainstorm  → Socratic requirements exploration before implementing
/create      → New feature scaffolding guided by App Builder
/debug       → Systematic DEBUG mode with root cause analysis
/deploy      → Pre-flight checks and deploy execution
/enhance     → Incremental improvement of existing code
/orchestrate → Multi-agent coordination for complex tasks
/plan        → Task breakdown into PLAN-XXXX without writing code
/preview     → Start/stop the local server
/status      → Project and session status panel
/test        → Test generation and execution
/ui-ux-pro-max → UI design with 50 visual styles
```

**Usage:**
```
/plan implement a payment system with Stripe
```

---

### Example 5 — Close Session

**Prompt:**
```
Close the session.
```

**What the AI does:**
1. Updates `memory/MODIFICATION_LOG.md` with: what was done / what changed / what remained pending
2. Enters `AUDITOR-PROTOCOL` → runs `memory/logs/SESSION-AUDIT-CHECKLIST.md`
3. Saves result in `memory/logs/AUDIT_YYYY-MM-DD_HH-MM-PASS.md`
4. Only closes after audit

---

## Reference Files

| I need to...                    | File                                 |
|---------------------------------|--------------------------------------|
| Understand the full system      | `memory/WORKFLOW_MEMORY_PLAYBOOK.md` |
| See agents, skills, and scripts | `kernel/ARCHITECTURE.md`             |
| Current project state           | `memory/progress.md`                 |
| History of changes              | `memory/MODIFICATION_LOG.md`         |
| Resolved bugs                   | `memory/logs/DEBUG-HISTORY.md`       |
| Fill in for a new project       | `kernel/project.toml` · `kernel/SYSTEM-TEMPLATE.md` |
| AI rules                        | `kernel/RULES.md` (sovereign)        |

---

## Philosophy

SFK starts from a simple premise: **the AI is intelligent, but not omniscient**. It doesn't know your code conventions, which bugs have already been fixed, or that you want approval before any commit.

SFK solves this with files — not prompts. Every rule is written once, in a fixed place, and applies to all sessions and to any AI that reads the project.

> *"SFK does not make the AI smarter. It makes the project's context unforgettable."*
