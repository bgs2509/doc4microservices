## Inter-Service Communication Examples

### HTTP API to API Communication
```python
# In api_service: calling another API service
import httpx
from typing import Optional, Dict, Any

class ExternalAPIService:
    """Service for communicating with other APIs."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout

    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile from user service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={"X-Request-ID": "unique-request-id"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting user {user_id}: {e}")
                return None
            except Exception as e:
                logger.error(f"Error getting user {user_id}: {e}")
                return None
```

### Event-Driven Communication via RabbitMQ
```python
# Publishing events (in any service)
async def publish_user_updated_event(
    rabbitmq_channel: aio_pika.Channel,
    user_id: int,
    changes: Dict[str, Any]
) -> None:
    """Publish user updated event."""
    event_data = {
        "event_type": "user.updated",
        "user_id": user_id,
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api_service",
    }

    message = aio_pika.Message(
        orjson.dumps(event_data),
        headers={
            "event_type": "user.updated",
            "user_id": str(user_id),
        },
    )

    exchange = await rabbitmq_channel.declare_exchange(
        "user_events",
        aio_pika.ExchangeType.TOPIC
    )

    await exchange.publish(message, routing_key="user.updated")

# Consuming events (in worker service)
async def setup_event_consumer(rabbitmq_channel: aio_pika.Channel) -> None:
    """Setup event consumer for user events."""
    exchange = await rabbitmq_channel.declare_exchange(
        "user_events",
        aio_pika.ExchangeType.TOPIC
    )

    queue = await rabbitmq_channel.declare_queue(
        "notifications.user_events",
        durable=True
    )

    await queue.bind(exchange, routing_key="user.*")

    async def process_user_event(message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            event_data = orjson.loads(message.body)
            event_type = event_data["event_type"]

            if event_type == "user.updated":
                await handle_user_updated(event_data)
            elif event_type == "user.created":
                await handle_user_created(event_data)

    await queue.consume(process_user_event)
```
