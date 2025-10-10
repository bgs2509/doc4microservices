# Kibana Dashboards

Create Kibana dashboards for log visualization, search, and analysis. Kibana provides the UI layer for Elasticsearch, enabling interactive exploration of logs, creation of visualizations, and building operational dashboards.

This document covers dashboard creation, saved searches, visualizations, and index patterns. Kibana transforms raw Elasticsearch data into actionable insights through interactive dashboards.

Without Kibana, teams query Elasticsearch via API. With Kibana, they explore logs visually, build dashboards in minutes, and share insights across the organization.

## Index Patterns

```bash
# Create index pattern via API
curl -X POST "http://kibana:5601/api/saved_objects/index-pattern" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" -d'
{
  "attributes": {
    "title": "logs-*",
    "timeFieldName": "@timestamp"
  }
}'
```

## Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Service Logs Overview",
    "panels": [
      {
        "type": "search",
        "title": "Recent Errors",
        "query": "level:error"
      },
      {
        "type": "visualization",
        "title": "Log Levels Over Time",
        "visType": "line"
      },
      {
        "type": "lens",
        "title": "Top Error Messages",
        "query": "level:error | stats count() by message"
      }
    ]
  }
}
```

## Saved Searches

```json
{
  "search": {
    "title": "Failed Loan Applications",
    "query": "service:finance_lending_api AND event:loan_creation_failed",
    "columns": ["@timestamp", "request_id", "user_id", "error.message"],
    "sort": [["@timestamp", "desc"]]
  }
}
```

## Best Practices

### DO: Use Filters

```
# CORRECT: Efficient filtering
service:"finance_lending_api" AND level:error AND @timestamp:[now-1h TO now]
```

### DO: Save Searches

```
# CORRECT: Reusable saved searches
Save commonly used queries for team sharing
```

## Checklist

- [ ] Create index patterns for log indices
- [ ] Build service overview dashboard
- [ ] Create error investigation dashboard
- [ ] Set up saved searches for common queries
- [ ] Configure time range defaults
- [ ] Set up dashboard auto-refresh
- [ ] Export dashboards as JSON for backup

## Related Documents

- `docs/atomic/observability/elk-stack/elasticsearch-setup.md` — Elasticsearch backend
- `docs/atomic/observability/logging/centralized-logging.md` — Logging patterns
