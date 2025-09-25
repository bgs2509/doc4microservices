# PostgreSQL Service Setup

PostgreSQL data services expose HTTP APIs that encapsulate relational data access. They use async SQLAlchemy and follow the Improved Hybrid separation.

## Dependencies

```toml
[project.dependencies]
fastapi = "^0.111"
sqlalchemy = "^2.0"
asyncpg = "^0.29"
alembic = "^1.13"
uvicorn = "^0.30"
pydantic = "^2.8"
```

## Engine and Session

```python
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.core.config import Settings


def build_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=30,
        pool_recycle=1800,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)
```

Use lifespan to create engine/session factory once and inject sessions per request.

## Migrations

- Manage schema changes with Alembic; run migrations during deployment before starting the API.
- Store migration scripts in `migrations/` with sequential revisions.
- Use `alembic.ini` configured for async engines (`sqlalchemy.url = postgresql+asyncpg://...`).

## Health Checks

- Expose `/ready` that verifies DB connectivity (`SELECT 1`).
- Monitor connection pool metrics (borrowed connections, wait time).

## Performance

- Tune indexes for common query patterns; review with `EXPLAIN ANALYZE`.
- Use prepared statements or SQLAlchemy compiled cache for hot queries.
- Avoid loading entire result sets; rely on pagination.

## Related Documents

- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/services/data-services/transaction-management.md`
- Legacy reference: `docs/legacy/architecture/data-access-rules.mdc`
