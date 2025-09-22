# Example: FastAPI Business Service

This document demonstrates the implementation of a **Business Service** using FastAPI. In accordance with the "Improved Hybrid Approach" architecture, this service **has no direct database access**. Instead, it uses an HTTP client to communicate with **Data Services**.

## Key Characteristics
- **Responsibility:** Implementation of business logic (e.g., user management, authentication).
- **Data Access:** Only through HTTP calls to other services (e.g., `postgres_data_service`).
- **Infrastructure:** Can use Redis for caching and RabbitMQ for event publishing.

---

## 1. Project Structure (api_service)

The structure is simplified as database models and repositories are removed.

```
services/api_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── auth.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── dependencies.py # Dependencies, including clients
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── auth_service.py
│   └── clients/
│       ├── __init__.py
│       └── user_data_client.py # HTTP client for data access
└── Dockerfile
```

---

## 2. HTTP Client for Data Access (`src/clients/user_data_client.py`)

This client encapsulates HTTP request logic to `postgres_data_service`.

```python
import httpx
import uuid
from typing import Optional, Dict, Any
from ..core.config import settings
from ..schemas.user import UserCreate

class UserDataClient:
    def __init__(self):
        self.base_url = settings.DATA_SERVICE_URL

    async def get_user_by_id(self, user_id: int, request_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={"X-Request-ID": request_id}
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                # Error handling logic should be here, e.g., logging
                print(f"HTTP error getting user {user_id}: {e}")
                return None

    async def create_user(self, user_data: UserCreate, request_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/users/",
                    json=user_data.model_dump(),
                    headers={"X-Request-ID": request_id}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP error creating user: {e}")
                return None

    async def get_user_by_username(self, username: str, request_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/by_username/{username}",
                    headers={"X-Request-ID": request_id}
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP error getting user by username {username}: {e}")
                return None
```

---

## 3. Updated Service (`src/services/user_service.py`)

The service now uses `UserDataClient` instead of a repository.

```python
import logging
import orjson
import aio_pika
import redis.asyncio as redis
from typing import Optional

from ..schemas.user import UserCreate, UserResponse
from ..clients.user_data_client import UserDataClient

logger = logging.getLogger(__name__)

class UserService:
    def __init__(
        self, 
        user_client: UserDataClient,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel
    ):
        self.user_client = user_client
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel

    async def create_user(self, user_data: UserCreate, request_id: str) -> Optional[UserResponse]:
        # Password hashing logic should be here, in the business service
        # hashed_password = ...
        # user_data.password = hashed_password

        created_user_data = await self.user_client.create_user(user_data, request_id)
        if not created_user_data:
            return None

        # Publish event to RabbitMQ
        await self._publish_user_event("user.created", created_user_data)

        logger.info(f"User created: {created_user_data['id']}")
        return UserResponse(**created_user_data)

    async def get_user_by_id(self, user_id: int, request_id: str) -> Optional[UserResponse]:
        # Try to get from Redis cache
        cache_key = f"user:{user_id}"
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            return UserResponse(**orjson.loads(cached_data))

        # If not in cache, go to data service via HTTP
        user_data = await self.user_client.get_user_by_id(user_id, request_id)
        if not user_data:
            return None

        # Cache the result
        await self.redis_client.setex(cache_key, 3600, orjson.dumps(user_data))
        return UserResponse(**user_data)

    async def _publish_user_event(self, event_type: str, user_data: dict) -> None:
        # ... (event publishing logic remains the same)
        pass
```

---

## 4. Main Application File (`src/main.py`)

`lifespan` now only manages connections to Redis and RabbitMQ.

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis
import aio_pika

from .core.config import settings
from .api.v1 import users, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis
    app.state.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Initialize RabbitMQ
    app.state.rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()

    yield

    # Close connections
    await app.state.redis.close()
    await app.state.rabbitmq_connection.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title="User Management Business Service",
        lifespan=lifespan
    )
    # ... (router registration)
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
    return app

app = create_app()
```