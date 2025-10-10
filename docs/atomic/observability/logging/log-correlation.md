# Log Correlation

Correlate logs across distributed microservices to trace complete request flows from initial client request through all backend services and background jobs. Log correlation enables debugging multi-service transactions by linking related log entries using shared correlation IDs (request_id, user_id, transaction_id).

This document covers request ID propagation patterns, correlation ID standards, tracing requests across FastAPI API → AsyncIO Worker → Aiogram Bot flows, querying correlated logs in Elasticsearch/CloudWatch, and implementing correlation metadata in structured logs. Log correlation transforms distributed logs into coherent request narratives.

Log correlation solves the distributed observability challenge: when a user request flows through API service → Worker service → Bot service, each emitting separate logs, correlation IDs link these logs into a single trace showing the complete request journey, execution order, timings, and any failures encountered across all services.

## Correlation ID Standards

### Request ID Format

```python
# Standard: req-{uuid}
request_id = f"req-{uuid.uuid4()}"
# Example: "req-550e8400-e29b-41d4-a716-446655440000"

# Alternative: timestamp + random
request_id = f"req-{int(time.time())}-{secrets.token_hex(8)}"
# Example: "req-1705318245-a3b4c5d6e7f8"
```

### Multiple Correlation IDs

```python
# Required correlation IDs
{
    "request_id": "req-abc-123",  # Request trace ID
    "user_id": "user-456",  # User identifier
    "session_id": "sess-789"  # Session identifier
}

# Optional business correlation IDs
{
    "loan_id": "loan-123",  # Business entity
    "transaction_id": "txn-456",  # Transaction trace
    "batch_id": "batch-789"  # Batch processing
}
```

## Request ID Generation

### API Gateway Pattern

```python
# CORRECT: Generate request_id at API entry point
from fastapi import FastAPI, Request
import uuid
import structlog

app = FastAPI()


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Add correlation IDs to all requests."""
    # Get or generate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = f"req-{uuid.uuid4()}"

    # Store in request state
    request.state.request_id = request_id

    # Bind to logger
    logger = structlog.get_logger().bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )
    request.state.logger = logger

    logger.info("request_started")

    response = await call_next(request)

    # Add to response headers
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed",
        status_code=response.status_code
    )

    return response


# INCORRECT: Generate new request_id for each service call
@app.post("/api/loans")
async def create_loan():
    request_id = str(uuid.uuid4())  # ❌ Loses correlation with original request
    logger.info("loan_created", request_id=request_id)
```

## Propagating Correlation IDs

### HTTP Client Propagation

```python
# CORRECT: Propagate request_id in HTTP headers
import httpx
import structlog

async def call_data_service(request_id: str, user_id: str):
    """Call data service with correlation headers."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://data-service:8000/api/users",
            headers={
                "X-Request-ID": request_id,  # Propagate request ID
                "X-User-ID": user_id
            },
            json={"email": "user@example.com"}
        )

        logger = structlog.get_logger().bind(
            request_id=request_id,
            user_id=user_id
        )
        logger.info(
            "data_service_called",
            status_code=response.status_code
        )

        return response


# INCORRECT: No correlation headers
async def call_data_service_wrong():
    response = await client.post(
        "http://data-service:8000/api/users",
        json={"email": "user@example.com"}  # ❌ Lost correlation
    )
```

### RabbitMQ Message Propagation

```python
# CORRECT: Include correlation IDs in message headers
import aio_pika
import structlog

async def publish_loan_event(request_id: str, loan_id: str, user_id: str):
    """Publish event with correlation metadata."""
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()

    message_body = {
        "loan_id": loan_id,
        "status": "pending",
        "amount": 10000
    }

    message = aio_pika.Message(
        body=json.dumps(message_body).encode(),
        headers={
            "X-Request-ID": request_id,  # Correlation ID
            "X-User-ID": user_id,
            "X-Loan-ID": loan_id
        },
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )

    exchange = await channel.declare_exchange("loan_events", aio_pika.ExchangeType.TOPIC)
    await exchange.publish(message, routing_key="loan.created")

    logger = structlog.get_logger().bind(
        request_id=request_id,
        loan_id=loan_id,
        user_id=user_id
    )
    logger.info("loan_event_published", event="loan.created")


# INCORRECT: No correlation in message
async def publish_event_wrong(loan_id: str):
    message = aio_pika.Message(body=json.dumps({"loan_id": loan_id}).encode())
    await exchange.publish(message, routing_key="loan.created")  # ❌ Lost correlation
```

### Worker Consumer Pattern

```python
# CORRECT: Extract and use correlation IDs from message
import aio_pika
import structlog

async def consume_loan_events():
    """Consume events and preserve correlation."""
    connection = await aio_pika.connect_robust("amqp://localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("loan_processing", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                # Extract correlation IDs
                request_id = message.headers.get("X-Request-ID", "unknown")
                user_id = message.headers.get("X-User-ID", "unknown")
                loan_id = message.headers.get("X-Loan-ID", "unknown")

                # Bind logger with correlation
                logger = structlog.get_logger().bind(
                    request_id=request_id,
                    user_id=user_id,
                    loan_id=loan_id,
                    service="finance_lending_worker"
                )

                logger.info("processing_loan_event")

                try:
                    await process_loan(loan_id, request_id, user_id)
                    logger.info("loan_processed_successfully")
                except Exception as e:
                    logger.error(
                        "loan_processing_failed",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        exc_info=True
                    )
```

## Cross-Service Correlation

### API → Worker → Bot Flow

```python
# Step 1: API Service
@app.post("/api/loans")
async def create_loan(request: Request, loan: LoanCreate):
    logger = request.state.logger
    request_id = request.state.request_id

    logger.info("loan_creation_started", amount=loan.amount)

    # Save to database via data service (propagate request_id)
    loan_id = await data_service.create_loan(request_id, loan)

    # Publish event for worker (include request_id in headers)
    await publish_loan_event(request_id, loan_id, loan.user_id)

    logger.info("loan_created", loan_id=loan_id)

    return {"loan_id": loan_id, "request_id": request_id}


# Step 2: Worker Service
async def process_loan(loan_id: str, request_id: str, user_id: str):
    """Process loan with inherited correlation."""
    logger = structlog.get_logger().bind(
        request_id=request_id,
        loan_id=loan_id,
        user_id=user_id,
        service="finance_lending_worker"
    )

    logger.info("credit_check_started")

    credit_score = await check_credit(user_id, request_id)

    logger.info("credit_check_completed", credit_score=credit_score)

    # Publish notification event for bot
    await publish_notification_event(request_id, user_id, loan_id, credit_score)


# Step 3: Bot Service
async def handle_notification(message: aio_pika.IncomingMessage):
    """Send notification with correlation context."""
    request_id = message.headers.get("X-Request-ID")
    user_id = message.headers.get("X-User-ID")
    loan_id = message.headers.get("X-Loan-ID")

    logger = structlog.get_logger().bind(
        request_id=request_id,
        user_id=user_id,
        loan_id=loan_id,
        service="finance_lending_bot"
    )

    logger.info("sending_bot_notification")

    telegram_user_id = await get_telegram_user_id(user_id, request_id)
    await bot.send_message(telegram_user_id, "Your loan has been approved!")

    logger.info("notification_sent")


# All logs share request_id="req-abc-123"
# Query: request_id="req-abc-123" returns complete trace:
# 1. API: loan_creation_started
# 2. API: loan_created
# 3. Worker: credit_check_started
# 4. Worker: credit_check_completed
# 5. Bot: sending_bot_notification
# 6. Bot: notification_sent
```

## Querying Correlated Logs

### Elasticsearch Query

```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"request_id": "req-abc-123"}}
      ]
    }
  },
  "sort": [
    {"timestamp": "asc"}
  ]
}
```

### Kibana Discover Query

```
request_id:"req-abc-123"
```

### CloudWatch Insights Query

```sql
fields @timestamp, service, event, message
| filter request_id = "req-abc-123"
| sort @timestamp asc
```

## Correlation Patterns

### User-Centric Correlation

```python
# CORRECT: Trace all actions for specific user
logger = structlog.get_logger().bind(
    user_id="user-456",
    session_id="sess-789"
)

# Query: user_id="user-456" AND @timestamp > "2025-01-15T00:00:00Z"
# Returns all user activity across all services
```

### Business Transaction Correlation

```python
# CORRECT: Trace complete business transaction
logger = structlog.get_logger().bind(
    transaction_id="txn-123",
    loan_id="loan-456",
    payment_id="pay-789"
)

# Query: transaction_id="txn-123"
# Returns: loan creation → credit check → payment → notification
```

## Best Practices

### DO: Propagate All Correlation IDs

```python
# CORRECT: Include all relevant IDs
headers = {
    "X-Request-ID": request_id,
    "X-User-ID": user_id,
    "X-Session-ID": session_id,
    "X-Trace-ID": trace_id
}


# INCORRECT: Missing IDs
headers = {"X-Request-ID": request_id}  # ❌ Lost user context
```

### DO: Log Correlation at Service Boundaries

```python
# CORRECT: Log when entering/exiting service
logger.info(
    "external_service_call_started",
    request_id=request_id,
    target_service="data_service",
    method="POST",
    endpoint="/api/users"
)

response = await call_external_service()

logger.info(
    "external_service_call_completed",
    request_id=request_id,
    status_code=response.status_code,
    duration_ms=duration
)


# INCORRECT: No boundary logging
response = await call_external_service()  # ❌ Cannot trace cross-service calls
```

### DON'T: Lose Correlation in Async Tasks

```python
# CORRECT: Pass correlation to background tasks
from fastapi import BackgroundTasks

@app.post("/api/loans")
async def create_loan(
    request: Request,
    background_tasks: BackgroundTasks
):
    request_id = request.state.request_id
    loan_id = "loan-123"

    # Pass correlation to background task
    background_tasks.add_task(
        send_confirmation_email,
        loan_id,
        request_id  # Propagate correlation
    )


async def send_confirmation_email(loan_id: str, request_id: str):
    logger = structlog.get_logger().bind(
        request_id=request_id,
        loan_id=loan_id
    )
    logger.info("sending_confirmation_email")


# INCORRECT: Lost correlation in background task
background_tasks.add_task(send_confirmation_email, loan_id)  # ❌ No request_id
```

## Checklist

- [ ] Generate request_id at API gateway
- [ ] Include request_id in all log entries
- [ ] Propagate request_id in HTTP headers (X-Request-ID)
- [ ] Include correlation IDs in RabbitMQ message headers
- [ ] Extract correlation IDs from incoming messages/requests
- [ ] Bind correlation IDs to logger context
- [ ] Log at service boundaries (entry/exit)
- [ ] Return request_id in API responses
- [ ] Propagate correlation to background tasks
- [ ] Use consistent ID formats (req-, user-, loan-, etc.)
- [ ] Include multiple correlation IDs (request, user, session)
- [ ] Test correlation across all services
- [ ] Query correlated logs in centralized logging system

## Related Documents

- `docs/atomic/observability/logging/structured-logging.md` — Structured logging with structlog
- `docs/atomic/observability/logging/request-id-tracking.md` — Request ID implementation details
- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing with OpenTelemetry
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging infrastructure
