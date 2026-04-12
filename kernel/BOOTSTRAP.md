## Bootstrap
Kernel Version 0.6
Goal: execute the session start checklist and ensure continuity without loss of context.

## LAYER 0 — Mandatory Loading (every session)

Always read, regardless of task type:
- `kernel/project.toml` — project identity, stack, URLs, and design tokens
- `kernel/SOUL.md` — AI behavior contract for this project
- `kernel/RULES.md` — governance + execution + memory + Git (sovereign)
- `kernel/SYSTEM.md` — technical and organizational rules for the project

## LAYER 1 — Selective Loading by Task Type

Consult `kernel/index.toml` to decide which additional files to load.
The index.toml defines triggers by task type and maps the corresponding files.

For onboarding or the first session, also load:
- `memory/WORKFLOW_MEMORY_PLAYBOOK.md` — overview of the work and memory system
- `kernel/ARCHITECTURE.md` — source of truth for agents, skills, and scripts
- `memory/MODIFICATION_LOG.md` — chronological macro context
- `memory/progress.md` — current state of modules

## Macro Context Reading
- Read `memory/MODIFICATION_LOG.md`:
  - with plan: milestones of START/END for the plan (plans in `memory/plans/PLAN-XXXX-`)
  - without plan: all point-in-time changes recorded in real time
- Read `memory/progress.md` for the current module state snapshot (quick read)
- Validate discrepancies between the log, the last plan, and the current workspace state.

## Mandatory Agentic Capabilities Protocol
- Before planning, responding technically, editing, or implementing, consult `kernel/ARCHITECTURE.md`.
- Treat `kernel/ARCHITECTURE.md` as the live source of truth. Do not rely on fixed lists scattered across other files.
- First check whether an applicable workflow exists in `kernel/workflows`.
- Then identify which agents and skills can support the task. If there is a match, use them as mandatory auxiliary resources for reasoning and execution.
- When choosing an agent, read the agent's file in `kernel/agents` and then selectively load the relevant `SKILL.md` files for the referenced skills.
- Do not read all skills by default. Read the inventory first, then the agent, then only the skills needed for the current task.
- For multi-domain, broad, ambiguous, or cross-specialty coordination tasks, prioritize `orchestrator` and/or the `agents-orchestrator` skill as the coordination layer.
- Workflows, agents, skills, and scripts must be treated as permanent auxiliary resources of the kernel, not as optional references.

### Response Format (MANDATORY)
When self-applying an agent or skill, notify the user:

```markdown
**Applying knowledge from `@[agent-name]`...** or 
**Applying knowledge from `@[skill-name]`...** 
[Continue with specialized response]
```

---

## Request Classifier (MANDATORY — Step 1)

Before any action, classify the request:

| Type | Triggers | Output |
|---|---|---|
| **QUESTION** | "what is", "how does", "explain" | Text response |
| **SURVEY/INTEL** | "analyze", "list files", "overview" | Session intel (no file) |
| **SIMPLE CODE** | "fix", "add", "change" (1 file) | Inline edit / no plan |
| **COMPLEX CODE** | "build", "create", "implement", "refactor" | `PLAN-XXXX` required |
| **DESIGN/UI** | "design", "UI", "page", "dashboard" | `PLAN-XXXX` required |

---

## Agent Routing Checklist (MANDATORY before code or design)

Before any code or design work, mentally complete:

| Step | Check | If fail |
|---|---|---|
| 1 | Did I identify the correct agent for this domain? | → STOP. Analyze the domain first. |
| 2 | Did I read the agent's `.md` file (or recall its rules)? | → STOP. Open `kernel/agents/{agent}.md` |
| 3 | Did I announce `🤖 Applying knowledge from @[agent]...`? | → STOP. Add it before responding. |
| 4 | Did I load the skills from the agent's frontmatter? | → STOP. Check the `skills:` field |

**Failure conditions:**
- ❌ Writing code without identifying an agent = **PROTOCOL VIOLATION**
- ❌ Skipping the announcement = **USER CANNOT VERIFY WHETHER AGENT WAS USED**

---

## Plans (`memory/plans/`)
- Check whether there is any `PLAN-XXXX-...` without `DONE`.
- If there is a plan without `DONE`, it is the primary source of continuity: read that plan first and continue from it.
- If all plans are marked `DONE`, read the most recent one to get up to date.
- If no plans are registered, assume that `memory/plans/` control has not yet started; consult `memory/MODIFICATION_LOG.md`.

## Decisions (`memory/decisions/`)
- Check for decisions with `Status: ACTIVE`.
- If no decisions are registered, assume this control started on 2026-02-26.

## Readback Confirmation (mandatory)
- After reading everything to the last line, provide a readback confirming:
  - understanding of the rules;
  - validations executed;
  - existence (or absence) of conflicts;
  - current situation;
  - next steps (when a plan is in progress);
  - workflow(s) evaluated for the session;
  - agents found in kernel/agents
  - skills found in kernel/skills
  - agent(s)/skill(s) that will be used as support, or an objective justification if none are needed

