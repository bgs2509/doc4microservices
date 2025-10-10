# Distributed Tracing

Implement end-to-end distributed tracing to track requests flowing through multiple microservices, enabling performance analysis, error debugging, and dependency mapping. Distributed tracing visualizes request paths across service boundaries, revealing bottlenecks, failures, and unexpected behaviors in complex microservices architectures.

This document covers tracing patterns for synchronous HTTP communication, asynchronous event-driven workflows via RabbitMQ, cross-service error propagation, trace visualization in Jaeger UI, performance analysis techniques, and debugging distributed failures. Distributed tracing transforms opaque microservices into transparent, observable systems.

Without distributed tracing, debugging production issues requires manually searching logs across dozens of services, guessing which service failed, and reconstructing request flows from timestamps. With tracing, you see the complete request journey in seconds: API → Data Service → Database → Worker → Notification Service, with exact timings and errors.

## End-to-End Request Flow

### HTTP API Request

```python
# Step 1: User calls finance_lending_api
@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    """Create loan - entry point for distributed trace."""
    # Span 1: "POST /api/loans" (automatic from FastAPI)

    # Span 2: Validate user (custom span)
    with tracer.start_as_current_span("validate_user") as span:
        span.set_attribute("user.id", loan.user_id)

        # Span 3: Call finance_data_postgres_api (automatic from HTTPX)
        user = await http_client.get(
            f"http://data-api:8000/api/users/{loan.user_id}"
        )
        # HTTP call creates child span with propagated trace context

    # Span 4: Check credit score (custom span)
    with tracer.start_as_current_span("credit_check") as span:
        # Span 5: Call external credit API (automatic from HTTPX)
        credit_score = await credit_api.get_score(loan.user_id)
        span.set_attribute("credit.score", credit_score)

    # Span 6: Save loan to database (automatic from SQLAlchemy)
    loan_record = await db.create_loan(loan)

    # Span 7: Publish event to RabbitMQ (manual span)
    with tracer.start_as_current_span("publish_loan_event") as span:
        await publish_event("loan.created", loan_record.id)

    return {"id": loan_record.id, "status": "pending"}


# Result: Single distributed trace with 7 spans showing complete flow
# Trace ID propagates through all HTTP calls and events
```

### Trace Visualization

```
Trace: create_loan (trace_id: abc123)
├─ POST /api/loans [200ms] (finance_lending_api)
│  ├─ validate_user [45ms]
│  │  └─ GET /api/users/456 [40ms] (finance_data_postgres_api)
│  │     └─ SELECT * FROM users [5ms] (postgres)
│  ├─ credit_check [80ms]
│  │  └─ POST /credit-score [75ms] (external_credit_api)
│  ├─ INSERT INTO loans [20ms] (postgres)
│  └─ publish_loan_event [10ms]
│     └─ RabbitMQ publish [8ms]
```

## Service-to-Service HTTP Tracing

### API to Data Service

```python
# finance_lending_api → finance_data_postgres_api
from opentelemetry.propagate import inject
import httpx

async def get_user(user_id: str) -> dict:
    """Call data service with trace context propagation."""
    with tracer.start_as_current_span("call_data_service") as span:
        span.set_attribute("service.name", "finance_data_postgres_api")
        span.set_attribute("endpoint", f"/api/users/{user_id}")

        headers = {}
        inject(headers)  # Inject trace context (traceparent header)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://data-api:8000/api/users/{user_id}",
                headers=headers
            )

        span.set_attribute("http.status_code", response.status_code)
        return response.json()


# finance_data_postgres_api receives request with trace context
@app.get("/api/users/{user_id}")
async def get_user_endpoint(user_id: str):
    """Handle request - trace context automatically extracted by FastAPI instrumentation."""
    # This span is child of calling service's span

    with tracer.start_as_current_span("fetch_user_from_db") as span:
        span.set_attribute("user.id", user_id)
        user = await db.get_user(user_id)  # Database query span created
        return user
```

### Multiple Service Calls

```python
@app.get("/api/loans/{loan_id}/details")
async def get_loan_details(loan_id: str):
    """Fetch loan details from multiple services."""
    with tracer.start_as_current_span("fetch_loan_details") as span:
        span.set_attribute("loan.id", loan_id)

        # Parallel calls - all part of same trace
        loan, user, documents = await asyncio.gather(
            get_loan(loan_id),      # Call data service
            get_user(loan.user_id),  # Call data service
            get_documents(loan_id)   # Call document service
        )
        # Each creates child span with propagated trace context

        span.set_attribute("user.id", user["id"])
        span.set_attribute("documents.count", len(documents))

        return {
            "loan": loan,
            "user": user,
            "documents": documents
        }


# Result trace:
# GET /api/loans/123/details [150ms]
# ├─ fetch_loan_details [145ms]
# │  ├─ get_loan [50ms] → finance_data_postgres_api
# │  ├─ get_user [45ms] → finance_data_postgres_api
# │  └─ get_documents [40ms] → finance_document_api
```

## Event-Driven Tracing

### RabbitMQ Producer

```python
from opentelemetry.propagate import inject
import aio_pika

async def publish_loan_created_event(loan_id: str, user_id: str):
    """Publish event with trace context."""
    with tracer.start_as_current_span("publish_loan_created") as span:
        span.set_attribute("loan.id", loan_id)
        span.set_attribute("event.type", "loan.created")

        # Inject trace context into message headers
        headers = {}
        inject(headers)

        message_body = {
            "loan_id": loan_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }

        message = aio_pika.Message(
            body=json.dumps(message_body).encode(),
            headers=headers,  # Trace context propagated
            content_type="application/json"
        )

        await channel.default_exchange.publish(
            message,
            routing_key="loans.created"
        )

        span.add_event("event_published")
```

### RabbitMQ Consumer

```python
from opentelemetry.propagate import extract

async def consume_loan_created(message: aio_pika.IncomingMessage):
    """Process event with trace context from producer."""
    # Extract trace context from message headers
    context = extract(message.headers)

    # Start span linked to producer's trace
    with tracer.start_as_current_span(
        "process_loan_created",
        context=context  # Links to original trace
    ) as span:
        body = json.loads(message.body.decode())
        loan_id = body["loan_id"]

        span.set_attribute("loan.id", loan_id)
        span.set_attribute("event.type", "loan.created")

        # Process loan (creates child spans)
        with tracer.start_as_current_span("generate_documents") as doc_span:
            await generate_loan_documents(loan_id)

        with tracer.start_as_current_span("send_notification") as notif_span:
            await send_approval_notification(loan_id)

        span.add_event("event_processed")

    await message.ack()


# Result: Async event processing linked to original trace
# Trace shows: API → RabbitMQ → Worker → Document Generation → Notification
```

### Multi-Stage Event Processing

```python
# Stage 1: API publishes event
@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    loan_id = await save_loan(loan)
    await publish_event("loan.created", loan_id)  # Trace continues here
    return {"id": loan_id}


# Stage 2: Worker processes event and publishes next stage
async def process_loan_created(message):
    context = extract(message.headers)
    with tracer.start_as_current_span("verify_loan", context=context) as span:
        loan_id = json.loads(message.body)["loan_id"]

        # Verify documents
        verified = await verify_documents(loan_id)

        if verified:
            # Publish next stage event
            await publish_event("loan.verified", loan_id)  # Trace continues

        span.set_attribute("verification.result", verified)


# Stage 3: Another worker handles verified loans
async def process_loan_verified(message):
    context = extract(message.headers)
    with tracer.start_as_current_span("approve_loan", context=context) as span:
        loan_id = json.loads(message.body)["loan_id"]

        # Final approval
        await approve_loan(loan_id)
        span.add_event("loan_approved")


# Result: Single trace spans entire workflow
# API → Worker1 (verify) → Worker2 (approve)
```

## Error Propagation

### HTTP Error Tracing

```python
@app.get("/api/loans/{loan_id}")
async def get_loan(loan_id: str):
    """Handle errors in distributed trace."""
    with tracer.start_as_current_span("get_loan") as span:
        span.set_attribute("loan.id", loan_id)

        try:
            # Call data service
            loan = await data_service.get_loan(loan_id)

            if not loan:
                # Record error in span
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, "Loan not found")
                )
                span.add_event("loan_not_found")
                raise HTTPException(status_code=404, detail="Loan not found")

            return loan

        except httpx.HTTPStatusError as e:
            # Record external service error
            span.record_exception(e)
            span.set_status(trace.Status(
                trace.StatusCode.ERROR,
                f"Data service error: {e.response.status_code}"
            ))
            raise HTTPException(
                status_code=502,
                detail="Data service unavailable"
            )

        except Exception as e:
            # Record unexpected error
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise


# Result: Error visible in trace with full context
# Trace shows: API → Data Service [ERROR 502] → Database timeout
```

### Event Processing Errors

```python
async def process_loan_event(message: aio_pika.IncomingMessage):
    """Handle errors in event processing."""
    context = extract(message.headers)

    with tracer.start_as_current_span(
        "process_loan_event",
        context=context
    ) as span:
        try:
            loan_id = json.loads(message.body)["loan_id"]
            span.set_attribute("loan.id", loan_id)

            # Process loan
            result = await process_loan(loan_id)

            await message.ack()
            span.add_event("message_processed")

        except ValueError as e:
            # Invalid message format
            span.record_exception(e)
            span.set_status(trace.Status(
                trace.StatusCode.ERROR,
                "Invalid message format"
            ))
            await message.reject(requeue=False)  # Dead letter queue

        except Exception as e:
            # Processing error - retry
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            await message.nack(requeue=True)  # Requeue for retry


# Result: Failed events visible in trace with error details
# Trace shows: API → Event → Worker [ERROR] → Retry
```

## Performance Analysis

### Identifying Bottlenecks

```python
# Query Jaeger for slow traces
# UI Filter: duration > 1000ms

# Analyze trace:
# Trace: create_loan [2500ms] ← SLOW
# ├─ POST /api/loans [2500ms]
# │  ├─ validate_user [50ms]
# │  ├─ credit_check [2300ms] ← BOTTLENECK
# │  │  └─ POST /credit-score [2250ms] ← External API slow
# │  └─ save_loan [100ms]

# Solution: Add caching for credit scores
@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    with tracer.start_as_current_span("credit_check") as span:
        # Check cache first
        cached_score = await redis.get(f"credit:{loan.user_id}")

        if cached_score:
            span.add_event("credit_score_cache_hit")
            credit_score = int(cached_score)
        else:
            # Call external API only if not cached
            credit_score = await credit_api.get_score(loan.user_id)
            await redis.setex(f"credit:{loan.user_id}", 3600, credit_score)
            span.add_event("credit_score_cache_miss")

        span.set_attribute("credit.score", credit_score)
```

### Comparing Traces

```python
# Before optimization:
# Trace: process_loan_batch [5000ms]
# └─ for each loan [5000ms total]
#    ├─ get_loan [100ms] × 50 = 5000ms

# After optimization (parallel processing):
# Trace: process_loan_batch [500ms]
# └─ asyncio.gather [500ms]
#    └─ get_loan [100ms] × 50 (parallel)

@app.post("/api/loans/batch")
async def process_loan_batch(loan_ids: list[str]):
    """Process loans in parallel."""
    with tracer.start_as_current_span("process_batch") as span:
        span.set_attribute("batch.size", len(loan_ids))

        # Parallel processing
        results = await asyncio.gather(
            *[process_loan(loan_id) for loan_id in loan_ids]
        )

        span.add_event("batch_completed")
        return results
```

## Trace Sampling

### Adaptive Sampling

```python
from opentelemetry.sdk.trace.sampling import (
    ParentBasedTraceIdRatio,
    TraceIdRatioBased
)

# CORRECT: Sample 10% in production, 100% for errors
class ErrorAwareSampler:
    """Sample all errors, 10% of successes."""

    def __init__(self):
        self.default_sampler = TraceIdRatioBased(0.1)

    def should_sample(self, context, trace_id, name, kind, attributes, links):
        # Always sample if error occurred
        if attributes.get("http.status_code", 0) >= 500:
            return trace.SamplingResult(
                decision=trace.SamplingDecision.RECORD_AND_SAMPLE
            )

        # Otherwise use default sampling
        return self.default_sampler.should_sample(
            context, trace_id, name, kind, attributes, links
        )


provider = TracerProvider(
    sampler=ErrorAwareSampler(),
    resource=resource
)
```

### Sampling by Endpoint

```python
# CORRECT: Sample critical endpoints 100%, others 10%
def custom_sampler(context, trace_id, name, kind, attributes):
    """Sample based on endpoint importance."""
    endpoint = attributes.get("http.route", "")

    # Critical endpoints: 100%
    if endpoint in ["/api/payments", "/api/loans/approve"]:
        return trace.SamplingResult(
            decision=trace.SamplingDecision.RECORD_AND_SAMPLE
        )

    # Other endpoints: 10%
    return TraceIdRatioBased(0.1).should_sample(
        context, trace_id, name, kind, attributes, None
    )
```

## Best Practices

### DO: Add Business Context

```python
# CORRECT: Add meaningful business attributes
with tracer.start_as_current_span("process_loan") as span:
    span.set_attribute("loan.id", loan_id)
    span.set_attribute("loan.amount", loan.amount)
    span.set_attribute("loan.status", "pending")
    span.set_attribute("user.id", user_id)
    span.set_attribute("user.tier", "premium")
    span.add_event("credit_check_passed", {"score": 750})


# INCORRECT: Missing context
with tracer.start_as_current_span("process"):  # ❌ Generic name
    result = do_something()  # ❌ No attributes
```

### DO: Propagate Context Everywhere

```python
# CORRECT: Propagate in all inter-service calls
headers = {}
inject(headers)  # Always inject before calling another service

response = await client.get(url, headers=headers)


# INCORRECT: Missing propagation
response = await client.get(url)  # ❌ New trace started, no linking
```

### DON'T: Create Excessive Spans

```python
# INCORRECT: Too granular
for item in items:
    with tracer.start_as_current_span(f"process_item_{item.id}"):
        process(item)  # ❌ 10000 spans for batch


# CORRECT: Appropriate granularity
with tracer.start_as_current_span("process_items") as span:
    span.set_attribute("item.count", len(items))
    for item in items:
        process(item)  # ✅ Single span for batch
```

## Checklist

- [ ] Instrument all HTTP client calls with trace context propagation
- [ ] Propagate trace context in RabbitMQ message headers
- [ ] Extract trace context in event consumers
- [ ] Add custom spans for business logic
- [ ] Record exceptions in spans with full context
- [ ] Add business attributes to spans (IDs, amounts, statuses)
- [ ] Add events for important milestones
- [ ] Configure sampling for production (10-20%)
- [ ] Test trace visualization in Jaeger UI
- [ ] Verify cross-service trace linking
- [ ] Analyze slow traces to identify bottlenecks
- [ ] Monitor trace sampling rate

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md` — OpenTelemetry configuration
- `docs/atomic/observability/tracing/trace-correlation.md` — Cross-service correlation
- `docs/atomic/observability/tracing/jaeger-configuration.md` — Jaeger backend setup
- `docs/atomic/observability/tracing/performance-monitoring.md` — Performance analysis
