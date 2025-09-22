# Complete Service Implementation Examples

This document provides comprehensive, working examples for all three service types in the microservices architecture. These examples follow all patterns defined in docs root categories (architecture/, services/, infrastructure/, observability/, quality/) and demonstrate real-world implementation scenarios.

## Table of Contents
- [FastAPI Service Example](#fastapi-service-example)
- [Aiogram Bot Service Example](#aiogram-bot-service-example)
- [AsyncIO Worker Service Example](#asyncio-worker-service-example)
- [Inter-Service Communication Examples](#inter-service-communication-examples)
- [Database Integration Examples](#database-integration-examples)
- [Testing Examples](#testing-examples)

## FastAPI Service Example

### Complete User Management API

#### Project Structure
```
services/api_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── system.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── auth.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── rabbitmq.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── auth_service.py
│   └── repositories/
│       ├── __init__.py
│       └── user_repository.py
├── tests/
├── pyproject.toml
└── Dockerfile
```

#### main.py
```python
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import aio_pika

from .core.config import settings
from .core.database import engine
from .api.system import router as system_router
from .api.v1 import users, auth

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting FastAPI application")

    # Initialize Redis
    app.state.redis = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        socket_keepalive_options={},
        health_check_interval=30,
    )

    # Initialize RabbitMQ
    app.state.rabbitmq_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL,
        client_properties={"connection_name": "api_service"}
    )
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()

    # Test connections
    await app.state.redis.ping()
    logger.info("Redis connection established")
    logger.info("RabbitMQ connection established")

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application")

    # Close Redis
    await app.state.redis.close()
    logger.info("Redis connection closed")

    # Close RabbitMQ
    await app.state.rabbitmq_channel.close()
    await app.state.rabbitmq_connection.close()
    logger.info("RabbitMQ connection closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="User Management API",
        description="Microservice for user management with authentication",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(system_router, tags=["system"])
    app.include_router(users.router, prefix="/api/v1", tags=["users"])
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

    return app


app = create_app()
```

#### Core Configuration
```python
# src/core/config.py
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@postgres:5432/microservices_db",
        description="Database connection URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL"
    )

    # RabbitMQ
    RABBITMQ_URL: str = Field(
        default="amqp://admin:admin123@rabbitmq:5672/",
        description="RabbitMQ connection URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiry")

    # API
    ALLOWED_HOSTS: list[str] = Field(default=["*"], description="Allowed CORS origins")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

#### Database Models
```python
# src/models/user.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
```

#### Pydantic Schemas
```python
# src/schemas/user.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Unique username")
    full_name: Optional[str] = Field(None, max_length=255, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(None, description="New email address")
    username: Optional[str] = Field(None, min_length=3, max_length=100, description="New username")
    full_name: Optional[str] = Field(None, max_length=255, description="New full name")
    is_active: Optional[bool] = Field(None, description="User active status")


class UserResponse(UserBase):
    """Schema for user response."""

    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="User active status")
    is_verified: bool = Field(..., description="User verification status")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")

    class Config:
        from_attributes = True
```

#### Service Layer
```python
# src/services/user_service.py
from __future__ import annotations

from typing import Optional, List
import logging

from passlib.context import CryptContext
import redis.asyncio as redis
import aio_pika
import orjson

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service layer for user operations."""

    def __init__(
        self,
        user_repository: UserRepository,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel,
    ) -> None:
        self.user_repository = user_repository
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        created_user = await self.user_repository.create(user)

        # Cache user
        cache_key = f"user:{created_user.id}"
        user_data_json = orjson.dumps({
            "id": created_user.id,
            "email": created_user.email,
            "username": created_user.username,
            "full_name": created_user.full_name,
            "is_active": created_user.is_active,
            "is_verified": created_user.is_verified,
        })
        await self.redis_client.setex(cache_key, 3600, user_data_json)

        # Publish user created event
        await self._publish_user_event("user.created", created_user)

        logger.info(f"User created: {created_user.id}")
        return UserResponse.model_validate(created_user)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID with caching."""
        # Try cache first
        cache_key = f"user:{user_id}"
        cached_data = await self.redis_client.get(cache_key)

        if cached_data:
            user_data = orjson.loads(cached_data)
            return UserResponse(**user_data)

        # Get from database
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        # Cache result
        user_data_json = orjson.dumps({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        })
        await self.redis_client.setex(cache_key, 3600, user_data_json)

        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user information."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        updated_user = await self.user_repository.update(user)

        # Invalidate cache
        cache_key = f"user:{user_id}"
        await self.redis_client.delete(cache_key)

        # Publish user updated event
        await self._publish_user_event("user.updated", updated_user)

        logger.info(f"User updated: {user_id}")
        return UserResponse.model_validate(updated_user)

    async def _publish_user_event(self, event_type: str, user: User) -> None:
        """Publish user event to RabbitMQ."""
        event_data = {
            "event_type": event_type,
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "timestamp": user.updated_at.isoformat(),
        }

        message = aio_pika.Message(
            orjson.dumps(event_data),
            headers={"event_type": event_type},
        )

        exchange = await self.rabbitmq_channel.declare_exchange(
            "user_events", aio_pika.ExchangeType.TOPIC
        )

        await exchange.publish(message, routing_key=event_type)
        logger.info(f"Published event: {event_type} for user {user.id}")
```

#### API Router
```python
# src/api/v1/users.py
from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...core.dependencies import get_redis, get_rabbitmq_channel
from ...schemas.user import UserCreate, UserUpdate, UserResponse
from ...services.user_service import UserService
from ...repositories.user_repository import UserRepository

router = APIRouter(prefix="/users")


async def get_user_service(
    db: AsyncSession = Depends(get_db_session),
    redis_client = Depends(get_redis),
    rabbitmq_channel = Depends(get_rabbitmq_channel),
) -> UserService:
    """Get user service with dependencies."""
    user_repository = UserRepository(db)
    return UserService(user_repository, redis_client, rabbitmq_channel)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user account."""
    try:
        return await user_service.create_user(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user information by ID."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update user information."""
    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

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

## Complete Testing Examples

### FastAPI Service Testing
```python
# tests/test_user_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
import pytest_asyncio

from src.main import app
from src.core.database import get_db_session
from src.schemas.user import UserCreate, UserResponse

@pytest.fixture
async def async_client():
    """Async test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }

    response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201

    user = response.json()
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]
    assert user["full_name"] == user_data["full_name"]
    assert "id" in user
    assert "created_at" in user

@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    """Test get user endpoint."""
    # First create a user
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpassword123"
    }

    create_response = await async_client.post("/api/v1/users/", json=user_data)
    created_user = create_response.json()
    user_id = created_user["id"]

    # Then get the user
    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200

    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == user_data["email"]
    assert user["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test getting a non-existent user."""
    response = await async_client.get("/api/v1/users/99999")

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
```

### Aiogram Bot Testing
```python
# tests/test_bot_handlers.py
import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, User, Chat
from aiogram import Bot

from src.bot.handlers.start import handle_start

@pytest.fixture
def mock_message():
    """Mock Telegram message."""
    user = User(id=123, is_bot=False, first_name="Test", username="testuser")
    chat = Chat(id=123, type="private")

    message = Mock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()
    message.bot = Mock(spec=Bot)

    return message

@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test /start command handler."""
    await handle_start(mock_message)

    mock_message.reply.assert_called_once()
    call_args = mock_message.reply.call_args[0][0]
    assert "Welcome" in call_args
    assert "testuser" in call_args
```

### Worker Service Testing
```python
# tests/test_media_processor.py
import pytest
from unittest.mock import AsyncMock, Mock
from io import BytesIO
from PIL import Image

from src.workers.media_processor import MediaProcessor

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.setex = AsyncMock()
    redis_mock.get = AsyncMock()
    return redis_mock

@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel."""
    channel_mock = AsyncMock()
    channel_mock.declare_exchange = AsyncMock()
    channel_mock.declare_queue = AsyncMock()
    return channel_mock

@pytest.fixture
def sample_image_data():
    """Create sample image data."""
    image = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()

@pytest.mark.asyncio
async def test_process_image(mock_redis, mock_rabbitmq_channel, sample_image_data):
    """Test image processing."""
    processor = MediaProcessor(mock_redis, mock_rabbitmq_channel)

    result = await processor._process_image(
        file_data=sample_image_data,
        processing_id="test-123",
        user_id=456
    )

    assert result["success"] is True
    assert "thumbnail_key" in result
    assert "compressed_key" in result
    assert "metadata" in result
    assert result["original_size"] > 0
    assert result["compressed_size"] > 0
    assert 0 < result["compression_ratio"] <= 1

    # Verify Redis calls
    assert mock_redis.setex.call_count == 2  # thumbnail + compressed
```

These comprehensive examples demonstrate:

1. **Complete service implementations** following all architectural patterns
2. **Real-world scenarios** with proper error handling and logging
3. **Inter-service communication** via HTTP and RabbitMQ
4. **Database integration** with caching and events
5. **Testing patterns** for all service types
6. **Production-ready code** with proper dependency injection, configuration, and observability

Each example follows the patterns defined in docs rule categories and provides a solid foundation for implementing microservices in your architecture.