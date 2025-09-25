# Routing Patterns

Routers translate HTTP requests into application service calls. Keep them transport-focused and free of business logic.

## Router Layout

```
src/api/v1/
├── __init__.py
├── users_router.py
└── orders_router.py
```

Each router defines:
- Endpoint metadata (`summary`, `description`, tags).
- DTO usage via `response_model`.
- Dependency injection for services, security, and context.

## Example

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from src.schemas.users import UserCreate, UserPublic
from src.application.users import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    return await service.create_user(payload)
```

## Best Practices

- Register routers in a central function (`register_routes(app)`), not inline in `main.py`.
- Use `APIRouter(prefix="/resource", tags=["resource"])` to keep URL namespaces consistent.
- Apply middlewares or dependencies at router level for shared concerns (authentication, rate limits).
- For feature toggles, guard entire routers rather than individual endpoints to simplify removal.

## Versioning

- Include routers under `/api/v{major}`; deprecate old versions using the `deprecated=True` flag in endpoint metadata.
- Avoid mixing experimental endpoints with stable ones; publish under `/api/experimental` if needed.

## Validation & Documentation

- Always set `response_model` and `status_code` explicitly.
- Use descriptive summaries and descriptions; these surface in the OpenAPI schema.
- Prefer `ORJSONResponse` for JSON payloads; specify per-endpoint when large responses demand streaming.

## Related Documents

- `docs/atomic/services/fastapi/schema-validation.md`
- `docs/atomic/services/fastapi/error-handling.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
