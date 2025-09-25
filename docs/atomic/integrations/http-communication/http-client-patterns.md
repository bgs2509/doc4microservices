# HTTP Client Patterns

Use `httpx.AsyncClient` as the standard HTTP client for inter-service calls.

## Construction

```python
from httpx import AsyncClient, Limits, Timeout


def build_client(settings):
    return AsyncClient(
        timeout=Timeout(5.0, connect=1.0),
        limits=Limits(max_connections=200, max_keepalive_connections=100),
        headers={"User-Agent": settings.service_name},
    )
```

- Create the client once per process (FastAPI lifespan, worker bootstrap) and reuse it for all requests.
- Close the client during shutdown to release sockets.

## Middleware

- Add logging middleware to capture method, URL, status, and duration.
- Inject tracing headers (`traceparent`, `tracestate`) per request.

## Resilience

- Wrap calls with retries/backoff (see `timeout-retry-patterns.md`).
- Detect unhealthy dependencies using circuit breakers and fallback behaviour.

## Testing

- Mock responses with `respx` or `pytest-httpx` in unit tests.
- Use Testcontainers or staging data services for end-to-end contract validation.

## Related Documents

- `docs/atomic/integrations/http-communication/timeout-retry-patterns.md`
- `docs/atomic/integrations/http-communication/error-handling-strategies.md`
