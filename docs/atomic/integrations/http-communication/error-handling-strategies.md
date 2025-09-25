# HTTP Error Handling Strategies

Handle downstream HTTP failures consistently and convert them into domain errors.

## Mapping

- 4xx responses indicate caller issues (validation, authorization). Translate into domain exceptions that surface meaningful Problem Details.
- 5xx responses indicate dependency outages. Log with WARN/ERROR and trigger retries or fallbacks.
- Timeouts are treated as transient failures; consider retries before raising circuit breaker events.

## Implementation

```python
from httpx import HTTPStatusError


async def fetch_user(client, url):
    try:
        response = await client.get(url)
        response.raise_for_status()
    except HTTPStatusError as exc:
        if 400 <= exc.response.status_code < 500:
            raise DomainValidationError(str(exc)) from exc
        raise DependencyUnavailableError(str(exc)) from exc
    return response.json()
```

## Observability

- Log status code, endpoint name, request ID, and retry count (if any).
- Emit metrics for error rates per dependency; set SLO thresholds and alerts.

## Fallbacks

- Provide cached data or default responses when appropriate.
- Surface clear messages to users while preserving diagnostics in logs.

## Related Documents

- `docs/atomic/integrations/http-communication/timeout-retry-patterns.md`
- `docs/atomic/services/fastapi/error-handling.md`
