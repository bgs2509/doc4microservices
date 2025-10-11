# Dependency Management

Workers depend on asynchronous clients (RabbitMQ, Redis, databases). Instantiate them once and share via lightweight containers.

## Building Dependencies

```python
from __future__ import annotations

from contextlib import AsyncExitStack
from dataclasses import dataclass
from src.worker.adapters.rabbitmq import RabbitMQClient
from src.worker.adapters.redis import RedisClient
from src.worker.config import Settings


@dataclass
class Dependencies:
    rabbitmq: RabbitMQClient
    redis: RedisClient


async def build_dependencies(settings: Settings, stack: AsyncExitStack) -> Dependencies:
    rabbitmq = RabbitMQClient(settings.rabbitmq_url)
    redis = RedisClient(settings.redis_url)

    await stack.enter_async_context(rabbitmq.connect())
    await stack.enter_async_context(redis.connect())

    return Dependencies(rabbitmq=rabbitmq, redis=redis)
```

`AsyncExitStack` ensures resources close automatically on exit.

## Guidelines

- Load configuration once in `main()` and pass to builders.
- Reuse the same dependencies across all tasks; do not create new connections in loops.
- Wrap third-party clients that lack async context managers to provide one yourself.
- Expose typed helpers (`deps.rabbitmq.channel`) but hide low-level connection details from tasks where possible.

## Testing

- Provide fake dependency objects with the same interface for unit tests.
- Integration tests can spin up real brokers via Testcontainers and call `build_dependencies()` with overridden URLs.

## Related Documents

- `docs/atomic/services/asyncio-workers/task-management.md`
- `docs/atomic/services/asyncio-workers/error-handling.md`
