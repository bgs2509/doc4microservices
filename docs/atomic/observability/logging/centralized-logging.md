# Centralized Logging

Aggregate logs from all microservices into a centralized logging system for unified search, analysis, alerting, and troubleshooting. Centralized logging enables querying logs across services, correlating distributed requests, monitoring system health, and debugging production issues without accessing individual service instances.

This document covers centralized logging architecture using Elasticsearch/CloudWatch/Loki, log shipping with Filebeat/Fluentd, log retention policies, access control, query patterns, dashboard creation, and alerting integration. Centralized logging is essential for production observability in distributed systems.

Centralized logging solves the distributed logs problem: in microservices architecture with dozens of services running hundreds of containers across multiple servers, logs are scattered everywhere. Without centralization, debugging requires SSH-ing into multiple servers, searching through local files, and manually correlating timestamps—an impossible task at scale.

## Architecture Patterns

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose.elk.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.15.0
    user: root
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

### Log Shipping with Filebeat

```yaml
# filebeat.yml
filebeat.autodiscover:
  providers:
    - type: docker
      hints.enabled: true

processors:
  - add_docker_metadata: ~
  - decode_json_fields:
      fields: ["message"]
      target: ""
      overwrite_keys: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "logs-%{[agent.version]}-%{+yyyy.MM.dd}"

setup.template.name: "logs"
setup.template.pattern: "logs-*"
```

## Application Configuration

### JSON Output to Stdout

```python
# CORRECT: JSON logs to stdout for Filebeat collection
import structlog

# Configure for production
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()  # JSON to stdout
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()
logger.info(
    "service_started",
    service="finance_lending_api",
    version="1.2.3"
)

# Filebeat reads from container stdout and ships to Elasticsearch
```

### Docker Labels for Routing

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    image: finance_lending_api:latest
    labels:
      - "logging.environment=production"
      - "logging.service=finance_lending_api"
      - "logging.index=production-api-logs"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Querying Logs

### Elasticsearch Query DSL

```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"service": "finance_lending_api"}},
        {"term": {"level": "error"}},
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "sort": [{"@timestamp": "desc"}],
  "size": 100
}
```

### Kibana Query Language (KQL)

```
# Errors in last hour
level:error AND @timestamp >= now-1h

# Specific request trace
request_id:"req-abc-123"

# Failed payments
event:payment_failed AND service:finance_lending_api

# Slow requests
duration_ms > 1000 AND @timestamp >= now-15m
```

### CloudWatch Logs Insights

```sql
fields @timestamp, service, event, message, request_id
| filter level = "error"
| filter service = "finance_lending_api"
| sort @timestamp desc
| limit 100
```

## Log Retention

### Elasticsearch ILM Policy

```json
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "forcemerge": {"max_num_segments": 1},
          "shrink": {"number_of_shards": 1}
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {"delete": {}}
      }
    }
  }
}
```

## Dashboards

### Kibana Dashboard Example

```json
{
  "title": "API Service Overview",
  "panels": [
    {
      "type": "metric",
      "title": "Total Requests (Last Hour)",
      "query": "service:finance_lending_api AND event:request_completed"
    },
    {
      "type": "line",
      "title": "Error Rate Over Time",
      "query": "service:finance_lending_api AND level:error"
    },
    {
      "type": "pie",
      "title": "Status Code Distribution",
      "query": "service:finance_lending_api",
      "field": "status_code"
    }
  ]
}
```

## Alerting

### Elasticsearch Watcher Alert

```json
{
  "trigger": {
    "schedule": {"interval": "5m"}
  },
  "input": {
    "search": {
      "request": {
        "indices": ["logs-*"],
        "body": {
          "query": {
            "bool": {
              "must": [
                {"term": {"level": "error"}},
                {"term": {"service": "finance_lending_api"}},
                {"range": {"@timestamp": {"gte": "now-5m"}}}
              ]
            }
          }
        }
      }
    }
  },
  "condition": {
    "compare": {"ctx.payload.hits.total": {"gt": 10}}
  },
  "actions": {
    "send_email": {
      "email": {
        "to": "ops@example.com",
        "subject": "High error rate detected",
        "body": "{{ctx.payload.hits.total}} errors in last 5 minutes"
      }
    }
  }
}
```

## Access Control

```python
# Elasticsearch API with authentication
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ["https://elasticsearch:9200"],
    basic_auth=("elastic", "password"),
    verify_certs=True,
    ca_certs="/path/to/ca.crt"
)

# Query with access control
results = es.search(
    index="logs-production-*",
    body={
        "query": {"term": {"service": "finance_lending_api"}}
    }
)
```

## Best Practices

### DO: Structure Logs for Search

```python
# CORRECT: Searchable structured logs
logger.info(
    "api_request",
    service="finance_lending_api",
    environment="production",
    request_id="req-abc-123",
    user_id="user-456",
    endpoint="/api/loans",
    method="POST",
    status_code=201,
    duration_ms=145
)

# Enables queries:
# - service:finance_lending_api
# - request_id:req-abc-123
# - duration_ms > 1000
```

### DO: Include Context Fields

```python
# CORRECT: Rich context for filtering
logger = structlog.get_logger().bind(
    service="finance_lending_api",
    environment="production",
    version="1.2.3",
    host=socket.gethostname()
)
```

### DON'T: Log to Files

```python
# INCORRECT: Local file logging
logging.basicConfig(filename='/var/log/app.log')  # ❌ Not centralized


# CORRECT: Stdout for container collection
structlog.configure(
    logger_factory=structlog.PrintLoggerFactory()  # Stdout
)
```

## Checklist

- [ ] Deploy centralized logging system (ELK/CloudWatch/Loki)
- [ ] Configure log shipping (Filebeat/Fluentd)
- [ ] Output JSON logs to stdout
- [ ] Add service metadata to all logs
- [ ] Configure log retention policies
- [ ] Create operational dashboards
- [ ] Set up error alerting
- [ ] Implement access control
- [ ] Test log ingestion from all services
- [ ] Document query patterns
- [ ] Train team on log searching
- [ ] Monitor log ingestion rates
- [ ] Test log retention deletion

## Related Documents

- `docs/atomic/observability/elk-stack/elasticsearch-setup.md` — Elasticsearch configuration
- `docs/atomic/observability/elk-stack/kibana-dashboards.md` — Kibana dashboard creation
- `docs/atomic/observability/logging/structured-logging.md` — Structured logging patterns
- `docs/atomic/observability/logging/log-correlation.md` — Log correlation across services
