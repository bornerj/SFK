# Contributing to SFK

Thank you for your interest in contributing to the **Structured Framework Kit (SFK)**!

---

## Ways to Contribute

- **Report bugs** — open an issue describing the problem, steps to reproduce, and expected behavior
- **Suggest new skills or agents** — open an issue with a description and use case
- **Improve existing documentation** — even small fixes are welcome
- **Submit workflow improvements** — propose changes to existing slash-command workflows
- **Fix typos and formatting** — always appreciated

---

## Before You Start

1. Check if there's already an open issue or pull request for what you want to do
2. For significant changes (new agents, new skills, structural changes), **open an issue first** to discuss the approach
3. For small fixes (typos, formatting, clarifications), go ahead and submit a PR

---

## Pull Request Guidelines

1. **Fork** the repository and create your branch from `main`
2. **Name your branch** descriptively: `feat/skill-graphql-patterns`, `fix/bootstrap-typo`, `docs/readme-update`
3. **Keep PRs focused** — one feature or fix per PR
4. **Test your changes** — if adding a skill, verify it works correctly with at least one AI
5. **Update documentation** if your change affects how SFK is used
6. **Update `CHANGELOG.md`** under an `[Unreleased]` section

---

## Skill Contribution Guidelines

Adding a new skill is one of the most valuable contributions. A skill must follow this structure:

```
kernel/skills/my-skill-name/
├── SKILL.md           ← Required: metadata + instructions
├── scripts/           ← Optional: Python or Bash scripts
├── references/        ← Optional: templates, docs, reference material
└── assets/            ← Optional: images, logos
```

### `SKILL.md` format

```markdown
---
name: my-skill-name
description: One-line description of when to use this skill. Be specific — this is used for automatic routing.
---

# Skill Name

Brief description of what this skill does.

## Instructions

[Detailed instructions for the AI to follow when this skill is active]
```

### Skill quality checklist

- [ ] Description is specific enough for automatic routing (not "general knowledge")
- [ ] Instructions are actionable and concrete, not vague
- [ ] No hardcoded project-specific assumptions (skills must be reusable)
- [ ] If using scripts, they work on Python 3.8+
- [ ] Skill name uses `kebab-case`
- [ ] Skill is listed in `kernel/ARCHITECTURE.md` under the appropriate category

---

## Agent Contribution Guidelines

New agents must be added to `kernel/agents/` as `agent-name.md` and registered in `kernel/ARCHITECTURE.md`.

An agent file must specify:
- Role and focus area
- Which skills it uses
- Behavioral guidelines for that domain

---

## Code of Conduct

Be respectful and constructive. This project is about making AI development collaboration better — let's keep the same spirit in how we collaborate with each other.

---

## Questions?

Open an issue with the `question` label.
