# Webhook Configuration

Webhook mode is recommended for production deployments behind HTTPS. The bot receives updates via FastAPI or another HTTP server.

## Architecture

```
Telegram → HTTPS → Webhook endpoint → Aiogram Dispatcher → Handlers
```

Use a lightweight FastAPI app to receive webhooks and forward them to the dispatcher running in the same process.

## Setup Steps

1. Expose a public HTTPS endpoint (NGINX, Cloudflare, AWS API Gateway).
2. Generate a secret path (`/webhook/<token-hash>`).
3. Register webhook with Telegram using `setWebhook`.
4. Verify SSL/TLS configuration.

## Example

```python
from __future__ import annotations

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from src.bot.factory import create_dispatcher


bot = Bot(token=settings.telegram_token)
dp = create_dispatcher(settings)
app = FastAPI()


@app.post(f"/webhook/{settings.webhook_secret}")
async def telegram_webhook(request: Request) -> dict[str, str]:
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"status": "ok"}
```

Run webhook server with Uvicorn; polling must be disabled.

## Operational Considerations

- Keep webhook endpoint stateless; rely on Redis/RabbitMQ for stateful operations.
- Validate the secret path to reject unauthorised requests.
- Gracefully handle retries by making handlers idempotent.
- Monitor delivery by inspecting Telegram webhook status (`getWebhookInfo`).

## Related Documents

- `docs/atomic/services/aiogram/bot-initialization.md`
- `docs/atomic/services/aiogram/handler-patterns.md`
