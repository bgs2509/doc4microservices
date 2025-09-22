# Example: Aiogram Business Service

This document demonstrates the implementation of a Telegram bot using Aiogram as a **Business Service**. The service has no direct database access and interacts with other system components through HTTP clients and message broker.

## Key Characteristics
- **Responsibility:** User interaction through Telegram, command and media file processing.
- **Data Access:** Only through HTTP calls to Data Services.
- **Communications:** Publishes events to RabbitMQ, can call other services via HTTP.

---

## 1. Project Structure (bot_service)

```
services/bot_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── bot/
│   │   ├── __init__.py
│   │   └── handlers.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── media_service.py
│   └── clients/
│       ├── __init__.py
│       └── user_data_client.py
└── Dockerfile
```

---

## 2. Handler Logic (`src/bot/handlers.py`)

Command and message handlers use HTTP client for data operations and service layer for business logic.

```python
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ..services.media_service import MediaService
from ..clients.user_data_client import UserDataClient

router = Router()
logger = logging.getLogger(__name__)

# Dependencies will be injected through middleware or factory
def get_media_service(**kwargs) -> MediaService:
    return MediaService(**kwargs)

def get_user_data_client() -> UserDataClient:
    return UserDataClient()

@router.message(Command("start"))
async def handle_start(message: Message):
    user_client = get_user_data_client()
    request_id = "some-request-id" # Should be generated in middleware

    # Check if user exists through Data Service
    user_data = await user_client.get_user_by_id(message.from_user.id, request_id)
    if not user_data:
        # If not, create user through Data Service
        create_payload = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "email": f"{message.from_user.id}@telegram.bot"
        }
        await user_client.create_user_from_bot(create_payload, request_id)
        await message.reply(f"Hello, new user {message.from_user.first_name}!")
    else:
        await message.reply(f"Welcome back, {message.from_user.first_name}!")

@router.message(F.photo)
async def handle_photo(message: Message, rabbitmq_channel, redis_client):
    media_service = get_media_service(
        rabbitmq_channel=rabbitmq_channel, 
        redis_client=redis_client
    )
    
    # Photo processing logic remains in service layer
    # This service will publish event to RabbitMQ for further processing by worker
    result = await media_service.process_photo_upload(
        user_id=message.from_user.id,
        photo=message.photo[-1]
    )

    if result["success"]:
        await message.reply(f"Photo accepted for processing! Task ID: {result['task_id']}")
    else:
        await message.reply("Failed to process photo.")
```

---

## 3. Service Layer (`src/services/media_service.py`)

The service is responsible for publishing events to RabbitMQ.

```python
import orjson
import aio_pika
import uuid

class MediaService:
    def __init__(self, rabbitmq_channel, redis_client):
        self.rabbitmq_channel = rabbitmq_channel
        self.redis_client = redis_client # Can be used for duplicate checking

    async def process_photo_upload(self, user_id: int, photo) -> dict:
        task_id = str(uuid.uuid4())
        message_body = orjson.dumps({
            "user_id": user_id,
            "file_id": photo.file_id,
            "file_size": photo.file_size,
            "task_id": task_id
        })

        message = aio_pika.Message(
            body=message_body,
            headers={"X-Request-ID": task_id}
        )

        # Publish task to queue for worker processing
        await self.rabbitmq_channel.default_exchange.publish(
            message,
            routing_key="media.process"
        )
        return {"success": True, "task_id": task_id}
```

---

## 4. Main Application File (`src/main.py`)

`main.py` initializes the bot, dispatcher, and dependencies such as RabbitMQ and Redis.

```python
import asyncio
import logging
import aio_pika
import redis.asyncio as redis
from aiogram import Bot, Dispatcher

from .bot import handlers
from .core.config import settings

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Initialize dependencies
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    rabbitmq_channel = await rabbitmq_connection.channel()

    # Inject dependencies into dispatcher
    dp["redis_client"] = redis_client
    dp["rabbitmq_channel"] = rabbitmq_channel

    dp.include_router(handlers.router)

    logger.info("Starting Bot service...")
    await dp.start_polling(bot)

    # Graceful shutdown
    await redis_client.close()
    await rabbitmq_connection.close()

if __name__ == "__main__":
    asyncio.run(main())
```
