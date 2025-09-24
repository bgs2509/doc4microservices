## 🛡️ Resilience Patterns

Resilience is a key characteristic of distributed systems. In this section, we'll examine two important patterns that help improve microservices reliability and stability: **Dead-Letter Queue (DLQ)** and **Circuit Breaker**.

### 1. Dead-Letter Queue (DLQ) in RabbitMQ

DLQ is a special queue where messages that cannot be successfully processed are redirected. This allows avoiding data loss and analyzing the cause of failure without blocking the main queue.

#### Configuration

DLQ configuration is performed in the consumer worker. We create the main queue and link it with the "dead" queue.

`src/workers/notification_sender.py`
```python
import aio_pika

class NotificationSender:
    # ... (init)

    async def start(self) -> None:
        self.running = True

        # 1. Declare "dead" queue and exchange
        dlx_exchange = await self.rabbitmq_channel.declare_exchange(
            "notifications.dlx",
            aio_pika.ExchangeType.FANOUT
        )
        dlq_queue = await self.rabbitmq_channel.declare_queue(
            "notifications.dlq",
            durable=True
        )
        await dlq_queue.bind(dlx_exchange)

        # 2. Declare main queue with DLQ arguments
        main_exchange = await self.rabbitmq_channel.declare_exchange(
            "notifications",
            aio_pika.ExchangeType.DIRECT
        )
        main_queue = await self.rabbitmq_channel.declare_queue(
            "notifications.send",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "notifications.dlx",
                # "x-dead-letter-routing-key": "some_key" # Optional
            }
        )
        await main_queue.bind(main_exchange, routing_key="notifications.send")

        # 3. Start consuming
        async with main_queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    # Simulate processing error for every second message
                    if message.delivery_tag % 2 == 0:
                        raise ValueError("Simulated processing error")

                    # Successful processing
                    logger.info(f"Successfully processed message: {message.body.decode()}")
                    await message.ack() # Acknowledge successful processing

                except Exception as e:
                    logger.error(f"Failed to process message. Rejecting. Error: {e}")
                    # 4. Reject message. `requeue=False` will send it to DLQ.
                    await message.reject(requeue=False)
```

**How it works:**
- When `message.reject(requeue=False)` is called for a message from `notifications.send`, RabbitMQ redirects it to the exchange specified in `x-dead-letter-exchange` (i.e., to `notifications.dlx`).
- `notifications.dlx` (FANOUT type) sends the message to all queues bound to it, i.e., to `notifications.dlq`.
- Now "problematic" messages are stored in `notifications.dlq`, and they can be examined or resent later without interfering with the main worker's operation.

### 2. Circuit Breaker

The Circuit Breaker pattern is used to protect the system from cascading failures. If some external service (e.g., another micro-API) starts constantly returning errors, Circuit Breaker "opens" and stops sending requests to it for some time, returning an error immediately. This gives the failing service time to recover.

We'll use the `pybreaker` library.

#### Installation
```bash
pip install pybreaker
```

#### Implementation

Let's create a decorator that wraps HTTP calls in `CircuitBreaker`.

`src/utils/circuit_breaker.py`
```python
from __future__ import annotations

import functools
import logging
from typing import Callable, Any

import httpx
from pybreaker import CircuitBreaker, CircuitBreakerError

# Create circuit breaker: 5 consecutive failures open circuit for 60 seconds
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
logger = logging.getLogger(__name__)


def with_circuit_breaker(func: Callable) -> Callable:
    """Decorator for wrapping function in Circuit Breaker."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await breaker.call_async(func, *args, **kwargs)
        except CircuitBreakerError:
            # Circuit is open, return error immediately
            logger.error("Circuit is open. Call failed immediately.")
            # Can return cached result or default response
            return None
        except httpx.HTTPStatusError as e:
            # Catch HTTP errors and pass them to circuit breaker
            logger.error(f"HTTP error occurred: {e}")
            raise # Pass exception further so breaker counts it
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    return wrapper
```

#### Application

Now let's apply this decorator to a method that calls an external service.

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
        """Get product details from external service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status() # Will raise exception for 4xx/5xx responses
            return response.json()
```

**How it works:**
- The `@with_circuit_breaker` decorator wraps the `get_product_details` call.
- If `get_product_details` executes successfully, `pybreaker` resets the failure counter.
- If `response.raise_for_status()` raises an `httpx.HTTPStatusError` exception, `pybreaker` increments the failure counter.
- After 5 consecutive failures (`fail_max=5`), the circuit breaker "opens".
- For the next 60 seconds (`reset_timeout=60`), any calls to `get_product_details` will immediately fail with `CircuitBreakerError`, without even attempting to send an HTTP request.
- After 60 seconds, the circuit breaker will enter "half-open" state and allow one call through. If it's successful, the circuit closes. If not, it opens again for 60 seconds.
