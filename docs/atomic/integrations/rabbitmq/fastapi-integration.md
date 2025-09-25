# RabbitMQ + FastAPI Integration

Manage RabbitMQ connections through FastAPI lifespan hooks and expose them via dependencies.

## Lifespan Setup

```python
from aio_pika import connect_robust


def build_lifespan(settings):
    async def startup(app):
        connection = await connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=20)
        app.state.rabbitmq_connection = connection
        app.state.rabbitmq_channel = channel

    async def shutdown(app):
        await app.state.rabbitmq_channel.close()
        await app.state.rabbitmq_connection.close()

    return startup, shutdown
```

## Dependency Provider

```python
from fastapi import Depends, Request
from aio_pika import Channel


def get_rabbitmq_channel(request: Request) -> Channel:
    return request.app.state.rabbitmq_channel
```

- Inject the channel into application services (`Depends(get_rabbitmq_channel)`).
- Encapsulate publish/consume helpers to keep routers clean.
- Ensure the channel is reused; never open a new connection per request.

## Testing

- Override `get_rabbitmq_channel` to supply fakes during unit tests.
- Use Testcontainers RabbitMQ for integration tests to validate publishing/consuming behaviour.

## Related Documents

- `docs/atomic/services/fastapi/lifespan-management.md`
- `docs/atomic/integrations/rabbitmq/testing-patterns.md`
- Legacy reference: `docs/legacy/infrastructure/rabbitmq_rules.mdc`
