## Inter-Service Communication Examples

### HTTP API to API Communication
```python
# In api_service: calling another API service using the shared HTTP client
from shared.http.base_client import DataServiceClient, HTTPNotFoundError, HTTPTimeoutError
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExternalAPIService(DataServiceClient):
    """Service for communicating with other APIs."""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(
            service_name="External API Service",
            base_url=base_url,
            timeout=timeout
        )

    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile from user service with proper error handling."""
        try:
            return await self.get(f"/api/v1/users/{user_id}")
        except HTTPNotFoundError:
            logger.info(f"User {user_id} not found")
            return None
        except HTTPTimeoutError:
            logger.error(f"Timeout getting user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting user {user_id}: {e}")
            return None
```

### Event-Driven Communication via RabbitMQ
```python
# Publishing events (in any service)
import aio_pika
import orjson
from datetime import datetime
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
