# Error Handling

Workers process asynchronous jobs where failure semantics differ from HTTP services. Handle exceptions thoughtfully to preserve message guarantees.

## Principles

- Treat expected business errors separately from infrastructure failures.
- Log errors with structured metadata (request ID, message ID, retry count).
- Decide on retry vs. dead-letter behaviour per queue.

## Pattern

```python
from __future__ import annotations

import asyncio
from src.worker.metrics import WorkerMetrics
from src.worker.exceptions import RecoverableError, FatalError


class PhotoConsumer:
    async def run(self) -> None:
        async for message in self.queue.consume():
            request_id = message.headers.get("x-request-id")
            try:
                await self.handle_message(message, request_id)
            except RecoverableError as exc:
                await message.nack(requeue=True)
                WorkerMetrics.retries.inc()
            except FatalError as exc:
                await message.reject(requeue=False)
                WorkerMetrics.dead_letters.inc()
            except Exception:
                await message.reject(requeue=False)
                raise
            else:
                await message.ack()
```

## Guidelines

- Use idempotency keys to avoid duplicate processing when requeueing.
- Wrap external calls with retries/backoff; raise `RecoverableError` for transient issues.
- Convert unexpected exceptions into alerts; allow orchestrator to restart worker if necessary.
- Ensure `CancelledError` is propagated during shutdown (do not swallow it).

## Monitoring

- Emit metrics for processed/failed/retried messages.
- Add structured logs with `reason=...` to speed up post-incident analysis.

## Related Documents

- `docs/atomic/services/asyncio-workers/task-management.md`
- `docs/atomic/observability/logging/log-correlation.md`
