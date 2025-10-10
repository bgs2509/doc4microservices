# Grafana Dashboards

Design and implement Grafana dashboards for visualizing metrics, monitoring service health, tracking SLIs/SLOs, and enabling data-driven operational decisions. Grafana dashboards transform raw Prometheus metrics into actionable insights through charts, graphs, heatmaps, and alerts, providing real-time visibility into system behavior.

This document covers dashboard design principles, panel configuration, visualization types (time series, gauges, heatmaps, tables), dashboard variables for filtering, alerting integration, and dashboard-as-code with JSON/YAML provisioning. Effective dashboards enable teams to detect issues quickly, understand system behavior, and make informed decisions.

Dashboards answer critical questions: Is the system healthy right now? Are we meeting SLOs? Which service is causing the slowdown? What happened during the incident? Where are resource bottlenecks? Without well-designed dashboards, metrics data remains inaccessible—teams waste time writing PromQL queries instead of solving problems.

## Dashboard Design Principles

### RED Method (Requests, Errors, Duration)

```yaml
# Dashboard structure for HTTP services
panels:
  - title: "Request Rate"
    query: rate(http_requests_total[5m])

  - title: "Error Rate"
    query: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m])

  - title: "Request Duration (P95)"
    query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### USE Method (Utilization, Saturation, Errors)

```yaml
# Dashboard structure for resources
panels:
  - title: "CPU Utilization"
    query: process_cpu_usage_percent

  - title: "Memory Saturation"
    query: process_memory_usage_bytes / process_memory_limit_bytes

  - title: "Database Connection Saturation"
    query: db_connections_active / db_connections_max

  - title: "Error Rate"
    query: rate(errors_total[5m])
```

## Dashboard JSON Configuration

### Complete Service Dashboard

```json
{
  "dashboard": {
    "title": "Finance Lending API - Service Overview",
    "tags": ["finance", "lending", "api"],
    "timezone": "utc",
    "refresh": "30s",
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "panels": [
      {
        "id": 1,
        "type": "graph",
        "title": "Request Rate",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"finance_lending_api\"}[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yaxes": [
          {"format": "reqps", "label": "Requests/sec"}
        ]
      },
      {
        "id": 2,
        "type": "singlestat",
        "title": "Error Rate",
        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 8},
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"finance_lending_api\",status_code=~\"5..\"}[5m]) / rate(http_requests_total{service=\"finance_lending_api\"}[5m])"
          }
        ],
        "format": "percentunit",
        "thresholds": "0.001,0.01",
        "colors": ["green", "yellow", "red"]
      },
      {
        "id": 3,
        "type": "graph",
        "title": "Request Duration (Percentiles)",
        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{service=\"finance_lending_api\"}[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"finance_lending_api\"}[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{service=\"finance_lending_api\"}[5m]))",
            "legendFormat": "P99"
          }
        ],
        "yaxes": [
          {"format": "s", "label": "Duration"}
        ]
      },
      {
        "id": 4,
        "type": "heatmap",
        "title": "Request Duration Heatmap",
        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_bucket{service=\"finance_lending_api\"}[5m])",
            "format": "heatmap"
          }
        ],
        "yAxis": {"format": "s"}
      }
    ]
  }
}
```

## Panel Types

### Time Series Graph

```json
{
  "type": "timeseries",
  "title": "Request Rate Over Time",
  "targets": [
    {
      "expr": "rate(http_requests_total[5m])",
      "legendFormat": "{{service}}"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "color": {"mode": "palette-classic"},
      "custom": {
        "lineWidth": 2,
        "fillOpacity": 10
      }
    }
  }
}
```

### Gauge Panel

```json
{
  "type": "gauge",
  "title": "CPU Usage",
  "targets": [
    {
      "expr": "process_cpu_usage_percent"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 70, "color": "yellow"},
          {"value": 90, "color": "red"}
        ]
      }
    }
  }
}
```

### Stat Panel (Single Value)

```json
{
  "type": "stat",
  "title": "Active Requests",
  "targets": [
    {
      "expr": "http_requests_in_progress"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "short",
      "color": {"mode": "thresholds"},
      "thresholds": {
        "steps": [
          {"value": 0, "color": "green"},
          {"value": 100, "color": "yellow"},
          {"value": 500, "color": "red"}
        ]
      }
    }
  }
}
```

### Table Panel

```json
{
  "type": "table",
  "title": "Top Endpoints by Latency",
  "targets": [
    {
      "expr": "topk(10, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))",
      "format": "table",
      "instant": true
    }
  ],
  "fieldConfig": {
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "Value"},
        "properties": [
          {"id": "unit", "value": "s"},
          {"id": "displayName", "value": "P95 Latency"}
        ]
      }
    ]
  }
}
```

### Heatmap Panel

```json
{
  "type": "heatmap",
  "title": "Request Duration Distribution",
  "targets": [
    {
      "expr": "rate(http_request_duration_seconds_bucket[5m])",
      "format": "heatmap"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "hideFrom": {
          "tooltip": false,
          "viz": false,
          "legend": false
        }
      }
    }
  },
  "options": {
    "calculate": false,
    "yAxis": {
      "unit": "s",
      "decimals": 2
    },
    "color": {
      "scheme": "interpolateSpectral"
    }
  }
}
```

## Dashboard Variables

### Service Selector

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "query": "label_values(http_requests_total, service)",
        "multi": false,
        "includeAll": false,
        "current": {
          "text": "finance_lending_api",
          "value": "finance_lending_api"
        }
      }
    ]
  }
}
```

**Usage in queries**:
```promql
rate(http_requests_total{service="$service"}[5m])
```

### Multiple Selection

```json
{
  "name": "endpoint",
  "type": "query",
  "query": "label_values(http_requests_total{service=\"$service\"}, endpoint)",
  "multi": true,
  "includeAll": true,
  "allValue": ".*"
}
```

**Usage with regex**:
```promql
rate(http_requests_total{service="$service", endpoint=~"$endpoint"}[5m])
```

### Time Interval Variable

```json
{
  "name": "interval",
  "type": "interval",
  "query": "1m,5m,10m,30m,1h",
  "current": {
    "text": "5m",
    "value": "5m"
  }
}
```

**Usage**:
```promql
rate(http_requests_total[$interval])
```

## Dashboard as Code

### Provisioning Configuration

```yaml
# grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: 'Services'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

### Docker Compose Integration

```yaml
# docker-compose.metrics.yml
version: '3.8'

services:
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  grafana_data:
```

## Alerting Integration

### Dashboard Alert Rule

```json
{
  "alert": {
    "name": "High Error Rate",
    "conditions": [
      {
        "evaluator": {
          "type": "gt",
          "params": [0.01]
        },
        "query": {
          "model": {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m]) / rate(http_requests_total[5m])"
          }
        }
      }
    ],
    "executionErrorState": "alerting",
    "frequency": "1m",
    "for": "5m",
    "message": "Error rate above 1% for 5 minutes",
    "notifications": [
      {"uid": "slack-notifications"}
    ]
  }
}
```

## Best Practices

### DO: Organize Dashboards by Audience

```yaml
# CORRECT: Audience-specific dashboards
dashboards:
  - name: "Service Health (Operations)"
    panels: [uptime, error_rate, latency, throughput]

  - name: "Business Metrics (Management)"
    panels: [loans_created, conversion_rate, revenue]

  - name: "Infrastructure (SRE)"
    panels: [cpu, memory, disk, network]
```

### DO: Use Consistent Time Ranges

```json
// CORRECT: Consistent time range across related panels
{
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "refresh": "30s"
}
```

### DO: Add Panel Descriptions

```json
{
  "description": "P95 latency measures the 95th percentile response time. 95% of requests complete faster than this value. SLO: < 500ms",
  "title": "Request Latency (P95)"
}
```

### DON'T: Overcrowd Dashboards

```yaml
# INCORRECT: Too many panels (cognitive overload)
panels: [panel1, panel2, ..., panel50]  # ❌ 50 panels

# CORRECT: Focused dashboard (6-12 panels)
panels: [request_rate, error_rate, latency_p95, cpu, memory, active_requests]  # ✅ 6 key metrics
```

### DON'T: Use Default Panel Titles

```json
// INCORRECT: Generic title
{"title": "Panel 1"}  // ❌ What does this show?

// CORRECT: Descriptive title
{"title": "Request Rate (req/s) - Last 6h"}  // ✅ Clear and specific
```

## Common Dashboard Patterns

### Golden Signals Dashboard

```json
{
  "title": "Service Golden Signals",
  "panels": [
    {
      "title": "Latency (P50, P95, P99)",
      "targets": [
        {"expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))"},
        {"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"},
        {"expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))"}
      ]
    },
    {
      "title": "Traffic (req/s)",
      "targets": [
        {"expr": "rate(http_requests_total[5m])"}
      ]
    },
    {
      "title": "Errors (rate)",
      "targets": [
        {"expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])"}
      ]
    },
    {
      "title": "Saturation (CPU, Memory, Connections)",
      "targets": [
        {"expr": "process_cpu_usage_percent"},
        {"expr": "process_memory_usage_bytes / process_memory_limit_bytes * 100"},
        {"expr": "db_connections_active / db_connections_max * 100"}
      ]
    }
  ]
}
```

### SLO Tracking Dashboard

```json
{
  "title": "SLO Compliance",
  "panels": [
    {
      "type": "gauge",
      "title": "Availability SLO (99.9%)",
      "targets": [
        {
          "expr": "(1 - rate(http_requests_total{status_code=~\"5..\"}[30d]) / rate(http_requests_total[30d])) * 100"
        }
      ],
      "thresholds": [
        {"value": 99.9, "color": "green"},
        {"value": 99.5, "color": "yellow"},
        {"value": 0, "color": "red"}
      ]
    },
    {
      "type": "gauge",
      "title": "Latency SLO (P95 < 500ms)",
      "targets": [
        {
          "expr": "(1 - count(histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5) / count(histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))) * 100"
        }
      ],
      "thresholds": [
        {"value": 99, "color": "green"},
        {"value": 95, "color": "yellow"},
        {"value": 0, "color": "red"}
      ]
    }
  ]
}
```

### Business Metrics Dashboard

```json
{
  "title": "Loan Service - Business Metrics",
  "panels": [
    {
      "type": "stat",
      "title": "Loans Created (Today)",
      "targets": [
        {"expr": "increase(loans_created_total[1d])"}
      ]
    },
    {
      "type": "graph",
      "title": "Loan Approval Rate",
      "targets": [
        {
          "expr": "rate(loans_created_total{status=\"approved\"}[5m]) / rate(loans_created_total[5m])",
          "legendFormat": "Approval Rate"
        }
      ]
    },
    {
      "type": "stat",
      "title": "Average Loan Amount",
      "targets": [
        {
          "expr": "rate(loan_amount_dollars_sum[1h]) / rate(loan_amount_dollars_count[1h])"
        }
      ],
      "format": "currencyUSD"
    }
  ]
}
```

## Python Dashboard Generator

```python
# scripts/generate_dashboard.py
import json
from typing import List, Dict

def generate_service_dashboard(service_name: str) -> Dict:
    """Generate standard service dashboard JSON."""
    return {
        "dashboard": {
            "title": f"{service_name} - Service Overview",
            "tags": [service_name.split("_")[0], service_name.split("_")[1]],
            "refresh": "30s",
            "panels": [
                generate_request_rate_panel(service_name, 0, 0),
                generate_error_rate_panel(service_name, 12, 0),
                generate_latency_panel(service_name, 0, 8),
                generate_resource_panel(service_name, 12, 8),
            ]
        }
    }

def generate_request_rate_panel(service: str, x: int, y: int) -> Dict:
    """Generate request rate panel."""
    return {
        "id": 1,
        "type": "graph",
        "title": "Request Rate",
        "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
        "targets": [
            {
                "expr": f'rate(http_requests_total{{service="{service}"}}[5m])',
                "legendFormat": "{{method}} {{endpoint}}"
            }
        ]
    }

# Usage
dashboard = generate_service_dashboard("finance_lending_api")
with open("dashboard.json", "w") as f:
    json.dump(dashboard, f, indent=2)
```

## Checklist

- [ ] Create service overview dashboard
- [ ] Implement golden signals panels (latency, traffic, errors, saturation)
- [ ] Add SLO tracking panels
- [ ] Configure dashboard variables (service, endpoint, interval)
- [ ] Set appropriate time ranges and refresh intervals
- [ ] Add panel descriptions and documentation
- [ ] Configure alert rules for critical metrics
- [ ] Test dashboard with real data
- [ ] Set up dashboard provisioning (dashboard-as-code)
- [ ] Create audience-specific dashboards (ops, business, SRE)
- [ ] Document dashboard usage and interpretation
- [ ] Review and optimize panel performance

## Related Documents

- `docs/atomic/observability/metrics/prometheus-setup.md` — Prometheus configuration
- `docs/atomic/observability/metrics/golden-signals.md` — Golden signals implementation
- `docs/atomic/observability/metrics/service-metrics.md` — Service-level metrics
- `docs/atomic/observability/metrics/custom-metrics.md` — Business metrics
