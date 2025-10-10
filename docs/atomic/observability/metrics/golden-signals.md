# Golden Signals Monitoring

Monitor the four golden signals (latency, traffic, errors, saturation) to assess service health and user experience. Golden signals provide comprehensive operational visibility by focusing on user-facing metrics that directly impact system reliability and performance.

This document covers implementing golden signals monitoring for microservices, defining SLIs (Service Level Indicators), setting SLOs (Service Level Objectives), alerting strategies, and Grafana dashboard design. Golden signals methodology originated from Google's Site Reliability Engineering practices.

Golden signals answer critical questions: Is the service fast enough? Is it handling expected load? Are users experiencing errors? Is the service approaching capacity limits? These four metrics provide early warning of issues before they escalate to outages.

## Four Golden Signals

### 1. Latency

**Definition**: Time to process requests

```python
from prometheus_client import Histogram

request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
```

**Query P95 latency**:
```promql
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
```

**SLO Example**: 95% of requests < 500ms

### 2. Traffic

**Definition**: Demand on system (requests/sec)

```python
from prometheus_client import Counter

requests_total = Counter(
    'http_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status_code']
)
```

**Query request rate**:
```promql
rate(http_requests_total[5m])
```

**SLO Example**: Handle 1000 req/sec

### 3. Errors

**Definition**: Rate of failed requests

```python
# Use same counter as traffic
# Filter by status_code=~"5.."
```

**Query error rate**:
```promql
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m])
```

**SLO Example**: < 0.1% error rate

### 4. Saturation

**Definition**: Resource utilization

```python
from prometheus_client import Gauge

cpu_usage_percent = Gauge('process_cpu_usage_percent', 'CPU usage')
memory_usage_bytes = Gauge('process_memory_usage_bytes', 'Memory usage')
db_connections_active = Gauge('db_connections_active', 'DB connections')
```

**Query saturation**:
```promql
# CPU saturation
process_cpu_usage_percent

# Memory saturation
process_memory_usage_bytes / process_memory_limit_bytes

# Database connection saturation
db_connections_active / db_connections_max
```

**SLO Example**: < 80% resource usage

## Complete Implementation

```python
# src/observability/golden_signals.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Latency
request_latency = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['service', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Traffic
request_count = Counter(
    'requests_total',
    'Total requests',
    ['service', 'endpoint', 'status']
)

# Errors (use request_count with status filter)

# Saturation
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage')
queue_size = Gauge('queue_size', 'Task queue size')


@app.middleware("http")
async def golden_signals_middleware(request, call_next):
    """Track all golden signals."""
    start_time = time.time()

    try:
        response = await call_next(request)

        # Latency
        request_latency.labels(
            service='finance_lending_api',
            endpoint=request.url.path
        ).observe(time.time() - start_time)

        # Traffic + Errors
        status = 'success' if response.status_code < 400 else 'error'
        request_count.labels(
            service='finance_lending_api',
            endpoint=request.url.path,
            status=status
        ).inc()

        return response

    except Exception:
        # Track errors
        request_count.labels(
            service='finance_lending_api',
            endpoint=request.url.path,
            status='error'
        ).inc()
        raise
```

## SLO Dashboard

```yaml
# Grafana dashboard panels
panels:
  - title: "Latency (P95)"
    query: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))
    threshold: 0.5  # 500ms
    alert: P95 > 500ms

  - title: "Traffic (req/s)"
    query: rate(requests_total[5m])
    threshold: 1000
    alert: Traffic > 1200 or < 10

  - title: "Error Rate"
    query: rate(requests_total{status="error"}[5m]) / rate(requests_total[5m])
    threshold: 0.001  # 0.1%
    alert: Error rate > 0.01

  - title: "Saturation (CPU)"
    query: cpu_usage_percent
    threshold: 80
    alert: CPU > 80%
```

## Alerting Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: golden_signals
    rules:
      # Latency alert
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        annotations:
          summary: "High latency detected"

      # Error rate alert
      - alert: HighErrorRate
        expr: rate(requests_total{status="error"}[5m]) / rate(requests_total[5m]) > 0.01
        for: 2m
        annotations:
          summary: "Error rate above 1%"

      # Saturation alert
      - alert: HighCPU
        expr: cpu_usage_percent > 80
        for: 5m
        annotations:
          summary: "CPU usage above 80%"
```

## Checklist

- [ ] Implement latency tracking (P50, P95, P99)
- [ ] Monitor traffic (requests/sec)
- [ ] Track error rates
- [ ] Monitor saturation (CPU, memory, connections)
- [ ] Define SLOs for each signal
- [ ] Create golden signals dashboard
- [ ] Set up alerts for SLO violations
- [ ] Test alert firing
- [ ] Document SLIs/SLOs
- [ ] Review SLOs quarterly

## Related Documents

- `docs/atomic/observability/metrics/prometheus-setup.md` — Prometheus configuration
- `docs/atomic/observability/metrics/service-metrics.md` — Service-level metrics
- `docs/atomic/observability/metrics/dashboards.md` — Dashboard creation
- `docs/atomic/observability/metrics/custom-metrics.md` — Custom metrics
