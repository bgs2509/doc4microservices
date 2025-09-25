# Testing Strategies

Data services must prove correctness across repositories, HTTP endpoints, and integration scenarios.

## Unit Tests

- Validate repositories against in-memory fakes or mocks for simple logic.
- Assert DTO validation catches schema violations before hitting the database.
- Ensure units of work commit/rollback as expected.

## Integration Tests

- Use Testcontainers to run PostgreSQL and MongoDB.
- Apply migrations before tests (Alembic, custom scripts).
- Exercise HTTP endpoints via `httpx.AsyncClient`; verify status codes and payload shapes.
- Validate transactional behaviour (rollback on failure, unique constraint handling).

## Contract Tests

- Snapshot OpenAPI schema and repository interfaces.
- Perform consumer-driven tests with business services to ensure response fields remain stable.

## Performance/Load Tests

- Benchmark heavy aggregate endpoints and large batch operations.
- Identify slow queries (EXPLAIN) and ensure indexes cover key paths.

## CI Expectations

- Coverage thresholds identical to other services (100% for touched code).
- Security scanners run against dependencies (`trivy`, `pip-audit`).
- Publish SQL logs for failing integration tests to aid diagnosis.

## Related Documents

- `docs/atomic/testing/integration-testing/database-testing.md`
- `docs/atomic/services/data-services/http-api-design.md`
- Legacy reference: `docs/legacy/architecture/data-access-rules.mdc`
