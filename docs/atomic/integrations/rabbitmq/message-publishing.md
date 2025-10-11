# Message Publishing

Publish messages using `aio-pika.Exchange.publish` with persistent delivery and structured headers.

## Example

```python
from aio_pika import Message, DeliveryMode
import json


async def publish_photo_received(exchange, payload, request_id: str) -> None:
    body = json.dumps(payload.model_dump()).encode()
    message = Message(
        body=body,
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
        headers={"x-request-id": request_id},
    )
    await exchange.publish(message, routing_key="photo.received", mandatory=True)
```

## Guidelines

- Serialize payloads with Pydantic DTOs to guarantee schema consistency.
- Include tracing headers (`x-request-id`, `traceparent`) for observability.
- Use publisher confirms to detect broker-side failures; retry with exponential backoff when publish fails.
- Avoid blocking the event loop; publish asynchronously and batch when necessary.

## Testing

- Assert messages reach the correct exchange/routing key using Testcontainers RabbitMQ and queue inspection.
- Validate headers and delivery mode in unit tests via `Message` inspection.

## Related Documents

- `docs/atomic/integrations/rabbitmq/dto-contracts.md`
- `docs/atomic/integrations/rabbitmq/idempotency-patterns.md`
