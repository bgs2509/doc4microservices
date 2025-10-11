# FastAPI Basic Setup

This guide covers the minimum scaffolding required to spin up a FastAPI business service that conforms to the Improved Hybrid Approach.

## Prerequisites

- Python 3.12+ with `uv` or `pip` for dependency management.
- `src/` layout prepared according to `docs/atomic/architecture/project-structure-patterns.md`.
- Shared configuration defined in `src/core/config.py` (Pydantic `BaseSettings`).

## Initial Project Structure

```
src/
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── health_router.py
├── application/
│   └── __init__.py
├── domain/
│   └── __init__.py
├── infrastructure/
│   └── __init__.py
├── schemas/
│   └── health.py
├── core/
│   ├── config.py
│   ├── logging.py
│   └── di.py
└── main.py
```

## Dependencies

```toml
# pyproject.toml
[project]
name = "my_fastapi_service"
requires-python = ">=3.12"

[project.dependencies]
fastapi = "^0.111"
uvicorn = "^0.30"
httpx = "^0.27"
sqlalchemy = "^2.0"          # optional, keep only if needed
asyncpg = "^0.29"             # optional, keep only if needed
orjson = "^3.10"
pydantic = "^2.8"
```

## Entry Point (`main.py`)

```python
from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from src.core.logging import configure_logging
from src.api.v1.health_router import router as health_router


def create_app() -> FastAPI:
    """Instantiate the FastAPI application with minimal defaults."""
    configure_logging()

    app = FastAPI(
        title="My FastAPI Service",
        version="1.0.0",
        default_response_class=None,  # override in routers where needed
    )

    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config=None,
    )
```

## Health Router (`health_router.py`)

```python
from __future__ import annotations

from fastapi import APIRouter, status
from src.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
```

## DTO Example (`schemas/health.py`)

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service liveness indicator")
```

## Startup Checklist

- [ ] Project structure matches the reference layout.
- [ ] Logging configured once in `create_app()`.
- [ ] `/api/v1/health` endpoint returns static status.
- [ ] Uvicorn entry point uses application factory instead of global side effects.

## Related Documents

- `docs/atomic/services/fastapi/application-factory.md`
- `docs/atomic/architecture/service-separation-principles.md`
