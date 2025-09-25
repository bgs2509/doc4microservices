# Redis + AsyncIO Integration

Background workers operate with pure AsyncIO; initialise Redis in `main()` and pass the client to tasks.

## Bootstrap

```python
from redis.asyncio import Redis


async def bootstrap(settings):
    redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await redis.ping()
    return redis
```

## Usage in Tasks

```python
async def process_event(event, redis):
    key = f"cache:event:{event.id}"
    await redis.setex(key, 600, event.model_dump_json())
```

- Share the client across tasks by storing it in a dependency container or dataclass.
- Close the client during shutdown (`await redis.close()`).

## Testing

- Provide fake Redis implementations for unit tests.
- Use Testcontainers for integration tests to validate concurrency and TTL behaviour.

## Related Documents

- `docs/atomic/services/asyncio-workers/dependency-management.md`
- `docs/atomic/integrations/redis/testing-patterns.md`
- Legacy reference: `docs/legacy/infrastructure/redis_rules.mdc`
