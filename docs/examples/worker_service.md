# Пример: Бизнес-сервис Worker

Этот документ демонстрирует реализацию фонового обработчика (Worker) как **Бизнес-сервиса**. Он не имеет прямого доступа к базе данных и взаимодействует с другими частями системы через HTTP-вызовы (к Сервисам Данных) и брокер сообщений (RabbitMQ).

## Ключевые характеристики
- **Ответственность:** Выполнение фоновых задач, таких как обработка медиафайлов, отправка уведомлений или анализ данных.
- **Доступ к данным:** Только через HTTP-клиенты.
- **Коммуникации:** Получает задачи из RabbitMQ и может вызывать другие сервисы по HTTP.

---

## 1. Структура проекта (worker_service)

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

## 2. Логика Воркера (`src/workers/media_processor.py`)

Воркер получает сообщение из RabbitMQ и использует HTTP-клиент для обновления информации в базе данных через Сервис Данных.

```python
import asyncio
import logging
import aio_pika
import orjson

from ..clients.user_data_client import UserDataClient # Предполагаем, что клиент есть

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self, rabbitmq_channel: aio_pika.Channel):
        self.rabbitmq_channel = rabbitmq_channel
        self.user_client = UserDataClient() # Инициализируем HTTP-клиент

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
                request_id = message.headers.get("X-Request-ID", "generated-worker-id")

                if not all([user_id, file_info]):
                    logger.error("Invalid message data")
                    return

                logger.info(f"Processing media for user {user_id}")
                
                # Логика обработки файла...
                processed_result = {"status": "processed", "path": "/path/to/processed/file"}

                # Обновляем статус пользователя через Сервис Данных по HTTP
                # Например, добавляем информацию о новом файле
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

## 3. Основной файл приложения (`src/main.py`)

`main.py` отвечает за запуск воркера и управление его жизненным циклом.

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