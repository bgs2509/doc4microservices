# Testing Strategies

Telegram bots require the same rigour as HTTP services. Cover handlers, integration with Telegram API, and messaging side effects.

## Unit Tests

- Use Aiogram's testing utilities (`aiogram.test`) or plain async tests with fakes.
- Call handlers directly with mocked `Message`/`CallbackQuery` objects.
- Provide fake Redis/RabbitMQ clients implementing the same interface.

```python
@pytest.mark.asyncio
async def test_handle_photo_publishes_event(fake_message, fake_redis, fake_rabbit, photo_service):
    await handle_photo(fake_message, rabbitmq=fake_rabbit, redis=fake_redis, service=photo_service)

    fake_rabbit.assert_published("photo.received")
```

## Integration Tests

- Use Testcontainers to start Redis and RabbitMQ.
- Spin up dispatcher via the real `build_lifespan` function and send synthetic updates.
- Verify published events, cached values, and Telegram responses (mock `Bot` HTTP calls).

## End-to-End Tests

- Optional but encouraged: send real updates via Telegram sandbox bots in staging.
- Ensure webhook endpoints respond with `200` quickly; tests should assert idempotency behaviour.

## CI Requirements

- Include bot tests in the standard pipeline (unit + integration).
- Validate that request ID middleware sets context for every update.
- Enforce coverage thresholds identical to API services.

## Related Documents

- `docs/atomic/testing/service-testing/aiogram-testing-patterns.md`
- `docs/atomic/architecture/quality-standards.md`
