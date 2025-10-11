# RabbitMQ + AsyncIO Integration

AsyncIO worker services own their event loop and should create one RabbitMQ connection per process.

## Bootstrap

```python
from aio_pika import connect_robust


async def bootstrap_rabbitmq(url: str):
    connection = await connect_robust(url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=50)
    return connection, channel
```

- Store the connection/channel in a dataclass along with other dependencies.
- Close them in the shutdown sequence to release broker resources.

## Consumers

- Run consumers inside `asyncio.TaskGroup` and propagate cancellation.
- Handle recoverable errors by `message.nack(requeue=True)`; dead-letter fatal messages.
- Combine with Redis idempotency when duplicate deliveries would cause side effects.

## Testing

- Use Testcontainers RabbitMQ to drive integration tests end-to-end.
- For unit tests, mock the channel interface (`publish`, `default_exchange`) with `AsyncMock`.

## Related Documents

- `docs/atomic/services/asyncio-workers/main-function-patterns.md`
- `docs/atomic/integrations/rabbitmq/testing-patterns.md`
