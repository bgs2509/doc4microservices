## Aiogram Bot Service Example

### Complete Telegram Bot with Media Processing

#### Project Structure
```
services/bot_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── start.py
│   │   │   ├── media.py
│   │   │   └── user.py
│   │   ├── middlewares/
│   │   │   ├── __init__.py
│   │   │   └── logging.py
│   │   └── filters/
│   │       ├── __init__.py
│   │       └── admin.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── dependencies.py
│   └── services/
│       ├── __init__.py
│       ├── media_service.py
│       └── user_service.py
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
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import redis.asyncio as redis
import aio_pika

from .core.config import settings
from .core.dependencies import setup_dependencies
from .bot.handlers import start, media, user
from .bot.middlewares.logging import LoggingMiddleware

logger = logging.getLogger(__name__)


async def setup_bot() -> tuple[Bot, Dispatcher]:
    """Setup bot and dispatcher."""
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Add middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Include routers
    dp.include_router(start.router)
    dp.include_router(media.router)
    dp.include_router(user.router)

    return bot, dp


async def setup_external_services() -> tuple[redis.Redis, aio_pika.Connection, aio_pika.Channel]:
    """Setup external service connections."""
    # Redis
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
    )
    await redis_client.ping()
    logger.info("Redis connection established")

    # RabbitMQ
    rabbitmq_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL,
        client_properties={"connection_name": "bot_service"}
    )
    rabbitmq_channel = await rabbitmq_connection.channel()
    logger.info("RabbitMQ connection established")

    return redis_client, rabbitmq_connection, rabbitmq_channel


async def shutdown_handler(
    redis_client: redis.Redis,
    rabbitmq_connection: aio_pika.Connection,
    rabbitmq_channel: aio_pika.Channel,
) -> None:
    """Graceful shutdown handler."""
    logger.info("Shutting down bot service...")

    # Close external connections
    await redis_client.close()
    await rabbitmq_channel.close()
    await rabbitmq_connection.close()

    logger.info("Bot service shutdown complete")


async def main() -> None:
    """Main function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup external services
    redis_client, rabbitmq_connection, rabbitmq_channel = await setup_external_services()

    # Setup bot
    bot, dp = await setup_bot()

    # Setup dependencies
    setup_dependencies(dp, redis_client, rabbitmq_channel)

    # Setup graceful shutdown
    def signal_handler():
        asyncio.create_task(shutdown_handler(redis_client, rabbitmq_connection, rabbitmq_channel))

    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await shutdown_handler(redis_client, rabbitmq_connection, rabbitmq_channel)


if __name__ == "__main__":
    asyncio.run(main())
```

#### Media Handler
```python
# src/bot/handlers/media.py
from __future__ import annotations

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
import aio_pika
import redis.asyncio as redis

from ...services.media_service import MediaService

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.photo)
async def handle_photo(
    message: Message,
    redis_client: redis.Redis,
    rabbitmq_channel: aio_pika.Channel,
) -> None:
    """Handle photo uploads."""
    if not message.photo:
        await message.reply("No photo found in message")
        return

    media_service = MediaService(redis_client, rabbitmq_channel)

    try:
        # Get the largest photo
        photo = message.photo[-1]

        # Download photo
        bot = message.bot
        file_info = await bot.get_file(photo.file_id)

        if not file_info.file_path:
            await message.reply("Failed to get file information")
            return

        file_data = await bot.download_file(file_info.file_path)

        if not file_data:
            await message.reply("Failed to download file")
            return

        # Process photo
        result = await media_service.process_photo(
            user_id=message.from_user.id,
            file_data=file_data.read(),
            file_name=f"photo_{photo.file_id}.jpg"
        )

        if result["success"]:
            await message.reply(
                f"✅ Photo processed successfully!\n"
                f"📁 File ID: {result['file_id']}\n"
                f"📏 Size: {result['file_size']} bytes\n"
                f"🔄 Processing ID: {result['processing_id']}"
            )

            # Send thumbnail if available
            if result.get("thumbnail"):
                thumbnail_file = BufferedInputFile(
                    result["thumbnail"],
                    filename="thumbnail.jpg"
                )
                await message.reply_photo(
                    thumbnail_file,
                    caption="📸 Generated thumbnail"
                )
        else:
            await message.reply(f"❌ Failed to process photo: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.reply("❌ An error occurred while processing your photo")


@router.message(F.document)
async def handle_document(
    message: Message,
    redis_client: redis.Redis,
    rabbitmq_channel: aio_pika.Channel,
) -> None:
    """Handle document uploads."""
    if not message.document:
        await message.reply("No document found in message")
        return

    # Check file size (limit to 10MB)
    if message.document.file_size and message.document.file_size > 10 * 1024 * 1024:
        await message.reply("❌ File too large. Maximum size is 10MB.")
        return

    media_service = MediaService(redis_client, rabbitmq_channel)

    try:
        # Download document
        bot = message.bot
        file_info = await bot.get_file(message.document.file_id)

        if not file_info.file_path:
            await message.reply("Failed to get file information")
            return

        file_data = await bot.download_file(file_info.file_path)

        if not file_data:
            await message.reply("Failed to download file")
            return

        # Process document
        result = await media_service.process_document(
            user_id=message.from_user.id,
            file_data=file_data.read(),
            file_name=message.document.file_name or f"document_{message.document.file_id}",
            mime_type=message.document.mime_type
        )

        if result["success"]:
            await message.reply(
                f"✅ Document processed successfully!\n"
                f"📁 File ID: {result['file_id']}\n"
                f"📄 Name: {result['file_name']}\n"
                f"📏 Size: {result['file_size']} bytes\n"
                f"🔄 Processing ID: {result['processing_id']}"
            )
        else:
            await message.reply(f"❌ Failed to process document: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await message.reply("❌ An error occurred while processing your document")


@router.message(Command("files"))
async def list_user_files(
    message: Message,
    redis_client: redis.Redis,
) -> None:
    """List user's uploaded files."""
    media_service = MediaService(redis_client, None)

    try:
        files = await media_service.get_user_files(message.from_user.id)

        if not files:
            await message.reply("📂 You haven't uploaded any files yet.")
            return

        file_list = []
        for file_info in files:
            file_list.append(
                f"📄 {file_info['file_name']}\n"
                f"   ID: {file_info['file_id']}\n"
                f"   Size: {file_info['file_size']} bytes\n"
                f"   Uploaded: {file_info['uploaded_at']}"
            )

        response = f"📂 Your files ({len(files)} total):\n\n" + "\n\n".join(file_list)

        # Split long messages
        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await message.reply(chunk)
        else:
            await message.reply(response)

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        await message.reply("❌ An error occurred while listing your files")
```
```