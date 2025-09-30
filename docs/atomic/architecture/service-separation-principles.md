# Service Separation Principles

This guide defines the boundaries between business, data, and platform services in the Improved Hybrid Approach. Keeping the separation strict prevents cascading failures, simplifies testing, and enables teams to ship independently.

## Guiding Rules

1. **Business logic stays in business services.** These services expose HTTP APIs, bot handlers, or background jobs. They never talk to databases directly and never own schema migrations.
2. **Data services own persistence.** Data services wrap PostgreSQL or MongoDB, enforce invariants close to the data, and expose domain-aware HTTP endpoints.
3. **Integration services provide shared infrastructure access.** Reusable adapters for Redis, RabbitMQ, or external APIs live here and are consumed by business/data services through dependency injection.
4. **Shared components are deliberately minimal.** Shared DTOs or utilities go to `shared/` only when multiple services depend on the same contract.
5. **Event loop ownership is explicit.** Each process manages exactly one event loop; cross-service communication uses HTTP or messaging.

## Responsibility Matrix

| Concern | Business Service | Data Service | Platform / Integration |
|---------|-----------------|--------------|------------------------|
| Domain logic | ✅ | 🚫 | 🚫 |
| Schema migrations | 🚫 | ✅ | 🚫 |
| External HTTP calls | ✅ (domain-specific) | 🚫 | ✅ (shared connectors) |
| Broker interactions | ✅ via adapters | 🚫 | ✅ (adapters, consumers) |
| Cache usage | ✅ via adapters | ✅ (internal caching) | ✅ (infrastructure) |
| Observability | ✅ (emit context) | ✅ (emit context) | ✅ (aggregate metrics/logs) |

## Boundary Checklist

- Business services **must not** import ORM models or repositories from data services.
- Data services **must not** leak database drivers or sessions to clients.
- Shared DTOs use suffixes (`...Create`, `...Update`, `...Public`) to clarify purpose.
- Any shared helper must be stateless and free of transport- or storage-specific assumptions.
- Version all HTTP APIs and keep backward-compatible responses until consumers migrate.

## Integration Patterns

- **HTTP** – use typed clients built on `httpx.AsyncClient`; provide retries with exponential backoff and propagate `X-Request-ID`.
- **Messaging** – use RabbitMQ via application-level publishers/subscribers; keep message DTOs in `shared/events/`.
- **Caching** – access Redis through well-defined key namespaces owned by the calling service; never re-use keys across domains.

## Anti-Patterns to Avoid

- Fat “shared” modules that contain business logic used by multiple services. Duplicate logic instead if domain contexts differ.
- Passing raw database cursors, ORM sessions, or repository instances across service boundaries.
- Embedding business validation inside data services—use domain-aware endpoints that validate inputs but keep core rules within business services.
- Starting multiple event loops inside the same container (see `event-loop-management.md`).

## Enforcement

- Code reviews block any direct DB access in business services (`rg "asyncpg" services/api-service` should return zero matches outside data services).
- CI runs static checks (import blocks, architecture tests) to detect illegal module dependencies.
- Deployment manifests isolate data services behind internal networks so only platform-approved clients can reach them.

## Related Materials

- `docs/atomic/architecture/improved-hybrid-overview.md`
- `docs/atomic/architecture/event-loop-management.md`
- `docs/atomic/services/fastapi/dependency-injection.md`
- Legacy reference: `docs/legacy/architecture/ms_best_practices_rules.mdc`
