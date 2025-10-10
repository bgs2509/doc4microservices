# RabbitMQ Integration Testing

Test RabbitMQ message publishing, consumption, routing, and acknowledgment with real RabbitMQ containers to verify message delivery, queue behavior, and exchange routing logic. Integration tests catch serialization errors, routing misconfigurations, and acknowledgment issues that mocks cannot detect.

This document covers testing patterns for aio-pika async client, message publishing/consuming, exchange and queue declarations, routing patterns, and error handling. RabbitMQ integration tests ensure events are routed correctly and consumed reliably.

Real RabbitMQ testing validates that messages serialize correctly, exchanges route to proper queues, and consumers process messages without loss. These tests catch protocol-specific issues and confirm resilience under failure scenarios.

## Publishing and Consuming

```python
# tests/integration/test_rabbitmq.py
import pytest
import json
import aio_pika
from finance_lending_api.events.publisher import EventPublisher


@pytest.mark.integration
async def test_publish_and_consume_message(rabbitmq_channel):
    """Test basic message publishing and consumption."""
    # Declare queue
    queue = await rabbitmq_channel.declare_queue("test.events", auto_delete=True)

    # Publish message
    publisher = EventPublisher(rabbitmq_channel)
    await publisher.publish_user_created(user_id="user-123", email="test@example.com")

    # Consume message
    message = await queue.get(timeout=5)
    assert message is not None

    event_data = json.loads(message.body.decode())
    assert event_data["user_id"] == "user-123"
    assert event_data["email"] == "test@example.com"

    await message.ack()


@pytest.mark.integration
async def test_message_acknowledgment(rabbitmq_channel):
    """Test that unacknowledged messages are redelivered."""
    queue = await rabbitmq_channel.declare_queue("ack.test", auto_delete=True)

    # Publish message
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(body=b"test message"),
        routing_key="ack.test"
    )

    # Consume but don't acknowledge
    message1 = await queue.get(timeout=1)
    assert message1 is not None
    # Don't call message1.ack()

    # Close channel (simulates consumer crash)
    await rabbitmq_channel.close()

    # Reconnect
    from tests.conftest import rabbitmq_connection
    new_channel = await rabbitmq_connection.channel()
    new_queue = await new_channel.get_queue("ack.test")

    # Message redelivered
    message2 = await new_queue.get(timeout=1)
    assert message2 is not None
    assert message2.body == b"test message"
    assert message2.redelivered is True

    await message2.ack()
```

## Exchange and Routing

```python
@pytest.mark.integration
async def test_topic_exchange_routing(rabbitmq_channel):
    """Test topic-based message routing."""
    # Declare topic exchange
    exchange = await rabbitmq_channel.declare_exchange(
        "events",
        type=aio_pika.ExchangeType.TOPIC,
        auto_delete=True
    )

    # Bind queues with routing patterns
    user_queue = await rabbitmq_channel.declare_queue("user.events", auto_delete=True)
    await user_queue.bind(exchange, routing_key="user.*")

    loan_queue = await rabbitmq_channel.declare_queue("loan.events", auto_delete=True)
    await loan_queue.bind(exchange, routing_key="loan.*")

    # Publish user event
    await exchange.publish(
        aio_pika.Message(body=b'{"event": "user_created"}'),
        routing_key="user.created"
    )

    # User queue receives it
    user_message = await user_queue.get(timeout=1)
    assert user_message is not None
    await user_message.ack()

    # Loan queue is empty
    with pytest.raises(aio_pika.exceptions.QueueEmpty):
        await loan_queue.get(timeout=0.1, fail=True)


@pytest.mark.integration
async def test_fanout_exchange_broadcasts(rabbitmq_channel):
    """Test fanout exchange broadcasts to all queues."""
    # Declare fanout exchange
    exchange = await rabbitmq_channel.declare_exchange(
        "broadcast",
        type=aio_pika.ExchangeType.FANOUT,
        auto_delete=True
    )

    # Bind multiple queues
    queue1 = await rabbitmq_channel.declare_queue("listener1", auto_delete=True)
    await queue1.bind(exchange)

    queue2 = await rabbitmq_channel.declare_queue("listener2", auto_delete=True)
    await queue2.bind(exchange)

    # Publish message
    await exchange.publish(
        aio_pika.Message(body=b"broadcast message"),
        routing_key=""  # Ignored by fanout
    )

    # Both queues receive message
    msg1 = await queue1.get(timeout=1)
    msg2 = await queue2.get(timeout=1)

    assert msg1.body == b"broadcast message"
    assert msg2.body == b"broadcast message"

    await msg1.ack()
    await msg2.ack()
```

## Dead Letter Exchange

```python
@pytest.mark.integration
async def test_dead_letter_queue(rabbitmq_channel):
    """Test that rejected messages go to dead letter exchange."""
    # Declare dead letter exchange
    dlx = await rabbitmq_channel.declare_exchange(
        "dead_letters",
        type=aio_pika.ExchangeType.DIRECT,
        auto_delete=True
    )

    dlq = await rabbitmq_channel.declare_queue("dead_letter_queue", auto_delete=True)
    await dlq.bind(dlx, routing_key="failed")

    # Declare main queue with DLX
    main_queue = await rabbitmq_channel.declare_queue(
        "main_queue",
        auto_delete=True,
        arguments={
            "x-dead-letter-exchange": "dead_letters",
            "x-dead-letter-routing-key": "failed"
        }
    )

    # Publish message
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(body=b"will be rejected"),
        routing_key="main_queue"
    )

    # Consume and reject
    message = await main_queue.get(timeout=1)
    await message.reject(requeue=False)  # Send to DLX

    # Message appears in dead letter queue
    dl_message = await dlq.get(timeout=1)
    assert dl_message.body == b"will be rejected"
    await dl_message.ack()
```

## Consumer Testing

```python
@pytest.mark.integration
async def test_consumer_processes_messages(rabbitmq_channel):
    """Test consumer processes messages correctly."""
    from finance_lending_api.events.consumer import UserEventConsumer

    queue = await rabbitmq_channel.declare_queue("user.events", auto_delete=True)
    consumer = UserEventConsumer(rabbitmq_channel)

    processed = []

    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            event = json.loads(message.body.decode())
            processed.append(event)

    await queue.consume(on_message)

    # Publish test event
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps({"user_id": "123"}).encode()),
        routing_key="user.events"
    )

    # Wait for processing
    import asyncio
    await asyncio.sleep(0.5)

    assert len(processed) == 1
    assert processed[0]["user_id"] == "123"
```

## Checklist

- [ ] Test publishing and consuming messages
- [ ] Test message acknowledgment and redelivery
- [ ] Test exchange routing (direct, topic, fanout)
- [ ] Test dead letter exchanges
- [ ] Test queue bindings and routing keys
- [ ] Test consumer error handling
- [ ] Use testcontainers for real RabbitMQ
- [ ] Clean up queues and exchanges after tests
- [ ] Mark integration tests with `@pytest.mark.integration`

## Related Documents

- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Docker containers for tests
- `docs/atomic/integrations/rabbitmq/message-publishing.md` — RabbitMQ publishing patterns
- `docs/atomic/integrations/rabbitmq/message-consumption.md` — Consumer implementation
- `docs/atomic/integrations/rabbitmq/exchange-patterns.md` — Exchange types and routing
