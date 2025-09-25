# FastAPI Lifespan Management

Lifespan hooks manage startup and shutdown for databases, caches, message brokers, and background tasks. Always use the `lifespan` parameter of `FastAPI` to encapsulate resource ownership.

## Template

```python
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import Settings
from src.infrastructure.db import Database
from src.infrastructure.redis import RedisClient
from src.infrastructure.messaging import RabbitMQClient


def build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = Database(settings.database_url)
        redis = RedisClient(settings.redis_url)
        rabbit = RabbitMQClient(settings.rabbitmq_url)

        await db.connect()
        await redis.connect()
        await rabbit.connect()

        app.state.db = db
        app.state.redis = redis
        app.state.rabbit = rabbit

        try:
            yield
        finally:
            await rabbit.close()
            await redis.close()
            await db.disconnect()

    return lifespan
```

## Guidelines

- Initialise resources once during startup; reuse through dependency injection.
- Set timeouts when connecting to external systems to avoid hanging deployments.
- Register health checks after connections succeed to prevent false positives.
- Remove state from `app.state` during shutdown to avoid memory leaks in reload mode.

## Monitoring

- Log startup and shutdown with request/trace IDs from `logging_rules` patterns.
- Emit Prometheus gauges for connection pool size and availability.
- Alert when connection retries exceed defined thresholds.

## Failure Handling

- Wrap connection attempts in retries (exponential backoff) but fail fast after a limited number of attempts.
- If a critical dependency fails to start, raise and let the orchestrator restart the container; do not swallow the exception.

## Related Documents

- `docs/atomic/services/fastapi/dependency-injection.md`
- `docs/atomic/architecture/event-loop-management.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
