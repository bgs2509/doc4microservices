# Service Implementation Examples and Patterns

> **📋 DOCUMENTATION TYPE**: Educational Examples - Teaching developers HOW to implement correctly
> **👥 TARGET USERS**: Human developers, teams, code reviewers
> **🔗 RELATED**: [AI Agents Framework](../../ai_agents/) *(or [.framework/ai_agents/](.framework/ai_agents/) when used as submodule)* | [Working Examples](../../use_cases/) *(or [.framework/use_cases/](.framework/use_cases/) when used as submodule)* | **[Complete Comparison Guide](../../CLAUDE.md#documentation-types-guide)**

This section contains comprehensive, production-ready code examples demonstrating the implementation of various service types and architectural patterns following the **"Improved Hybrid Approach"** architecture. All examples implement patterns from `docs/` *(or `.framework/docs/` when used as submodule)* rules and include:

- **RFC 7807 Error Handling**: Standardized problem details responses
- **Request Tracking**: Correlation ID and request ID middleware
- **Security Best Practices**: Proper password hashing, JWT authentication
- **Real Testing**: Testcontainers integration for database testing
- **Pagination & Filtering**: Complete data access patterns
- **Observability**: Structured logging and tracing integration

## Implementation Examples

Examples demonstrate the **Improved Hybrid Approach** with centralized data services and HTTP-only business logic communication.

> **📖 ARCHITECTURAL FOUNDATION**: All examples follow the principles defined in the [Architecture Guide](../docs/LINKS_REFERENCE.md#core-documentation) and implement patterns from the [IDE Rules & Patterns](../docs/LINKS_REFERENCE.md#ide-rules-and-patterns).

---

## Core Service Examples

### Data Services (Centralized Database Access)

- **[PostgreSQL Data Service Example](./postgres_data_service.md)**: Complete implementation of centralized PostgreSQL access service with SQLAlchemy 2.x, repositories, migrations, and HTTP API endpoints.
  - *Related*: [FastAPI Service Example](./fastapi_service.md#3-user-data-client) (HTTP client usage), [Shared HTTP Client](./shared_http_client.md) (client implementation)

- **[MongoDB Data Service Example](./mongodb_data_service.md)**: Comprehensive MongoDB data service with Motor driver, aggregation pipelines, analytics collections, and document validation.
  - *Related*: [Worker Service Example](./worker_service.md) (analytics tracking), [Shared HTTP Client](./shared_http_client.md#usage-examples) (client integration)

### Business Services (HTTP-Only Data Access)

- **[FastAPI Business Service Example](./fastapi_service.md)**: Complete FastAPI business service with HTTP-only data access, authentication, caching, event publishing, and proper middleware.
  - *Dependencies*: [PostgreSQL Data Service](./postgres_data_service.md), [MongoDB Data Service](./mongodb_data_service.md)
  - *Uses*: [Shared HTTP Client](./shared_http_client.md#usage-examples), [Comprehensive Testing](./comprehensive_testing.md#unit-testing-examples)

- **[Aiogram Business Service Example](./aiogram_service.md)**: Telegram bot implementation with HTTP data access, media processing, and RabbitMQ event publishing.
  - *Dependencies*: [PostgreSQL Data Service](./postgres_data_service.md#6-api-endpoints-srcapiv1userspy), [MongoDB Data Service](./mongodb_data_service.md#6-api-endpoints-srcapiv1analyticspy)
  - *Related*: [Worker Service Example](./worker_service.md) (media processing), [Communication Patterns](./communication_patterns.md) (event handling)

- **[Worker Business Service Example](./worker_service.md)**: AsyncIO background workers with HTTP data access, queue processing, and batch operations.
  - *Dependencies*: [MongoDB Data Service](./mongodb_data_service.md#5-analytics-repository) (analytics), [PostgreSQL Data Service](./postgres_data_service.md) (user data)
  - *Integrates*: [Shared HTTP Client](./shared_http_client.md), [Resilience Patterns](./resilience_patterns.md)

## Shared Infrastructure and Utilities

### HTTP Communication

- **[Shared HTTP Client Module](./shared_http_client.md)**: Enterprise-grade HTTP client with RFC 7807 error handling, circuit breakers, retry logic, and type safety.
  - *Used by*: [FastAPI Service](./fastapi_service.md#3-user-data-client), [Aiogram Service](./aiogram_service.md), [Worker Service](./worker_service.md)
  - *Testing*: [Comprehensive Testing](./comprehensive_testing.md#unit-testing-examples) (mocking patterns)

### Testing Framework

- **[Comprehensive Testing Examples](./comprehensive_testing.md)**: Complete testing suite with testcontainers, performance testing, E2E workflows, and mocking strategies.
  - *Tests*: All service examples above
  - *Patterns*: [Shared HTTP Client](./shared_http_client.md#testing-the-shared-client) testing, service integration testing

## Architectural Patterns and Practices

### Core Architecture Patterns

- **[Authentication and Authorization in Business Service](./authentication.md)**: JWT authentication implementation adapted for HTTP-only data access architecture.
  - *Implements*: [FastAPI Service](./fastapi_service.md) authentication patterns
  - *Uses*: [PostgreSQL Data Service](./postgres_data_service.md) for user verification

- **[Inter-Service Communication Patterns](./communication_patterns.md)**: Examples of HTTP synchronous and RabbitMQ asynchronous communication between services.
  - *Demonstrates*: [FastAPI](./fastapi_service.md) ↔ [Data Services](./postgres_data_service.md), [Aiogram](./aiogram_service.md) → [Worker](./worker_service.md) communication
  - *Uses*: [Shared HTTP Client](./shared_http_client.md) for reliable communication

- **[Resilience Patterns](./resilience_patterns.md)**: Circuit breakers, retries, timeouts, and graceful degradation patterns.
  - *Implemented in*: [Shared HTTP Client](./shared_http_client.md), all business services
  - *Tested in*: [Comprehensive Testing](./comprehensive_testing.md#end-to-end-testing-examples) (failure scenarios)

### Observability and Quality

- **[Observability](./observability.md)**: Structured logging, tracing, metrics collection, and request correlation across all services.
  - *Applied in*: All service examples
  - *Validated by*: [Comprehensive Testing](./comprehensive_testing.md#integration-testing-examples) (correlation testing)

- **[Comprehensive Testing Examples](./comprehensive_testing.md)**: Complete testing suite with testcontainers, performance testing, E2E workflows, and mocking strategies.
  - *Extended by*: [Comprehensive Testing](./comprehensive_testing.md)
  - *Applies to*: All service examples above

## Higher-Level Integration Examples

### Complete Use Case Implementation

- **[Use Case Integration Example](./use_case_integration.md)**: Complete guide for structuring and integrating use cases into the microservices architecture, demonstrating service coordination, data flow, and event-driven patterns.
  - *Demonstrates*: Integration of all service types working together
  - *References*: Task Management use case (`use_cases/task_management/` *or `.framework/use_cases/task_management/` when used as submodule*)
  - *Patterns*: Service isolation, HTTP-only data access, event-driven communication

### AI-Powered Development

- **[AI Agents Usage Example](./ai_agents_usage.md)**: Complete guide for using AI agents to automatically generate microservices from business requirements, including template-based code generation and quality validation.
  - *Utilizes*: Service templates in `ai_agents/generators/service_templates/` *(or `.framework/ai_agents/generators/service_templates/` when used as submodule)*
  - *Generates*: Production-ready service implementations
  - *Validates*: Architectural compliance and code quality

## Infrastructure and Operations

### Complete Infrastructure Stack

- **[Infrastructure Setup Example](./infrastructure_setup.md)**: Complete guide for setting up the full observability and infrastructure stack including PostgreSQL, MongoDB, Redis, RabbitMQ, Prometheus, Grafana, Jaeger, and ELK stack.
  - *Includes*: Docker Compose configurations, networking, security
  - *Supports*: All service examples and use cases
  - *Features*: Health checks, monitoring, logging aggregation

### Production Deployment

- **[Deployment Patterns Example](./deployment_patterns.md)**: Production-ready deployment strategies including blue-green deployment, rolling updates, canary releases, database migrations, and zero-downtime deployment.
  - *Covers*: Service versioning, database schema evolution, rollback procedures
  - *Implements*: Graceful shutdown, health check strategies
  - *Supports*: Production-grade reliability and availability

### Performance and Monitoring

- **[Performance Monitoring Example](./performance_monitoring.md)**: Comprehensive performance testing, monitoring setup, alerting, and optimization techniques including load testing, stress testing, and real-time monitoring.
  - *Features*: Custom metrics collection, Prometheus integration, alerting rules
  - *Includes*: Load testing frameworks, chaos engineering, capacity planning
  - *Validates*: SLA compliance and system performance