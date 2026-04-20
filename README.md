# SFK — Structured Framework Kit

> A Persistent Intelligence Layer for AI-driven software systems.

---

## The Problem

Software systems don’t have memory.

Critical knowledge lives inside developers:
- Architecture decisions
- Debugging history
- Edge cases
- System behavior

This creates systemic inefficiencies:

- Dependency on senior engineers  
- Slow onboarding  
- Repeated mistakes  
- Time wasted reconstructing context  

And AI made this worse.

AI depends on context.  
But context disappears every session.

---

## The Core Insight

Software has logic.  
But it doesn’t have memory.

---

## The Solution

SFK embeds structured, persistent intelligence directly into your project.

Not documentation.  
Not chat history.  

**Executable, reusable knowledge.**

---

## What SFK Enables

- Systems that remember decisions  
- AI that operates with context awareness  
- Debugging that reuses past solutions  
- Reduced dependency on individuals  
- Faster onboarding and issue resolution  

---

## How It Works

SFK introduces three layers:

### 1. Control Layer (`kernel/`)
Defines identity, rules, architecture, and behavior.

### 2. Memory Layer (`memory/`)
Stores decisions, logs, plans, and system evolution.

### 3. Execution Layer
Agents, skills, and workflows orchestrate execution.

---

## Key Concept: Context Routing

Instead of loading everything into AI context:

- SFK loads only what is necessary  
- At the exact moment it is needed  

Result:

- Lower token usage  
- Higher precision  
- More reliable outputs  

---

## Use Cases

- Legacy systems with tribal knowledge  
- Teams dependent on key individuals  
- AI-assisted development environments  
- Complex systems with high debugging cost  

---

## Why This Matters

We are moving from:

**Stateless development**  
→ Context is constantly rebuilt  

To:

**Stateful intelligence systems**  
→ Knowledge is embedded and reusable  

---

## Quickstart

### Requirements

- Python 3.8+
- PowerShell 5+ (Windows) or Bash (Linux/macOS — see [Shell Script](#shell-script-linuxmacos))

### 1. Clone this repository

```bash
git clone https://github.com/Jeiel/sfk.git
cd sfk
```

### 2. Create a new project from the template

**Windows (PowerShell):**
```powershell
# Interactive wizard — recommended for first use
.\new-project.ps1

# Direct mode with parameters
.\new-project.ps1 -Target "C:\projects\my-project" -ProjectName "MyProject" -InitGit
```

**Linux/macOS (Bash):**
```bash
# Interactive wizard
bash new-project.sh

# Direct mode
python tools/jb_kit_turbo.py /path/to/my-project --project-name MyProject --init-git
```

### 3. Fill in your project identity

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
service  = "Node.js API (Express)"

[hosting.database]
provider = "Railway"
service  = "PostgreSQL — separate service in the same Railway project"

[stack.frontend]
framework = "Vite + React"
version   = "React 18 / Vite 5"
styling   = "TailwindCSS 3.4.17"

[stack.backend]
framework = "Express"
orm       = "Prisma"
language  = "TypeScript (strict) — Node.js 20+ ESM"

[design]
framework         = "TailwindCSS"
framework_version = "3.4.17"
build_command     = "npx tailwindcss@3.4.17 -i input.css -o output.css"

[environments.railway]
vars = ["DATABASE_URL", "JWT_SECRET", "APP_API_URL", "APP_WEB_URL", "CORS_ORIGIN"]

[environments.vercel]
vars = ["VITE_API_URL", "VITE_WEB_URL"]

[[integrations]]
name     = "Stripe"
purpose  = "Payment processing"
env_vars = ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"]
```

### 4. Start your AI session

In your first message of every session:

```
Read kernel/BOOTSTRAP.md and give me your confirmation readback.
```

From there, the AI operates within the project's rules without needing re-explanation.

---

## What's inside

```
sfk/
├── kernel/               ← AI control layer
│   ├── BOOTSTRAP.md      ← Session entry point (required)
│   ├── RULES.md          ← Governance, process, memory & Git (sovereign)
│   ├── SOUL.md           ← AI behavior contract (portable)
│   ├── project.toml      ← Project identity, stack, URLs, design tokens
│   ├── index.toml        ← Declarative session router by task type
│   ├── SYSTEM.md         ← Technical contract (fill per project)
│   ├── agents/           ← 20 specialist AI agents
│   ├── skills/           ← 56 domain knowledge modules
│   ├── workflows/        ← 11 slash-command procedures
│   └── scripts/          ← Validation & audit scripts
│
├── memory/               ← Persistence layer
│   ├── MODIFICATION_LOG.md          ← Chronological framework/project change log
│   ├── progress.md                  ← Current module and delivery state
│   ├── PR-XXXX-DESCRIPTION.md       ← Reusable PR description template
│   ├── plans/
│   │   └── PLAN-XXXX-DONE-subject.md ← Reusable completed-plan template
│   ├── decisions/
│   │   └── DECISION-XXX.md          ← Reusable decision template
│   └── logs/
│       ├── BUILD-HISTORY.md
│       ├── DEBUG-HISTORY.md
│       ├── DRIFT-RULES.md
│       └── SESSION-AUDIT-CHECKLIST.md
│
├── docs/                 ← Product documentation
│   ├── project/
│   ├── config/
│   └── evolutive_changes/
│
├── tools/                ← Scaffolding tools
│   └── jb_kit_turbo.py
│
├── new-project.ps1       ← Windows wizard
├── new-project.sh        ← Linux/macOS wizard
├── update-project.sh     ← Framework updater for existing projects
└── INSTRUCTIONS.md       ← Full usage guide
```

---

## Capabilities

| Resource      | Count | Description                                                  |
|---------------|-------|--------------------------------------------------------------|
| **Agents**    | 20    | Specialist AI personas (frontend, backend, DBA, security...) |
| **Skills**    | 56    | Domain knowledge modules loaded on-demand                    |
| **Workflows** | 11    | Slash-command procedures (`/plan`, `/debug`, `/deploy`...)   |
| **Scripts**   | 5     | Validation, audit and preview automation                     |

### Slash commands

```
/brainstorm   → Socratic requirements discovery
/create       → Scaffold new features with App Builder
/debug        → Systematic debug with root cause analysis
/deploy       → Pre-flight checks and deploy execution
/enhance      → Incremental improvement of existing code
/orchestrate  → Multi-agent coordination for complex tasks
/plan         → Task breakdown into PLAN-XXXX without writing code
/preview      → Start/stop local server
/status       → Project and session status panel
/test         → Test generation and execution
/ui-ux-pro-max → UI design with 50 visual styles
```

---

## Compatible AIs

SFK works with any AI that reads text files. Native integration files included:

| AI / IDE     | Integration file            |
|--------------|-----------------------------|
| Claude Code  | `.clauderules`              |
| Windsurf     | `.windsurfrules`            |
| Cursor       | `.cursor/rules/` (56 rules) |
| Any other    | `kernel/BOOTSTRAP.md`       |

---

## How it works

SFK operates in three layers:

```
┌────────────────────────────────────────────────────────────┐
│  CONTROL & CAPABILITIES  (kernel/)                         │
│  project.toml · SOUL.md · RULES.md · index.toml            │
│  BOOTSTRAP.md · ARCHITECTURE.md                            │
│  agents/ · skills/ · workflows/ · scripts/                 │
└────────────────┬───────────────────────────────────────────┘
                 │ persists to
┌────────────────▼────────────────────┐
│  MEMORY  (memory/)                  │  ← Everything is logged
│  MODIFICATION_LOG · plans/ · debug  │
│  decisions/ · progress.md           │
└─────────────────────────────────────┘
```

### Session flow

1. AI reads `kernel/BOOTSTRAP.md` → loads identity, rules, behavior (LAYER 0)
2. Consults `kernel/index.toml` → loads only files relevant to the task type (LAYER 1)
3. Checks `memory/progress.md` → snapshot of current module state
4. Checks `memory/plans/` → resumes active plan if any
5. Classifies request → selects agent and skills → executes
6. Logs result to `memory/MODIFICATION_LOG.md` or the active plan

---

## Documentation

- **[INSTRUCTIONS.md](./INSTRUCTIONS.md)** — Full usage guide with practical examples
- **[kernel/ARCHITECTURE.md](./kernel/ARCHITECTURE.md)** — All agents, skills, and scripts
- **[kernel/README.md](./kernel/README.md)** — Kernel structure and precedence hierarchy
- **[memory/WORKFLOW_MEMORY_PLAYBOOK.md](./memory/WORKFLOW_MEMORY_PLAYBOOK.md)** — Memory system internals

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](./LICENSE).


---

## Acknowledgements & Credits
While the SFK concept and architecture are original and proprietary, this project utilizes and builds upon the following open-source resources:

- Antigravity Awesome Skills - Used some Skills and Agents  
- dotcontext - Concept Idea of using behavior controls and router to direct AI  
- Agency Agents - Inspiration and logic for some Skills and agents  

---
