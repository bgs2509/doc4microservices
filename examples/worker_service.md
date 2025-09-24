# Example: Worker Business Service

This document demonstrates the implementation of a background processor (Worker) as a **Business Service**. It has no direct database access and interacts with other system components through HTTP calls (to Data Services) and message broker (RabbitMQ).

## Key Characteristics
- **Responsibility:** Execution of background tasks such as media file processing, notification sending, or data analysis.
- **Data Access:** Only through HTTP clients.
- **Communications:** Receives tasks from RabbitMQ and can call other services via HTTP.

---

## 1. Project Structure (worker_service)

```
services/worker_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── workers/
│   │   ├── __init__.py
│   │   └── media_processor.py
│   └── clients/
│       ├── __init__.py
│       └── user_data_client.py
└── Dockerfile
```

---

## 2. Worker Logic (`src/workers/media_processor.py`)

The worker receives messages from RabbitMQ and uses HTTP client to update information in the database through Data Service.

```python
import asyncio
import logging
import uuid
import aio_pika
import orjson

from shared.http.base_client import DataServiceClient, HTTPNotFoundError
from ..core.config import settings

logger = logging.getLogger(__name__)

class UserDataClient(DataServiceClient):
    """Client for PostgreSQL Data Service communication."""

    def __init__(self):
        super().__init__(
            service_name="PostgreSQL Data Service",
            base_url=settings.POSTGRES_DATA_SERVICE_URL,
            timeout=settings.HTTP_CLIENT_TIMEOUT,
            retries=settings.HTTP_CLIENT_RETRIES
        )

    async def update_user_files(self, user_id: int, update_payload: dict, request_id: str):
        """Update user files data."""
        try:
            return await self.patch(f"/api/v1/users/{user_id}/files", json=update_payload)
        except HTTPNotFoundError:
            return None

class MediaProcessor:
    def __init__(self, rabbitmq_channel: aio_pika.Channel):
        self.rabbitmq_channel = rabbitmq_channel
        self.user_client = UserDataClient() # Initialize HTTP client

    async def start(self):
        queue = await self.rabbitmq_channel.declare_queue("media.process", durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self._process_message(message)

    async def _process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                data = orjson.loads(message.body)
                user_id = data.get("user_id")
                file_info = data.get("file_info")
                request_id = message.headers.get("X-Request-ID", f"worker_{uuid.uuid4().hex}")

                if not all([user_id, file_info]):
                    logger.error("Invalid message data")
                    return

                logger.info(f"Processing media for user {user_id}")

                # File processing logic...
                processed_result = {"status": "processed", "path": "/path/to/processed/file"}

                # Update user status through Data Service via HTTP
                # For example, add information about new file
                update_payload = {"new_file": processed_result}
                update_success = await self.user_client.update_user_files(user_id, update_payload, request_id)

                if update_success:
                    logger.info(f"Successfully updated user {user_id} via data service.")
                else:
                    logger.error(f"Failed to update user {user_id} via data service.")

            except Exception as e:
                logger.error(f"Error processing message: {e}")
```

---

## 3. Main Application File (`src/main.py`)

`main.py` is responsible for starting the worker and managing its lifecycle.

```python
import asyncio
import logging
import signal
import aio_pika

from .core.config import settings
from .workers.media_processor import MediaProcessor

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Worker service...")

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    media_processor = MediaProcessor(channel)
    
    loop = asyncio.get_event_loop()
    worker_task = loop.create_task(media_processor.start())

    # Graceful shutdown
    def shutdown():
        logger.info("Shutdown signal received.")
        worker_task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    finally:
        await connection.close()
        logger.info("Worker service stopped.")

if __name__ == "__main__":
    asyncio.run(main())
```