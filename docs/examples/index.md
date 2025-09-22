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

### Data Services (Centralized Database Access)

- **[PostgreSQL Data Service Example](./postgres_data_service.md)**: Complete implementation of centralized PostgreSQL access service with SQLAlchemy 2.x, repositories, migrations, and HTTP API endpoints.
  - *Related*: [FastAPI Service Example](./fastapi_service.md#4-user-data-client-srcclientsuser_data_clientpy) (HTTP client usage), [Shared HTTP Client](./shared_http_client.md) (client implementation)

- **[MongoDB Data Service Example](./mongodb_data_service.md)**: Comprehensive MongoDB data service with Motor driver, aggregation pipelines, analytics collections, and document validation.
  - *Related*: [Worker Service Example](./worker_service.md) (analytics tracking), [Shared HTTP Client](./shared_http_client.md#usage-examples) (client integration)

### Business Services (HTTP-Only Data Access)

- **[FastAPI Business Service Example](./fastapi_service.md)**: Complete FastAPI business service with HTTP-only data access, authentication, caching, event publishing, and proper middleware.
  - *Dependencies*: [PostgreSQL Data Service](./postgres_data_service.md), [MongoDB Data Service](./mongodb_data_service.md)
  - *Uses*: [Shared HTTP Client](./shared_http_client.md#1-fastapi-service-integration-api_servicesrcclientsdata_clientspy), [Comprehensive Testing](./comprehensive_testing.md#unit-testing-examples)

- **[Aiogram Business Service Example](./aiogram_service.md)**: Telegram bot implementation with HTTP data access, media processing, and RabbitMQ event publishing.
  - *Dependencies*: [PostgreSQL Data Service](./postgres_data_service.md#6-api-endpoints-srcapiv1userspy), [MongoDB Data Service](./mongodb_data_service.md#6-api-endpoints-srcapiv1analyticspy)
  - *Related*: [Worker Service Example](./worker_service.md) (media processing), [Communication Patterns](./communication_patterns.md) (event handling)

- **[Worker Business Service Example](./worker_service.md)**: AsyncIO background workers with HTTP data access, queue processing, and batch operations.
  - *Dependencies*: [MongoDB Data Service](./mongodb_data_service.md#5-analytics-repository) (analytics), [PostgreSQL Data Service](./postgres_data_service.md) (user data)
  - *Integrates*: [Shared HTTP Client](./shared_http_client.md), [Resilience Patterns](./resilience_patterns.md)

## Shared Infrastructure and Utilities

### HTTP Communication

- **[Shared HTTP Client Module](./shared_http_client.md)**: Enterprise-grade HTTP client with RFC 7807 error handling, circuit breakers, retry logic, and type safety.
  - *Used by*: [FastAPI Service](./fastapi_service.md#2-user-data-client), [Aiogram Service](./aiogram_service.md), [Worker Service](./worker_service.md)
  - *Testing*: [Comprehensive Testing](./comprehensive_testing.md#unit-testing-examples) (mocking patterns)

### Testing Framework

- **[Comprehensive Testing Examples](./comprehensive_testing.md)**: Complete testing suite with testcontainers, performance testing, E2E workflows, and mocking strategies.
  - *Tests*: All service examples above
  - *Patterns*: [Shared HTTP Client](./shared_http_client.md#testing-the-shared-client) testing, service integration testing

## Architectural Patterns and Practices

### Core Architecture Patterns

- **[Authentication and Authorization in Business Service](./authentication.md)**: JWT authentication implementation adapted for HTTP-only data access architecture.
  - *Implements*: [FastAPI Service](./fastapi_service.md#6-authentication-service) patterns
  - *Uses*: [PostgreSQL Data Service](./postgres_data_service.md) for user verification

- **[Inter-Service Communication Patterns](./communication_patterns.md)**: Examples of HTTP synchronous and RabbitMQ asynchronous communication between services.
  - *Demonstrates*: [FastAPI](./fastapi_service.md) ↔ [Data Services](./postgres_data_service.md), [Aiogram](./aiogram_service.md) → [Worker](./worker_service.md) communication
  - *Uses*: [Shared HTTP Client](./shared_http_client.md) for reliable communication

- **[Resilience Patterns](./resilience_patterns.md)**: Circuit breakers, retries, timeouts, and graceful degradation patterns.
  - *Implemented in*: [Shared HTTP Client](./shared_http_client.md#circuit-breaker-patterns), all business services
  - *Tested in*: [Comprehensive Testing](./comprehensive_testing.md#end-to-end-testing-examples) (failure scenarios)

### Observability and Quality

- **[Observability](./observability.md)**: Structured logging, tracing, metrics collection, and request correlation across all services.
  - *Applied in*: All service examples
  - *Validated by*: [Comprehensive Testing](./comprehensive_testing.md#integration-testing-examples) (correlation testing)

- **[Testing Strategies](./testing_strategies.md)**: Advanced testing patterns for microservices with real databases, HTTP mocking, and service interaction testing.
  - *Extended by*: [Comprehensive Testing](./comprehensive_testing.md)
  - *Applies to*: All service examples above