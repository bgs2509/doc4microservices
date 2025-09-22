# Service Implementation Examples and Patterns

This section contains comprehensive, production-ready code examples demonstrating the implementation of various service types and architectural patterns following the **"Improved Hybrid Approach"** architecture. All examples implement patterns from `docs/` rules and include:

- **RFC 7807 Error Handling**: Standardized problem details responses
- **Request Tracking**: Correlation ID and request ID middleware
- **Security Best Practices**: Proper password hashing, JWT authentication
- **Real Testing**: Testcontainers integration for database testing
- **Pagination & Filtering**: Complete data access patterns
- **Observability**: Structured logging and tracing integration

## Architecture Overview

Examples demonstrate the two-tier service architecture:

1. **Data Services**: Centralized database access with HTTP APIs (`db_postgres_service`, `db_mongo_service`)
2. **Business Services**: HTTP-only data access with business logic (`api_service`, `bot_service`, `worker_service`)

All examples follow the principles defined in [`../guides/ARCHITECTURE_GUIDE.md`](../guides/ARCHITECTURE_GUIDE.md) and implement patterns from [`../INDEX.md`](../INDEX.md).

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