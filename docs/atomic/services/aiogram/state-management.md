# State Management

Aiogram's FSM helps track conversational state. Use it sparingly and persist state externally when resilience is required.

## Setup

```python
from __future__ import annotations

from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram import Dispatcher


class PhotoFlow(StatesGroup):
    waiting_for_caption = State()


def configure_state(dp: Dispatcher, redis_url: str) -> None:
    storage = RedisStorage.from_url(redis_url)
    dp.storage = storage
```

## Usage

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.bot.states import PhotoFlow

router = Router()


@router.message(F.photo)
async def ask_for_caption(message: Message, state: FSMContext) -> None:
    await state.set_state(PhotoFlow.waiting_for_caption)
    await message.answer("Please provide a caption.")


@router.message(PhotoFlow.waiting_for_caption)
async def receive_caption(message: Message, state: FSMContext) -> None:
    caption = message.text or ""
    await state.clear()
    await message.answer(f"Received caption: {caption}")
```

## Guidelines

- Store minimal data in the FSM; large payloads belong in Redis or database services.
- Clean up state transitions (`await state.clear()`) to prevent stale sessions.
- Combine state with idempotency checks to avoid repeated processing after restarts.
- Persist FSM storage in Redis or database to survive restarts; in-memory storage is acceptable only for development.

## Related Documents

- `docs/atomic/services/aiogram/dependency-injection.md`
- `docs/atomic/integrations/redis/key-naming-conventions.md`
