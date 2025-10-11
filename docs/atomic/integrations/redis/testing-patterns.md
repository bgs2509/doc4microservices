# Redis Testing Patterns

Testing ensures Redis usage remains correct across services.

## Unit Tests

- Mock Redis client methods (`setnx`, `expire`, `get`) with `unittest.mock.AsyncMock`.
- Verify key naming helpers and TTL logic.
- Ensure serialization helpers handle edge cases such as timezone-aware datetimes.

## Integration Tests

- Launch Redis via Testcontainers for each test module.
- Reuse the event loop provided by `pytest-asyncio`; avoid nested `asyncio.run` calls.
- Assert behaviour under concurrency by issuing parallel commands with `asyncio.gather`.

## Failure Scenarios

- Stop the container mid-test to simulate connection loss and confirm the service retries or fails fast.
- Test idempotency collisions by issuing duplicate operations with the same key.

## Tooling

- Capture metrics/logs during integration tests to validate observability expectations.
- Lightweight fakes (for example, `fakeredis`) are acceptable for pure logic tests, but prefer real Redis for integration coverage.

## Related Documents

- `docs/atomic/testing/integration-testing/redis-testing.md`
- `docs/atomic/integrations/redis/idempotency-patterns.md`
