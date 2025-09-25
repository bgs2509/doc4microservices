# Main Function Patterns

Workers own their event loop. The `main()` coroutine orchestrates configuration, dependency setup, task orchestration, and shutdown.

## Boilerplate

```python
from __future__ import annotations

import asyncio
import signal
from contextlib import AsyncExitStack
from src.worker.config import get_settings
from src.worker.dependencies import build_dependencies
from src.worker.task_runner import start_tasks, stop_tasks


async def main() -> None:
    settings = get_settings()
    stack = AsyncExitStack()

    async with stack:
        deps = await build_dependencies(settings, stack)
        stop_event = asyncio.Event()

        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_running_loop().add_signal_handler(sig, stop_event.set)

        tasks = await start_tasks(deps)

        await stop_event.wait()
        await stop_tasks(tasks)
```

## Guidelines

- Use `AsyncExitStack` to manage resources (redis connections, RabbitMQ channels).
- Register signal handlers once per process.
- Wrap main body with structured logging context to include request IDs for emitted events.
- Add health check hooks if the worker exposes metrics or status endpoints.

## Testing

- Unit-test `build_dependencies` with fakes.
- Integration-test `main()` via `asyncio.run(main())` in controlled environment; assert cleanup occurs when stop event is triggered.

## Related Documents

- `docs/atomic/services/asyncio-workers/signal-handling.md`
- `docs/atomic/services/asyncio-workers/task-management.md`
- Legacy reference: `docs/legacy/services/asyncio_rules.mdc`
