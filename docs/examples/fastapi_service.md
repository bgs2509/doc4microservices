# Пример: Бизнес-сервис FastAPI

Этот документ демонстрирует реализацию **Бизнес-сервиса** на FastAPI. В соответствии с архитектурой "Improved Hybrid Approach", этот сервис **не имеет прямого доступа к базе данных**. Вместо этого он использует HTTP-клиент для обращения к **Сервису Данных**.

## Ключевые характеристики
- **Ответственность:** Реализация бизнес-логики (например, управление пользователями, аутентификация).
- **Доступ к данным:** Только через HTTP-вызовы к другим сервисам (например, `postgres_data_service`).
- **Инфраструктура:** Может использовать Redis для кэширования и RabbitMQ для публикации событий.

---

## 1. Структура проекта (api_service)

Структура упрощается, так как из нее уходят модели и репозитории БД.

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
│   │   └── dependencies.py # Зависимости, включая клиенты
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── auth_service.py
│   └── clients/
│       ├── __init__.py
│       └── user_data_client.py # HTTP-клиент для доступа к данным
└── Dockerfile
```

---

## 2. HTTP-клиент для доступа к данным (`src/clients/user_data_client.py`)

Этот клиент инкапсулирует логику HTTP-запросов к `postgres_data_service`.

```python
import httpx
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
                # Здесь должна быть логика обработки ошибок, например, логирование
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
```

---

## 3. Обновленный сервис (`src/services/user_service.py`)

Сервис теперь использует `UserDataClient` вместо репозитория.

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
        # Логика хеширования пароля должна быть здесь, в бизнес-сервисе
        # hashed_password = ...
        # user_data.password = hashed_password

        created_user_data = await self.user_client.create_user(user_data, request_id)
        if not created_user_data:
            return None

        # Публикуем событие в RabbitMQ
        await self._publish_user_event("user.created", created_user_data)

        logger.info(f"User created: {created_user_data['id']}")
        return UserResponse(**created_user_data)

    async def get_user_by_id(self, user_id: int, request_id: str) -> Optional[UserResponse]:
        # Попытка получить из кэша Redis
        cache_key = f"user:{user_id}"
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            return UserResponse(**orjson.loads(cached_data))

        # Если в кэше нет, идем в сервис данных по HTTP
        user_data = await self.user_client.get_user_by_id(user_id, request_id)
        if not user_data:
            return None

        # Кэшируем результат
        await self.redis_client.setex(cache_key, 3600, orjson.dumps(user_data))
        return UserResponse(**user_data)

    async def _publish_user_event(self, event_type: str, user_data: dict) -> None:
        # ... (логика публикации события остается прежней)
        pass
```

---

## 4. Основной файл приложения (`src/main.py`)

`lifespan` теперь управляет только подключениями к Redis и RabbitMQ.

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis
import aio_pika

from .core.config import settings
from .api.v1 import users, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация Redis
    app.state.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Инициализация RabbitMQ
    app.state.rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    app.state.rabbitmq_channel = await app.state.rabbitmq_connection.channel()
    
    yield
    
    # Закрытие соединений
    await app.state.redis.close()
    await app.state.rabbitmq_connection.close()

def create_app() -> FastAPI:
    app = FastAPI(
        title="User Management Business Service",
        lifespan=lifespan
    )
    # ... (подключение роутеров)
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
    return app

app = create_app()
```