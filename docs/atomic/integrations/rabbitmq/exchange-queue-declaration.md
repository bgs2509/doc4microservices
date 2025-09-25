# Exchange and Queue Declaration

Declare exchanges and queues explicitly at startup to guarantee consistent topology across environments.

## Pattern

```python
from aio_pika import ExchangeType


async def ensure_topology(channel):
    exchange = await channel.declare_exchange(
        "photos.events",
        ExchangeType.TOPIC,
        durable=True,
    )

    queue = await channel.declare_queue(
        "q.file_handling.photo_received",
        durable=True,
    )

    await queue.bind(exchange, routing_key="photo.received")
    return exchange, queue
```

## Guidelines

- Use durable exchanges/queues unless the workload is truly transient.
- Prefer `topic` exchanges for routing flexibility; document routing keys.
- Keep naming consistent: `<domain>.<event>` for routing keys, `q.<service>.<purpose>` for queues.
- Declare dead-letter queues for failure scenarios and bind them with explicit routing keys.

## Infrastructure as Code

- Reflect the same topology in Terraform/Helm or automation scripts to avoid drift.
- Record the exchange/queue mapping in documentation for consumers.

## Related Documents

- `docs/atomic/integrations/rabbitmq/message-publishing.md`
- `docs/atomic/integrations/rabbitmq/message-consuming.md`
- Legacy reference: `docs/legacy/infrastructure/rabbitmq_rules.mdc`
