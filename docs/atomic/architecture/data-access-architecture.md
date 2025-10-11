# Data Access Architecture

Data services encapsulate all database interactions and expose domain-specific HTTP APIs. Business services remain database agnostic and communicate through typed HTTP clients.

## Architectural Overview

- Each data service is a standalone FastAPI application dedicated to one persistence technology (PostgreSQL or MongoDB).
- Data services implement both CRUD and domain-aware operations (aggregations, joins) while keeping business logic in the calling services.
- HTTP is the only approved transport between business and data services.

## PostgreSQL Service Guidelines

- Use SQLAlchemy 2.x with async sessions and connection pooling.
- Manage transactions explicitly; roll back on exceptions to keep the pool healthy.
- Provide pagination, filtering, and sorting for list endpoints.
- Version endpoints under `/api/v1` and document them via OpenAPI.
- Maintain migrations with Alembic; migrations run as part of CI and deployment.

## MongoDB Service Guidelines

- Use Motor for non-blocking access and rely on typed Pydantic models for validation.
- Apply collection-level indexes and validate schemas to enforce structure.
- Support aggregation pipelines for analytics scenarios.
- Provide document-level access control where domain requirements demand it.

## Business Service Integration

1. Create typed HTTP clients that wrap `httpx.AsyncClient` calls.
2. Propagate correlation headers (`X-Request-ID`, `X-User-ID`).
3. Handle network failures with retries, circuit breakers, and fallback logic.
4. Cache read-heavy endpoints when latency or throughput requires it (Redis, in-memory caches).
5. Mock HTTP clients in unit tests; rely on Testcontainers for integration tests.

## Error Handling

- Use RFC 7807 Problem Details responses for consistency.
- Map validation errors to `400`, conflicts to `409`, not found to `404`, and unexpected issues to `500`.
- Log structured errors including correlation ids and service names.
- Fall back gracefully when data services are unavailable by returning meaningful error codes to callers.

## Performance Considerations

- Tune connection pool sizes based on workload (minimum/maximum connections, timeouts).
- Ensure every list endpoint uses pagination and query filters to avoid full table scans.
- Monitor query plans (`EXPLAIN ANALYZE`) and add indexes aligned with access patterns.
- Measure end-to-end latency (business service → data service → DB) and alert on regressions.

## Security

- Validate incoming payloads with Pydantic models; never trust raw JSON.
- Enforce authentication and authorisation at the edge or through service mesh policies.
- Keep secrets and connection strings in environment variables or secret stores.
- Use TLS for inter-service communication in production environments.

## Testing Strategy

- Unit test repositories and domain adapters with mocks/stubs.
- Integration test endpoints with real databases via Testcontainers.
- Contract test HTTP interactions between business and data services to detect breaking changes early.

## Related Documents

- `docs/atomic/services/data-services/postgres-service-setup.md`
- `docs/atomic/services/data-services/mongo-service-setup.md`
- `docs/atomic/integrations/http-communication/http-client-patterns.md`
