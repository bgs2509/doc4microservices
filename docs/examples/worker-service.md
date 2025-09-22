## AsyncIO Worker Service Example

### Complete Background Processing Worker

#### Project Structure
```
services/worker_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── media_processor.py
│   │   ├── notification_sender.py
│   │   └── data_analyzer.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py
│   │   └── notification_service.py
│   └── utils/
│       ├── __init__.py
│       └── retry.py
├── tests/
├── pyproject.toml
└── Dockerfile
```

#### main.py
```python
from __future__ import annotations

import asyncio
import logging
import signal
from typing import Dict, Any, Callable
import os

import redis.asyncio as redis
import aio_pika

from .core.config import settings
from .workers.media_processor import MediaProcessor
from .workers.notification_sender import NotificationSender
from .workers.data_analyzer import DataAnalyzer

logger = logging.getLogger(__name__)


class WorkerService:
    """Main worker service coordinator."""

    def __init__(self) -> None:
        self.redis_client: redis.Redis | None = None
        self.rabbitmq_connection: aio_pika.Connection | None = None
        self.rabbitmq_channel: aio_pika.Channel | None = None
        self.workers: Dict[str, Any] = {}
        self.running = False

    async def setup(self) -> None:
        """Setup external connections and workers."""
        # Setup Redis
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
        await self.redis_client.ping()
        logger.info("Redis connection established")

        # Setup RabbitMQ
        self.rabbitmq_connection = await aio_pika.connect_robust(
            settings.RABBITMQ_URL,
            client_properties={"connection_name": "worker_service"}
        )
        self.rabbitmq_channel = await self.rabbitmq_connection.channel()
        await self.rabbitmq_channel.set_qos(prefetch_count=10)
        logger.info("RabbitMQ connection established")

        # Setup workers
        self.workers = {
            "media_processor": MediaProcessor(self.redis_client, self.rabbitmq_channel),
            "notification_sender": NotificationSender(self.redis_client, self.rabbitmq_channel),
            "data_analyzer": DataAnalyzer(self.redis_client, self.rabbitmq_channel),
        }

        logger.info(f"Initialized {len(self.workers)} workers")

    async def start_workers(self) -> None:
        """Start all workers."""
        self.running = True
        tasks = []

        for worker_name, worker in self.workers.items():
            task = asyncio.create_task(
                worker.start(),
                name=f"worker-{worker_name}"
            )
            tasks.append(task)
            logger.info(f"Started worker: {worker_name}")

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Workers cancelled")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            raise

    async def stop_workers(self) -> None:
        """Stop all workers gracefully."""
        self.running = False

        # Stop workers
        for worker_name, worker in self.workers.items():
            try:
                await worker.stop()
                logger.info(f"Stopped worker: {worker_name}")
            except Exception as e:
                logger.error(f"Error stopping worker {worker_name}: {e}")

        # Close connections
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

        if self.rabbitmq_channel:
            await self.rabbitmq_channel.close()

        if self.rabbitmq_connection:
            await self.rabbitmq_connection.close()
            logger.info("RabbitMQ connection closed")


async def main() -> None:
    """Main function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    worker_service = WorkerService()

    # Setup graceful shutdown
    def shutdown_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(worker_service.stop_workers())

    signal.signal(signal.SIGINT, lambda s, f: shutdown_handler())
    signal.signal(signal.SIGTERM, lambda s, f: shutdown_handler())

    try:
        await worker_service.setup()
        logger.info("Starting worker service...")
        await worker_service.start_workers()
    except Exception as e:
        logger.error(f"Worker service error: {e}")
        raise
    finally:
        await worker_service.stop_workers()


if __name__ == "__main__":
    asyncio.run(main())
```

#### Media Processor Worker
```python
# src/workers/media_processor.py
from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any
import json
from io import BytesIO

import redis.asyncio as redis
import aio_pika
from PIL import Image
import orjson

from ..services.image_service import ImageService
from ..utils.retry import with_retry

logger = logging.getLogger(__name__)


class MediaProcessor:
    """Worker for processing media files."""

    def __init__(self, redis_client: redis.Redis, rabbitmq_channel: aio_pika.Channel) -> None:
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.image_service = ImageService()
        self.running = False

    async def start(self) -> None:
        """Start processing media files."""
        self.running = True

        # Declare exchange and queue
        exchange = await self.rabbitmq_channel.declare_exchange(
            "media_processing",
            aio_pika.ExchangeType.DIRECT
        )

        queue = await self.rabbitmq_channel.declare_queue(
            "media.process",
            durable=True
        )

        await queue.bind(exchange, routing_key="media.process")

        # Start consuming
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self.running:
                    break

                await self._process_message(message)

    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
        logger.info("Media processor stopped")

    async def _process_message(self, message: aio_pika.IncomingMessage) -> None:
        """Process a single message."""
        async with message.process():
            try:
                # Parse message
                data = orjson.loads(message.body)
                processing_id = data.get("processing_id")
                file_data = data.get("file_data")
                file_type = data.get("file_type", "image")
                user_id = data.get("user_id")

                if not all([processing_id, file_data, user_id]):
                    logger.error("Invalid message data")
                    return

                logger.info(f"Processing media: {processing_id}")

                # Update status
                await self._update_processing_status(processing_id, "processing")

                # Process based on file type
                if file_type == "image":
                    result = await self._process_image(file_data, processing_id, user_id)
                else:
                    result = {"success": False, "error": f"Unsupported file type: {file_type}"}

                # Update final status
                if result["success"]:
                    await self._update_processing_status(processing_id, "completed", result)
                    await self._publish_completion_event(processing_id, user_id, result)
                else:
                    await self._update_processing_status(processing_id, "failed", result)

                logger.info(f"Completed processing: {processing_id}")

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                processing_id = data.get("processing_id") if 'data' in locals() else "unknown"
                await self._update_processing_status(processing_id, "failed", {"error": str(e)})

    @with_retry(max_attempts=3, delay=1.0)
    async def _process_image(self, file_data: bytes, processing_id: str, user_id: int) -> Dict[str, Any]:
        """Process image file."""
        try:
            # Open image
            image = Image.open(BytesIO(file_data))

            # Generate thumbnail
            thumbnail = await self.image_service.create_thumbnail(image, (200, 200))

            # Compress image
            compressed = await self.image_service.compress_image(image, quality=85)

            # Extract metadata
            metadata = await self.image_service.extract_metadata(image)

            # Save processed files to storage (Redis for demo)
            thumbnail_key = f"thumbnail:{processing_id}"
            compressed_key = f"compressed:{processing_id}"

            await self.redis_client.setex(thumbnail_key, 86400, thumbnail)  # 24h TTL
            await self.redis_client.setex(compressed_key, 86400, compressed)  # 24h TTL

            return {
                "success": True,
                "thumbnail_key": thumbnail_key,
                "compressed_key": compressed_key,
                "metadata": metadata,
                "original_size": len(file_data),
                "compressed_size": len(compressed),
                "compression_ratio": len(compressed) / len(file_data),
            }

        except Exception as e:
            logger.error(f"Error processing image {processing_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _update_processing_status(
        self,
        processing_id: str,
        status: str,
        result: Dict[str, Any] | None = None
    ) -> None:
        """Update processing status in Redis."""
        status_key = f"processing:{processing_id}"
        status_data = {
            "status": status,
            "updated_at": asyncio.get_event_loop().time(),
        }

        if result:
            status_data["result"] = result

        await self.redis_client.setex(
            status_key,
            3600,  # 1 hour TTL
            orjson.dumps(status_data)
        )

    async def _publish_completion_event(
        self,
        processing_id: str,
        user_id: int,
        result: Dict[str, Any]
    ) -> None:
        """Publish processing completion event."""
        event_data = {
            "event_type": "media.processing.completed",
            "processing_id": processing_id,
            "user_id": user_id,
            "result": result,
            "timestamp": asyncio.get_event_loop().time(),
        }

        message = aio_pika.Message(
            orjson.dumps(event_data),
            headers={"event_type": "media.processing.completed"},
        )

        exchange = await self.rabbitmq_channel.declare_exchange(
            "events",
            aio_pika.ExchangeType.TOPIC
        )

        await exchange.publish(message, routing_key="media.processing.completed")
        logger.info(f"Published completion event for processing: {processing_id}")
```
