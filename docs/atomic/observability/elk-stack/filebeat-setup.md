# Filebeat Setup

Configure Filebeat for lightweight log shipping from containers to Elasticsearch or Logstash. Filebeat provides reliable log collection with minimal resource usage, automatic container discovery, and guaranteed delivery through persistent queues.

This document covers Filebeat deployment with Docker, autodiscovery configuration, multiline log handling, and performance optimization. Filebeat is the standard way to ship logs from Docker containers to the ELK stack.

Filebeat solves the log collection problem: instead of each container writing directly to Elasticsearch (inefficient), Filebeat tails container logs, enriches them with metadata, and ships them reliably to your centralized logging system.

## Docker Deployment

```yaml
# docker-compose.filebeat.yml
version: '3.8'

services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.15.0
    container_name: filebeat
    user: root
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - filebeat_data:/usr/share/filebeat/data
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - LOGSTASH_HOSTS=logstash:5044
    command: ["filebeat", "-e", "-strict.perms=false"]
    depends_on:
      - elasticsearch

volumes:
  filebeat_data:
```

## Autodiscovery Configuration

```yaml
# filebeat.yml
filebeat.autodiscover:
  providers:
    - type: docker
      hints.enabled: true
      hints.default_config:
        type: container
        paths:
          - /var/lib/docker/containers/${data.container.id}/*.log

processors:
  - add_docker_metadata: ~
  - decode_json_fields:
      fields: ["message"]
      target: ""
      overwrite_keys: true
  - drop_event:
      when:
        or:
          - contains:
              container.name: "filebeat"
          - contains:
              message: "healthcheck"

output.elasticsearch:
  hosts: ["${ELASTICSEARCH_HOSTS:elasticsearch:9200}"]
  index: "logs-%{[service]:other}-%{+yyyy.MM.dd}"
  template.name: "logs"
  template.pattern: "logs-*"

# Alternative: Output to Logstash
# output.logstash:
#   hosts: ["${LOGSTASH_HOSTS:logstash:5044}"]
```

## Service-Specific Configuration

```yaml
# Service hints via Docker labels
services:
  finance_lending_api:
    labels:
      - "co.elastic.logs/module=python"
      - "co.elastic.logs/multiline.pattern=^\\d{4}-\\d{2}-\\d{2}"
      - "co.elastic.logs/multiline.negate=true"
      - "co.elastic.logs/multiline.match=after"
      - "co.elastic.logs/processors.1.decode_json_fields.fields=message"
      - "co.elastic.logs/processors.1.decode_json_fields.target=json"
```

## Multiline Configuration

```yaml
filebeat.inputs:
  - type: container
    paths:
      - /var/lib/docker/containers/*/*.log
    multiline.pattern: '^\d{4}-\d{2}-\d{2}|^\{'
    multiline.negate: true
    multiline.match: after
    multiline.timeout: 5s
    multiline.max_lines: 500
```

## Best Practices

### DO: Use Autodiscovery

```yaml
# CORRECT: Autodiscovery with hints
filebeat.autodiscover:
  providers:
    - type: docker
      hints.enabled: true
```

### DO: Add Metadata

```yaml
# CORRECT: Enrich logs with Docker metadata
processors:
  - add_docker_metadata:
      host: "unix:///var/run/docker.sock"
```

## Checklist

- [ ] Deploy Filebeat with Docker
- [ ] Configure autodiscovery for containers
- [ ] Set up multiline pattern for stack traces
- [ ] Add Docker metadata enrichment
- [ ] Configure output to Elasticsearch or Logstash
- [ ] Test log shipping from containers
- [ ] Monitor Filebeat metrics

## Related Documents

- `docs/atomic/observability/elk-stack/elasticsearch-setup.md` — Elasticsearch configuration
- `docs/atomic/observability/elk-stack/logstash-configuration.md` — Logstash pipeline
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging patterns