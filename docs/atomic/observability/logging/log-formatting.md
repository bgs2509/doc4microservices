# Log Formatting Standards

Define consistent log formatting standards across all microservices to ensure logs are readable, parseable, and searchable in centralized logging systems. Log formatting standards establish field naming conventions, timestamp formats, message templates, and error representations that enable efficient debugging and monitoring.

This document covers log message structure, field naming conventions (snake_case), timestamp formatting (ISO 8601), log level standards, message templates for common events, multi-line log handling, and error formatting best practices. Consistent formatting enables reliable log parsing across all services regardless of programming language or framework.

Log formatting standards treat logs as a consistent data format across the entire microservices architecture. When all services emit logs with identical field names, timestamp formats, and message structures, centralized logging systems can aggregate, search, and analyze logs from any service using the same queries and dashboards.

## Log Message Structure

### Standard Format

```json
{
    "timestamp": "2025-01-15T10:30:45.123456Z",
    "level": "info",
    "service": "finance_lending_api",
    "environment": "production",
    "version": "1.2.3",
    "event": "user_created",
    "message": "User created successfully",
    "request_id": "req-abc-123",
    "user_id": "user-456",
    "duration_ms": 45,
    "context": {
        "additional": "nested data"
    }
}
```

### Required Fields

Every log entry must include:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | ISO 8601 timestamp with microseconds and UTC timezone | `2025-01-15T10:30:45.123456Z` |
| `level` | string | Log level (lowercase) | `debug`, `info`, `warning`, `error`, `critical` |
| `service` | string | Service name (`{context}_{domain}_{type}`) | `finance_lending_api` |
| `event` | string | Event name (snake_case) | `user_created`, `payment_processed` |
| `message` | string | Human-readable message | `User created successfully` |

### Optional Standard Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `request_id` | string | Request correlation ID | `req-abc-123` |
| `user_id` | string | User identifier | `user-456` |
| `environment` | string | Deployment environment | `production`, `staging`, `development` |
| `version` | string | Service version (semver) | `1.2.3` |
| `host` | string | Hostname or container ID | `api-pod-7f4d9b` |
| `duration_ms` | integer | Operation duration in milliseconds | `145` |
| `status_code` | integer | HTTP status code | `201`, `404`, `500` |
| `error_type` | string | Exception class name | `ValueError`, `HTTPException` |
| `error_message` | string | Exception message | `Invalid input: amount must be positive` |

## Field Naming Conventions

### snake_case for Field Names

```python
# CORRECT: snake_case field names
logger.info(
    "payment_processed",
    payment_id="pay-123",
    user_id="user-456",
    amount_usd=99.99,
    transaction_type="credit_card",
    merchant_name="Example Store"
)


# INCORRECT: Mixed naming conventions
logger.info(
    "PaymentProcessed",  # ❌ PascalCase event
    paymentID="pay-123",  # ❌ camelCase
    "user-id"="user-456",  # ❌ kebab-case
    AMOUNT=99.99  # ❌ SCREAMING_SNAKE_CASE
)
```

### Consistent Field Names Across Services

```python
# CORRECT: Same field names across all services

# API service
logger.info("request_started", request_id="req-123", user_id="user-456")

# Worker service
logger.info("task_started", request_id="req-123", user_id="user-456")

# Bot service
logger.info("command_received", request_id="req-123", user_id="user-456")

# Enables query: request_id="req-123" across all services


# INCORRECT: Different field names for same concept
# API service
logger.info("request", req_id="req-123", uid="user-456")  # ❌

# Worker service
logger.info("task", requestId="req-123", userId="user-456")  # ❌

# Cannot correlate across services
```

### Reserved Field Names

Do not use these field names for custom data:

- `timestamp` — Reserved for log timestamp
- `level` — Reserved for log level
- `message` — Reserved for human-readable message
- `event` — Reserved for event name
- `service` — Reserved for service name
- `logger` — Reserved for logger name
- `exc_info` — Reserved for exception information

## Timestamp Formatting

### ISO 8601 with UTC Timezone

```python
# CORRECT: ISO 8601 with microseconds and UTC
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()
# Output: "2025-01-15T10:30:45.123456+00:00"

# Preferred: Use 'Z' suffix for UTC
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
# Output: "2025-01-15T10:30:45.123456Z"


# INCORRECT: Local time without timezone
timestamp = datetime.now().isoformat()  # ❌ Ambiguous timezone
# Output: "2025-01-15T10:30:45.123456" (which timezone?)

# INCORRECT: Non-standard format
timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")  # ❌
# Output: "2025/01/15 10:30:45" (not ISO 8601)
```

### Structlog Configuration

```python
import structlog

structlog.configure(
    processors=[
        # ISO 8601 timestamp with 'Z' suffix
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer()
    ]
)
```

## Log Level Standards

### Level Naming

Always use lowercase log levels in JSON output:

```python
# CORRECT: Lowercase levels
{
    "level": "debug",
    "level": "info",
    "level": "warning",
    "level": "error",
    "level": "critical"
}


# INCORRECT: Uppercase or mixed case
{
    "level": "INFO",  # ❌
    "level": "Warning",  # ❌
    "level": "ERROR"  # ❌
}
```

### Level Guidelines

```python
import structlog

logger = structlog.get_logger()

# DEBUG: Detailed diagnostic information for developers
logger.debug(
    "cache_lookup",
    key="user:123",
    hit=True,
    ttl_seconds=3600
)

# INFO: Normal application events
logger.info(
    "user_login",
    user_id="user-123",
    ip_address="192.168.1.1"
)

# WARNING: Unexpected but handled situations
logger.warning(
    "rate_limit_approaching",
    user_id="user-123",
    requests=950,
    limit=1000,
    reset_time="2025-01-15T11:00:00Z"
)

# ERROR: Error conditions that affect operations
logger.error(
    "payment_failed",
    payment_id="pay-456",
    reason="insufficient_funds",
    amount_required=100.00,
    amount_available=50.00
)

# CRITICAL: Critical system failures requiring immediate action
logger.critical(
    "database_unavailable",
    database="postgres",
    host="db.local",
    retry_count=5,
    last_error="connection timeout"
)
```

## Message Templates

### Event-Driven Messages

```python
# CORRECT: Event name + context
logger.info(
    "loan_application_submitted",  # Event (snake_case)
    loan_id="loan-789",
    user_id="user-123",
    amount=10000,
    purpose="business"
)


# INCORRECT: Verbose sentences
logger.info(
    "A loan application has been submitted by user-123 for $10,000"  # ❌ Not searchable
)
```

### Consistent Naming Patterns

Use consistent verb tenses and patterns:

```python
# CORRECT: Consistent patterns

# Past tense for completed events
logger.info("user_created", user_id="user-123")
logger.info("payment_processed", payment_id="pay-456")
logger.info("email_sent", recipient="user@example.com")

# Present continuous for ongoing operations
logger.info("processing_payment", payment_id="pay-456")
logger.info("sending_email", recipient="user@example.com")

# Failures
logger.error("user_creation_failed", reason="duplicate_email")
logger.error("payment_processing_failed", reason="timeout")


# INCORRECT: Inconsistent patterns
logger.info("UserWasCreated")  # ❌ PascalCase, verbose
logger.info("payment-process")  # ❌ kebab-case, ambiguous tense
logger.error("Failed to send email")  # ❌ Sentence, not event name
```

## Multi-Line Logs

### Newlines in Messages

```python
# CORRECT: Escape newlines in JSON
logger.info(
    "stack_trace_captured",
    error_type="ValueError",
    stack_trace="Traceback (most recent call last):\n  File \"app.py\", line 42\n    raise ValueError()"
)

# JSON output (newlines escaped):
{
    "event": "stack_trace_captured",
    "stack_trace": "Traceback (most recent call last):\\n  File \\"app.py\\", line 42\\n    raise ValueError()"
}


# INCORRECT: Unescaped newlines break JSON parsing
logger.info(
    "stack_trace",
    trace="""
    Line 1
    Line 2
    Line 3
    """  # ❌ Breaks JSON parsing
)
```

### Nested Context

```python
# CORRECT: Use nested objects for complex data
logger.info(
    "http_request_completed",
    request={
        "method": "POST",
        "path": "/api/loans",
        "headers": {
            "user-agent": "Mozilla/5.0",
            "content-type": "application/json"
        }
    },
    response={
        "status_code": 201,
        "body_size": 1024
    }
)


# INCORRECT: Flatten complex data into strings
logger.info(
    "request",
    data="POST /api/loans, headers: {...}, status: 201"  # ❌ Unparseable
)
```

## Error Formatting

### Exception Information

```python
# CORRECT: Structured exception logging
import structlog

logger = structlog.get_logger()

try:
    result = await process_payment(payment_id="pay-123")
except ValueError as e:
    logger.error(
        "payment_validation_failed",
        payment_id="pay-123",
        error_type="ValueError",
        error_message=str(e),
        exc_info=True  # Include full traceback
    )
except httpx.HTTPError as e:
    logger.error(
        "payment_api_error",
        payment_id="pay-123",
        error_type="HTTPError",
        status_code=e.response.status_code if e.response else None,
        url=str(e.request.url),
        exc_info=True
    )


# INCORRECT: String concatenation
except Exception as e:
    logger.error(f"Error processing payment: {e}")  # ❌ Lost context
```

### Error Field Standards

```python
# Standard error fields:
{
    "event": "operation_failed",
    "error_type": "ValueError",  # Exception class name
    "error_message": "Amount must be positive",  # Exception message
    "error_code": "INVALID_AMOUNT",  # Application error code (optional)
    "stack_trace": "Traceback...",  # Full stack trace
    "recoverable": false  # Whether error is recoverable (optional)
}
```

## Numeric Values

### Units in Field Names

```python
# CORRECT: Include units in field names
logger.info(
    "api_request_completed",
    duration_ms=145,  # Milliseconds
    duration_seconds=0.145,  # Seconds
    body_size_bytes=2048,  # Bytes
    timeout_seconds=30  # Seconds
)


# INCORRECT: Ambiguous units
logger.info(
    "request_completed",
    duration=145,  # ❌ Milliseconds? Seconds?
    size=2048,  # ❌ Bytes? Kilobytes?
    timeout=30  # ❌ Seconds? Minutes?
)
```

### Number Formatting

```python
# CORRECT: Use native numeric types
logger.info(
    "payment_processed",
    amount=99.99,  # Float
    quantity=5,  # Integer
    tax_rate=0.08  # Decimal as float
)


# INCORRECT: Numbers as strings
logger.info(
    "payment_processed",
    amount="99.99",  # ❌ String, not number
    quantity="5"  # ❌ String, not integer
)
```

## Boolean Values

```python
# CORRECT: Use native boolean type
logger.info(
    "user_verified",
    user_id="user-123",
    email_verified=True,  # Boolean
    phone_verified=False,  # Boolean
    kyc_completed=True  # Boolean
)


# INCORRECT: Strings or numbers for booleans
logger.info(
    "user_status",
    verified="true",  # ❌ String
    active=1  # ❌ Integer
)
```

## Best Practices

### DO: Use Consistent Field Order

```python
# CORRECT: Consistent field order (high-priority first)
logger.info(
    "loan_processed",
    loan_id="loan-123",  # Identifiers first
    user_id="user-456",
    status="approved",  # Status/result
    amount=10000,  # Details
    purpose="business",
    duration_ms=145  # Metrics last
)
```

### DO: Include Context for Debugging

```python
# CORRECT: Rich context
logger.error(
    "loan_approval_failed",
    loan_id="loan-123",
    user_id="user-456",
    credit_score=620,
    required_score=650,
    income=45000,
    debt_ratio=0.45,
    reason="insufficient_credit_score"
)


# INCORRECT: Minimal context
logger.error("Loan approval failed")  # ❌ Cannot debug
```

### DON'T: Use Ambiguous Field Names

```python
# CORRECT: Specific field names
logger.info(
    "users_processed",
    total_users=1000,
    processed_users=950,
    failed_users=50
)


# INCORRECT: Ambiguous names
logger.info(
    "users",
    count=1000,  # ❌ Count of what?
    num=950,  # ❌ Number of what?
    errors=50  # ❌ Error count? Error IDs?
)
```

### DON'T: Include Redundant Data

```python
# CORRECT: Concise, non-redundant
logger.info(
    "payment_processed",
    payment_id="pay-123",
    amount=99.99,
    currency="USD"
)


# INCORRECT: Redundant data
logger.info(
    "payment_processed",
    payment_id="pay-123",
    payment_identifier="pay-123",  # ❌ Duplicate
    amount=99.99,
    amount_dollars=99.99,  # ❌ Duplicate
    currency="USD",
    currency_code="USD"  # ❌ Duplicate
)
```

## Checklist

- [ ] Use snake_case for all field names
- [ ] Include required fields (timestamp, level, service, event, message)
- [ ] Use ISO 8601 timestamps with UTC timezone
- [ ] Use lowercase log level names
- [ ] Use consistent event naming patterns (past tense for completed events)
- [ ] Escape newlines and special characters in JSON
- [ ] Include error_type and error_message for exceptions
- [ ] Use native types (numbers, booleans) not strings
- [ ] Include units in field names (duration_ms, size_bytes)
- [ ] Maintain consistent field order across logs
- [ ] Avoid ambiguous or redundant field names
- [ ] Include sufficient context for debugging
- [ ] Test log formatting in development

## Related Documents

- `docs/atomic/observability/logging/structured-logging.md` — Structured logging implementation with structlog
- `docs/atomic/observability/logging/log-correlation.md` — Correlating logs across services
- `docs/atomic/observability/logging/request-id-tracking.md` — Request ID propagation
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging infrastructure
