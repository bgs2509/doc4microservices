# Structured Logging Patterns

Implement structured logging with JSON format to enable efficient log parsing, filtering, searching, and analysis in centralized logging systems. Structured logging emits machine-readable log entries with consistent field names and data types instead of unstructured plain text messages.

This document covers structured logging implementation with Python's structlog library, JSON formatting, log enrichment with context data (request IDs, user IDs, service names), log levels configuration, and integration with centralized logging systems like Elasticsearch and CloudWatch. Structured logs enable powerful query capabilities and automated alerting on specific conditions.

Structured logging treats logs as data, not text. Each log entry is a structured JSON object with well-defined fields for timestamp, level, message, and custom context. This approach enables querying logs by specific fields, aggregating metrics from logs, and correlating logs across distributed services for end-to-end request tracing.

## Why Structured Logging

### Benefits

**Queryability**: Filter logs by exact field values instead of regex patterns
```python
# Query: user_id="user-123" AND status_code=500
# Instead of parsing: "User user-123 received 500 error"
```

**Aggregation**: Calculate metrics directly from logs
```python
# Count errors by endpoint: GROUP BY endpoint WHERE level="error"
# Instead of parsing text patterns
```

**Correlation**: Link logs across services using request_id
```python
# Trace request flow: request_id="req-abc" across API → Worker → Bot
```

**Machine Parsing**: Automated analysis without regex fragility
```python
# Reliable: log["duration_ms"] > 1000
# vs. Fragile: re.search(r'took (\d+)ms', message)
```

## Structlog Setup

### Installation

```bash
# Install structlog
pip install structlog==24.1.0

# Install optional dependencies
pip install python-json-logger==2.0.7
```

### Basic Configuration

```python
# src/core/logging_config.py
import structlog
from typing import Any

def configure_structured_logging() -> None:
    """Configure structlog for JSON output."""
    structlog.configure(
        processors=[
            # Add log level to event dict
            structlog.stdlib.add_log_level,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add stack info for exceptions
            structlog.processors.StackInfoRenderer(),
            # Format exceptions
            structlog.processors.format_exc_info,
            # Render as JSON
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Call once at application startup
configure_structured_logging()
logger = structlog.get_logger()
```

## JSON Log Format

### Standard Log Structure

```python
import structlog

logger = structlog.get_logger()

# CORRECT: Structured log with context
logger.info(
    "user_logged_in",
    user_id="user-123",
    email="user@example.com",
    ip_address="192.168.1.1",
    duration_ms=45
)

# Output JSON:
{
    "event": "user_logged_in",
    "level": "info",
    "timestamp": "2025-01-15T10:30:45.123Z",
    "user_id": "user-123",
    "email": "user@example.com",
    "ip_address": "192.168.1.1",
    "duration_ms": 45
}


# INCORRECT: Unstructured string interpolation
logger.info(f"User {user_id} logged in from {ip_address}")

# Output: Plain text, hard to query
# "User user-123 logged in from 192.168.1.1"
```

### Required Fields

Every log entry should include:

```python
{
    "timestamp": "2025-01-15T10:30:45.123Z",  # ISO 8601 format
    "level": "info",                           # debug, info, warning, error, critical
    "event": "user_created",                   # Event name (snake_case)
    "service": "finance_lending_api",          # Service name
    "request_id": "req-abc-123",               # Request correlation ID
    "message": "User created successfully"     # Human-readable message
}
```

## Context Enrichment

### Service-Level Context

```python
# src/core/logging_config.py
import structlog
from src.core.config import settings

def get_logger() -> structlog.BoundLogger:
    """Get logger with service-level context."""
    logger = structlog.get_logger()
    return logger.bind(
        service=settings.SERVICE_NAME,
        environment=settings.ENVIRONMENT,
        version=settings.VERSION
    )


# Usage in application code
logger = get_logger()
logger.info("service_started", port=8000)

# Output includes service context:
{
    "event": "service_started",
    "service": "finance_lending_api",
    "environment": "production",
    "version": "1.2.3",
    "port": 8000
}
```

### Request-Level Context

```python
# CORRECT: FastAPI middleware for request context
from fastapi import Request
import structlog
import uuid

async def logging_middleware(request: Request, call_next):
    """Add request context to all logs."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Bind request context to logger
    logger = structlog.get_logger().bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )

    # Store logger in request state
    request.state.logger = logger

    logger.info("request_started")

    response = await call_next(request)

    logger.info(
        "request_completed",
        status_code=response.status_code,
        duration_ms=calculate_duration()
    )

    return response


# Usage in endpoint
@router.post("/api/loans")
async def create_loan(request: Request, loan: LoanCreate):
    logger = request.state.logger  # Get logger with request context
    logger.info("creating_loan", amount=loan.amount)
    # All logs automatically include request_id, method, path
```

### User Context

```python
# CORRECT: Add user context after authentication
from fastapi import Depends

async def get_current_user(request: Request) -> User:
    """Authenticate user and enrich logger."""
    user = await authenticate(request)

    # Bind user context to logger
    request.state.logger = request.state.logger.bind(
        user_id=user.id,
        user_email=user.email,
        user_role=user.role
    )

    return user


@router.get("/api/profile")
async def get_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    logger = request.state.logger
    logger.info("profile_accessed")
    # Log includes: request_id, user_id, user_email, user_role
```

## Log Levels

### Standard Levels

```python
import structlog

logger = structlog.get_logger()

# DEBUG: Detailed diagnostic information
logger.debug("cache_hit", key="user:123", ttl=3600)

# INFO: General informational events
logger.info("loan_application_submitted", loan_id="loan-456", amount=10000)

# WARNING: Warning events that should be monitored
logger.warning("rate_limit_approaching", user_id="user-789", requests=950, limit=1000)

# ERROR: Error events requiring attention
logger.error("payment_processing_failed", payment_id="pay-123", reason="insufficient_funds")

# CRITICAL: Critical failures requiring immediate action
logger.critical("database_connection_lost", host="postgres.local", retry_count=5)
```

### Environment-Based Configuration

```python
# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""

    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_JSON: bool = True    # JSON format for production


# src/core/logging_config.py
import logging
from src.core.config import settings

def configure_log_level():
    """Configure log level from environment."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s" if settings.LOG_JSON else "%(levelname)s: %(message)s"
    )
```

## Application Patterns

### FastAPI Integration

```python
# CORRECT: Structured logging in FastAPI
from fastapi import FastAPI, Request
import structlog

app = FastAPI()
logger = structlog.get_logger()


@app.on_event("startup")
async def startup_event():
    """Log service startup."""
    logger.info(
        "service_starting",
        service="finance_lending_api",
        port=8000,
        environment="production"
    )


@app.post("/api/loans")
async def create_loan(request: Request, loan: LoanCreate):
    """Create loan with structured logging."""
    logger = request.state.logger

    logger.info(
        "loan_creation_started",
        user_id=loan.user_id,
        amount=loan.amount,
        purpose=loan.purpose
    )

    try:
        result = await loan_service.create_loan(loan)
        logger.info(
            "loan_created",
            loan_id=result.id,
            status=result.status
        )
        return result

    except InsufficientCreditError as e:
        logger.warning(
            "loan_rejected_credit",
            user_id=loan.user_id,
            credit_score=e.credit_score,
            required_score=e.required_score
        )
        raise HTTPException(status_code=422, detail="Insufficient credit score")

    except Exception as e:
        logger.error(
            "loan_creation_failed",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
```

### Aiogram Bot Integration

```python
# CORRECT: Structured logging in Aiogram bot
from aiogram import Bot, Dispatcher, types
import structlog

logger = structlog.get_logger().bind(service="finance_lending_bot")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    """Handle /start command with structured logging."""
    logger = structlog.get_logger().bind(
        user_id=message.from_user.id,
        username=message.from_user.username,
        chat_id=message.chat.id
    )

    logger.info("bot_command_received", command="start")

    try:
        await message.reply("Welcome to Finance Lending Bot!")
        logger.info("bot_response_sent", command="start")

    except Exception as e:
        logger.error(
            "bot_command_failed",
            command="start",
            error=str(e),
            exc_info=True
        )
```

### Background Worker Integration

```python
# CORRECT: Structured logging in AsyncIO worker
import structlog
import asyncio

logger = structlog.get_logger().bind(service="finance_lending_worker")


async def process_loan_application(loan_id: str):
    """Process loan with structured logging."""
    task_logger = logger.bind(loan_id=loan_id, task="process_loan")

    task_logger.info("task_started")

    try:
        loan = await fetch_loan(loan_id)
        task_logger.info("loan_fetched", amount=loan.amount)

        credit_score = await check_credit(loan.user_id)
        task_logger.info("credit_checked", score=credit_score)

        decision = await make_decision(loan, credit_score)
        task_logger.info(
            "decision_made",
            decision=decision.status,
            reason=decision.reason
        )

        await notify_user(loan.user_id, decision)
        task_logger.info("task_completed", duration_ms=calculate_duration())

    except Exception as e:
        task_logger.error(
            "task_failed",
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise
```

## Exception Logging

### Structured Exception Context

```python
# CORRECT: Log exceptions with structured context
import structlog

logger = structlog.get_logger()

try:
    result = await external_api.call(user_id="user-123")
except httpx.HTTPError as e:
    logger.error(
        "external_api_error",
        user_id="user-123",
        error_type="HTTPError",
        status_code=e.response.status_code if e.response else None,
        url=str(e.request.url),
        exc_info=True  # Include full traceback
    )
    raise

except Exception as e:
    logger.critical(
        "unexpected_error",
        error_type=type(e).__name__,
        error_message=str(e),
        exc_info=True
    )
    raise


# INCORRECT: Unstructured exception logging
except Exception as e:
    logger.error(f"Error occurred: {e}")  # Lost context, no traceback
```

## Testing Structured Logs

### Capturing Logs in Tests

```python
# CORRECT: Test structured log output
import pytest
import structlog
from structlog.testing import LogCapture


def test_loan_creation_logs():
    """Test loan creation emits correct structured logs."""
    cap = LogCapture()
    structlog.configure(processors=[cap])

    logger = structlog.get_logger()
    logger.info("loan_created", loan_id="loan-123", amount=10000)

    # Assert log structure
    assert len(cap.entries) == 1
    assert cap.entries[0]["event"] == "loan_created"
    assert cap.entries[0]["loan_id"] == "loan-123"
    assert cap.entries[0]["amount"] == 10000
```

## Best Practices

### DO: Use Consistent Event Names

```python
# CORRECT: Consistent event naming (snake_case)
logger.info("user_created", user_id="user-123")
logger.info("user_updated", user_id="user-123")
logger.info("user_deleted", user_id="user-123")

# Enables queries: event IN ("user_created", "user_updated", "user_deleted")


# INCORRECT: Inconsistent naming
logger.info("UserCreated")  # PascalCase
logger.info("user-updated")  # kebab-case
logger.info("USER_DELETED")  # SCREAMING_SNAKE_CASE
```

### DO: Log Structured Data, Not Formatted Strings

```python
# CORRECT: Structured fields
logger.info(
    "payment_processed",
    payment_id="pay-123",
    amount=99.99,
    currency="USD",
    user_id="user-456"
)

# Query: SELECT * WHERE amount > 100 AND currency = 'USD'


# INCORRECT: String interpolation
logger.info(f"Processed payment pay-123 for $99.99 USD by user-456")
# Cannot query by amount or currency
```

### DO: Include Context in Every Log

```python
# CORRECT: Rich context
logger.info(
    "api_request_completed",
    request_id="req-abc",
    method="POST",
    path="/api/loans",
    status_code=201,
    duration_ms=145,
    user_id="user-123"
)


# INCORRECT: Minimal context
logger.info("Request completed")  # No context to debug issues
```

### DON'T: Log Sensitive Data

```python
# CORRECT: Mask sensitive data
logger.info(
    "user_authenticated",
    user_id="user-123",
    email="u***@example.com",  # Masked
    ip_address="192.168.1.1"
)


# INCORRECT: Log passwords, tokens, PII
logger.info(
    "login_attempt",
    email="user@example.com",
    password="secret123",  # ❌ Never log passwords
    credit_card="4111-1111-1111-1111"  # ❌ Never log payment data
)
```

### DON'T: Over-Log in Hot Paths

```python
# CORRECT: Log summaries, not every iteration
total_processed = 0
for user in users:
    await process_user(user)
    total_processed += 1

logger.info("batch_processed", total_users=total_processed, duration_ms=duration)


# INCORRECT: Log every iteration
for user in users:  # 10,000 users
    logger.info("processing_user", user_id=user.id)  # ❌ 10,000 log entries!
```

## Configuration Examples

### Development Configuration

```python
# Development: Human-readable console output
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer()  # Colored, formatted output
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
```

### Production Configuration

```python
# Production: JSON output for centralized logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()  # JSON for Elasticsearch/CloudWatch
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

## Checklist

- [ ] Install structlog library
- [ ] Configure JSON log format
- [ ] Add service-level context (service name, environment, version)
- [ ] Implement request-level context (request_id, method, path)
- [ ] Add user context after authentication
- [ ] Use consistent event naming (snake_case)
- [ ] Log structured data, not formatted strings
- [ ] Include relevant context in every log
- [ ] Configure appropriate log levels per environment
- [ ] Implement exception logging with exc_info=True
- [ ] Mask sensitive data (passwords, tokens, PII)
- [ ] Avoid over-logging in hot paths
- [ ] Test log output in unit tests
- [ ] Integrate with centralized logging system

## Related Documents

- `docs/atomic/observability/logging/log-formatting.md` — Log formatting standards and conventions
- `docs/atomic/observability/logging/log-correlation.md` — Correlating logs across distributed services
- `docs/atomic/observability/logging/request-id-tracking.md` — Request ID propagation and tracking
- `docs/atomic/observability/logging/sensitive-data-handling.md` — Handling sensitive data in logs
- `docs/atomic/observability/logging/centralized-logging.md` — Centralized logging infrastructure setup
