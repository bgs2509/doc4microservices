# Request ID Tracking

Implement request ID tracking to trace individual requests through distributed microservices architecture, enabling end-to-end request flow debugging, performance analysis, and error tracking. Request IDs provide unique identifiers linking all operations related to a single user request across multiple services.

This document covers request ID generation strategies, propagation through HTTP headers and message queues, middleware implementation for FastAPI and Aiogram, extracting request IDs from incoming requests, and querying logs by request ID. Request ID tracking is foundational for distributed observability.

Request ID tracking enables answering critical questions: What happened to user request X? Which services did it touch? Where did it fail? How long did each step take? Without request IDs, debugging distributed systems requires manually correlating logs across services using timestamps—an error-prone and time-consuming process.

## Request ID Generation

### UUID-Based IDs

```python
import uuid

def generate_request_id() -> str:
    """Generate unique request ID."""
    return f"req-{uuid.uuid4()}"

# Example: "req-550e8400-e29b-41d4-a716-446655440000"
```

### Timestamp + Random

```python
import time
import secrets

def generate_request_id() -> str:
    """Generate request ID with timestamp prefix."""
    timestamp = int(time.time())
    random_suffix = secrets.token_hex(8)
    return f"req-{timestamp}-{random_suffix}"

# Example: "req-1705318245-a3b4c5d6e7f8"
```

## FastAPI Middleware

### Request ID Middleware

```python
# CORRECT: Middleware generates or extracts request ID
from fastapi import FastAPI, Request
import uuid
import structlog

app = FastAPI()


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID to all requests."""
    # Extract from header or generate new
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = f"req-{uuid.uuid4()}"

    # Store in request state
    request.state.request_id = request_id

    # Bind to logger
    logger = structlog.get_logger().bind(request_id=request_id)
    request.state.logger = logger

    # Process request
    response = await call_next(request)

    # Return request ID in response header
    response.headers["X-Request-ID"] = request_id

    return response


# Usage in endpoint
@app.get("/api/users/{user_id}")
async def get_user(user_id: str, request: Request):
    logger = request.state.logger
    request_id = request.state.request_id

    logger.info("fetching_user", user_id=user_id)

    return {"user_id": user_id, "request_id": request_id}
```

## HTTP Header Propagation

### Outgoing Requests

```python
# CORRECT: Propagate request ID in HTTP client
import httpx
import structlog

async def call_data_service(request_id: str, user_id: str):
    """Call external service with request ID."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://data-service:8000/api/users/{user_id}",
            headers={"X-Request-ID": request_id}  # Propagate
        )

        logger = structlog.get_logger().bind(request_id=request_id)
        logger.info(
            "data_service_called",
            status_code=response.status_code,
            user_id=user_id
        )

        return response.json()


# INCORRECT: No request ID propagation
async def call_service_wrong(user_id: str):
    response = await client.get(f"http://data-service:8000/api/users/{user_id}")
    # ❌ Lost request correlation
```

## RabbitMQ Message Tracking

### Publishing Messages

```python
# CORRECT: Include request ID in message headers
import aio_pika
import json

async def publish_loan_event(request_id: str, loan_id: str):
    """Publish event with request ID."""
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()

    message = aio_pika.Message(
        body=json.dumps({"loan_id": loan_id}).encode(),
        headers={"X-Request-ID": request_id},
        content_type="application/json"
    )

    exchange = await channel.declare_exchange("loan_events", aio_pika.ExchangeType.TOPIC)
    await exchange.publish(message, routing_key="loan.created")

    logger.info("event_published", request_id=request_id, loan_id=loan_id)
```

### Consuming Messages

```python
# CORRECT: Extract request ID from message
async def consume_loan_events():
    """Consume events with request ID tracking."""
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("loan_processing")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                # Extract request ID
                request_id = message.headers.get("X-Request-ID", "unknown")

                # Bind to logger
                logger = structlog.get_logger().bind(request_id=request_id)
                logger.info("processing_loan_event")

                await process_loan(message, request_id)
```

## Aiogram Bot Integration

```python
# CORRECT: Generate request ID for bot messages
from aiogram import Bot, Dispatcher, types
import uuid
import structlog

bot = Bot(token="TOKEN")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    """Handle /start with request ID."""
    request_id = f"req-{uuid.uuid4()}"

    logger = structlog.get_logger().bind(
        request_id=request_id,
        user_id=message.from_user.id
    )

    logger.info("bot_command_received", command="start")

    await message.reply(f"Hello! Your request ID: {request_id}")

    logger.info("bot_response_sent")
```

## Background Tasks

```python
# CORRECT: Pass request ID to background tasks
from fastapi import BackgroundTasks

@app.post("/api/loans")
async def create_loan(
    request: Request,
    background_tasks: BackgroundTasks
):
    request_id = request.state.request_id

    # Pass request ID to background task
    background_tasks.add_task(
        send_notification,
        loan_id="loan-123",
        request_id=request_id
    )

    return {"request_id": request_id}


async def send_notification(loan_id: str, request_id: str):
    """Send notification with request tracking."""
    logger = structlog.get_logger().bind(
        request_id=request_id,
        loan_id=loan_id
    )
    logger.info("sending_notification")
    # Notification logic
```

## Querying by Request ID

### Elasticsearch

```json
{
  "query": {
    "term": {"request_id": "req-abc-123"}
  },
  "sort": [{"timestamp": "asc"}]
}
```

### Kibana

```
request_id:"req-abc-123"
```

### CloudWatch Insights

```sql
fields @timestamp, service, event
| filter request_id = "req-abc-123"
| sort @timestamp asc
```

## Best Practices

### DO: Generate Once at Entry Point

```python
# CORRECT: Generate at API gateway
@app.middleware("http")
async def middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4()}"
    request.state.request_id = request_id
    return await call_next(request)


# INCORRECT: Generate multiple times
def handler1():
    request_id = str(uuid.uuid4())  # ❌

def handler2():
    request_id = str(uuid.uuid4())  # ❌ Different ID
```

### DO: Include in All Logs

```python
# CORRECT: Bind to logger
logger = structlog.get_logger().bind(request_id=request_id)
logger.info("event1")
logger.info("event2")
# Both logs include request_id


# INCORRECT: Manual inclusion
logger.info("event1", request_id=request_id)  # Verbose
logger.info("event2")  # ❌ Forgot request_id
```

### DO: Return in API Responses

```python
# CORRECT: Return request ID to client
@app.post("/api/loans")
async def create_loan(request: Request):
    request_id = request.state.request_id
    return {
        "loan_id": "loan-123",
        "request_id": request_id  # Client can use for support
    }
```

## Checklist

- [ ] Generate request ID at API entry point
- [ ] Extract existing request ID from X-Request-ID header
- [ ] Store request ID in request state
- [ ] Bind request ID to logger context
- [ ] Propagate request ID in HTTP headers
- [ ] Include request ID in RabbitMQ message headers
- [ ] Extract request ID from incoming messages
- [ ] Pass request ID to background tasks
- [ ] Return request ID in API responses
- [ ] Add X-Request-ID to response headers
- [ ] Use consistent format (req-{uuid})
- [ ] Test request ID propagation across services
- [ ] Query logs by request ID in centralized system

## Related Documents

- `docs/atomic/observability/logging/log-correlation.md` — Log correlation across services
- `docs/atomic/observability/logging/structured-logging.md` — Structured logging with structlog
- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging setup
