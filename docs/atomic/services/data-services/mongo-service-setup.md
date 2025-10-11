# MongoDB Service Setup

MongoDB data services handle document-centric workloads via async Motor clients.

## Dependencies

```toml
[project.dependencies]
motor = "^3.5"
fastapi = "^0.111"
pydantic = "^2.8"
```

## Client Initialization

```python
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import Settings


def build_client(settings: Settings) -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(
        settings.mongo_url,
        maxPoolSize=settings.mongo_max_pool,
        minPoolSize=settings.mongo_min_pool,
        serverSelectionTimeoutMS=5000,
    )
    return client
```

Use lifespan to connect/disconnect the client. Expose specific databases/collections via repositories.

## Schema Validation

- Define Pydantic models for documents and enforce them before inserts.
- Configure MongoDB JSON schema validators where appropriate.
- Maintain indexes in code or migrations and apply them during startup.

## Aggregations

- Store aggregation pipelines close to repositories; keep them deterministic and documented.
- Test pipelines with realistic datasets.

## Health Checks

- Ping the database (`await client.admin.command("ping")`) in readiness probes.
- Monitor pool utilisation and slow queries via MongoDB profiler (production only with caution).

## Related Documents

- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/services/data-services/http-api-design.md`
