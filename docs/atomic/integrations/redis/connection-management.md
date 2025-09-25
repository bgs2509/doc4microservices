# Redis Connection Management

Use a single asynchronous Redis client per process, configured with connection pooling and constructed during service startup.

## Client Construction

```python
from redis.asyncio import Redis


def build_redis(url: str) -> Redis:
    return Redis.from_url(
        url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=100,
    )
```

- Instantiate the client inside FastAPI lifespan, Aiogram startup, or the worker `main()` coroutine.
- Store the client in application state (`app.state.redis`) or dispatcher startup context; never create clients per request.
- Close the client gracefully on shutdown to flush pending commands.

## Timeouts and Reliability

- Configure socket/connect timeouts to avoid hanging on network outages (`Redis.from_url(..., socket_timeout=5.0)`).
- Wrap initial connection attempts with retries (exponential backoff) but fail fast when the service cannot reach Redis.
- Use health checks that issue lightweight `PING` commands.

## Pool Sizing

- Size pools according to workload; start with `max_connections=100` for web services, lower for workers.
- Monitor pool usage via metrics to detect saturation and tune accordingly.

## Observability

- Log connection lifecycle events (`redis_connected`, `redis_disconnected`) with request IDs from logging middleware.
- Emit metrics for command durations and error counts.

## Related Documents

- `docs/atomic/integrations/redis/key-naming-conventions.md`
- `docs/atomic/services/fastapi/dependency-injection.md`
- Legacy reference: `docs/legacy/infrastructure/redis_rules.mdc`
