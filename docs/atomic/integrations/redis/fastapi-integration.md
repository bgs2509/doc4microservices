# Redis + FastAPI Integration

Expose Redis to route handlers via FastAPI dependency injection while keeping the event loop single and healthy.

## Lifespan Registration

```python
from redis.asyncio import Redis
from contextlib import asynccontextmanager


def build_lifespan(settings):
    @asynccontextmanager
    async def lifespan(app):
        redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await redis.ping()
        app.state.redis = redis
        try:
            yield
        finally:
            await redis.close()

    return lifespan
```

## Dependency Provider

```python
from fastapi import Depends


def get_redis(app = Depends()) -> Redis:
    return app.state.redis
```

- Inject the dependency into handlers (`async def handler(redis: Redis = Depends(get_redis))`).
- Optionally wrap Redis operations in application services to avoid leaking low-level commands.

## Testing

- Override the dependency with a fake or Testcontainers-backed Redis instance during tests.
- Ensure tests share the event loop provided by `pytest-asyncio`; avoid `asyncio.run`.

## Observability

- Log cache hits/misses with request IDs.
- Export metrics per endpoint (latency impact, hit rate) to Prometheus.

## Related Documents

- `docs/atomic/services/fastapi/dependency-injection.md`
- `docs/atomic/integrations/redis/testing-patterns.md`
- Legacy reference: `docs/legacy/infrastructure/redis_rules.mdc`
