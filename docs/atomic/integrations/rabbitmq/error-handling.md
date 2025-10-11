# Error Handling

Robust messaging requires clear strategies for retries, dead letters, and alerting.

## Classification

- **Recoverable errors** – transient issues (network blips, temporary downstream failure). Requeue the message with backoff.
- **Fatal errors** – invalid payloads, schema mismatches. Reject without requeue and route to dead-letter queues.
- **Operational errors** – connection loss, channel closures. Reconnect and resume consumption.

## Implementation

```python
from aio_pika import IncomingMessage
from src.worker.exceptions import RecoverableError, FatalError


async def handle_payload(message: IncomingMessage) -> None:
    try:
        event = EventDTO.model_validate_json(message.body)
        await service.process(event)
    except RecoverableError as exc:
        await message.nack(requeue=True)
    except FatalError as exc:
        await message.reject(requeue=False)
        await dead_letter_store.save(message, reason=str(exc))
    else:
        await message.ack()
```

## Observability

- Log outcome with routing key, message id, and decision (`ack`, `nack`, `reject`).
- Emit Prometheus counters for retries and dead letters; trigger alerts when thresholds are exceeded.
- Capture failed payloads for later analysis (secure storage with TTL).

## Related Documents

- `docs/atomic/services/asyncio-workers/error-handling.md`
- `docs/atomic/integrations/rabbitmq/idempotency-patterns.md`
