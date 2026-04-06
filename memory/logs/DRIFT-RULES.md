## Drift Rules

1. If files related to auth or security are modified
and there is no change in `memory/decisions/DECISION-XXX.md` — FAIL

2. If a commit indicates a bug fix and `memory/logs/DEBUG-HISTORY.md` is not updated — FAIL

3. If `/apps/api/prisma/schema.prisma` or migrations change and there is no record in `memory/MODIFICATION_LOG.md` — FAIL

4. Every endpoint must use Zod. If Zod is not found — FAIL
