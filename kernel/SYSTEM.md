## System (Technical and Organizational Rules)

These rules define the engineering standards for the project.
Process, continuity, and memory rules are in `kernel/RULES.md`.
Must be reviewed BEFORE the start of the project.

## Language and Stack
- TypeScript with strict mode.
- Node.js 20+ with ESM modules.
- API in Express.
- ORM: Prisma with PostgreSQL.
- E2E Tests: Playwright.
- Main frontend: Vite + React.
- Additional product context: Next.js App Router and Stripe.

## Code Style
- Use functional components (React).
- Prefer `const` over `let`.
- Use explicit return types in TypeScript.
- Avoid `any` (use only when strictly necessary).
- Use `async/await`; do not use callbacks when a clear async alternative exists.

## Logging
- NEVER use `console.log()`.
- Use the project logger: `import { logger } from './utils/logger'`
- Allowed levels: `logger.info()`, `logger.warn()`, `logger.error()`.
- Never log sensitive data (passwords, tokens, PII).

## Error Handling
- Handle errors structurally (do not let critical failures propagate without context).

```ts
try {
  const result = await operation();
  return { success: true, data: result };
} catch (error) {
  logger.error('Operation failed', { error });
  return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
}
```

## Security and Input Validation
- Validate all input with an explicit schema.
- Assume all external input is malicious.
- Use parameterized queries; never concatenate user input in SQL.

```ts
// Good
await db.query('SELECT * FROM users WHERE email = $1', [email]);

// Bad
await db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

## Technical Architecture
- Business rules and functions live in the backend (Express + Prisma).
- Frontend does not access the database directly; it only consumes HTTP/JSON APIs.
- Controller handles HTTP; business logic stays in services/repositories.
- Sensitive routes must use `requireAuth` and `requireAdmin`.
- Errors must follow the pattern in `apps/api/src/lib/messages.ts`.
- Validation responses return `detail` only in `NODE_ENV=development`.

## Zod and Message Consistency
- All input must have an explicit Zod schema.
- Messages should be normalized per project locale when necessary.
- Phone and email validations must be consistent between backend and frontend.

## Prisma + PostgreSQL
- Prisma is the only database access layer in the backend.
- Migrations must be versioned (Prisma Migrate).
- Create seeds for base/feature/error scenarios when necessary.
- Views/materialized views/database functions must be versioned and documented.
- If the database changes (`schema.prisma` or migration), run `npx prisma generate` in `apps/api` before continuing.

## Frontend (Vite + React)
- Frontend consumes APIs; no direct database queries.
- API messages should be normalized on the client side (e.g.: locale-aware mapping).
- Login/signup modals must clear error/success state when opened/closed.

## Payments (Stripe)
- Never store card numbers.
- Use Stripe tokenization.
- Log payment attempts.
- Handle failures gracefully.
- Use idempotency keys.

## State Management
- Use React Context for theme/user when applicable.
- Avoid unnecessary global state.
- Server state remains on the server.
- Client state should be minimal.

## Engineering Philosophy
- Readability above cleverness.
- Explicit above implicit.
- Simple above complex.
- Prefer removing obsolete code rather than commenting it out.

## Tests (technical standard)
- Write tests for business logic.
- Cover edge cases and error states.
- Use descriptive test names.
- Prefer integration tests when they deliver more practical confidence.
