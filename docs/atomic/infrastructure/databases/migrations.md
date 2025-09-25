# Database Migrations

Manage schema changes with automated migrations to keep environments in sync.

## Tooling

- Use Alembic for PostgreSQL; enforce one revision per merge request.
- For MongoDB, maintain migration scripts (Python modules) that apply incremental changes (indexes, schema adjustments).
- Version control migration scripts inside each data service repository.

## Process

1. Generate migration from model changes (`alembic revision --autogenerate`).
2. Review migration SQL manually; ensure destructive operations are safe.
3. Apply migrations locally and in CI (Testcontainers) before merging.
4. Run migrations during deployment before starting the new application version.

## Rollback

- Provide downgrade scripts where feasible; if not, document manual rollback steps.
- Take backups before applying breaking schema changes.

## Observability

- Log migration start/finish events with version numbers.
- Fail deployments when migrations do not apply cleanly; avoid ignoring errors.

## Related Documents

- `docs/atomic/services/data-services/transaction-management.md`
- `docs/atomic/infrastructure/deployment/ci-cd-patterns.md`
