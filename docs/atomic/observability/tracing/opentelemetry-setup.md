# OpenTelemetry Setup

Configure OpenTelemetry for distributed tracing, enabling end-to-end request tracking across microservices. OpenTelemetry provides vendor-neutral instrumentation for collecting traces, metrics, and logs, with automatic instrumentation for popular frameworks like FastAPI, making distributed systems observable.

This document covers OpenTelemetry SDK installation, automatic instrumentation for FastAPI/Aiogram/AsyncIO services, OTLP exporter configuration for Jaeger/Zipkin backends, context propagation patterns, span attributes and events, and performance considerations. OpenTelemetry is the CNCF standard for observability instrumentation.

Distributed tracing answers critical questions: Why is this request slow? Which service is the bottleneck? How do requests flow through the system? What caused this error? Without tracing, debugging distributed systems requires manually correlating timestamps across logs—an impossible task when requests traverse dozens of services.

## Installation

### Core Dependencies

```bash
# Install OpenTelemetry SDK and instrumentation
pip install opentelemetry-api==1.22.0
pip install opentelemetry-sdk==1.22.0
pip install opentelemetry-instrumentation-fastapi==0.43b0
pip install opentelemetry-instrumentation-httpx==0.43b0
pip install opentelemetry-instrumentation-sqlalchemy==0.43b0
pip install opentelemetry-instrumentation-redis==0.43b0
pip install opentelemetry-exporter-otlp==1.22.0
```

### Jaeger Exporter (Alternative)

```bash
# Use OTLP exporter (recommended) or Jaeger-specific exporter
pip install opentelemetry-exporter-jaeger==1.22.0
```

## Basic Configuration

### FastAPI Integration

```python
# src/core/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def configure_tracing(service_name: str) -> None:
    """Configure OpenTelemetry tracing."""
    # Create resource with service name
    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        "environment": "production",
        "version": "1.2.3"
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure OTLP exporter (Jaeger/Zipkin)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://jaeger:4317",  # OTLP gRPC endpoint
        insecure=True
    )

    # Add batch processor for performance
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)


# src/main.py
from fastapi import FastAPI
from src.core.tracing import configure_tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure tracing before app creation
configure_tracing("finance_lending_api")

app = FastAPI()

# Instrument FastAPI automatically
FastAPIInstrumentor.instrument_app(app)


@app.get("/api/loans")
async def get_loans():
    """Endpoint automatically traced by OpenTelemetry."""
    return {"loans": []}
```

## Automatic Instrumentation

### HTTP Requests (HTTPX)

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import httpx

# Instrument HTTPX for outgoing HTTP requests
HTTPXClientInstrumentor().instrument()

# All HTTP requests are automatically traced
async with httpx.AsyncClient() as client:
    response = await client.get("http://data-api:8000/api/users")
    # Span automatically created with HTTP method, URL, status code
```

### Database Queries (SQLAlchemy)

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import create_async_engine

# Instrument SQLAlchemy for database tracing
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
SQLAlchemyInstrumentor().instrument(engine=engine)

# All database queries are automatically traced
async with engine.begin() as conn:
    result = await conn.execute("SELECT * FROM loans")
    # Span automatically created with SQL query and duration
```

### Redis Operations

```python
from opentelemetry.instrumentation.redis import RedisInstrumentor
import redis.asyncio as redis

# Instrument Redis for cache tracing
RedisInstrumentor().instrument()

# All Redis operations are automatically traced
redis_client = redis.Redis(host="redis", port=6379)
await redis_client.get("user:123")
# Span automatically created with Redis command and key
```

## Manual Instrumentation

### Creating Custom Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    """Create loan with custom tracing."""
    # Automatic span from FastAPI instrumentation

    # Add custom span for business logic
    with tracer.start_as_current_span("process_loan_application") as span:
        # Add attributes to span
        span.set_attribute("loan.amount", loan.amount)
        span.set_attribute("loan.purpose", loan.purpose)
        span.set_attribute("user.id", loan.user_id)

        try:
            # Perform credit check (creates child span)
            with tracer.start_as_current_span("credit_check") as credit_span:
                credit_score = await check_credit(loan.user_id)
                credit_span.set_attribute("credit.score", credit_score)

            # Approve or reject loan
            if credit_score > 700:
                span.set_attribute("loan.status", "approved")
                span.add_event("loan_approved", {"reason": "good_credit"})
                return {"status": "approved"}
            else:
                span.set_attribute("loan.status", "rejected")
                span.add_event("loan_rejected", {"reason": "low_credit"})
                return {"status": "rejected"}

        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
```

### Span Attributes

```python
# CORRECT: Add meaningful attributes
span.set_attribute("http.method", "POST")
span.set_attribute("http.url", "/api/loans")
span.set_attribute("http.status_code", 201)
span.set_attribute("user.id", "user-123")
span.set_attribute("loan.id", "loan-456")
span.set_attribute("loan.amount", 50000)
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.operation", "INSERT")


# INCORRECT: Don't add sensitive data or high cardinality
span.set_attribute("user.password", "secret")  # ❌ Sensitive data
span.set_attribute("request.body", json.dumps(body))  # ❌ Large data
span.set_attribute("timestamp", time.time())  # ❌ High cardinality
```

### Span Events

```python
# Add events to mark important moments in span
span.add_event("credit_check_started")

span.add_event("credit_check_completed", {
    "score": 750,
    "duration_ms": 145
})

span.add_event("notification_sent", {
    "type": "email",
    "recipient": "user@example.com"
})
```

## Context Propagation

### HTTP Headers Propagation

```python
from opentelemetry.propagate import inject
import httpx

# CORRECT: Propagate trace context in HTTP headers
async def call_data_api(user_id: str) -> dict:
    """Call another service with trace context."""
    headers = {}

    # Inject trace context into headers
    inject(headers)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://data-api:8000/api/users/{user_id}",
            headers=headers  # Trace context propagated
        )

    return response.json()
```

### RabbitMQ Message Propagation

```python
from opentelemetry.propagate import inject, extract
import aio_pika

# Producer: Inject trace context into message headers
async def publish_loan_event(loan_id: str):
    """Publish event with trace context."""
    headers = {}
    inject(headers)  # Inject trace context

    message = aio_pika.Message(
        body=json.dumps({"loan_id": loan_id}).encode(),
        headers=headers  # Trace context in message headers
    )

    await channel.default_exchange.publish(message, routing_key="loans")


# Consumer: Extract trace context from message headers
async def consume_loan_event(message: aio_pika.IncomingMessage):
    """Process event with trace context."""
    # Extract trace context from message headers
    context = extract(message.headers)

    # Start new span with extracted context as parent
    with tracer.start_as_current_span(
        "process_loan_event",
        context=context  # Link to parent trace
    ) as span:
        loan_id = json.loads(message.body.decode())["loan_id"]
        span.set_attribute("loan.id", loan_id)

        # Process event (traced as child span)
        await process_loan(loan_id)
```

## Aiogram Bot Tracing

```python
# src/bot/main.py
from opentelemetry import trace
from aiogram import Bot, Dispatcher, types

tracer = trace.get_tracer(__name__)

# Configure tracing
configure_tracing("finance_lending_bot")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    """Handle /start command with tracing."""
    with tracer.start_as_current_span("handle_start_command") as span:
        span.set_attribute("user.id", message.from_user.id)
        span.set_attribute("command", "start")

        # Call API (automatically traced if HTTPX instrumented)
        user = await get_user(message.from_user.id)

        await message.reply(f"Welcome, {user['name']}!")
```

## Background Worker Tracing

```python
# src/worker/tasks.py
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

# Configure tracing
configure_tracing("finance_lending_worker")


async def process_loan_approval(loan_id: str):
    """Process loan approval with tracing."""
    with tracer.start_as_current_span("process_loan_approval") as span:
        span.set_attribute("loan.id", loan_id)

        # Fetch loan data (creates child span)
        loan = await get_loan(loan_id)

        # Perform credit check (creates child span)
        credit_score = await check_credit(loan["user_id"])
        span.set_attribute("credit.score", credit_score)

        # Update loan status (creates child span)
        await update_loan_status(loan_id, "approved")

        span.add_event("loan_processing_completed")
```

## Docker Configuration

### Jaeger Backend

```yaml
# docker-compose.tracing.yml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:1.52
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC receiver
      - "4318:4318"    # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

### Service Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    image: finance_lending_api:latest
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
      - OTEL_SERVICE_NAME=finance_lending_api
      - OTEL_TRACES_SAMPLER=parentbased_traceidratio
      - OTEL_TRACES_SAMPLER_ARG=1.0  # 100% sampling (development)
    depends_on:
      - jaeger
```

## Sampling Configuration

### Production Sampling

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# CORRECT: Sample 10% of traces in production
provider = TracerProvider(
    sampler=TraceIdRatioBased(0.1),  # 10% sampling
    resource=resource
)


# INCORRECT: 100% sampling in production (high overhead)
provider = TracerProvider(
    sampler=TraceIdRatioBased(1.0),  # ❌ 100% sampling
    resource=resource
)
```

### Parent-Based Sampling

```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

# CORRECT: Sample based on parent decision
provider = TracerProvider(
    sampler=ParentBasedTraceIdRatio(0.1),
    resource=resource
)
# If parent sampled, child sampled; otherwise follow ratio
```

## Performance Considerations

### Batch Export

```python
# CORRECT: Batch span export for performance
from opentelemetry.sdk.trace.export import BatchSpanProcessor

span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=2048,
    schedule_delay_millis=5000,  # 5 seconds
    max_export_batch_size=512
)


# INCORRECT: Immediate export (high latency)
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

span_processor = SimpleSpanProcessor(otlp_exporter)  # ❌ Blocks on export
```

### Resource Limits

```python
# CORRECT: Limit span attributes and events
span.set_attribute("request.headers", headers[:100])  # ✅ Truncate large data

# INCORRECT: Unlimited data
span.set_attribute("request.body", json.dumps(body))  # ❌ Can be megabytes
```

## Best Practices

### DO: Use Semantic Conventions

```python
# CORRECT: Use OpenTelemetry semantic conventions
from opentelemetry.semconv.trace import SpanAttributes

span.set_attribute(SpanAttributes.HTTP_METHOD, "POST")
span.set_attribute(SpanAttributes.HTTP_URL, "/api/loans")
span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, 201)
span.set_attribute(SpanAttributes.DB_SYSTEM, "postgresql")
span.set_attribute(SpanAttributes.DB_STATEMENT, "SELECT * FROM loans")
```

### DO: Record Exceptions

```python
# CORRECT: Record exceptions in spans
try:
    result = await perform_operation()
except Exception as e:
    span.record_exception(e)
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
    raise
```

### DON'T: Create Too Many Spans

```python
# INCORRECT: Excessive span creation (performance overhead)
for i in range(10000):
    with tracer.start_as_current_span(f"iteration_{i}"):  # ❌ 10k spans
        process_item(i)


# CORRECT: Batch operations
with tracer.start_as_current_span("process_items") as span:
    span.set_attribute("item.count", 10000)
    for i in range(10000):
        process_item(i)  # ✅ Single span for batch
```

## Environment Variables

```bash
# OpenTelemetry environment variables
export OTEL_SERVICE_NAME="finance_lending_api"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://jaeger:4317"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_TRACES_SAMPLER="parentbased_traceidratio"
export OTEL_TRACES_SAMPLER_ARG="0.1"  # 10% sampling
export OTEL_RESOURCE_ATTRIBUTES="environment=production,version=1.2.3"
```

## Checklist

- [ ] Install OpenTelemetry SDK and instrumentation libraries
- [ ] Configure tracer provider with service name and resource
- [ ] Set up OTLP exporter for Jaeger/Zipkin
- [ ] Instrument FastAPI with automatic instrumentation
- [ ] Instrument HTTPX for HTTP client tracing
- [ ] Instrument SQLAlchemy for database tracing
- [ ] Instrument Redis for cache tracing
- [ ] Add custom spans for business logic
- [ ] Propagate trace context in HTTP headers
- [ ] Propagate trace context in RabbitMQ messages
- [ ] Configure sampling for production (10-20%)
- [ ] Use batch span processor for performance
- [ ] Follow OpenTelemetry semantic conventions
- [ ] Test trace collection in Jaeger UI

## Related Documents

- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing patterns
- `docs/atomic/observability/tracing/trace-correlation.md` — Cross-service trace correlation
- `docs/atomic/observability/tracing/jaeger-configuration.md` — Jaeger setup and configuration
- `docs/atomic/observability/tracing/performance-monitoring.md` — Performance analysis with tracing
