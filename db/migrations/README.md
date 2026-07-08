# DB Migrations — Sequential, Append-Only

Every database schema/data change lives here as a numbered SQL file. This is the
single fixed location for the database lifecycle (D3) — no migration lives anywhere else.

## Naming
```
NNNN_<verb>_<subject>.sql      e.g. 0001_create_users.sql
                                    0002_add_orders_index.sql
                                    0007_migrate_mysql_to_postgres.sql
```
- `NNNN` is a zero-padded sequence starting at `0001`.
- **Append-only. Never renumber or edit an applied migration** — add a new one.
- One logical change per file.

## Rules
- Order is the timeline. The number IS the history (which is why you never renumber).
- Every migration that gets applied is logged in `memory/logs/BUILD-HISTORY.md`
  (when it ran, on which environment, and why).
- Cross-engine moves (e.g. MySQL → PostgreSQL), data copies, and backfills are
  ordinary numbered migrations — plus a `DECISION-XXX` if it was an architectural call.
- Seed/fixture data goes in `../seeds/`, not here.
- Path is declared in `sfk.toml -> [db]`.
