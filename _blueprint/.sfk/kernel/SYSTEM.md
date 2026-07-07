## System (Technical and Organizational Rules)

These rules define the engineering standards for the project.
Process, continuity, and memory rules are in `kernel/RULES.md`.
Must be reviewed BEFORE the start of the project.

> Fill in this file using `kernel/SYSTEM-TEMPLATE.md` as a guide.
> Remove sections that do not apply to your stack.
> This file is read and enforced by the AI in every session.

## Language and Stack
[FILL IN — Use kernel/project.toml as reference]

## Code Style
[FILL IN — Define your project's conventions]

## Logging
[FILL IN — Define the logging strategy]

Invariant rules (for any stack):
- NEVER use `console.log()` / `print()` in production code
- Use the project logger (define path here)
- Never log sensitive data (passwords, tokens, PII)

## Error Handling
[FILL IN — Define the error handling pattern]

Invariant rules:
- Critical errors do not propagate without context
- Never expose stack traces or internal details to the end user

## Security and Input Validation
These rules are invariant — do not remove:
- Validate all input with explicit schema (Zod | Pydantic | Joi | etc.)
- Assume all external input is malicious
- Use parameterized queries — never concatenate user input in SQL
- Never hardcode secrets, tokens, or credentials

## Technical Architecture
[FILL IN — Define layers and responsibilities]

## Tests
[FILL IN — Define the testing strategy]

Invariant rules:
- Write tests for business logic
- Cover edge cases and error states
- Use descriptive test names

## Database
[FILL IN — Define database access rules]

## Engineering Philosophy
These rules are universal — always keep:
- Readability above cleverness
- Explicit above implicit
- Simple above complex
- Remove obsolete code rather than commenting it out
