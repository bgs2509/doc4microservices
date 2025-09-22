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
