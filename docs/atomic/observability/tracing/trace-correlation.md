# Trace Correlation

Correlate traces with logs and metrics to achieve unified observability across distributed systems. Trace correlation enables jumping from a slow trace to related logs, linking error logs to traces for root cause analysis, and correlating performance metrics with specific requests, creating a complete operational picture.

This document covers correlation ID propagation patterns, linking traces to structured logs, associating metrics with trace context, unified observability dashboards in Grafana, debugging workflows that leverage all three signals (traces/logs/metrics), and exemplar-based correlation. Correlation transforms isolated observability signals into a cohesive narrative.

Without correlation, engineers waste hours jumping between tools: finding a slow trace in Jaeger, manually searching for request IDs in Kibana logs, then checking Grafana metrics for the same timeframe. With correlation, you click a trace span → see related logs → view associated metrics → identify root cause in seconds, not hours.

## Correlation IDs

### Request ID Propagation

```python
# src/middleware/correlation.py
from opentelemetry import trace
import structlog
import uuid

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Propagate correlation IDs across all signals."""
    # Get or generate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = f"req-{uuid.uuid4()}"

    # Get trace context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

    # Bind all IDs to logger
    logger = structlog.get_logger().bind(
        request_id=request_id,
        trace_id=trace_id,
        span_id=span_id,
        service="finance_lending_api"
    )

    # Add IDs to span attributes
    span.set_attribute("request.id", request_id)

    # Store in request state
    request.state.request_id = request_id
    request.state.trace_id = trace_id
    request.state.span_id = span_id
    request.state.logger = logger

    # Log request with all IDs
    logger.info(
        "http_request_started",
        method=request.method,
        path=request.url.path
    )

    response = await call_next(request)

    # Add IDs to response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id

    logger.info(
        "http_request_completed",
        status_code=response.status_code,
        duration_ms=compute_duration()
    )

    return response
```

### Correlation in Logs

```python
# Result: Every log has request_id, trace_id, span_id
{
    "timestamp": "2024-01-10T10:30:45.123Z",
    "level": "info",
    "event": "http_request_started",
    "service": "finance_lending_api",
    "request_id": "req-abc-123",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7",
    "method": "POST",
    "path": "/api/loans"
}

# Query logs by trace ID:
# Kibana: trace_id:"4bf92f3577b34da6a3ce929d0e0e4736"
# Shows all logs from all services in this trace
```

## Trace to Log Correlation

### Link Trace Spans to Logs

```python
@app.post("/api/loans")
async def create_loan(loan: LoanCreate, request: Request):
    """Create loan with correlated logs."""
    logger = request.state.logger

    with tracer.start_as_current_span("create_loan") as span:
        span.set_attribute("loan.amount", loan.amount)
        span.set_attribute("user.id", loan.user_id)

        # Log with trace context
        logger.info(
            "loan_creation_started",
            loan_amount=loan.amount,
            user_id=loan.user_id
        )

        try:
            # Check credit
            with tracer.start_as_current_span("credit_check") as credit_span:
                credit_score = await check_credit(loan.user_id)

                # Log result with span context
                logger.info(
                    "credit_check_completed",
                    credit_score=credit_score,
                    span_name=credit_span.name
                )

                if credit_score < 650:
                    logger.warning(
                        "loan_rejected_low_credit",
                        credit_score=credit_score,
                        threshold=650
                    )
                    span.set_attribute("loan.status", "rejected")
                    raise HTTPException(
                        status_code=400,
                        detail="Insufficient credit score"
                    )

            # Save loan
            loan_record = await db.create_loan(loan)

            logger.info(
                "loan_created",
                loan_id=loan_record.id,
                status="approved"
            )

            return {"id": loan_record.id}

        except Exception as e:
            logger.error(
                "loan_creation_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            span.record_exception(e)
            raise


# Result: Click trace span in Jaeger → copy trace_id → paste in Kibana
# Instantly see all logs from this request across all services
```

### Jaeger to Kibana Integration

```yaml
# Jaeger UI configuration
jaeger:
  query:
    base-path: /
    ui-config: |
      {
        "linkPatterns": [
          {
            "type": "logs",
            "key": "trace_id",
            "url": "https://kibana.example.com/app/kibana#/discover?_a=(query:(query_string:(query:'trace_id:#{trace_id}')))",
            "text": "View Logs in Kibana"
          }
        ]
      }

# Result: "View Logs" button in Jaeger UI opens Kibana with trace logs
```

## Trace to Metrics Correlation

### Exemplars (Prometheus + Grafana)

```python
from prometheus_client import Histogram
from opentelemetry import trace

# Create histogram with exemplar support
request_duration = Histogram(
    'http_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)


@app.middleware("http")
async def metrics_with_exemplars(request: Request, call_next):
    """Record metrics with trace exemplars."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    # Get trace context for exemplar
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')

    # Record metric with exemplar (trace ID)
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(
        duration,
        exemplar={'trace_id': trace_id}  # Link to trace
    )

    return response


# Result: Grafana shows high latency spike → click spike → see trace ID
# Click "View Trace" → opens Jaeger with exact slow request
```

### Metrics Dashboard with Trace Links

```yaml
# Grafana dashboard with trace links
panels:
  - title: "Request Latency (P95)"
    targets:
      - expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
    options:
      dataLinks:
        - title: "View Traces"
          url: "https://jaeger.example.com/search?service=${__field.labels.service}&start=${__from}&end=${__to}"

  - title: "Error Rate"
    targets:
      - expr: rate(http_requests_total{status_code=~"5.."}[5m])
    options:
      dataLinks:
        - title: "View Error Traces"
          url: "https://jaeger.example.com/search?service=${__field.labels.service}&tags={\"error\":\"true\"}"
```

## Unified Observability Dashboard

### Grafana Unified View

```json
{
  "dashboard": {
    "title": "Finance Lending API - Unified Observability",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {"expr": "rate(http_requests_total[5m])"}
        ],
        "dataLinks": [
          {
            "title": "View Traces",
            "url": "https://jaeger.example.com/search?service=finance_lending_api&start=${__from}&end=${__to}"
          }
        ]
      },
      {
        "title": "Error Logs (Last 100)",
        "type": "logs",
        "targets": [
          {
            "query": "level:error AND service:finance_lending_api",
            "datasource": "Elasticsearch"
          }
        ],
        "options": {
          "showTime": true,
          "showLabels": true
        }
      },
      {
        "title": "Slow Traces (> 1s)",
        "type": "table",
        "targets": [
          {
            "datasource": "Jaeger",
            "query": "service=finance_lending_api duration>1s"
          }
        ]
      }
    ]
  }
}
```

## Debugging Workflows

### Scenario 1: High Latency Investigation

```python
# Step 1: Grafana shows P95 latency spike at 10:30 AM
# Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
# Result: P95 = 2.5 seconds (normally 200ms)

# Step 2: Click exemplar → opens Jaeger with trace ID
# Trace: POST /api/loans [2500ms]
# ├─ credit_check [2300ms] ← BOTTLENECK
# │  └─ POST /credit-score [2250ms]

# Step 3: Copy trace_id from Jaeger → search in Kibana
# Kibana query: trace_id:"4bf92f3577b34da6a3ce929d0e0e4736"
# Logs show:
{
    "event": "credit_check_timeout",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "error": "External API timeout after 2000ms",
    "upstream_service": "credit_bureau_api"
}

# Root cause identified: External API timeout
# Solution: Add timeout + circuit breaker + caching
```

### Scenario 2: Error Rate Investigation

```python
# Step 1: Grafana shows error rate spike
# Query: rate(http_requests_total{status_code=~"5.."}[5m])
# Result: 50 errors/sec (normally 0)

# Step 2: Click "View Error Traces" → Jaeger filtered by error=true
# Multiple traces show:
# POST /api/loans [ERROR 500]
# └─ database_query [ERROR] "Connection pool exhausted"

# Step 3: Search logs by trace_id in Kibana
# Logs reveal:
{
    "event": "database_connection_failed",
    "error": "FATAL: remaining connection slots reserved",
    "active_connections": 100,
    "max_connections": 100
}

# Root cause: Database connection pool exhaustion
# Solution: Increase pool size, add connection timeout
```

### Scenario 3: User-Reported Issue

```python
# User reports: "My loan application failed"

# Step 1: Get request_id from user's screenshot/email
# request_id: "req-abc-123"

# Step 2: Search logs in Kibana
# Query: request_id:"req-abc-123"
# Logs show:
{
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "event": "loan_creation_failed",
    "error": "User verification failed",
    "user_id": "user-456"
}

# Step 3: Open trace in Jaeger
# URL: https://jaeger/trace/4bf92f3577b34da6a3ce929d0e0e4736
# Trace shows:
# POST /api/loans [500ms]
# └─ verify_user [ERROR 404]
#    └─ GET /api/users/456 [ERROR 404] "User not found"

# Step 4: Check user service metrics in Grafana
# Query: rate(http_requests_total{service="data_api",endpoint="/api/users/:id",status_code="404"}[1h])
# Result: 404 rate spiked at 9:00 AM (during user migration)

# Root cause: User not migrated to new database
# Solution: Complete user migration, sync user data
```

## Correlation Best Practices

### DO: Always Propagate IDs

```python
# CORRECT: Propagate request_id, trace_id everywhere
headers = {
    "X-Request-ID": request_id,
    "X-Trace-ID": trace_id
}
inject(headers)  # OpenTelemetry trace context

async with httpx.AsyncClient() as client:
    await client.post(url, headers=headers)

# Publish to RabbitMQ
message = aio_pika.Message(
    body=body,
    headers={
        "request_id": request_id,
        "trace_id": trace_id
    }
)


# INCORRECT: Missing correlation IDs
await client.post(url)  # ❌ No request_id, no trace_id
```

### DO: Include IDs in All Logs

```python
# CORRECT: Bind IDs to logger
logger = structlog.get_logger().bind(
    request_id=request_id,
    trace_id=trace_id,
    span_id=span_id,
    service="finance_lending_api"
)

logger.info("operation_completed", result="success")


# INCORRECT: Missing IDs
logger.info("operation completed")  # ❌ Can't correlate
```

### DO: Add Trace Links to Dashboards

```python
# CORRECT: Enable click-through from metrics to traces
panels:
  - title: "Error Rate"
    dataLinks:
      - title: "View Error Traces"
        url: "https://jaeger/search?tags={\"error\":\"true\"}&start=${__from}"


# INCORRECT: No navigation between tools
# Users manually copy timestamps and search
```

### DON'T: Use Different ID Formats

```python
# INCORRECT: Inconsistent ID formats
api_service:    request_id = "req-abc-123"
data_service:   request_id = "ABC123"      # ❌ Different format
worker_service: request_id = "req_abc_123" # ❌ Underscore vs hyphen


# CORRECT: Consistent format across all services
request_id = f"req-{uuid.uuid4()}"  # ✅ Always "req-{uuid}"
```

## Implementation Checklist

- [ ] Add correlation middleware to all services
- [ ] Generate or extract request_id in API gateway/first service
- [ ] Propagate request_id in all HTTP headers (X-Request-ID)
- [ ] Propagate trace context with OpenTelemetry (traceparent header)
- [ ] Include request_id in all RabbitMQ message headers
- [ ] Bind request_id, trace_id, span_id to structured logger
- [ ] Add trace_id to all log entries
- [ ] Return request_id in API responses (X-Request-ID header)
- [ ] Configure Jaeger → Kibana integration (link patterns)
- [ ] Add exemplars to Prometheus metrics
- [ ] Configure Grafana → Jaeger integration (data links)
- [ ] Create unified observability dashboard
- [ ] Document debugging workflows for common scenarios
- [ ] Test correlation: trace → logs → metrics → back to trace

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md` — OpenTelemetry configuration
- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing patterns
- `docs/atomic/observability/logging/structured-logging.md` — Structured logging
- `docs/atomic/observability/logging/log-correlation.md` — Log correlation techniques
- `docs/atomic/observability/metrics/custom-metrics.md` — Metrics with exemplars
