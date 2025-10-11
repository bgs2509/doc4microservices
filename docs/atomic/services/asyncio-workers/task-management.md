# Task Management

Manage background tasks explicitly to avoid orphaned coroutines and to ensure proper shutdown.

## Launching Tasks

```python
from __future__ import annotations

import asyncio
from typing import Iterable
from src.worker.consumers import PhotoConsumer


async def start_tasks(deps) -> list[asyncio.Task[None]]:
    consumer = PhotoConsumer(deps.rabbitmq, deps.redis)
    task = asyncio.create_task(consumer.run(), name="photo-consumer")
    return [task]
```

## Coordinating Shutdown

```python
async def stop_tasks(tasks: Iterable[asyncio.Task[None]]) -> None:
    for task in tasks:
        task.cancel()

    for task in tasks:
        try:
            await task
        except asyncio.CancelledError:
            continue
```

## Supervising Loops

- Use `asyncio.TaskGroup` (Python 3.12+) to supervise multiple consumers.
- Ensure tasks periodically check `asyncio.current_task().cancelled()` or a shared `stop_event`.
- Log task lifecycle events (`task_started`, `task_cancelled`, `task_failed`).

## Backpressure & Concurrency

- Limit concurrency via worker pools or semaphores when processing heavy workloads.
- Implement retry/backoff inside consumers for transient failures.
- For RabbitMQ, use QoS to control message prefetch.

## Related Documents

- `docs/atomic/services/asyncio-workers/error-handling.md`
- `docs/atomic/architecture/event-loop-management.md`
