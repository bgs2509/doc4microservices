# Naming Conventions

This standard enforces an underscore-only policy across the codebase. Hyphens are prohibited except where external tooling requires them (e.g., `docker-compose.yml`).

## Core Rules

| Area | Convention | Examples |
|------|------------|----------|
| Files & folders | `snake_case` | `user_service/`, `api_endpoints/`, `docker_compose.yml` |
| Python modules | `snake_case` | `user_repository.py`, `order_dto.py` |
| Classes | `PascalCase` | `UserService`, `OrderRepository` |
| Functions & variables | `snake_case` | `get_user_by_id`, `max_retry_attempts` |
| Constants | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `MAX_CONNECTIONS` |
| JSON fields & query params | `snake_case` | `{ "created_at": "..." }`, `?user_id=...` |
| Databases | `snake_case` | `user_service_db`, `order_items`, `fk_order_customer` |

## Python Code

- Modules and packages must use `snake_case`.
- Classes use `PascalCase`; data classes and Pydantic models follow the same rule.
- Functions, methods, and variables use `snake_case`.
- Constants use `UPPER_SNAKE_CASE` and live at module scope.
- DTOs adopt descriptive suffixes (`...Base`, `...Create`, `...Update`, `...Public`, `...Payload`). Avoid generic names like `DataDTO`.

## APIs and Contracts

- REST paths use `snake_case` segments: `/api/v1/user_accounts/{user_id}`.
- Query parameters and JSON keys follow `snake_case`.
- OpenAPI operation IDs use `snake_case` (`get_user_by_id`).
- Response payloads should never expose internal IDs or enums with hyphens.

## Databases

- Table names, columns, indexes, and constraints all use `snake_case`.
- PostgreSQL schemas follow the same pattern (`public` is acceptable).
- MongoDB collections use `snake_case` (`analytics_events`).
- Migrations use sequential prefixes (`202501010101_initial_schema.py`).

## Infrastructure

- Docker services, containers, and volumes use `snake_case` (`redis_cache`, `user_api_service`).
- Kubernetes manifests (if used) align with this policy except where the platform enforces hyphenated names.
- Git branches prefer `feature/snake_case_summary` to avoid escaping issues in scripts.

## Exceptions

Some tools mandate hyphenated or fixed names. These are allowed and documented:

- `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`, `docker-compose.test.yml`.
- `.gitignore`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`, `.dockerignore`.
- Third-party packages in `pyproject.toml` or `requirements.txt` (e.g., `flask-sqlalchemy`).
- HTTP headers (e.g., `X-Request-ID`, `Content-Type`).

Any new exception must be documented in the consuming service’s README and, if long-lived, added to this list.

## Migration Guidance

1. Audit filenames, folders, and identifiers with `rg --pcre2 "-"` and rename offenders.
2. Provide aliases or redirects when renaming public APIs to maintain backward compatibility.
3. Update documentation, logs, and metrics to reflect new names.
4. Add regression tests where renaming may impact serialisation or external consumers.

## Related Documents

- `docs/atomic/architecture/project-structure-patterns.md`
- `docs/atomic/testing/quality-assurance/linting-standards.md`
- Legacy reference: `docs/legacy/architecture/naming_conventions.mdc`
