# Sentry Integration

Integrate Sentry for real-time error tracking, alerting, and debugging across microservices. Sentry provides automatic error capture, stack trace deobfuscation, release tracking, and performance monitoring.

This document covers Sentry SDK setup for FastAPI/Aiogram, error capture configuration, performance tracing, and alert rules. Sentry transforms cryptic production errors into actionable bug reports with full context.

Without Sentry, errors are buried in logs. With Sentry, every error triggers alerts with stack traces, user context, and breadcrumbs showing what led to the failure.

## FastAPI Integration

```python
# src/core/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

def init_sentry(dsn: str, environment: str = "production"):
    """Initialize Sentry error tracking."""
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(level="ERROR", event_level="ERROR")
        ],
        traces_sample_rate=0.1,  # 10% performance monitoring
        profiles_sample_rate=0.1,  # 10% profiling
        attach_stacktrace=True,
        send_default_pii=False,  # GDPR compliance
        before_send=filter_sensitive_data
    )

def filter_sensitive_data(event, hint):
    """Filter sensitive data before sending to Sentry."""
    # Remove sensitive fields
    if "extra" in event:
        for key in ["password", "token", "api_key", "secret"]:
            event["extra"].pop(key, None)
    return event

# src/main.py
from src.core.sentry_config import init_sentry

init_sentry(
    dsn="https://key@sentry.io/project",
    environment="production"
)
```

## Manual Error Capture

```python
import sentry_sdk

try:
    result = await risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e, extra={
        "loan_id": loan_id,
        "user_id": user_id,
        "operation": "credit_check"
    })
    raise
```

## Performance Monitoring

```python
with sentry_sdk.start_transaction(op="task", name="process_loan"):
    with sentry_sdk.start_span(op="db", description="fetch_user"):
        user = await db.get_user(user_id)
    
    with sentry_sdk.start_span(op="http", description="credit_check"):
        score = await credit_api.check(user_id)
```

## Docker Configuration

```yaml
services:
  api:
    environment:
      - SENTRY_DSN=https://key@sentry.io/project
      - SENTRY_ENVIRONMENT=production
      - SENTRY_RELEASE=${GIT_SHA}
```

## Alert Rules

```python
# Sentry Alert Configuration
{
  "name": "High Error Rate",
  "conditions": [
    {"id": "event_frequency", "value": 100, "interval": "1h"}
  ],
  "actions": [
    {"id": "notify_email", "targetIdentifier": "ops@example.com"},
    {"id": "notify_slack", "channel": "#alerts"}
  ]
}
```

## Best Practices

### DO: Add Context

```python
# CORRECT: Rich context for debugging
sentry_sdk.set_context("loan", {
    "id": loan_id,
    "amount": amount,
    "status": status
})
```

### DON'T: Log Sensitive Data

```python
# INCORRECT: PII in Sentry
sentry_sdk.capture_message(f"User {email} failed")  # ❌

# CORRECT: No PII
sentry_sdk.capture_message(f"User {user_id} failed")  # ✅
```

## Checklist

- [ ] Install Sentry SDK
- [ ] Configure DSN and environment
- [ ] Add integrations (FastAPI, SQLAlchemy)
- [ ] Set up error filtering
- [ ] Configure performance monitoring
- [ ] Create alert rules
- [ ] Test error capture
- [ ] Set up release tracking

## Related Documents

- `docs/atomic/observability/error-tracking/error-grouping.md` — Error grouping strategies
- `docs/atomic/observability/error-tracking/alerting-patterns.md` — Alert configuration
