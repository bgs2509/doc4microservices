# Testing Strategies

FastAPI services must ship with comprehensive unit, integration, and contract tests that follow the global quality standards.

## Unit Tests

- Use `pytest` with `pytest-asyncio` for async endpoints.
- Mock external dependencies by overriding FastAPI dependencies (`app.dependency_overrides`).
- Focus on application services and domain logic; routers should simply orchestrate.

```python
@pytest.mark.asyncio
async def test_create_user_returns_201(fastapi_client, fake_user_service):
    fastapi_client.app.dependency_overrides[get_user_service] = lambda: fake_user_service

    response = await fastapi_client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "full_name": "Test", "password": "P@ssw0rd!!!!"},
    )

    assert response.status_code == 201
```

## Integration Tests

- Use Testcontainers to spin up PostgreSQL/MongoDB/Redis as required.
- Run tests against the real HTTP API using `httpx.AsyncClient` or `FastAPI AsyncClient`.
- Seed data via migrations or fixtures; clean up between tests.

## Contract Tests

- Snapshot the OpenAPI schema to detect breaking changes.
- Use consumer-driven contracts (e.g., Pact) when other teams depend on the API.

## Non-Functional Tests

- Execute load tests for critical paths, referencing `performance-optimization.md`.
- Add security tests (auth bypass attempts, rate limits) as part of service-specific suites.

## CI Expectations

- CI must run unit + integration suites, linting, type checks, and security scans.
- Coverage reports must meet the platform threshold (100% for new/changed lines).
- Publish test artefacts (coverage.xml, junit.xml) for visibility.

## Related Documents

- `docs/atomic/testing/integration-testing/http-integration-testing.md`
- `docs/atomic/architecture/quality-standards.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
