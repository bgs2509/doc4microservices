# RabbitMQ + Aiogram Integration

Use dispatcher startup/shutdown callbacks to manage RabbitMQ connections inside bot services.

## Startup Hook

```python
from aio_pika import connect_robust
from aiogram import Dispatcher


def register_rabbitmq(dp: Dispatcher, url: str) -> None:
    connection_ref: dict[str, object] = {}

    async def on_startup() -> dict[str, object]:
        connection = await connect_robust(url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        connection_ref["connection"] = connection
        connection_ref["channel"] = channel
        return {"rabbitmq": channel}

    async def on_shutdown() -> None:
        await connection_ref["channel"].close()
        await connection_ref["connection"].close()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
```

Handlers receive the channel via dependency injection (`async def handle(message, rabbitmq)`), allowing them to publish or acknowledge messages without opening new connections.

## Testing

- Replace the startup hook with a fake channel when unit testing handlers.
- Use Testcontainers RabbitMQ for integration tests to validate publishing and consuming behaviour.

## Related Documents

- `docs/atomic/services/aiogram/dependency-injection.md`
- `docs/atomic/integrations/rabbitmq/testing-patterns.md`
- Legacy reference: `docs/legacy/infrastructure/rabbitmq_rules.mdc`
