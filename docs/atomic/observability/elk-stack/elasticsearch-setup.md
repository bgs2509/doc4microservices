# Elasticsearch Setup

Deploy and configure Elasticsearch for centralized log storage, full-text search, and analytics across microservices. Elasticsearch provides distributed, scalable storage for structured logs, traces, and metrics, enabling millisecond-latency queries across terabytes of operational data.

This document covers Elasticsearch cluster deployment with Docker, index management and templates, retention policies with ILM (Index Lifecycle Management), performance tuning for high-volume log ingestion, security configuration, and backup strategies. Proper Elasticsearch setup ensures reliable log storage and fast search capabilities at scale.

Elasticsearch transforms raw logs into searchable intelligence: instead of grepping through files on dozens of servers, you query all logs instantly with Kibana. Complex questions like "show all errors for user-123 across all services in the last hour" return results in milliseconds, not minutes.

## Docker Deployment

### Single Node (Development)

```yaml
# docker-compose.elasticsearch.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=false
      - xpack.security.http.ssl.enabled=false
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  elasticsearch_data:
```

### Production Cluster

```yaml
# docker-compose.elasticsearch-cluster.yml
version: '3.8'

services:
  elasticsearch-master:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch-master
    environment:
      - node.name=elasticsearch-master
      - cluster.name=es-cluster
      - discovery.seed_hosts=elasticsearch-master,elasticsearch-data1,elasticsearch-data2
      - cluster.initial_master_nodes=elasticsearch-master
      - node.roles=master
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=true
      - xpack.security.transport.ssl.enabled=true
      - xpack.security.transport.ssl.verification_mode=certificate
      - xpack.security.transport.ssl.keystore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
      - xpack.security.transport.ssl.truststore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_master_data:/usr/share/elasticsearch/data
      - ./elastic-certificates.p12:/usr/share/elasticsearch/config/elastic-certificates.p12:ro
    networks:
      - elastic

  elasticsearch-data1:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch-data1
    environment:
      - node.name=elasticsearch-data1
      - cluster.name=es-cluster
      - discovery.seed_hosts=elasticsearch-master,elasticsearch-data1,elasticsearch-data2
      - cluster.initial_master_nodes=elasticsearch-master
      - node.roles=data,ingest
      - "ES_JAVA_OPTS=-Xms4g -Xmx4g"
      - xpack.security.enabled=true
      - xpack.security.transport.ssl.enabled=true
      - xpack.security.transport.ssl.verification_mode=certificate
      - xpack.security.transport.ssl.keystore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
      - xpack.security.transport.ssl.truststore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
    volumes:
      - elasticsearch_data1:/usr/share/elasticsearch/data
      - ./elastic-certificates.p12:/usr/share/elasticsearch/config/elastic-certificates.p12:ro
    networks:
      - elastic

  elasticsearch-data2:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    container_name: elasticsearch-data2
    environment:
      - node.name=elasticsearch-data2
      - cluster.name=es-cluster
      - discovery.seed_hosts=elasticsearch-master,elasticsearch-data1,elasticsearch-data2
      - cluster.initial_master_nodes=elasticsearch-master
      - node.roles=data,ingest
      - "ES_JAVA_OPTS=-Xms4g -Xmx4g"
      - xpack.security.enabled=true
      - xpack.security.transport.ssl.enabled=true
      - xpack.security.transport.ssl.verification_mode=certificate
      - xpack.security.transport.ssl.keystore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
      - xpack.security.transport.ssl.truststore.path=/usr/share/elasticsearch/config/elastic-certificates.p12
    volumes:
      - elasticsearch_data2:/usr/share/elasticsearch/data
      - ./elastic-certificates.p12:/usr/share/elasticsearch/config/elastic-certificates.p12:ro
    networks:
      - elastic

networks:
  elastic:

volumes:
  elasticsearch_master_data:
  elasticsearch_data1:
  elasticsearch_data2:
```

## Index Templates

### Log Index Template

```bash
# Create index template for application logs
curl -X PUT "http://localhost:9200/_index_template/logs-template" \
  -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logs-*"],
  "priority": 100,
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.refresh_interval": "5s",
      "index.codec": "best_compression"
    },
    "mappings": {
      "properties": {
        "@timestamp": {"type": "date"},
        "service": {"type": "keyword"},
        "level": {"type": "keyword"},
        "event": {"type": "keyword"},
        "message": {"type": "text"},
        "request_id": {"type": "keyword"},
        "trace_id": {"type": "keyword"},
        "span_id": {"type": "keyword"},
        "user_id": {"type": "keyword"},
        "loan_id": {"type": "keyword"},
        "error": {
          "properties": {
            "type": {"type": "keyword"},
            "message": {"type": "text"},
            "stack_trace": {"type": "text"}
          }
        },
        "duration_ms": {"type": "long"},
        "status_code": {"type": "integer"}
      }
    }
  }
}
'
```

### Trace Index Template

```bash
# Create index template for Jaeger traces
curl -X PUT "http://localhost:9200/_index_template/jaeger-span-template" \
  -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["jaeger-span-*"],
  "priority": 100,
  "template": {
    "settings": {
      "number_of_shards": 5,
      "number_of_replicas": 1,
      "index.codec": "best_compression",
      "index.mapping.nested_objects.limit": 50000
    },
    "mappings": {
      "properties": {
        "traceID": {"type": "keyword"},
        "spanID": {"type": "keyword"},
        "operationName": {"type": "keyword"},
        "serviceName": {"type": "keyword"},
        "startTime": {"type": "long"},
        "duration": {"type": "long"},
        "tags": {"type": "nested"},
        "logs": {"type": "nested"},
        "references": {"type": "nested"}
      }
    }
  }
}
'
```

## Index Lifecycle Management (ILM)

### Create ILM Policy

```bash
# Create ILM policy for log retention
curl -X PUT "http://localhost:9200/_ilm/policy/logs-policy" \
  -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "1d",
            "max_size": "50gb",
            "max_docs": 100000000
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "3d",
        "actions": {
          "set_priority": {
            "priority": 50
          },
          "allocate": {
            "number_of_replicas": 0
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "cold": {
        "min_age": "7d",
        "actions": {
          "set_priority": {
            "priority": 0
          },
          "searchable_snapshot": {
            "snapshot_repository": "backup-repo"
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
'
```

### Apply ILM to Indices

```bash
# Apply ILM policy to log indices
curl -X PUT "http://localhost:9200/logs-*/_settings" \
  -H 'Content-Type: application/json' -d'
{
  "index": {
    "lifecycle": {
      "name": "logs-policy",
      "rollover_alias": "logs"
    }
  }
}
'
```

## Performance Tuning

### JVM Heap Settings

```yaml
# docker-compose.yml - Production heap settings
environment:
  - "ES_JAVA_OPTS=-Xms8g -Xmx8g"  # 50% of available RAM

# Best practices:
# - Set Xms = Xmx (prevent heap resizing)
# - Use 50% of RAM for heap (max 32GB)
# - Leave 50% for filesystem cache
```

### Indexing Performance

```bash
# Bulk indexing optimization
curl -X PUT "http://localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' -d'
{
  "transient": {
    "indices.memory.index_buffer_size": "30%",
    "indices.memory.min_index_buffer_size": "96mb",
    "indices.recovery.max_bytes_per_sec": "100mb",
    "cluster.routing.allocation.node_concurrent_recoveries": 5
  }
}
'

# Disable refresh during bulk load
curl -X PUT "http://localhost:9200/logs-*/_settings" \
  -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "-1"
  }
}
'

# Re-enable after bulk load
curl -X PUT "http://localhost:9200/logs-*/_settings" \
  -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "5s"
  }
}
'
```

### Query Performance

```bash
# Query cache settings
curl -X PUT "http://localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' -d'
{
  "transient": {
    "indices.queries.cache.size": "20%",
    "indices.requests.cache.size": "5%"
  }
}
'

# Force merge old indices for better query performance
curl -X POST "http://localhost:9200/logs-2024.01.*/_forcemerge?max_num_segments=1"
```

## Security Configuration

### Enable Security

```bash
# Generate certificates
docker exec -it elasticsearch-master \
  /usr/share/elasticsearch/bin/elasticsearch-certutil cert \
  --silent --pem --in /tmp/instances.yml --out /tmp/certs.zip

# Set built-in user passwords
docker exec -it elasticsearch-master \
  /usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive
```

### Create Users and Roles

```bash
# Create read-only role for developers
curl -X POST "http://localhost:9200/_security/role/logs_reader" \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["logs-*"],
      "privileges": ["read", "view_index_metadata"]
    }
  ]
}
'

# Create user with logs_reader role
curl -X POST "http://localhost:9200/_security/user/developer" \
  -u elastic:password \
  -H 'Content-Type: application/json' -d'
{
  "password": "dev_password",
  "roles": ["logs_reader"],
  "full_name": "Developer User"
}
'
```

## Python Client

### Connection Setup

```python
# src/core/elasticsearch_client.py
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import structlog

logger = structlog.get_logger()

class ElasticsearchClient:
    """Async Elasticsearch client for log ingestion."""

    def __init__(self, hosts: list[str], username: str = None, password: str = None):
        """Initialize Elasticsearch client."""
        self.client = AsyncElasticsearch(
            hosts=hosts,
            basic_auth=(username, password) if username else None,
            verify_certs=True,
            ssl_show_warn=False,
            retry_on_timeout=True,
            max_retries=3,
            timeout=30
        )

    async def index_log(self, log_entry: dict) -> None:
        """Index single log entry."""
        try:
            await self.client.index(
                index=f"logs-{log_entry['@timestamp'][:10]}",
                document=log_entry
            )
        except Exception as e:
            logger.error("Failed to index log", error=str(e))

    async def bulk_index_logs(self, logs: list[dict]) -> None:
        """Bulk index multiple log entries."""
        actions = [
            {
                "_index": f"logs-{log['@timestamp'][:10]}",
                "_source": log
            }
            for log in logs
        ]

        try:
            await async_bulk(self.client, actions)
        except Exception as e:
            logger.error("Bulk indexing failed", error=str(e))

    async def search_logs(self, query: dict, size: int = 100) -> list[dict]:
        """Search logs with query."""
        try:
            response = await self.client.search(
                index="logs-*",
                body={"query": query, "size": size},
                sort=[{"@timestamp": "desc"}]
            )
            return [hit["_source"] for hit in response["hits"]["hits"]]
        except Exception as e:
            logger.error("Search failed", error=str(e))
            return []

    async def close(self):
        """Close Elasticsearch connection."""
        await self.client.close()
```

### Usage Example

```python
# src/services/log_service.py
from src.core.elasticsearch_client import ElasticsearchClient

# Initialize client
es_client = ElasticsearchClient(
    hosts=["http://localhost:9200"],
    username="elastic",
    password="password"
)

# Index log
await es_client.index_log({
    "@timestamp": "2024-01-10T10:30:45.123Z",
    "service": "finance_lending_api",
    "level": "error",
    "event": "loan_creation_failed",
    "request_id": "req-abc-123",
    "trace_id": "trace-xyz-789",
    "error": {
        "type": "ValidationError",
        "message": "Invalid loan amount"
    }
})

# Search logs
results = await es_client.search_logs({
    "bool": {
        "must": [
            {"term": {"service": "finance_lending_api"}},
            {"term": {"level": "error"}},
            {"range": {"@timestamp": {"gte": "now-1h"}}}
        ]
    }
})

# Cleanup
await es_client.close()
```

## Monitoring

### Cluster Health

```bash
# Check cluster health
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# Check node stats
curl -X GET "http://localhost:9200/_nodes/stats?pretty"

# Check index stats
curl -X GET "http://localhost:9200/logs-*/_stats?pretty"
```

### Prometheus Metrics

```yaml
# docker-compose.yml - Add Elasticsearch exporter
elasticsearch-exporter:
  image: quay.io/prometheuscommunity/elasticsearch-exporter:v1.6.0
  command:
    - '--es.uri=http://elasticsearch:9200'
    - '--es.all'
    - '--es.indices'
  ports:
    - "9114:9114"
  depends_on:
    - elasticsearch
```

## Backup and Recovery

### Snapshot Repository

```bash
# Create snapshot repository
curl -X PUT "http://localhost:9200/_snapshot/backup-repo" \
  -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/backups",
    "compress": true
  }
}
'

# Create snapshot
curl -X PUT "http://localhost:9200/_snapshot/backup-repo/snapshot-$(date +%Y%m%d)"

# Restore snapshot
curl -X POST "http://localhost:9200/_snapshot/backup-repo/snapshot-20240110/_restore" \
  -H 'Content-Type: application/json' -d'
{
  "indices": "logs-*",
  "ignore_unavailable": true,
  "include_global_state": false
}
'
```

## Best Practices

### DO: Use Index Templates

```bash
# CORRECT: Define mappings via templates
curl -X PUT "http://localhost:9200/_index_template/logs-template"
# Ensures consistent mappings across all log indices


# INCORRECT: Let Elasticsearch auto-detect mappings
# ❌ Can lead to mapping conflicts and inefficient storage
```

### DO: Configure Retention

```yaml
# CORRECT: ILM policy with clear retention
phases:
  delete:
    min_age: "30d"  # Delete after 30 days


# INCORRECT: No retention policy
# ❌ Disk fills up, cluster fails
```

### DON'T: Use Too Many Shards

```json
// INCORRECT: Over-sharding
{
  "settings": {
    "number_of_shards": 20  // ❌ Too many for small index
  }
}

// CORRECT: Right-size shards
{
  "settings": {
    "number_of_shards": 3  // ✅ 10-50GB per shard target
  }
}
```

## Checklist

- [ ] Deploy Elasticsearch with Docker
- [ ] Configure cluster settings (single-node or cluster)
- [ ] Create index templates for logs and traces
- [ ] Configure ILM policies for retention
- [ ] Set appropriate JVM heap size (50% of RAM)
- [ ] Enable security and create users/roles
- [ ] Configure snapshot repository for backups
- [ ] Set up Elasticsearch exporter for Prometheus
- [ ] Test log indexing and searching
- [ ] Verify cluster health status is green
- [ ] Document Elasticsearch endpoints and credentials
- [ ] Schedule regular snapshots

## Related Documents

- `docs/atomic/observability/elk-stack/logstash-configuration.md` — Logstash pipeline setup
- `docs/atomic/observability/elk-stack/filebeat-setup.md` — Log shipping configuration
- `docs/atomic/observability/elk-stack/kibana-dashboards.md` — Visualization setup
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging patterns