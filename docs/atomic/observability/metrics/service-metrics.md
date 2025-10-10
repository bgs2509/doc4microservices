# Service-Level Metrics

Track service health, performance, and resource usage with standardized service-level metrics. Service metrics enable monitoring individual microservice behavior, detecting performance degradation, capacity planning, and troubleshooting service-specific issues.

This document covers essential service metrics (request rate, latency, error rate, resource usage), implementing metrics middleware for FastAPI and Aiogram, tracking database operations, monitoring async tasks, and establishing service SLIs/SLOs. Service metrics provide operational visibility into each microservice.

Service metrics answer operational questions: Is this service healthy? What's the request throughput? Are errors increasing? Is memory leaking? Is database performance degrading? Without service metrics, operators cannot distinguish between healthy services and failing ones until complete outages occur.

## Core Service Metrics

### HTTP Request Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Request count
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# Request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Active requests
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Current HTTP requests being processed'
)

# Request size
http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    buckets=[100, 1000, 10000, 100000, 1000000]
)

# Response size
http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    buckets=[100, 1000, 10000, 100000, 1000000]
)
```

### Database Metrics

```python
# Database operations
db_operations_total = Counter(
    'db_operations_total',
    'Total database operations',
    ['operation', 'table', 'status']
)

db_operation_duration_seconds = Histogram(
    'db_operation_duration_seconds',
    'Database operation duration',
    ['operation', 'table'],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
)

# Connection pool
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Idle database connections'
)
```

### Cache Metrics

```python
# Cache operations
cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']  # result: hit, miss
)

cache_operation_duration_seconds = Histogram(
    'cache_operation_duration_seconds',
    'Cache operation duration',
    ['operation']
)
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track HTTP metrics."""
    # Track active requests
    http_requests_in_progress.inc()

    # Track request size
    content_length = request.headers.get("content-length", 0)
    http_request_size_bytes.observe(int(content_length))

    # Time request
    start_time = time.time()

    try:
        response = await call_next(request)

        # Track duration
        duration = time.time() - start_time
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        # Track request count
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        # Track response size
        if hasattr(response, "body"):
            http_response_size_bytes.observe(len(response.body))

        return response

    finally:
        http_requests_in_progress.dec()
```

## Database Instrumentation

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start."""
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query completion."""
    total = time.time() - conn.info['query_start_time'].pop()

    # Extract table name from statement
    table = extract_table_from_sql(statement)
    operation = extract_operation_from_sql(statement)

    db_operation_duration_seconds.labels(
        operation=operation,
        table=table
    ).observe(total)

    db_operations_total.labels(
        operation=operation,
        table=table,
        status='success'
    ).inc()
```

## Resource Metrics

```python
import psutil
from prometheus_client import Gauge

# CPU usage
process_cpu_usage_percent = Gauge(
    'process_cpu_usage_percent',
    'Process CPU usage percentage'
)

# Memory usage
process_memory_usage_bytes = Gauge(
    'process_memory_usage_bytes',
    'Process memory usage in bytes'
)

# Update periodically
def update_resource_metrics():
    """Update resource metrics."""
    process = psutil.Process()
    process_cpu_usage_percent.set(process.cpu_percent())
    process_memory_usage_bytes.set(process.memory_info().rss)
```

## Aiogram Bot Metrics

```python
from aiogram import Bot, Dispatcher
from prometheus_client import Counter, Histogram

# Bot metrics
bot_messages_received_total = Counter(
    'bot_messages_received_total',
    'Total messages received',
    ['command']
)

bot_messages_sent_total = Counter(
    'bot_messages_sent_total',
    'Total messages sent',
    ['status']
)

bot_message_processing_duration_seconds = Histogram(
    'bot_message_processing_duration_seconds',
    'Message processing duration',
    ['command']
)


@dp.message_handler()
async def track_message(message: types.Message):
    """Track bot message metrics."""
    command = message.text.split()[0] if message.text else "unknown"

    bot_messages_received_total.labels(command=command).inc()

    start_time = time.time()
    try:
        await process_message(message)

        bot_messages_sent_total.labels(status='success').inc()

    except Exception:
        bot_messages_sent_total.labels(status='failure').inc()
        raise

    finally:
        duration = time.time() - start_time
        bot_message_processing_duration_seconds.labels(
            command=command
        ).observe(duration)
```

## Querying Service Metrics

```promql
# Request rate (requests/sec)
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# Database query time
rate(db_operation_duration_seconds_sum[5m])
/ rate(db_operation_duration_seconds_count[5m])

# Cache hit rate
rate(cache_operations_total{result="hit"}[5m])
/ rate(cache_operations_total[5m])

# Memory usage (MB)
process_memory_usage_bytes / 1024 / 1024
```

## Checklist

- [ ] Implement HTTP request metrics
- [ ] Track request duration and count
- [ ] Monitor error rates
- [ ] Instrument database operations
- [ ] Track cache hit/miss rates
- [ ] Monitor resource usage (CPU, memory)
- [ ] Expose /metrics endpoint
- [ ] Test metric collection
- [ ] Create service dashboards
- [ ] Set up SLO-based alerts

## Related Documents

- `docs/atomic/observability/metrics/prometheus-setup.md` — Prometheus setup
- `docs/atomic/observability/metrics/custom-metrics.md` — Custom business metrics
- `docs/atomic/observability/metrics/golden-signals.md` — Golden signals monitoring
- `docs/atomic/observability/metrics/dashboards.md` — Grafana dashboards
