# Bot Initialization

Correct bot and dispatcher setup ensures single event loop ownership and predictable lifecycle management.

## Lifespan Pattern

```python
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from src.bot.config import Settings
from src.bot.dependencies import RedisClient, RabbitMQClient


def build_lifespan(settings: Settings, dp: Dispatcher):
    @asynccontextmanager
    async def lifespan(bot: Bot):
        redis = RedisClient(settings.redis_url)
        rabbit = RabbitMQClient(settings.rabbitmq_url)

        await redis.connect()
        await rabbit.connect()

        dp.startup.register(lambda: {"redis": redis, "rabbitmq": rabbit})
        dp.shutdown.register(redis.close)
        dp.shutdown.register(rabbit.close)

        try:
            await dp.start_polling(bot)
            yield
        finally:
            await dp.storage.close()  # if storage is used

    return lifespan
```

## Guidelines

- Initialise Bot with connection pooling (`session=ClientSession()` when using custom HTTP settings).
- Configure logging before starting polling to capture early failures.
- Use `asyncio.run()` only in the main module.
- Register signal handlers to cancel polling gracefully (Aiogram handles this internally, but explicit logging helps).

## Webhook Mode

See `webhook-configuration.md` for production webhook setups when polling is not acceptable.

## Related Documents

- `docs/atomic/services/aiogram/dependency-injection.md`
- `docs/atomic/architecture/event-loop-management.md`
- Legacy reference: `docs/legacy/services/aiogram_rules.mdc`
