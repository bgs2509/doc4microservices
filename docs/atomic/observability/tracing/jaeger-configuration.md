# Jaeger Configuration

Configure Jaeger backend for production-grade distributed tracing storage, querying, and visualization. Jaeger provides the complete tracing infrastructure: collectors for receiving spans from applications, storage backends for persisting traces, query API for retrieving traces, and UI for visual trace analysis.

This document covers Jaeger architecture (collector, query, ingester), storage backends (Elasticsearch, Cassandra, in-memory), Docker deployment configurations, collector tuning for high throughput, retention policies, sampling strategies, and query optimization. Proper Jaeger configuration ensures reliable trace collection and fast query performance at scale.

Jaeger backend must handle thousands of spans per second, store traces for days/weeks, and enable sub-second queries across millions of traces. Without proper configuration, Jaeger becomes a bottleneck: dropped spans due to overloaded collectors, slow queries from inadequate storage, or excessive infrastructure costs from retention misconfiguration.

## Jaeger Architecture

```
┌─────────────┐
│ Application │
│  (OTLP)     │
└──────┬──────┘
       │ gRPC/HTTP
       ▼
┌──────────────┐     ┌──────────────┐
│   Collector  │────▶│   Storage    │
│              │     │ (ES/Cassandra)│
└──────────────┘     └──────┬───────┘
                             │
                             ▼
┌──────────────┐     ┌──────────────┐
│   Query API  │────▶│   Jaeger UI  │
│              │     │              │
└──────────────┘     └──────────────┘
```

## Docker Compose Setup

### All-in-One (Development)

```yaml
# docker-compose.jaeger.yml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:1.52
    container_name: jaeger
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC collector
      - "4318:4318"    # OTLP HTTP collector
    environment:
      - COLLECTOR_OTLP_ENABLED=true
      - SPAN_STORAGE_TYPE=memory
      - MEMORY_MAX_TRACES=10000
    restart: unless-stopped
```

### Production with Elasticsearch

```yaml
# docker-compose.jaeger-prod.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  jaeger-collector:
    image: jaegertracing/jaeger-collector:1.52
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - ES_NUM_SHARDS=3
      - ES_NUM_REPLICAS=1
      - COLLECTOR_OTLP_ENABLED=true
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_QUEUE_SIZE=10000
      - COLLECTOR_NUM_WORKERS=100
    ports:
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
      - "9411:9411"  # Zipkin compatible
    depends_on:
      - elasticsearch

  jaeger-query:
    image: jaegertracing/jaeger-query:1.52
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - QUERY_BASE_PATH=/jaeger
    ports:
      - "16686:16686"
    depends_on:
      - elasticsearch

  jaeger-ingester:
    image: jaegertracing/jaeger-ingester:1.52
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

## Storage Backends

### In-Memory (Development Only)

```yaml
# jaeger-all-in-one with in-memory storage
environment:
  - SPAN_STORAGE_TYPE=memory
  - MEMORY_MAX_TRACES=10000  # Keep last 10k traces

# Pros: Fast, simple, no external dependencies
# Cons: Data lost on restart, limited capacity
```

### Elasticsearch (Recommended for Production)

```yaml
# jaeger-collector with Elasticsearch
environment:
  - SPAN_STORAGE_TYPE=elasticsearch
  - ES_SERVER_URLS=http://elasticsearch:9200
  - ES_INDEX_PREFIX=jaeger
  - ES_NUM_SHARDS=3
  - ES_NUM_REPLICAS=1
  - ES_BULK_SIZE=5000000       # 5MB bulk size
  - ES_BULK_WORKERS=10
  - ES_BULK_FLUSH_INTERVAL=1s

# Pros: Production-ready, scalable, fast queries, JSON storage
# Cons: Requires ES cluster, higher resource usage
```

### Cassandra (Alternative for Production)

```yaml
# jaeger-collector with Cassandra
environment:
  - SPAN_STORAGE_TYPE=cassandra
  - CASSANDRA_SERVERS=cassandra:9042
  - CASSANDRA_KEYSPACE=jaeger_v1_dc1
  - CASSANDRA_LOCAL_DC=dc1
  - CASSANDRA_CONSISTENCY=LOCAL_QUORUM

# Pros: High write throughput, distributed, resilient
# Cons: Complex setup, slower queries than ES
```

## Collector Configuration

### High-Throughput Settings

```yaml
# jaeger-collector optimized for high load
environment:
  # Queue settings
  - COLLECTOR_QUEUE_SIZE=10000        # Span queue size
  - COLLECTOR_NUM_WORKERS=100          # Concurrent workers

  # Batch processing
  - ES_BULK_SIZE=5000000              # 5MB batches
  - ES_BULK_WORKERS=10                 # Parallel bulk indexing
  - ES_BULK_FLUSH_INTERVAL=1s          # Flush every second

  # Protocol support
  - COLLECTOR_OTLP_ENABLED=true
  - COLLECTOR_ZIPKIN_HOST_PORT=:9411

  # Health check
  - COLLECTOR_HEALTH_CHECK_HTTP_PORT=14269

resources:
  limits:
    memory: 2Gi
    cpu: 2
  requests:
    memory: 1Gi
    cpu: 1
```

### Sampling Configuration

```yaml
# jaeger-collector with adaptive sampling
environment:
  - SAMPLING_STRATEGIES_FILE=/etc/jaeger/sampling.json

# /etc/jaeger/sampling.json
{
  "service_strategies": [
    {
      "service": "finance_lending_api",
      "type": "probabilistic",
      "param": 0.1  # 10% sampling
    },
    {
      "service": "finance_lending_worker",
      "type": "probabilistic",
      "param": 0.05  # 5% sampling (lower priority)
    }
  ],
  "default_strategy": {
    "type": "probabilistic",
    "param": 0.001  # 0.1% for unknown services
  }
}
```

## Query Service Configuration

### Performance Tuning

```yaml
# jaeger-query optimized settings
environment:
  - SPAN_STORAGE_TYPE=elasticsearch
  - ES_SERVER_URLS=http://elasticsearch:9200
  - ES_MAX_SPAN_AGE=168h  # 7 days query window
  - QUERY_MAX_CLOCK_SKEW_ADJUSTMENT=1s
  - QUERY_BASE_PATH=/jaeger
  - QUERY_STATIC_FILES=/go/jaeger-ui/

  # Request limits
  - QUERY_TIMEOUT=30s
  - QUERY_MAX_RETRIES=3

resources:
  limits:
    memory: 1Gi
    cpu: 1
  requests:
    memory: 512Mi
    cpu: 500m
```

## UI Configuration

### Custom Branding

```yaml
# jaeger-query with custom UI config
volumes:
  - ./jaeger-ui-config.json:/etc/jaeger/jaeger-ui-config.json:ro

environment:
  - QUERY_UI_CONFIG=/etc/jaeger/jaeger-ui-config.json
```

```json
// jaeger-ui-config.json
{
  "monitor": {
    "menuEnabled": true
  },
  "dependencies": {
    "menuEnabled": true
  },
  "archiveEnabled": true,
  "tracking": {
    "gaID": "UA-000000-1"
  },
  "linkPatterns": [
    {
      "type": "logs",
      "key": "trace_id",
      "url": "https://kibana.example.com/app/kibana#/discover?_a=(query:(query_string:(query:'trace_id:#{trace_id}')))",
      "text": "View Logs in Kibana"
    },
    {
      "type": "metrics",
      "key": "service",
      "url": "https://grafana.example.com/d/service?var-service=#{service}",
      "text": "View Metrics in Grafana"
    }
  ]
}
```

## Retention Policies

### Elasticsearch Index Lifecycle

```bash
# Create ILM policy for Jaeger indices
curl -X PUT "http://elasticsearch:9200/_ilm/policy/jaeger-ilm-policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "3d",
        "actions": {
          "allocate": {
            "number_of_replicas": 0
          },
          "forcemerge": {
            "max_num_segments": 1
          }
        }
      },
      "delete": {
        "min_age": "7d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
'

# Apply policy to Jaeger indices
curl -X PUT "http://elasticsearch:9200/jaeger-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "lifecycle": {
      "name": "jaeger-ilm-policy"
    }
  }
}
'
```

### Manual Cleanup Script

```bash
#!/bin/bash
# cleanup_old_traces.sh

# Delete traces older than 7 days
CUTOFF_DATE=$(date -d '7 days ago' +%Y-%m-%d)

curl -X DELETE "http://elasticsearch:9200/jaeger-span-${CUTOFF_DATE}"
curl -X DELETE "http://elasticsearch:9200/jaeger-service-${CUTOFF_DATE}"

echo "Deleted indices older than ${CUTOFF_DATE}"
```

## Monitoring Jaeger

### Collector Metrics

```yaml
# Expose Prometheus metrics
environment:
  - METRICS_BACKEND=prometheus
  - METRICS_HTTP_ROUTE=/metrics

# Scrape with Prometheus
scrape_configs:
  - job_name: 'jaeger-collector'
    static_configs:
      - targets: ['jaeger-collector:14269']
```

### Key Metrics

```promql
# Spans received per second
rate(jaeger_collector_spans_received_total[5m])

# Spans dropped (queue full)
rate(jaeger_collector_spans_dropped_total[5m])

# Queue size
jaeger_collector_queue_length

# Batch processing latency
histogram_quantile(0.95, jaeger_collector_save_latency_bucket)

# Storage write errors
rate(jaeger_collector_spans_storage_errors_total[5m])
```

### Alerting Rules

```yaml
# prometheus/alerts/jaeger.yml
groups:
  - name: jaeger
    rules:
      - alert: JaegerCollectorDroppedSpans
        expr: rate(jaeger_collector_spans_dropped_total[5m]) > 100
        for: 5m
        annotations:
          summary: "Jaeger dropping spans - queue overloaded"

      - alert: JaegerCollectorHighLatency
        expr: histogram_quantile(0.95, rate(jaeger_collector_save_latency_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "Jaeger storage latency high - check Elasticsearch"

      - alert: JaegerCollectorStorageErrors
        expr: rate(jaeger_collector_spans_storage_errors_total[5m]) > 10
        for: 2m
        annotations:
          summary: "Jaeger storage errors - check Elasticsearch health"
```

## Best Practices

### DO: Use Elasticsearch for Production

```yaml
# CORRECT: Production setup with Elasticsearch
services:
  jaeger-collector:
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
      - ES_NUM_REPLICAS=1  # Replication for durability

  elasticsearch:
    deploy:
      replicas: 3  # ES cluster for availability


# INCORRECT: In-memory storage in production
services:
  jaeger:
    environment:
      - SPAN_STORAGE_TYPE=memory  # ❌ Data loss on restart
```

### DO: Configure Retention Policies

```yaml
# CORRECT: Automatic trace deletion after 7 days
environment:
  - ES_INDEX_DATE_SEPARATOR=-
  - ES_CREATE_INDEX_TEMPLATES=true

# ILM policy deletes old indices automatically


# INCORRECT: No retention policy
# ❌ Elasticsearch fills up, queries slow down, costs increase
```

### DO: Monitor Collector Health

```yaml
# CORRECT: Expose metrics and health checks
environment:
  - METRICS_BACKEND=prometheus
  - COLLECTOR_HEALTH_CHECK_HTTP_PORT=14269

healthcheck:
  test: ["CMD", "wget", "-q", "--spider", "http://localhost:14269/"]
  interval: 30s
  timeout: 10s
  retries: 3


# INCORRECT: No health checks
# ❌ Can't detect collector failures
```

### DON'T: Use Default Queue Sizes for Production

```yaml
# INCORRECT: Default queue size (too small)
environment:
  # Defaults: COLLECTOR_QUEUE_SIZE=2000
  # ❌ Spans dropped under load


# CORRECT: Tuned for high throughput
environment:
  - COLLECTOR_QUEUE_SIZE=10000      # ✅ Larger queue
  - COLLECTOR_NUM_WORKERS=100        # ✅ More workers
  - ES_BULK_SIZE=5000000             # ✅ Larger batches
```

## Kubernetes Deployment

### Helm Chart

```bash
# Add Jaeger Helm repository
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts

# Install Jaeger with Elasticsearch
helm install jaeger jaegertracing/jaeger \
  --set provisionDataStore.cassandra=false \
  --set provisionDataStore.elasticsearch=true \
  --set storage.type=elasticsearch \
  --set storage.elasticsearch.host=elasticsearch \
  --set storage.elasticsearch.port=9200 \
  --set collector.service.otlp.grpc.port=4317 \
  --set collector.autoscaling.enabled=true \
  --set collector.autoscaling.minReplicas=3 \
  --set collector.autoscaling.maxReplicas=10
```

### Custom Values

```yaml
# values.yaml
collector:
  resources:
    limits:
      memory: 2Gi
      cpu: 2
    requests:
      memory: 1Gi
      cpu: 1

  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80

  env:
    - name: COLLECTOR_QUEUE_SIZE
      value: "10000"
    - name: COLLECTOR_NUM_WORKERS
      value: "100"

query:
  resources:
    limits:
      memory: 1Gi
      cpu: 1

storage:
  type: elasticsearch
  elasticsearch:
    host: elasticsearch-master
    port: 9200
    scheme: http
    indexPrefix: jaeger
```

## Checklist

- [ ] Deploy Jaeger collector with OTLP support
- [ ] Configure Elasticsearch storage backend
- [ ] Set up retention policies (7-30 days)
- [ ] Tune collector queue and worker settings
- [ ] Configure sampling strategies per service
- [ ] Deploy Jaeger query service
- [ ] Expose Jaeger UI
- [ ] Add Kibana/Grafana links to UI
- [ ] Set up Prometheus scraping for Jaeger metrics
- [ ] Configure alerting for dropped spans and storage errors
- [ ] Test trace ingestion and query performance
- [ ] Document Jaeger URLs for team

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md` — OpenTelemetry SDK configuration
- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing patterns
- `docs/atomic/observability/tracing/trace-correlation.md` — Linking traces to logs/metrics
- `docs/atomic/observability/elk-stack/elasticsearch-setup.md` — Elasticsearch configuration
