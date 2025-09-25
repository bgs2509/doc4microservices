# FastAPI Application Factory

Use an application factory to keep side effects out of module scope, enable dependency overrides in tests, and wire integrations explicitly.

## Factory Pattern

```python
from __future__ import annotations

from fastapi import FastAPI
from src.core.config import Settings, get_settings
from src.core.logging import configure_logging
from src.core.di import Container
from src.api.routes import register_routes


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    container = Container(settings=settings)

    app = FastAPI(
        title=settings.service_name,
        version=settings.version,
        default_response_class=container.default_response_class(),
        lifespan=container.build_lifespan(),
    )

    register_routes(app)
    app.state.container = container
    return app
```

## Container Responsibilities

- Construct singletons (database engine, Redis client, RabbitMQ connections).
- Expose dependency providers (`get_user_service`, `get_unit_of_work`).
- Provide lifespan context manager for startup/shutdown (see `lifespan-management.md`).

## Testing with the Factory

```python
from fastapi.testclient import TestClient
from src.main import create_app
from src.tests.factories import TestContainer


def test_health_endpoint() -> None:
    app = create_app(settings=TestContainer.settings())
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

## Advantages

- **Deterministic boot** – settings resolved once, DI container centralised.
- **Override-friendly** – tests inject fake dependencies via `dependency_overrides` or container hooks.
- **Reduced cold start** – heavy resources initialised during lifespan, not at import time.

## Checklist

- [ ] `create_app()` accepts optional settings for tests.
- [ ] Container/DI wiring happens inside the factory.
- [ ] Routes registered via dedicated helper (no inline definitions in `main.py`).
- [ ] `app.state` stores container for internal usage only (never imported directly).

## Related Documents

- `docs/atomic/services/fastapi/lifespan-management.md`
- `docs/atomic/architecture/project-structure-patterns.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
