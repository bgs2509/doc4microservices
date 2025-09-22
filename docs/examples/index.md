# Service Implementation Examples and Patterns

This section contains a comprehensive set of practical code examples demonstrating the implementation of various service types and architectural patterns in accordance with the **"Improved Hybrid Approach"** principle.

## Example Architecture

Examples are divided into two service types:

1.  **Data Service**: Responsible for direct database interaction and provides HTTP API for data access.
2.  **Business Services**: Implement business logic and access data exclusively through HTTP calls to Data Services.

---

## Core Service Examples

- **[PostgreSQL Data Service Example](./postgres_data_service.md)**: Implementation of a service that encapsulates all PostgreSQL interaction logic, including models, repositories, and migrations.

- **[FastAPI Business Service Example](./fastapi_service.md)**: FastAPI API implementation that uses Data Services for operations and has no direct database access.

- **[Aiogram Business Service Example](./aiogram_service.md)**: Ready-to-use Telegram bot that follows the architecture and works with data through HTTP.

- **[Worker Business Service Example](./worker_service.md)**: Asynchronous worker for background tasks, interacting with other services via HTTP and message broker.

## Architectural Patterns and Practices

- **[Authentication and Authorization in Business Service](./authentication.md)**: JWT authentication implementation example adapted for service separation architecture.

- **[Inter-Service Communication Patterns](./communication_patterns.md)**: Examples of synchronous (REST) and asynchronous (event-driven) communication.

- **[Resilience Patterns](./resilience_patterns.md)**: Implementation of patterns such as Dead-Letter Queue and Circuit Breaker.

- **[Observability](./observability.md)**: Practical examples of structured logging, tracing, and metrics collection.

- **[Testing Strategies](./testing_strategies.md)**: Examples of writing unit and integration tests for all service types.