# Пример: Бизнес-сервис Aiogram

Этот документ демонстрирует реализацию Telegram-бота на Aiogram как **Бизнес-сервиса**. Сервис не имеет прямого доступа к базе данных и взаимодействует с другими компонентами системы через HTTP-клиенты и брокер сообщений.

## Ключевые характеристики
- **Ответственность:** Взаимодействие с пользователем через Telegram, обработка команд и медиафайлов.
- **Доступ к данным:** Только через HTTP-вызовы к Сервисам Данных.
- **Коммуникации:** Публикует события в RabbitMQ, может вызывать другие сервисы по HTTP.

---

## 1. Структура проекта (bot_service)

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

## 2. Логика обработчиков (`src/bot/handlers.py`)

Обработчики команд и сообщений используют HTTP-клиент для работы с данными и сервисный слой для бизнес-логики.

```python
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ..services.media_service import MediaService
from ..clients.user_data_client import UserDataClient

router = Router()
logger = logging.getLogger(__name__)

# Зависимости будут внедрены через middleware или фабрику
def get_media_service(**kwargs) -> MediaService:
    return MediaService(**kwargs)

def get_user_data_client() -> UserDataClient:
    return UserDataClient()

@router.message(Command("start"))
async def handle_start(message: Message):
    user_client = get_user_data_client()
    request_id = "some-request-id" # Должен генерироваться в middleware

    # Проверяем, существует ли пользователь, через Сервис Данных
    user_data = await user_client.get_user_by_id(message.from_user.id, request_id)
    if not user_data:
        # Если нет, создаем его через Сервис Данных
        create_payload = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "email": f"{message.from_user.id}@telegram.bot"
        }
        await user_client.create_user_from_bot(create_payload, request_id)
        await message.reply(f"Привет, новый пользователь {message.from_user.first_name}!")
    else:
        await message.reply(f"С возвращением, {message.from_user.first_name}!")

@router.message(F.photo)
async def handle_photo(message: Message, rabbitmq_channel, redis_client):
    media_service = get_media_service(
        rabbitmq_channel=rabbitmq_channel, 
        redis_client=redis_client
    )
    
    # Логика обработки фото остается в сервисном слое
    # Этот сервис будет публиковать событие в RabbitMQ для дальнейшей обработки воркером
    result = await media_service.process_photo_upload(
        user_id=message.from_user.id,
        photo=message.photo[-1]
    )

    if result["success"]:
        await message.reply(f"Фото принято в обработку! ID задачи: {result['task_id']}")
    else:
        await message.reply("Не удалось обработать фото.")
```

---

## 3. Сервисный слой (`src/services/media_service.py`)

Сервис отвечает за публикацию событий в RabbitMQ.

```python
import orjson
import aio_pika
import uuid

class MediaService:
    def __init__(self, rabbitmq_channel, redis_client):
        self.rabbitmq_channel = rabbitmq_channel
        self.redis_client = redis_client # Может использоваться для проверки дубликатов

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
            headers={"X-Request-ID": "some-request-id"}
        )

        # Публикуем задачу в очередь для обработки воркером
        await self.rabbitmq_channel.default_exchange.publish(
            message,
            routing_key="media.process"
        )
        return {"success": True, "task_id": task_id}
```

---

## 4. Основной файл приложения (`src/main.py`)

`main.py` инициализирует бота, диспетчер и зависимости, такие как RabbitMQ и Redis.

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

    # Инициализация зависимостей
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    rabbitmq_channel = await rabbitmq_connection.channel()

    # Внедрение зависимостей в диспетчер
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
