# Error Handling

Return consistent, debuggable error responses using RFC 7807 Problem Details.

## Problem Details Structure

```json
{
  "type": "https://docs.example.com/errors/resource-not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "User 42 not found",
  "instance": "urn:request:123e4567-e89b-12d3-a456-426614174000",
  "code": "USER_NOT_FOUND",
  "context": {
    "resource": "user",
    "id": "42"
  }
}
```

## Implementation Pattern

```python
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from src.core.errors import DomainError, NotFoundError


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    problem = {
        "type": exc.problem_type,
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.message,
        "instance": str(request.state.request_id),
        "code": exc.code,
        "context": exc.context,
    }
    return JSONResponse(problem, status_code=exc.status_code)
```

Register handlers inside `create_app()`.

```python
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
```

## Guidelines

- Convert Pydantic validation errors (`RequestValidationError`) into Problem Details with field paths (`data.attributes.name`).
- Avoid `raise HTTPException(...)` in routers; instead raise domain/application exceptions.
- Include request IDs and correlation IDs in responses for traceability.
- Hide sensitive details; log full error context but redact secrets before returning to clients.

## Testing

- Unit-test exception handlers to ensure correct payload shape.
- Integration tests should assert status codes and `code` values for each error scenario.

## Related Documents

- `docs/atomic/observability/logging/structured-logging.md`
- `docs/atomic/services/fastapi/security-patterns.md`
