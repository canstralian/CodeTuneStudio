---
name: debug-db
description: Diagnose database connectivity, migration, schema, and SQLite/PostgreSQL compatibility issues in CodeTuneStudio
---

# Debug database issues

Use this skill when the task involves database errors, migration failures, schema mismatches, locked database issues, or portability problems between PostgreSQL and SQLite.

## Goals

- Identify the failure mode precisely
- Prefer non-destructive inspection first
- Preserve support for both PostgreSQL and SQLite fallback
- Fix the issue with the smallest correct change

## Workflow

1. Identify the active database path or configuration.
   - Check relevant environment usage, especially `DATABASE_URL`.
   - Inspect startup and DB initialization code before changing anything.

2. Run the repository health checks that already exist.
   - Start with `python db_check.py` when available.
   - If the issue is migration-related, inspect migration configuration and run the appropriate migration status or upgrade command.

3. Inspect the schema and model boundary.
   - Compare SQLAlchemy models, migration files, and actual usage paths.
   - Look for assumptions that work only on PostgreSQL or only on SQLite.

4. Classify the issue.
   Common categories:
   - connection/configuration failure
   - migration drift
   - schema mismatch
   - SQLite locking/concurrency limitation
   - backend-specific SQL or type usage
   - session/transaction lifecycle bug

5. Fix conservatively.
   - Preserve both PostgreSQL and SQLite compatibility.
   - Avoid destructive reset unless the user explicitly wants it or it is clearly required.
   - If suggesting a destructive reset, label it clearly.

6. Validate.
   - Run the smallest relevant tests first.
   - Run broader tests only if the database surface touched is broad.
   - Report exactly what was validated.

## Notes

- Do not add database-specific behavior unless guarded and justified.
- Treat SQLite reset as destructive.
- Prefer migration repair and code fixes over deleting the database.