# DB Seeds — Fixtures & Reference Data

Seed and fixture scripts: test data, reference/lookup data, and demo datasets.

## Naming
```
NNNN_<subject>.sql     e.g. 0001_reference_countries.sql
                            0002_test_users.sql
```

## Rules
- Keep seeds **idempotent** where possible (safe to re-run).
- Separate reference data (ships to production) from test data (dev/staging only) —
  make the distinction clear in the filename or a header comment.
- Application of seeds is logged in `memory/logs/BUILD-HISTORY.md`.
- Schema changes go in `../migrations/`, not here.
