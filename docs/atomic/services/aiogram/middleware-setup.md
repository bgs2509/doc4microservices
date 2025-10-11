# Middleware Setup

Middleware is the right place to inject cross-cutting concerns such as request IDs, tracing, and dependency context.

## Request ID Middleware

```python
from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Any, Awaitable, Callable
from src.core.logging import generate_request_id, set_request_id


class RequestIDMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        request_id = generate_request_id(
            "tg",
            user_id=getattr(event.message.from_user, "id", None),
            chat_id=getattr(event.message.chat, "id", None),
        )
        set_request_id(request_id)
        data["request_id"] = request_id

        return await handler(event, data)
```

Register during startup:

```python
from src.bot.middlewares.request_id import RequestIDMiddleware

dp.update.middleware(RequestIDMiddleware())
```

## Dependency Middleware

- Use startup hooks (`dp.startup.register`) to inject Redis/RabbitMQ clients into handler data.
- Optionally use middleware to fetch contextual data (user profile, feature flags) in a cached manner.

## Ordering

- Request ID middleware should run first.
- Authentication middleware (if any) should precede handlers that depend on user context.
- Rate limiting middleware should run after request ID to reuse correlation IDs in logs.

## Testing

- Use Aiogram test utilities to assert middleware attaches `request_id`.
- Ensure middleware is excluded or adjusted in unit tests to keep them deterministic.

## Related Documents

- `docs/atomic/services/aiogram/handler-patterns.md`
- `docs/atomic/observability/logging/request-id-tracking.md`
