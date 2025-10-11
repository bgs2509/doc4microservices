# AsyncIO Worker Basic Setup

AsyncIO worker services run background jobs outside of HTTP request cycles. This guide covers the minimum bootstrap.

## Directory Layout

```
src/
├── worker/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── photo_consumer.py
│   └── services/
│       └── photo_processor.py
└── shared/
    └── events/
        └── photo_received.py
```

## Dependencies

```toml
[project.dependencies]
aio-pika = "^9.4"
redis = "^5.0"
asyncpg = "^0.29"  # optional
pydantic = "^2.8"
```

## Entry Point (`main.py`)

```python
from __future__ import annotations

import asyncio
from contextlib import suppress
from src.worker.bootstrap import bootstrap


async def main() -> None:
    await bootstrap()


if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
```

`bootstrap()` connects to Redis/RabbitMQ, configures logging, and launches consumer tasks (see `task-management.md`).

## Checklist

- [ ] `asyncio.run(main())` invoked only in `__main__` guard.
- [ ] Configuration loaded before logging.
- [ ] External clients instantiated once and passed to tasks.
- [ ] Signal handlers registered to stop gracefully.

## Related Documents

- `docs/atomic/services/asyncio-workers/main-function-patterns.md`
- `docs/atomic/architecture/event-loop-management.md`
