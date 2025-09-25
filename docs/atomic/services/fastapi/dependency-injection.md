# Dependency Injection

Use FastAPI dependencies and a lightweight service container to provide integrations, application services, and security context.

## Provider Pattern

```python
from __future__ import annotations

from collections.abc import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.di import Container
from src.infrastructure.db import get_session
from src.application.users import UserService


def get_container() -> Container:
    return Container.current()


def get_db_session(
    container: Container = Depends(get_container),
) -> AsyncGenerator[AsyncSession, None]:
    session = container.db_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    container: Container = Depends(get_container),
) -> UserService:
    return container.user_service(session=session)
```

## Design Guidelines

- Dependencies must be idempotent and quick to resolve.
- Use `Depends` for business services and security; avoid global singletons.
- Keep dependency functions in `src/core/di.py` or feature-specific modules.
- For simple configuration, return `Settings` directly from `Depends(get_settings)`.

## Override Strategy

```python
from fastapi.testclient import TestClient
from src.main import create_app
from tests.fakes.users import FakeUserService


def test_override_user_service() -> None:
    app = create_app()

    app.dependency_overrides[get_user_service] = lambda: FakeUserService()

    client = TestClient(app)
    response = client.post("/api/v1/users", json={"email": "test@example.com"})

    assert response.status_code == 201
```

## Anti-Patterns

- Creating database engines or Redis clients inside dependencies; initialise them during lifespan.
- Using dependency overrides to swap infrastructure in production (keep overrides for tests and local experiments only).
- Passing around `FastAPI` app instances; rely on DI instead.

## Related Documents

- `docs/atomic/services/fastapi/lifespan-management.md`
- `docs/atomic/architecture/service-separation-principles.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
