# Improved Hybrid Approach Overview

The Improved Hybrid Approach combines strict service boundaries with shared tooling to keep delivery fast while ensuring architectural discipline. Business capabilities live in independently deployable services, data is exposed through dedicated data services, and cross-cutting concerns (observability, queues, caches) are delivered as platform components.

## Goals

- Preserve clear separation between **business**, **data**, and **supporting** services.
- Provide a consistent developer experience across REST APIs, bots, and background workers.
- Allow incremental adoption inside existing products without breaking production traffic.
- Ensure every service can be tested, deployed, and scaled independently.

## Service Landscape

| Category | Role | Examples |
|----------|------|----------|
| Business services | Deliver user-facing or domain logic via HTTP or messaging interfaces. | `template_business_api`, `template_business_bot`, `template_business_worker` |
| Data services | Own direct database access and expose domain-driven HTTP APIs. | `template_data_postgres_api`, `template_data_mongo_api` |
| Integration services | Provide reusable interfaces to brokers, caches, third-party APIs. | Redis, RabbitMQ bridges |
| Platform components | Observability, CI/CD, configuration, shared libraries. | `docs/atomic/*`, `scripts/` |

## Interaction Model

1. Business services call data services over HTTP (never direct DB connections).
2. Integration services (Redis, RabbitMQ) are accessed through adapters published by the platform team.
3. Shared DTOs live under `src/shared/` to avoid duplication while respecting domain boundaries.
4. Observability context (request id, trace id) flows through every hop via headers and logging formatters.

```
Client → Business Service → HTTP → Data Service → Database
           │
           └→ Messaging / Cache via dedicated adapters
```

## Architectural Tenets

- **Single Source of Truth** – the `docs/atomic/` tree defines authoritative guidance. Legacy `.mdc` rules remain available in `docs/legacy/` for historical reference.
- **HTTP-only Data Access** – business services rely on typed clients that wrap HTTP calls and hide retry logic. Contracts are versioned (`/api/v1`) and validated with Pydantic schemas.
- **Async First** – all services share a single event loop per process, using async drivers for databases, queues, and HTTP clients.
- **Operational Transparency** – each service exposes `/health` and `/ready`, publishes Prometheus metrics, and emits structured logs with request correlation.
- **Quality Gates** – CI enforces linting, typing, security scans, and full test coverage before deployment.

## When to Use

- Greenfield microservice deployments that require rapid iteration without losing governance.
- Brownfield monolith extractions where domain logic must be separated from data access.
- Teams that share the same platform primitives (FastAPI, Aiogram, AsyncIO workers) and want strongly guided defaults.

## Migration Notes

1. Inventory current services and classify them as business, data, or integration components.
2. Move legacy rule files into `docs/legacy/` (already complete) and map each to its atomic successor.
3. Establish typed HTTP clients for every data-service dependency, using the patterns in `docs/atomic/services/*`.
4. Update CI/CD to run the mandatory verification steps described in `docs/atomic/architecture/quality-standards.md`.
5. Communicate the new documentation baseline to every squad and deprecate direct references to `.mdc` files.

## Related Materials

- `docs/atomic/architecture/service-separation-principles.md`
- `docs/atomic/architecture/project-structure-patterns.md`
- `docs/atomic/services/fastapi/basic-setup.md`
- Legacy context: `docs/legacy/architecture/ms_best_practices_rules.mdc`
