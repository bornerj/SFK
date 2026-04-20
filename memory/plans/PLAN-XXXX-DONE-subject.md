# PLAN-XXXX — Plan Title

Use this file as an example of a completed plan.

Naming pattern:
- in progress: `PLAN-0001-subject.md`
- completed: `PLAN-0001-DONE-subject.md`

When to use:
- medium or large work;
- deliveries with multiple phases;
- structural, flow, or architectural changes;
- efforts that need traceability and checkpoints.

Status: DONE
Date: YYYY-MM-DD
Last updated: YYYY-MM-DD
Type: WEB APP | API | LIBRARY | INFRA | OTHER
Priority: High | Medium | Low

## Objective

Describe the main objective of the plan in one short paragraph.

## Current State

- record the context found before or during execution
- list what was already in place
- list restrictions, dependencies, or decisions that influenced the work

## Scope Locked for MVP

- item 1 in scope
- item 2 in scope
- item 3 in scope

## Out of Scope for This Plan

- item 1 out of scope
- item 2 out of scope
- item 3 out of scope

## Decisions Applied

- `DECISION-001`: summary of the applied decision
- `DECISION-002`: summary of the applied decision

## Phases

### Phase 1 — Nome da fase

Status: DONE

Deliverables:
- primary delivery 1
- primary delivery 2

Evidence:
- `src/...`
- `docs/...`

### Phase 2 — Nome da fase

Status: DONE

Deliverables:
- primary delivery 1
- primary delivery 2

Evidence:
- `src/...`
- `memory/...`

## Validation Status

Completed:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

Pending:
- non-blocking item, if any

## Risks and Gaps

- accepted risk
- remaining technical debt
- desirable future validation

## Next Execution Steps

1. Formally close this plan.
2. Update `memory/progress.md`, if applicable.
3. Open a new plan or record the next block in `MODIFICATION_LOG`, if needed.

## Completion Criteria

Explain why the plan can be marked as `DONE`.

Examples:
- main scope delivered;
- validations executed;
- remaining risks recorded;
- memory updated.

## Git Record of Delivery

- Validated branch: `[branch-name]`
- Validated environment: `[local, staging, or production]`
- Relevant commits:
  - `abc1234` — short summary
  - `def5678` — short summary
