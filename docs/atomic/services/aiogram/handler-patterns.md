# Handler Patterns

Handlers orchestrate domain services in response to Telegram updates. Keep them concise, deterministic, and idempotent.

## Basic Handler Structure

```python
from __future__ import annotations

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from src.bot.services.photo_service import PhotoService
from src.bot.dependencies import get_photo_service

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Hi! Send me a photo.")


@router.message()
async def handle_photo(
    message: Message,
    photo_service: PhotoService,
) -> None:
    await photo_service.process_photo(message)
```

## Principles

- Register handlers via routers, not directly on the dispatcher.
- Filter aggressively: use `F.photo`, `F.text`, or custom filters to avoid expensive branching inside handlers.
- Delegate domain logic to services (e.g., `PhotoService`).
- Propagate Request IDs via middleware; handlers should rely on context rather than generating their own IDs unless necessary.

## Error Handling

- Wrap domain/service exceptions and provide user-friendly Telegram responses.
- Log exceptions with context; avoid leaking secrets or internal IDs.
- Use fallback handlers (`router.errors.register`) for unhandled exceptions to notify users gracefully.

## Idempotency

- Use Redis to prevent duplicate processing (store message IDs keyed by user/chat).
- Check idempotency before downloading large files or publishing events.

## Related Documents

- `docs/atomic/services/aiogram/dependency-injection.md`
- `docs/atomic/services/aiogram/testing-strategies.md`
