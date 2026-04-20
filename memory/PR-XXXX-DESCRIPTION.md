# PR Description Example

Use this file as a template to document a relevant delivery in the project.

Naming pattern:
- `PR-0001-DESCRIPTION.md`
- `PR-0002-DESCRIPTION.md`

When to use:
- when closing an important delivery block;
- when completing a relevant plan;
- when preparing context for publication, review, or handoff.

---

# [short delivery title]

## Objective

Explain in 1 or 2 sentences what this delivery solved.

Examples:
- add admin authentication;
- fix the payment flow;
- publish a new landing page version.

## What Was Done

### Product and Flow

- describe the main visible changes for users, admins, or operations
- list the flows that were created, changed, or removed
- keep the focus on what actually changed

### Technical

- describe backend, frontend, database, integrations, or infrastructure changes
- mention migrations, schema changes, APIs, jobs, or validations

### Memory and Governance

- state which plans were completed or updated
- state which decisions were created, replaced, or invalidated
- list the important documentation that was updated

## Main Files

### Code

- `src/...`
- `src/...`
- `src/...`

### Memory and Documentation

- `memory/...`
- `docs/...`
- `kernel/...`

## Validation

- `npm run lint`
- `npm run typecheck`
- `npm run build`
- `[another relevant command]`

## Notes

- record delivery limits
- highlight important behaviors for review
- note accepted risks or next steps when needed
