## Паттерны отказоустойчивости

Отказоустойчивость — ключевая характеристика распределенных систем. В этом разделе мы рассмотрим два важных паттерна, которые помогают повысить надежность и стабильность микросервисов: **Dead-Letter Queue (DLQ)** и **Circuit Breaker**.

### 1. Dead-Letter Queue (DLQ) в RabbitMQ

DLQ — это специальная очередь, куда перенаправляются сообщения, которые не могут быть успешно обработаны. Это позволяет избежать потери данных и проанализировать причину сбоя, не блокируя основную очередь.

#### Настройка

Настройка DLQ выполняется в воркере-потребителе. Мы создаем основную очередь и связываем ее с "мертвой" очередью.

`src/workers/notification_sender.py`
```python
import aio_pika

class NotificationSender:
    # ... (init)

    async def start(self) -> None:
        self.running = True

        # 1. Объявляем "мертвую" очередь и exchange
        dlx_exchange = await self.rabbitmq_channel.declare_exchange(
            "notifications.dlx", 
            aio_pika.ExchangeType.FANOUT
        )
        dlq_queue = await self.rabbitmq_channel.declare_queue(
            "notifications.dlq", 
            durable=True
        )
        await dlq_queue.bind(dlx_exchange)

        # 2. Объявляем основную очередь с аргументами для DLQ
        main_exchange = await self.rabbitmq_channel.declare_exchange(
            "notifications", 
            aio_pika.ExchangeType.DIRECT
        )
        main_queue = await self.rabbitmq_channel.declare_queue(
            "notifications.send",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "notifications.dlx",
                # "x-dead-letter-routing-key": "some_key" # Опционально
            }
        )
        await main_queue.bind(main_exchange, routing_key="notifications.send")

        # 3. Начинаем потребление
        async with main_queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    # Имитируем ошибку обработки для каждого второго сообщения
                    if message.delivery_tag % 2 == 0:
                        raise ValueError("Simulated processing error")

                    # Успешная обработка
                    logger.info(f"Successfully processed message: {message.body.decode()}")
                    await message.ack() # Подтверждаем успешную обработку
                
                except Exception as e:
                    logger.error(f"Failed to process message. Rejecting. Error: {e}")
                    # 4. Отклоняем сообщение. `requeue=False` отправит его в DLQ.
                    await message.reject(requeue=False)
```

**Как это работает:**
- Когда `message.reject(requeue=False)` вызывается для сообщения из `notifications.send`, RabbitMQ перенаправляет его в exchange, указанный в `x-dead-letter-exchange` (т.е. в `notifications.dlx`).
- `notifications.dlx` (типа `FANOUT`) отправляет сообщение во все связанные с ним очереди, то есть в `notifications.dlq`.
- Теперь "проблемные" сообщения хранятся в `notifications.dlq`, и их можно изучить или переотправить позже, не мешая работе основного воркера.

### 2. Circuit Breaker (Предохранитель)

Паттерн "Предохранитель" используется для защиты системы от каскадных сбоев. Если какой-то внешний сервис (например, другое микро-API) начинает постоянно возвращать ошибки, Circuit Breaker "размыкается" и перестает отправлять на него запросы на некоторое время, возвращая ошибку немедленно. Это дает сбойному сервису время на восстановление.

Мы будем использовать библиотеку `pybreaker`.

#### Установка
```bash
pip install pybreaker
```

#### Реализация

Создадим декоратор, который оборачивает HTTP-вызовы в `CircuitBreaker`.

`src/utils/circuit_breaker.py`
```python
from __future__ import annotations

import functools
from typing import Callable, Any

import httpx
from pybreaker import CircuitBreaker, CircuitBreakerError

# Создаем предохранитель: 5 сбоев подряд открывают цепь на 60 секунд
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)


def with_circuit_breaker(func: Callable) -> Callable:
    """Декоратор для обертывания функции в Circuit Breaker."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await breaker.call_async(func, *args, **kwargs)
        except CircuitBreakerError:
            # Цепь разомкнута, возвращаем ошибку немедленно
            logger.error("Circuit is open. Call failed immediately.")
            # Можно вернуть кэшированный результат или стандартный ответ
            return None 
        except httpx.HTTPStatusError as e:
            # Ловим HTTP ошибки и передаем их в предохранитель
            logger.error(f"HTTP error occurred: {e}")
            raise # Передаем исключение дальше, чтобы breaker его засчитал
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    return wrapper
```

#### Применение

Теперь применим этот декоратор к методу, который вызывает внешний сервис.

`src/services/external_api_service.py`
```python
import httpx
from typing import Optional, Dict, Any

from ..utils.circuit_breaker import with_circuit_breaker

class ExternalAPIService:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    @with_circuit_breaker
    async def get_product_details(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Получить детали продукта из внешнего сервиса."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status() # Вызовет исключение для 4xx/5xx ответов
            return response.json()
```

**Как это работает:**
- Декоратор `@with_circuit_breaker` оборачивает вызов `get_product_details`.
- Если `get_product_details` успешно выполняется, `pybreaker` сбрасывает счетчик сбоев.
- Если `response.raise_for_status()` вызывает исключение `httpx.HTTPStatusError`, `pybreaker` увеличивает счетчик сбоев.
- После 5 сбоев подряд (`fail_max=5`), предохранитель "размыкается".
- В течение следующих 60 секунд (`reset_timeout=60`) любые вызовы `get_product_details` будут немедленно завершаться с ошибкой `CircuitBreakerError`, даже не пытаясь отправить HTTP-запрос.
- По истечении 60 секунд предохранитель перейдет в состояние "полуоткрыто" и пропустит один вызов. Если он будет успешным, цепь замкнется. Если нет — снова разомкнется на 60 секунд.
