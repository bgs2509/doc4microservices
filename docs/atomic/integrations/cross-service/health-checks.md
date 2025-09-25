# Health Checks

Health checks signal readiness and liveness to orchestrators and other services.

## Types

- **Liveness** – indicates the process is running. Should be lightweight and never depend on external systems.
- **Readiness** – confirms the service can accept traffic (database connections, caches, message brokers initialised).
- **Dependency-specific** – optional endpoints for detailed diagnostics (`/health/db`, `/health/rabbitmq`).

## Implementation

- Expose `/health` and `/ready` at the root (non-versioned) router.
- Return structured JSON with status and optional metadata (component states, build version).
- Fail readiness when critical dependencies are unavailable; orchestrators will remove the instance from load balancing.

## Monitoring

- Capture health-check response times and failure counts in metrics.
- Integrate health endpoints with uptime monitors and alerting rules.

## Related Documents

- `docs/atomic/architecture/improved-hybrid-overview.md`
- `docs/atomic/services/fastapi/basic-setup.md`
