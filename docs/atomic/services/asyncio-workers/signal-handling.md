# Signal Handling

Graceful shutdown prevents data loss and avoids orphaned tasks. Workers must listen for POSIX signals and stop cleanly.

## Implementation

```python
from __future__ import annotations

import asyncio
import signal
from typing import Iterable


def register_signal_handlers(loop: asyncio.AbstractEventLoop, stop_event: asyncio.Event) -> None:
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)


def unregister_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.remove_signal_handler(sig)
```

Usage in `main()`:

```python
stop_event = asyncio.Event()
loop = asyncio.get_running_loop()
register_signal_handlers(loop, stop_event)

try:
    await stop_event.wait()
finally:
    unregister_signal_handlers(loop)
```

## Shutdown Workflow

1. Signal handler sets `stop_event`.
2. Long-running tasks check `stop_event.is_set()` and exit loops.
3. Consumers acknowledge in-flight messages and close connections.
4. Resources disposed (RabbitMQ, Redis, DB) via `AsyncExitStack` or explicit closures.
5. Log `worker_shutdown_completed` with context for observability.

## Testing

- Simulate signals in integration tests (`os.kill(os.getpid(), signal.SIGTERM)` inside subprocess).
- Assert tasks cancel gracefully without raising unhandled exceptions.

## Related Documents

- `docs/atomic/services/asyncio-workers/task-management.md`
- `docs/atomic/observability/logging/structured-logging.md`
- Legacy reference: `docs/legacy/services/asyncio_rules.mdc`
