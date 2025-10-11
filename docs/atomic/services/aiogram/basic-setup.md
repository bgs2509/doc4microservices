# Aiogram Basic Setup

This file captures the minimal scaffold for an Aiogram-based Telegram bot service operating within the Improved Hybrid Approach.

## Prerequisites

- Python 3.12+
- `aiogram>=3.4`
- Access to Telegram bot token (stored in secrets, not in code)
- Redis and RabbitMQ endpoints provided via settings

## Project Skeleton

```
src/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── photos.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── request_id.py
│   └── services/
│       ├── __init__.py
│       └── photo_service.py
├── shared/
│   └── dtos/
│       └── photo_payload.py
└── tests/
```

## Dependencies

```toml
[project.dependencies]
aiogram = "^3.4"
redis = "^5.0"
aio-pika = "^9.4"
httpx = "^0.27"
```

## Entry Point

```python
from __future__ import annotations

import asyncio
from aiogram import Bot, Dispatcher
from src.bot.config import get_settings
from src.bot.handlers import register_handlers
from src.bot.lifespan import build_lifespan


def main() -> None:
    settings = get_settings()
    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher()

    register_handlers(dp)

    lifespan = build_lifespan(settings, dp)

    asyncio.run(lifespan(bot, dp))


if __name__ == "__main__":
    main()
```

## Checklist

- [ ] Bot token sourced from configuration, never hard-coded.
- [ ] Dispatcher and Bot initialised exactly once.
- [ ] Handlers are registered via dedicated function to maintain clarity.
- [ ] Lifespan handles Redis/RabbitMQ setup (see `bot-initialization.md`).

## Related Documents

- `docs/atomic/services/aiogram/bot-initialization.md`
- `docs/atomic/architecture/service-separation-principles.md`
