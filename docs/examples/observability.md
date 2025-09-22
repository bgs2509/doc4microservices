## Observability

Observability is the ability to understand the internal state of a system from its external outputs. The three pillars of observability are **Logs**, **Metrics**, and **Traces**. In this section, we'll explore how to implement them in our services.

### 1. Structured Logging with Correlation ID

Structured logs (e.g., in JSON format) are easy to parse and analyze. `Correlation ID` is a unique identifier assigned to a request and passed through all services that the request affects. This allows tracking the complete request path in a distributed system.

We'll use `structlog` and custom middleware for FastAPI.

#### Installation
```bash
pip install structlog "uvicorn[standard]"
```

#### Implementation

`src/middlewares/correlation_id.py`
```python
from __future__ import annotations

import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# Context variable for storing request ID
CORRELATION_ID_CTX_KEY = "correlation_id"
correlation_id_ctx: ContextVar[str] = ContextVar(CORRELATION_ID_CTX_KEY, default=None)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Try to get ID from header or generate new one
        correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set ID in context variable
        token = correlation_id_ctx.set(correlation_id)

        response = await call_next(request)

        # Add ID to response header
        response.headers["X-Request-ID"] = correlation_id

        # Reset context variable
        correlation_id_ctx.reset(token)

        return response
```

#### Configuring `structlog`

Now let's configure `structlog` to add `correlation_id` to each log entry.

`src/logging_config.py`
```python
import logging
import structlog

from .middlewares.correlation_id import correlation_id_ctx

def setup_logging():
    """Configure structured logging."""

    def add_correlation_id(logger, method_name, event_dict):
        """Add correlation_id to log entry if it exists in context."""
        correlation_id = correlation_id_ctx.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_correlation_id,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

#### Integration in `main.py`
```python
from .logging_config import setup_logging
from .middlewares.correlation_id import CorrelationIdMiddleware

# Call at the very beginning
setup_logging()

app = FastAPI(...)
app.add_middleware(CorrelationIdMiddleware)
```

### 2. Metrics with Prometheus

Prometheus is the de facto standard for metrics collection. We can easily add a `/metrics` endpoint to our FastAPI application.

#### Installation
```bash
pip install prometheus-fastapi-instrumentator
```

#### Implementation

`src/main.py`
```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# ... (middleware)

# Add Prometheus instrumentor
Instrumentator().instrument(app).expose(app)

# ... (routers)
```

Now, if you run the application, the `/metrics` endpoint will be available with basic metrics (request latency, count, etc.).

#### Adding Custom Metrics

```python
# src/services/user_service.py
from prometheus_client import Counter

# Create counter for created users
USERS_CREATED_COUNTER = Counter("users_created_total", "Total number of users created", ["source"])

class UserService:
    # ...
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # ...
        created_user = await self.user_repository.create(user)

        # Increment counter
        USERS_CREATED_COUNTER.labels(source="api").inc()

        # ...
        return UserResponse.model_validate(created_user)
```

### 3. Distributed Tracing with OpenTelemetry

Tracing allows visualizing the complete request path through multiple services. OpenTelemetry is the standard for trace collection.

#### Installation
```bash
pip install opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-httpx
```

#### Implementation

Let's configure trace export to console (in a real project this would be Jaeger, Zipkin, or another collector).

`src/tracing_config.py`
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(app: FastAPI):
    """Configure distributed tracing."""
    # Set up tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Configure console export
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    # Instrument FastAPI application
    FastAPIInstrumentor.instrument_app(app)

    # Instrument HTTPX client for trace header propagation
    HTTPXClientInstrumentor().instrument()

    print("OpenTelemetry tracing configured.")
```

#### Integration in `main.py`
```python
from .tracing_config import setup_tracing

app = FastAPI(...)

# ... (middleware)

# Configure tracing
setup_tracing(app)

# ... (routers)
```

Now with each API request, trace spans will appear in the console. If an HTTP request is made from one service to another (also instrumented), OpenTelemetry will automatically link them into a single trace thanks to `HTTPXClientInstrumentor`.
