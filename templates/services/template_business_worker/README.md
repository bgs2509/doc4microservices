# AsyncIO Worker Service Template

**Status**: 🚧 In Development
**Purpose**: Background task processing with AsyncIO and RabbitMQ

## Overview

This template provides an AsyncIO-based background worker service for processing tasks asynchronously through RabbitMQ message queues.

## Key Features

- Pure AsyncIO implementation
- RabbitMQ consumer with aio-pika
- Task retry logic with exponential backoff
- Dead letter queue handling
- Graceful shutdown handling
- HTTP calls to data services
- Structured logging with correlation IDs
- Health check endpoint

## Architecture Compliance

Following the mandatory service separation:
- Runs as separate container/process
- Consumes messages from RabbitMQ
- Calls data services via HTTP only
- No direct database access
- Stateless processing

## Service Structure

```
template_business_worker/
├── src/
│   ├── main.py              # Worker entry point
│   ├── config.py            # Configuration
│   ├── worker.py            # Main worker class
│   ├── consumers/           # Message consumers
│   │   ├── base.py         # Base consumer class
│   │   └── task_consumer.py # Task-specific consumers
│   ├── processors/          # Business logic processors
│   │   └── task_processor.py
│   ├── clients/             # HTTP clients for data services
│   ├── utils/               # Utility functions
│   │   ├── retry.py        # Retry logic
│   │   └── logging.py      # Structured logging
│   └── health.py           # Health check server
├── tests/                   # Unit tests
├── Dockerfile               # Container definition
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Usage

When using this template:

1. **Rename the service**: Replace `template_business_worker` with your actual service name (e.g., `finance_lending_worker`)
2. **Configure RabbitMQ**: Set connection parameters and queues
3. **Define consumers**: Create message consumers for your queues
4. **Implement processors**: Add business logic for task processing
5. **Setup data access**: Configure HTTP clients for data services
6. **Handle errors**: Implement retry and dead letter strategies

## Example Consumer

```python
class TaskConsumer(BaseConsumer):
    async def process_message(self, message: IncomingMessage):
        async with message.process():
            try:
                # Parse message
                data = json.loads(message.body.decode())

                # Process task
                result = await self.processor.process(data)

                # Call data service
                await self.data_client.save_result(result)

                # Acknowledge message
                await message.ack()
            except Exception as e:
                # Retry or send to DLQ
                await self.handle_error(message, e)
```

## Environment Variables

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
QUEUE_NAME=task_queue
DLQ_NAME=task_dlq
DATA_SERVICE_URL=http://template_data_postgres_api:8001
MAX_RETRIES=3
RETRY_DELAY=5
LOG_LEVEL=INFO
HEALTH_CHECK_PORT=8003
```

## Queue Configuration

```yaml
Queues:
  - task_queue:
      durable: true
      arguments:
        x-dead-letter-exchange: dlx
        x-dead-letter-routing-key: task_dlq
        x-message-ttl: 3600000

  - task_dlq:
      durable: true
      arguments:
        x-message-ttl: 86400000
```

## Health Check

The worker exposes a simple HTTP health endpoint:
- `GET /health` - Returns 200 if worker is running
- `GET /ready` - Returns 200 if RabbitMQ connection is active

## Related Documentation

- [AsyncIO Workers](../../../docs/atomic/services/asyncio-workers/)
- [RabbitMQ Integration](../../../docs/atomic/integrations/rabbitmq/)
- [HTTP Communication](../../../docs/atomic/integrations/http-communication/)
- Error Handling Patterns - See framework documentation

---

**Note**: This is a template. Full implementation coming soon.