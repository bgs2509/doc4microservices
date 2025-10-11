# Message Consuming

Consumers must acknowledge messages explicitly and implement retry/dead-letter policies.

## Example

```python
from aio_pika import IncomingMessage
from contextlib import suppress


async def consume(queue):
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(requeue=False):
                await handle_payload(message)
```

`message.process()` automatically acknowledges on successful completion and rejects on exceptions.

## Guidelines

- Wrap business logic in try/except and raise domain-specific errors to control requeue behaviour.
- Set QoS (`prefetch_count`) to balance throughput and fairness among consumers.
- Use dead-letter queues for failed messages that should not be retried automatically.
- Preserve idempotency by checking Redis or database state before applying side effects.

## Observability

- Log message IDs, routing keys, and request IDs.
- Emit metrics for processed, retried, and dead-lettered messages.

## Related Documents

- `docs/atomic/services/asyncio-workers/error-handling.md`
- `docs/atomic/integrations/rabbitmq/error-handling.md`
