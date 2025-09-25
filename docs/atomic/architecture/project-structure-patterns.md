# Project Structure Patterns

This document details the canonical structure for repositories using the Improved Hybrid Approach. Treat it as the authoritative map for scaffolding new services and auditing existing ones.

## Repository Layout

```
my_service/
├── docs/                   # Documentation (this framework when used directly)
├── scripts/                # Automation helpers
├── src/
│   ├── api/                # Transport adapters (FastAPI routers, webhooks)
│   ├── application/        # Use cases, orchestrators
│   ├── domain/             # Entities, value objects, domain services
│   ├── infrastructure/     # Repositories, HTTP clients, broker adapters
│   ├── schemas/            # Pydantic DTOs (request/response)
│   ├── core/               # Configuration, logging, settings
│   └── tasks/              # Background jobs, celery-style workers
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── service/
│   └── e2e/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Service Modules

- **api/** – minimal routing logic; no business decisions.
- **application/** – orchestrates domain operations and applies use-case logic.
- **domain/** – pure business rules with no framework dependencies.
- **infrastructure/** – concrete adapters (ORM, HTTP, messaging, caching).
- **schemas/** – request/response models grouped by feature area.
- **core/** – settings, logging setup, dependency injection container, typed configuration.
- **tasks/** – background processing (cron workers, scheduled jobs).

## Shared Components

- Cross-service DTOs reside in `src/shared/dtos/` with clear ownership.
- Shared events live in `src/shared/events/` to align messaging contracts.
- Utilities under `src/shared/utils/` remain stateless and generic.

## Documentation Expectations

- Each service ships a README with run/test/build instructions and links back to the relevant atomic files.
- Architecture decisions are captured via ADRs (see `docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md`).
- When the framework is used as a submodule, treat `.framework/docs/atomic/` as read-only source material.

## Environment and Configuration

- Manage settings through `pydantic.BaseSettings` under `src/core/config.py`.
- Store secrets in environment variables or secret managers; never commit secrets.
- Provide `.env.example` with non-sensitive defaults for developers.

## Testing Layout

- `tests/unit/` mirrors the `src/` structure.
- `tests/integration/` houses Testcontainers-based scenarios.
- `tests/service/` exercises full service stacks (HTTP, bots, or workers).
- `tests/e2e/` cover cross-service journeys.

## Tooling

- AI scaffolding anchors (e.g., `# @cursor-include-router-anchor`) belong in infrastructure/application layers to support generators without polluting domain code.
- CI scripts live in `scripts/` and are referenced from the Makefile or task runner.
- Use `uv` or `pip` with lock files to guarantee repeatable environments.

## Related Documents

- `docs/atomic/architecture/naming-conventions.md`
- `docs/reference/PROJECT_STRUCTURE.md`
- Legacy reference: `docs/legacy/architecture/ms_best_practices_rules.mdc`
