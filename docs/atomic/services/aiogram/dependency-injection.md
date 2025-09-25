# Dependency Injection

Aiogram exposes simple DI hooks via dispatcher startup/shutdown callbacks. Use them to provide infrastructure clients to handlers.

## Startup Registration

```python
from __future__ import annotations

from aiogram import Dispatcher
from src.bot.dependencies import RedisClient, RabbitMQClient


def register_dependencies(dp: Dispatcher, redis: RedisClient, rabbit: RabbitMQClient) -> None:
    async def on_startup() -> dict[str, object]:
        return {
            "redis": redis,
            "rabbitmq": rabbit,
        }

    dp.startup.register(on_startup)

    async def on_shutdown() -> None:
        await redis.close()
        await rabbit.close()

    dp.shutdown.register(on_shutdown)
```

## Handler Signature

```python
from aiogram.types import Message
from src.bot.dependencies import RedisClient, RabbitMQClient


async def handle_photo(
    message: Message,
    redis: RedisClient,
    rabbitmq: RabbitMQClient,
) -> None:
    ...
```

Aiogram injects dependency values into handler parameters using the keys returned from startup.

## Guidelines

- Instantiate clients once during lifespan, not per handler.
- Add typing aliases for clarity (`type Redis = RedisClient` if needed).
- Compose services in factories (`get_photo_service(redis, rabbitmq)`) when handlers require higher-level abstractions.

## Testing

- Provide fakes directly in unit tests (handlers accept parameters explicitly).
- For integration tests, reuse real clients from Testcontainers and register them via the same mechanism.

## Related Documents

- `docs/atomic/services/aiogram/middleware-setup.md`
- `docs/atomic/services/aiogram/testing-strategies.md`
- Legacy reference: `docs/legacy/services/aiogram_rules.mdc`
