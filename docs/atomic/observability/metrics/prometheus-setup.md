# Prometheus Setup

Configure Prometheus for collecting, storing, and querying metrics from microservices. Prometheus provides time-series metric storage, powerful query language (PromQL), service discovery, and alerting capabilities essential for monitoring distributed systems.

This document covers Prometheus installation with Docker, configuration for scraping FastAPI/Aiogram services, service discovery, metric retention, and integration with Python prometheus_client library. Prometheus is the foundation of metrics-based observability.

Prometheus enables answering operational questions: Is the system healthy? What's the request rate? How many errors occurred? What's the 95th percentile latency? How much memory is each service using? Without metrics, teams operate blind, discovering issues only after users report them.

## Docker Setup

```yaml
# docker-compose.metrics.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

volumes:
  prometheus_data:
```

## Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    environment: 'production'

scrape_configs:
  - job_name: 'finance_lending_api'
    static_configs:
      - targets: ['api:8000']
        labels:
          service: 'finance_lending_api'

  - job_name: 'finance_data_postgres_api'
    static_configs:
      - targets: ['data-api:8000']
        labels:
          service: 'finance_data_postgres_api'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

## Python Integration

```python
# Install prometheus_client
pip install prometheus-client==0.19.0
```

```python
# src/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from fastapi import FastAPI, Response

app = FastAPI()

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Track request metrics."""
    active_requests.inc()

    with http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).time():
        response = await call_next(request)

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()

    active_requests.dec()
    return response


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )
```

## Service Discovery

```yaml
# prometheus.yml - Docker service discovery
scrape_configs:
  - job_name: 'docker'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: [__meta_docker_container_label_prometheus_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_docker_container_label_prometheus_port]
        target_label: __address__
        replacement: '$1:${1}'
```

## Best Practices

### DO: Label Consistently

```python
# CORRECT: Consistent labels
http_requests_total.labels(
    method="POST",
    endpoint="/api/loans",
    status_code=201
).inc()


# INCORRECT: Inconsistent labels
http_requests_total.labels("POST", "/api/loans", "201").inc()  # ❌ Positional
```

### DO: Use Appropriate Metric Types

```python
# Counter: Monotonically increasing
requests_total = Counter('requests_total', 'Total requests')

# Gauge: Can go up or down
active_connections = Gauge('active_connections', 'Active connections')

# Histogram: Observations (durations, sizes)
request_duration = Histogram('request_duration_seconds', 'Request duration')

# Summary: Similar to histogram (use histogram)
```

## Querying

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])

# 95th percentile latency
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Memory usage
process_resident_memory_bytes / 1024 / 1024
```

## Checklist

- [ ] Install Prometheus with Docker
- [ ] Configure scrape targets
- [ ] Instrument services with prometheus_client
- [ ] Expose /metrics endpoint
- [ ] Test metric collection
- [ ] Configure retention policy
- [ ] Set up service discovery (optional)
- [ ] Create Grafana dashboards
- [ ] Configure alerting rules

## Related Documents

- `docs/atomic/observability/metrics/custom-metrics.md` — Custom metric implementation
- `docs/atomic/observability/metrics/service-metrics.md` — Service-level metrics
- `docs/atomic/observability/metrics/golden-signals.md` — Golden signals monitoring
- `docs/atomic/observability/metrics/dashboards.md` — Grafana dashboard creation
