# Testing Strategies

AsyncIO workers require rigorous tests to prevent regressions in long-running processes.

## Unit Tests

- Test task functions in isolation using fakes for Redis/RabbitMQ.
- Use `pytest.mark.asyncio` and manually create event loops where needed.
- Mock time/clock functions when testing retries or backoff.

```python
@pytest.mark.asyncio
async def test_process_photo_retries_on_recoverable_error(fake_deps, photo_consumer):
    fake_deps.rabbitmq.raise_on_publish(RecoverableError())

    await photo_consumer.handle_message(fake_message, request_id="req-123")

    assert fake_message.nacked
```

## Integration Tests

- Launch Testcontainers for RabbitMQ/Redis, run consumer logic against real queues.
- Trigger stop events to ensure graceful shutdown path is covered.
- Verify that messages are acknowledged or requeued as expected.

## End-to-End Tests

- Optional but valuable: run workers together with producers in staging, send real events, and assert downstream effects (database writes, HTTP callbacks).

## CI Expectations

- Workers share the same CI pipeline as other services: linting, typing, tests, security scans.
- Coverage thresholds apply; critical paths must be 100% covered.
- Publish logs from integration tests for debugging intermittent failures.

## Related Documents

- `docs/atomic/testing/service-testing/asyncio-testing-patterns.md`
- `docs/atomic/services/asyncio-workers/error-handling.md`
- Legacy reference: `docs/legacy/services/asyncio_rules.mdc`
