# Logstash Configuration

Configure Logstash pipelines for log processing, transformation, and enrichment before indexing into Elasticsearch. Logstash provides powerful data transformation capabilities through filters, enabling parsing of unstructured logs, field extraction, data enrichment, and conditional routing.

This document covers pipeline configuration, input plugins for various log sources, filter plugins for data transformation, output configuration for Elasticsearch, performance tuning, and monitoring. Proper Logstash configuration ensures logs are properly structured and enriched before storage.

Logstash acts as the ETL layer for logs: it receives raw logs from various sources, parses them into structured fields, enriches them with additional context, and routes them to appropriate Elasticsearch indices. Without Logstash, you'd need custom parsing logic in every application.

## Pipeline Configuration

### Basic Pipeline

```ruby
# logstash/pipeline/logstash.conf
input {
  # Receive logs from Filebeat
  beats {
    port => 5044
    ssl => false
  }

  # Direct TCP input
  tcp {
    port => 5000
    codec => json_lines
  }

  # HTTP input endpoint
  http {
    port => 8080
    codec => json
  }
}

filter {
  # Parse JSON logs
  if [message] =~ /^\{/ {
    json {
      source => "message"
      target => "parsed"
    }

    mutate {
      remove_field => ["message"]
    }
  }

  # Add timestamp if missing
  if ![timestamp] {
    ruby {
      code => "event.set('timestamp', Time.now.utc.iso8601)"
    }
  }

  # Parse log level
  if [level] {
    mutate {
      lowercase => ["level"]
    }
  }
}

output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{[service]}-%{+YYYY.MM.dd}"
    template_name => "logs-template"
    template => "/usr/share/logstash/templates/logs-template.json"
    template_overwrite => true
  }

  # Debug output
  if [@metadata][debug] {
    stdout {
      codec => rubydebug
    }
  }
}
```

## Docker Deployment

```yaml
# docker-compose.logstash.yml
version: '3.8'

services:
  logstash:
    image: docker.elastic.co/logstash/logstash:8.15.0
    container_name: logstash
    ports:
      - "5044:5044"  # Beats input
      - "5000:5000"  # TCP input
      - "8080:8080"  # HTTP input
      - "9600:9600"  # Monitoring API
    environment:
      - "LS_JAVA_OPTS=-Xms2g -Xmx2g"
      - PIPELINE_WORKERS=4
      - PIPELINE_BATCH_SIZE=125
      - PIPELINE_BATCH_DELAY=50
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logstash/templates:/usr/share/logstash/templates:ro
      - logstash_data:/usr/share/logstash/data
    depends_on:
      - elasticsearch

volumes:
  logstash_data:
```

## Advanced Filters

### Log Parsing

```ruby
filter {
  # Parse application logs
  if [service] == "finance_lending_api" {
    grok {
      match => {
        "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:log_message}"
      }
    }

    # Extract request ID from message
    if [log_message] =~ /request_id/ {
      grok {
        match => {
          "log_message" => "request_id=%{UUID:request_id}"
        }
      }
    }
  }

  # Parse nginx access logs
  if [service] == "nginx" {
    grok {
      match => {
        "message" => '%{IPORHOST:remote_ip} - %{DATA:user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{DATA:url} HTTP/%{NUMBER:http_version}" %{NUMBER:status_code} %{NUMBER:bytes_sent} "%{DATA:referrer}" "%{DATA:user_agent}"'
      }
    }

    mutate {
      convert => {
        "status_code" => "integer"
        "bytes_sent" => "integer"
      }
    }
  }
}
```

### Data Enrichment

```ruby
filter {
  # GeoIP enrichment
  if [remote_ip] {
    geoip {
      source => "remote_ip"
      target => "geoip"
      fields => ["country_name", "city_name", "location"]
    }
  }

  # User enrichment from database
  if [user_id] {
    jdbc_streaming {
      jdbc_driver_library => "/usr/share/logstash/mysql-connector-java.jar"
      jdbc_driver_class => "com.mysql.cj.jdbc.Driver"
      jdbc_connection_string => "jdbc:mysql://mysql:3306/users"
      jdbc_user => "logstash"
      jdbc_password => "password"
      statement => "SELECT name, email, tier FROM users WHERE id = :userid"
      parameters => { "userid" => "user_id" }
      target => "user_info"
    }
  }

  # Add environment metadata
  mutate {
    add_field => {
      "environment" => "${ENVIRONMENT:production}"
      "datacenter" => "${DATACENTER:us-east-1}"
      "cluster" => "${CLUSTER:main}"
    }
  }
}
```

## Conditional Routing

```ruby
output {
  # Route by log level
  if [level] == "error" or [level] == "fatal" {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "errors-%{+YYYY.MM.dd}"
    }

    # Send critical errors to alerting
    if [level] == "fatal" {
      http {
        url => "https://alerts.example.com/webhook"
        http_method => "post"
        format => "json"
      }
    }
  }

  # Route by service
  else if [service] {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "logs-%{[service]}-%{+YYYY.MM.dd}"
    }
  }

  # Default routing
  else {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "logs-other-%{+YYYY.MM.dd}"
    }
  }

  # Archive to S3
  if [archive] == true {
    s3 {
      region => "us-east-1"
      bucket => "logs-archive"
      prefix => "logstash/%{+YYYY/MM/dd}/"
      codec => "json_lines"
    }
  }
}
```

## Performance Tuning

### Pipeline Settings

```yaml
# logstash/config/pipelines.yml
- pipeline.id: main
  pipeline.workers: 8
  pipeline.batch.size: 250
  pipeline.batch.delay: 50
  queue.type: persisted
  queue.max_bytes: 4gb
  queue.checkpoint.writes: 1024

- pipeline.id: metrics
  pipeline.workers: 2
  pipeline.batch.size: 100
  config.string: |
    input { pipeline { address => metrics } }
    output { elasticsearch { index => "metrics-%{+YYYY.MM.dd}" } }
```

### JVM Configuration

```bash
# logstash/config/jvm.options
-Xms4g
-Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+ParallelRefProcEnabled
-XX:+UnlockExperimentalVMOptions
-XX:+DisableExplicitGC
-Djava.awt.headless=true
```

## Monitoring

### Metrics API

```bash
# Check pipeline stats
curl -X GET "http://localhost:9600/_node/stats/pipelines?pretty"

# Check JVM stats
curl -X GET "http://localhost:9600/_node/stats/jvm?pretty"

# Check hot threads
curl -X GET "http://localhost:9600/_node/hot_threads?pretty"
```

### Prometheus Metrics

```yaml
# Enable monitoring
docker run -d \
  -p 9600:9600 \
  docker.elastic.co/logstash/logstash:8.15.0 \
  -e "xpack.monitoring.enabled=true" \
  -e "xpack.monitoring.elasticsearch.hosts=http://elasticsearch:9200"
```

## Best Practices

### DO: Use Persistent Queues

```ruby
# CORRECT: Persistent queue for reliability
queue.type: persisted
queue.max_bytes: 1gb

# INCORRECT: Memory queue (data loss on crash)
queue.type: memory  # ❌ Not reliable
```

### DON'T: Complex Ruby Code

```ruby
# INCORRECT: Complex processing in Ruby filter
ruby {
  code => "
    # ❌ 50 lines of complex logic
    # Move to dedicated service
  "
}

# CORRECT: Simple field manipulation
ruby {
  code => "event.set('timestamp', Time.now.utc.iso8601)"  # ✅ Simple
}
```

## Checklist

- [ ] Configure Logstash pipeline with inputs/filters/outputs
- [ ] Set up JSON parsing for structured logs
- [ ] Configure Grok patterns for unstructured logs
- [ ] Add data enrichment filters if needed
- [ ] Configure conditional routing by service/level
- [ ] Tune pipeline workers and batch size
- [ ] Enable persistent queues for reliability
- [ ] Set appropriate JVM heap size
- [ ] Configure monitoring endpoint
- [ ] Test pipeline with sample logs
- [ ] Verify logs are properly indexed in Elasticsearch
- [ ] Document custom Grok patterns

## Related Documents

- `docs/atomic/observability/elk-stack/elasticsearch-setup.md` — Elasticsearch configuration
- `docs/atomic/observability/elk-stack/filebeat-setup.md` — Log shipping setup
- `docs/atomic/observability/logging/log-formatting.md` — Log format standards