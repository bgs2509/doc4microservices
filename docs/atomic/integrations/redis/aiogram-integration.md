# Redis + Aiogram Integration

Aiogram relies on a single event loop, so Redis must be initialised once and injected into handlers via dispatcher startup hooks.

## Startup Hook

```python
from aiogram import Dispatcher
from redis.asyncio import Redis


def register_redis(dp: Dispatcher, redis: Redis) -> None:
    async def on_startup() -> dict[str, object]:
        await redis.ping()
        return {"redis": redis}

    dp.startup.register(on_startup)

    async def on_shutdown() -> None:
        await redis.close()

    dp.shutdown.register(on_shutdown)
```

## Handler Usage

```python
from aiogram.types import Message
from redis.asyncio import Redis


async def handle_photo(message: Message, redis: Redis) -> None:
    key = f"idempotency:photo:{message.message_id}"
    if await redis.setnx(key, "processed"):
        await redis.expire(key, 3600)
        await message.answer("Photo accepted")
    else:
        await message.answer("Duplicate photo")
```

## Testing

- Provide fakes or Testcontainers Redis inside integration tests and register them with `register_redis`.
- Use Aiogram testing utilities to verify dependency injection.

## Related Documents

- `docs/atomic/services/aiogram/dependency-injection.md`
- `docs/atomic/integrations/redis/idempotency-patterns.md`
