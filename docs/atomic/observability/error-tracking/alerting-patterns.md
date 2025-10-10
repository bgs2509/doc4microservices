# Alerting Patterns

Design effective alerting strategies for production errors and performance issues. Proper alerting ensures critical issues are noticed immediately while avoiding alert fatigue from noise.

This document covers alert rules, severity levels, routing, and escalation policies. Good alerting patterns mean the right people are notified about the right problems at the right time.

Without proper alerting, critical errors go unnoticed until users complain. With smart alerting, you catch and fix issues before users are impacted.

## Alert Severity Levels

```python
# src/core/alerting.py
from enum import Enum

class AlertSeverity(Enum):
    CRITICAL = "critical"  # Page immediately (database down)
    HIGH = "high"         # Notify on-call (error spike)
    MEDIUM = "medium"     # Notify team (degraded performance)
    LOW = "low"           # Log only (minor issues)

def determine_severity(error: Exception, context: dict) -> AlertSeverity:
    """Determine alert severity based on error and context."""
    # Critical: Infrastructure failures
    if isinstance(error, (DatabaseConnectionError, RedisConnectionError)):
        return AlertSeverity.CRITICAL
    
    # High: Business-critical failures
    if context.get("endpoint") in ["/api/payments", "/api/loans/approve"]:
        if isinstance(error, HTTPException) and error.status_code >= 500:
            return AlertSeverity.HIGH
    
    # Medium: Degraded service
    if context.get("response_time_ms", 0) > 5000:
        return AlertSeverity.MEDIUM
    
    return AlertSeverity.LOW
```

## Alert Rules

```yaml
# prometheus/alerts.yml
groups:
  - name: error_tracking
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 10
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High error rate detected"
          
      - alert: CriticalServiceDown
        expr: up{service="finance_lending_api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
```

## Notification Routing

```python
# Alert routing configuration
ALERT_ROUTES = {
    AlertSeverity.CRITICAL: [
        {"type": "pagerduty", "key": "critical-incidents"},
        {"type": "slack", "channel": "#incidents"},
        {"type": "email", "to": "oncall@example.com"}
    ],
    AlertSeverity.HIGH: [
        {"type": "slack", "channel": "#alerts"},
        {"type": "email", "to": "team@example.com"}
    ],
    AlertSeverity.MEDIUM: [
        {"type": "slack", "channel": "#monitoring"}
    ],
    AlertSeverity.LOW: [
        {"type": "log"}
    ]
}
```

## Alert Aggregation

```python
from datetime import datetime, timedelta
from collections import defaultdict

class AlertAggregator:
    def __init__(self, window_minutes: int = 5):
        self.window = timedelta(minutes=window_minutes)
        self.alerts = defaultdict(list)
    
    def add(self, alert_key: str, alert: dict):
        """Add alert to aggregation window."""
        now = datetime.now()
        self.alerts[alert_key].append((now, alert))
        
        # Clean old alerts
        cutoff = now - self.window
        self.alerts[alert_key] = [
            (ts, a) for ts, a in self.alerts[alert_key] 
            if ts > cutoff
        ]
    
    def should_alert(self, alert_key: str, threshold: int = 5) -> bool:
        """Check if aggregated alerts exceed threshold."""
        return len(self.alerts[alert_key]) >= threshold
```

## Best Practices

### DO: Alert on Symptoms

```python
# CORRECT: Alert on user-visible symptoms
if response_time_p95 > 1000:  # Users experiencing slowness
    send_alert(AlertSeverity.HIGH)
```

### DON'T: Alert on Every Error

```python
# INCORRECT: Alert fatigue
for error in all_errors:
    send_alert()  # ❌ Too noisy

# CORRECT: Alert on error rate
if error_rate > threshold:
    send_alert()  # ✅ Actionable
```

## Checklist

- [ ] Define alert severity levels
- [ ] Create routing rules by severity
- [ ] Set up notification channels (Slack, PagerDuty)
- [ ] Implement alert aggregation
- [ ] Configure escalation policies
- [ ] Test alert delivery
- [ ] Document on-call procedures

## Related Documents

- `docs/atomic/observability/error-tracking/sentry-integration.md` — Error capture
- `docs/atomic/observability/error-tracking/error-grouping.md` — Error grouping
- `docs/atomic/observability/metrics/prometheus-setup.md` — Metrics alerting
