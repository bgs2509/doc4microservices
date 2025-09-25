# RabbitMQ Connection Management

Use `aio-pika.connect_robust` to create resilient connections and channels that survive broker restarts.

## Bootstrap

```python
from aio_pika import connect_robust


async def build_connection(url: str):
    connection = await connect_robust(url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=50)
    return connection, channel
```

- Create the connection at service startup (FastAPI lifespan, Aiogram startup, worker `main()`).
- Store the channel in application state or a dependency container.
- Close connection and channel on shutdown to flush acknowledgements.

## Reliability

- Enable publisher confirms (`await channel.set_qos(...)` plus `mandatory=True` when publishing) for critical events.
- Use reconnection loops with exponential backoff when the broker is unavailable.
- Monitor heartbeat timeouts and adjust according to network latency.

## Observability

- Log connection lifecycle events with request IDs when available.
- Expose metrics for publish/consume rates, retries, and connection state.

## Related Documents

- `docs/atomic/integrations/rabbitmq/exchange-queue-declaration.md`
- `docs/atomic/services/asyncio-workers/dependency-management.md`
- Legacy reference: `docs/legacy/infrastructure/rabbitmq_rules.mdc`
