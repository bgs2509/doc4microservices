# RabbitMQ Testing Patterns

Verify messaging behaviour using a mix of fakes and live brokers.

## Unit Tests

- Mock `aio_pika.Exchange.publish` to assert routing keys, headers, and payloads.
- Validate DTO serialization/deserialization without touching the broker.
- Confirm error handling chooses the correct ack/nack/reject path using `AsyncMock` messages.

## Integration Tests

- Start RabbitMQ with Testcontainers and declare exchanges/queues during setup.
- Publish messages and wait for consumers to process them; assert side effects (database writes, Redis keys, HTTP callbacks).
- Use explicit timeouts so tests fail fast when consumers stall.

## Failure Scenarios

- Stop the container mid-test to ensure reconnection logic resumes consumption.
- Publish malformed payloads to confirm they end up in dead-letter queues and alerts fire.

## Tooling

- Query the management API to inspect queue depth and confirm cleanup.
- Capture request IDs in logs to trace end-to-end flows across producers and consumers.

## Related Documents

- `docs/atomic/testing/integration-testing/rabbitmq-testing.md`
- `docs/atomic/integrations/rabbitmq/error-handling.md`
