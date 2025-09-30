# Documentation Index

The documentation is organised into atomic knowledge modules with a dedicated legacy archive. Use this index as the entry point for the authoritative materials.

## Quick Navigation

| Need | Go To |
|------|-------|
| Understand architecture | [Improved Hybrid Overview](atomic/architecture/improved-hybrid-overview.md) |
| Implement a FastAPI service | [FastAPI Basic Setup](atomic/services/fastapi/basic-setup.md) |
| Configure integrations | [Redis Connection Management](atomic/integrations/redis/connection-management.md) |
| Prepare infrastructure | [PostgreSQL Setup](atomic/infrastructure/databases/postgresql-setup.md) |
| Set up observability | [Structured Logging Patterns](atomic/observability/logging/structured-logging.md) |
| Align testing strategy | [Pytest Setup](atomic/testing/unit-testing/pytest-setup.md) |
| Reference legacy rules | [Legacy Documentation Archive](legacy/README.md) |

## Documentation Pillars

### Core Guides
- [Architecture Guide](LINKS_REFERENCE.md#core-documentation) — canonical architectural principles
- [Development Commands](LINKS_REFERENCE.md#developer-guides) — command reference for local workflows
- [Use Case Implementation Guide](LINKS_REFERENCE.md#developer-guides) — step-by-step delivery process
- [Agent Workflow](guides/AGENT_WORKFLOW.md) — end-to-end agent operating model

### Reference Materials
- [Technical Specifications](LINKS_REFERENCE.md#core-documentation) — platform versions and runtime constraints
- [Troubleshooting Guide](LINKS_REFERENCE.md#developer-guides) — diagnostics and recovery procedures
- [Agent Context Summary](reference/AGENT_CONTEXT_SUMMARY.md) — onboarding context for AI agents
- [Agent Toolbox](reference/AGENT_TOOLBOX.md) — machine-friendly command catalogue
- [Deliverables Catalog](reference/DELIVERABLES_CATALOG.md) — artefact ownership and storage rules
- [Prompt Templates](reference/PROMPT_TEMPLATES.md) — reusable communication templates
- [Architecture Decision Log Template](reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md) — ADR format and conventions
- [Framework Improvement Roadmap](development/FRAMEWORK_IMPROVEMENT_ROADMAP.md) — platform evolution backlog

### Agent Templates & Checklists
- [Prompt Validation Guide](guides/PROMPT_VALIDATION_GUIDE.md) — pre-work validation checklist
- [Requirements Intake Template](guides/REQUIREMENTS_INTAKE_TEMPLATE.md) — capturing functional and non-functional needs
- [Implementation Plan Template](guides/IMPLEMENTATION_PLAN_TEMPLATE.md) — planning artefact for approvals
- [Agent Verification Checklist](quality/AGENT_VERIFICATION_CHECKLIST.md) — release quality gates
- [QA Report Template](quality/QA_REPORT_TEMPLATE.md) — final QA handoff format

## Atomic Knowledge Base

See [Atomic Documentation Hub](atomic/README.md) for contribution rules.

### Architecture

- [Improved Hybrid Approach Overview](atomic/architecture/improved-hybrid-overview.md) — High-level view of the improved hybrid service model.
- [Service Separation Principles](atomic/architecture/service-separation-principles.md) — Guidelines for splitting responsibilities across services.
- [Event Loop Management](atomic/architecture/event-loop-management.md) — Ownership, lifecycle, and orchestration rules for event loops.
- [Data Access Architecture](atomic/architecture/data-access-architecture.md) — Patterns for safe data access and service boundaries.
- [DDD and Hexagonal Principles](atomic/architecture/ddd-hexagonal-principles.md) — DDD layering and hexagonal architecture applications.
- [Naming Conventions](atomic/architecture/naming-conventions.md) — Mandatory naming standards for code and infrastructure.
- [Quality Standards](atomic/architecture/quality-standards.md) — Quality bar, verification steps, and acceptance criteria.
- [Project Structure Patterns](atomic/architecture/project-structure-patterns.md) — Reference microservice and repository structures.

### Services

#### FastAPI

- [FastAPI Basic Setup](atomic/services/fastapi/basic-setup.md) — Baseline FastAPI service bootstrap.
- [FastAPI Application Factory](atomic/services/fastapi/application-factory.md) — App factory pattern and lifecycle.
- [FastAPI Lifespan Management](atomic/services/fastapi/lifespan-management.md) — Startup and shutdown handling.
- [FastAPI Routing Patterns](atomic/services/fastapi/routing-patterns.md) — Routing structure and API design.
- [FastAPI Dependency Injection](atomic/services/fastapi/dependency-injection.md) — DI patterns and container usage.
- [FastAPI Schema Validation](atomic/services/fastapi/schema-validation.md) — Pydantic schema patterns.
- [FastAPI Error Handling](atomic/services/fastapi/error-handling.md) — HTTP error handling strategies.
- [FastAPI Security Patterns](atomic/services/fastapi/security-patterns.md) — Authentication and authorization approaches.
- [FastAPI OpenAPI Documentation](atomic/services/fastapi/openapi-documentation.md) — OpenAPI customization and docs.
- [FastAPI Performance Optimization](atomic/services/fastapi/performance-optimization.md) — Performance tuning and profiling.
- [FastAPI Testing Strategies](atomic/services/fastapi/testing-strategies.md) — Testing guidance for FastAPI services.

#### Aiogram

- [Aiogram Basic Setup](atomic/services/aiogram/basic-setup.md) — Baseline Aiogram bot configuration.
- [Aiogram Bot Initialization](atomic/services/aiogram/bot-initialization.md) — Bot and dispatcher initialization.
- [Aiogram Handler Patterns](atomic/services/aiogram/handler-patterns.md) — Message and callback handler structure.
- [Aiogram Middleware Setup](atomic/services/aiogram/middleware-setup.md) — Middleware registration and ordering.
- [Aiogram State Management](atomic/services/aiogram/state-management.md) — Finite state machine usage.
- [Aiogram Dependency Injection](atomic/services/aiogram/dependency-injection.md) — DI patterns for Aiogram.
- [Aiogram Webhook Configuration](atomic/services/aiogram/webhook-configuration.md) — Webhook versus polling configuration.
- [Aiogram Testing Strategies](atomic/services/aiogram/testing-strategies.md) — Testing approaches for bots.

#### AsyncIO Workers

- [AsyncIO Worker Basic Setup](atomic/services/asyncio-workers/basic-setup.md) — Baseline AsyncIO worker bootstrap.
- [AsyncIO Main Function Patterns](atomic/services/asyncio-workers/main-function-patterns.md) — Patterns for worker entrypoints.
- [AsyncIO Signal Handling](atomic/services/asyncio-workers/signal-handling.md) — Graceful shutdown and signal processing.
- [AsyncIO Task Management](atomic/services/asyncio-workers/task-management.md) — Task orchestration and supervision.
- [AsyncIO Dependency Management](atomic/services/asyncio-workers/dependency-management.md) — Dependency wiring and context.
- [AsyncIO Worker Error Handling](atomic/services/asyncio-workers/error-handling.md) — Failure handling and retries.
- [AsyncIO Worker Testing Strategies](atomic/services/asyncio-workers/testing-strategies.md) — Testing async workers.

#### Data Services

- [PostgreSQL Service Setup](atomic/services/data-services/postgres-service-setup.md) — PostgreSQL-focused data service setup.
- [MongoDB Service Setup](atomic/services/data-services/mongo-service-setup.md) — MongoDB-focused data service setup.
- [Data Service Repository Patterns](atomic/services/data-services/repository-patterns.md) — Repository implementations and patterns.
- [Data Service HTTP API Design](atomic/services/data-services/http-api-design.md) — Designing HTTP APIs for data services.
- [Data Service Transaction Management](atomic/services/data-services/transaction-management.md) — Transaction and consistency guidance.
- [Data Service Testing Strategies](atomic/services/data-services/testing-strategies.md) — Testing data service behaviour.

### Integrations

#### Redis

- [Redis Connection Management](atomic/integrations/redis/connection-management.md) — Connection pooling and clients.
- [Redis Key Naming Conventions](atomic/integrations/redis/key-naming-conventions.md) — Key naming standards.
- [Redis Data Serialization](atomic/integrations/redis/data-serialization.md) — Serialization practices.
- [Redis Idempotency Patterns](atomic/integrations/redis/idempotency-patterns.md) — Idempotency with Redis.
- [Redis Caching Strategies](atomic/integrations/redis/caching-strategies.md) — Caching patterns and TTL guidance.
- [Redis and FastAPI Integration](atomic/integrations/redis/fastapi-integration.md) — FastAPI + Redis patterns.
- [Redis and Aiogram Integration](atomic/integrations/redis/aiogram-integration.md) — Aiogram + Redis integration.
- [Redis and AsyncIO Integration](atomic/integrations/redis/asyncio-integration.md) — Redis usage from workers.
- [Redis Testing Patterns](atomic/integrations/redis/testing-patterns.md) — Testing Redis interactions.

#### RabbitMQ

- [RabbitMQ Connection Management](atomic/integrations/rabbitmq/connection-management.md) — Connection and channel handling.
- [RabbitMQ Exchange and Queue Declaration](atomic/integrations/rabbitmq/exchange-queue-declaration.md) — Exchange/queue setup patterns.
- [RabbitMQ Message Publishing](atomic/integrations/rabbitmq/message-publishing.md) — Publishing strategies and confirmations.
- [RabbitMQ Message Consuming](atomic/integrations/rabbitmq/message-consuming.md) — Consumer patterns and ack flow.
- [RabbitMQ DTO Contracts](atomic/integrations/rabbitmq/dto-contracts.md) — Message DTO and schema rules.
- [RabbitMQ Error Handling](atomic/integrations/rabbitmq/error-handling.md) — Error handling and dead letters.
- [RabbitMQ Idempotency Patterns](atomic/integrations/rabbitmq/idempotency-patterns.md) — Idempotency strategies for messaging.
- [RabbitMQ and FastAPI Integration](atomic/integrations/rabbitmq/fastapi-integration.md) — FastAPI integration patterns.
- [RabbitMQ and Aiogram Integration](atomic/integrations/rabbitmq/aiogram-integration.md) — Aiogram integration patterns.
- [RabbitMQ and AsyncIO Integration](atomic/integrations/rabbitmq/asyncio-integration.md) — Worker integration patterns.
- [RabbitMQ Testing Patterns](atomic/integrations/rabbitmq/testing-patterns.md) — Testing messaging workflows.

#### HTTP Communication

- [Business to Data Service Calls](atomic/integrations/http-communication/business-to-data-calls.md) — Business → data service HTTP patterns.
- [HTTP Client Patterns](atomic/integrations/http-communication/http-client-patterns.md) — HTTP client configuration and reuse.
- [HTTP Error Handling Strategies](atomic/integrations/http-communication/error-handling-strategies.md) — Resilience for HTTP clients.
- [HTTP Timeout and Retry Patterns](atomic/integrations/http-communication/timeout-retry-patterns.md) — Timeouts, retries, and circuit breakers.
- [HTTP Request Tracing](atomic/integrations/http-communication/request-tracing.md) — Request ID propagation.
- [HTTP Integration Testing](atomic/integrations/http-communication/testing-http-integration.md) — Testing cross-service HTTP flows.

#### Cross-Service

- [Cross-Service Discovery](atomic/integrations/cross-service/service-discovery.md) — Service discovery approaches.
- [Cross-Service Health Checks](atomic/integrations/cross-service/health-checks.md) — Health check patterns.
- [Cross-Service Graceful Shutdown](atomic/integrations/cross-service/graceful-shutdown.md) — Coordinated shutdown across services.
- [Cross-Service Distributed Tracing](atomic/integrations/cross-service/distributed-tracing.md) — Cross-service trace correlation.

### Security
- [Authentication Guide](atomic/security/authentication-guide.md) — Core authentication patterns and flows.
- [Authorization Patterns](atomic/security/authorization-patterns.md) — RBAC, ABAC, and policy enforcement strategies.

### File Storage & Media
- [File Upload Patterns](atomic/file-storage/upload-patterns.md) — Validation, scanning, and multi-storage flows.
- [Cloud Storage Integration](atomic/file-storage/cloud-integration.md) — Provider-agnostic storage adapters.
- [Media Processing Workflows](atomic/file-storage/media-processing.md) — Transcoding, optimization, and pipelines.
- [CDN Integration](atomic/file-storage/cdn-integration.md) — Edge delivery and cache invalidation patterns.

### External Integrations
- [Payment Gateway Integration](atomic/external-integrations/payment-gateways.md) — PCI-safe payment flows and reconciliation.
- [Communication APIs](atomic/external-integrations/communication-apis.md) — Email, SMS, and voice integration patterns.
- [Webhook Handling](atomic/external-integrations/webhook-handling.md) — Secure inbound webhook processing.
- [API Rate Limiting](atomic/external-integrations/api-rate-limiting.md) — Protection against API overuse.

### Real-time Communication
- [WebSocket Patterns](atomic/real-time/websocket-patterns.md) — Connection lifecycle, scaling, and security.
- [Server-Sent Events](atomic/real-time/sse-implementation.md) — Streaming updates with SSE.
- [Push Notifications](atomic/real-time/push-notifications.md) — Device messaging workflows.
- [Real-Time Synchronization Patterns](atomic/real-time/real-time-sync-patterns.md) — Conflict-free data sync strategies.

### Infrastructure

#### API Gateway

- [Nginx Setup and Configuration](atomic/infrastructure/api-gateway/nginx-setup.md) — Basic nginx setup as API Gateway.
- [Nginx Routing Patterns](atomic/infrastructure/api-gateway/routing-patterns.md) — Advanced routing strategies for microservices.
- [Nginx Security Hardening](atomic/infrastructure/api-gateway/security-hardening.md) — Security best practices, rate limiting, and DDoS protection.
- [Nginx SSL Configuration](atomic/infrastructure/api-gateway/ssl-configuration.md) — HTTPS setup and certificate management.

#### Databases

- [Database PostgreSQL Setup](atomic/infrastructure/databases/postgresql-setup.md) — PostgreSQL configuration and tuning.
- [Database MongoDB Setup](atomic/infrastructure/databases/mongodb-setup.md) — MongoDB configuration and tuning.
- [Database Connection Pooling](atomic/infrastructure/databases/connection-pooling.md) — Pooling strategies.
- [Database Migrations](atomic/infrastructure/databases/migrations.md) — Migration tooling and workflows.
- [Database Performance Optimization](atomic/infrastructure/databases/performance-optimization.md) — Performance troubleshooting.

#### Containerization

- [Dockerfile Patterns](atomic/infrastructure/containerization/dockerfile-patterns.md) — Dockerfile best practices.
- [Docker Compose Setup](atomic/infrastructure/containerization/docker-compose-setup.md) — Compose configuration standards.
- [Container Networking](atomic/infrastructure/containerization/container-networking.md) — Networking patterns for containers.
- [Container Volume Management](atomic/infrastructure/containerization/volume-management.md) — Volume usage and persistence.
- [Multi-Stage Builds](atomic/infrastructure/containerization/multi-stage-builds.md) — Multi-stage Docker build patterns.

#### Configuration

- [Environment Variables Management](atomic/infrastructure/configuration/environment-variables.md) — Managing environment variables.
- [Secrets Management](atomic/infrastructure/configuration/secrets-management.md) — Secrets storage and rotation.
- [Settings Patterns](atomic/infrastructure/configuration/settings-patterns.md) — Application settings organization.
- [Configuration Validation](atomic/infrastructure/configuration/configuration-validation.md) — Validating configuration at startup.

#### Deployment

- [Production Deployment](atomic/infrastructure/deployment/production-deployment.md) — Deploying to production.
- [Development Environment Setup](atomic/infrastructure/deployment/development-environment.md) — Local development environment.
- [CI/CD Patterns](atomic/infrastructure/deployment/ci-cd-patterns.md) — CI/CD pipeline guidance.
- [Deployment Monitoring Setup](atomic/infrastructure/deployment/monitoring-setup.md) — Monitoring deployed services.

### Observability

#### Logging

- [Structured Logging Patterns](atomic/observability/logging/structured-logging.md) — Structured logging guidelines.
- [Request ID Tracking](atomic/observability/logging/request-id-tracking.md) — Request ID and correlation IDs.
- [Log Correlation](atomic/observability/logging/log-correlation.md) — Correlating log events.
- [Log Formatting Standards](atomic/observability/logging/log-formatting.md) — Log formatting rules.
- [Sensitive Data Handling](atomic/observability/logging/sensitive-data-handling.md) — Protecting sensitive data in logs.
- [Centralized Logging](atomic/observability/logging/centralized-logging.md) — Centralized log aggregation.

#### Metrics

- [Prometheus Setup](atomic/observability/metrics/prometheus-setup.md) — Prometheus configuration.
- [Service-Level Metrics](atomic/observability/metrics/service-metrics.md) — Service-level metric expectations.
- [Golden Signals Implementation](atomic/observability/metrics/golden-signals.md) — Measuring and monitoring golden signals.
- [Custom Metrics Patterns](atomic/observability/metrics/custom-metrics.md) — Creating custom metrics.
- [Monitoring Dashboards](atomic/observability/metrics/dashboards.md) — Grafana and dashboard practices.

#### Tracing

- [OpenTelemetry Setup](atomic/observability/tracing/opentelemetry-setup.md) — Setting up OpenTelemetry.
- [Distributed Tracing](atomic/observability/tracing/distributed-tracing.md) — Distributed tracing strategy.
- [Jaeger Configuration](atomic/observability/tracing/jaeger-configuration.md) — Configuring Jaeger.
- [Trace Correlation](atomic/observability/tracing/trace-correlation.md) — Correlating traces across services.
- [Tracing for Performance Monitoring](atomic/observability/tracing/performance-monitoring.md) — Tracing performance diagnostics.

#### Error Tracking

- [Sentry Integration](atomic/observability/error-tracking/sentry-integration.md) — Integrating Sentry.
- [Error Grouping Strategies](atomic/observability/error-tracking/error-grouping.md) — Grouping and triaging errors.
- [Error Alerting Patterns](atomic/observability/error-tracking/alerting-patterns.md) — Alerting best practices.

#### ELK Stack

- [Elasticsearch Setup](atomic/observability/elk-stack/elasticsearch-setup.md) — Configuring Elasticsearch.
- [Logstash Configuration](atomic/observability/elk-stack/logstash-configuration.md) — Configuring Logstash.
- [Kibana Dashboards](atomic/observability/elk-stack/kibana-dashboards.md) — Kibana dashboard practices.
- [Filebeat Setup](atomic/observability/elk-stack/filebeat-setup.md) — Configuring Filebeat.

### Testing

#### Unit Testing

- [Pytest Setup](atomic/testing/unit-testing/pytest-setup.md) — Pytest configuration and conventions.
- [Test Fixture Patterns](atomic/testing/unit-testing/fixture-patterns.md) — Fixture organization.
- [Mocking Strategies](atomic/testing/unit-testing/mocking-strategies.md) — Mocking guidance.
- [Parametrized Tests](atomic/testing/unit-testing/parametrized-tests.md) — Using parametrized tests.
- [Coverage Requirements](atomic/testing/unit-testing/coverage-requirements.md) — Coverage targets and reporting.

#### Integration Testing

- [Testcontainers Setup](atomic/testing/integration-testing/testcontainers-setup.md) — Testcontainers usage.
- [Database Integration Testing](atomic/testing/integration-testing/database-testing.md) — Database integration testing.
- [Redis Integration Testing](atomic/testing/integration-testing/redis-testing.md) — Redis integration tests.
- [RabbitMQ Integration Testing](atomic/testing/integration-testing/rabbitmq-testing.md) — RabbitMQ integration tests.
- [HTTP Integration Testing](atomic/testing/integration-testing/http-integration-testing.md) — HTTP integration validation.

#### Service Testing

- [FastAPI Service Testing Patterns](atomic/testing/service-testing/fastapi-testing-patterns.md) — Testing FastAPI services.
- [Aiogram Service Testing Patterns](atomic/testing/service-testing/aiogram-testing-patterns.md) — Testing Aiogram bots.
- [AsyncIO Service Testing Patterns](atomic/testing/service-testing/asyncio-testing-patterns.md) — Testing async workers.
- [Data Service Testing Patterns](atomic/testing/service-testing/data-service-testing.md) — Testing data services.

#### End-to-End Testing

- [End-to-End Test Setup](atomic/testing/end-to-end-testing/e2e-test-setup.md) — E2E infrastructure setup.
- [User Journey Testing](atomic/testing/end-to-end-testing/user-journey-testing.md) — User journey test design.
- [End-to-End Performance Testing](atomic/testing/end-to-end-testing/performance-testing.md) — Performance testing guidance.

#### Quality Assurance

- [Linting Standards](atomic/testing/quality-assurance/linting-standards.md) — Static analysis and linting.
- [Type Checking](atomic/testing/quality-assurance/type-checking.md) — Type checking setup.
- [Security Testing](atomic/testing/quality-assurance/security-testing.md) — Security testing guidance.
- [Code Review Checklist](atomic/testing/quality-assurance/code-review-checklist.md) — Checklist for reviews.

## Legacy Archive

Historical `.mdc` sources are preserved for traceability. Reference them only for context; new guidance must be captured in the atomic knowledge base.

- [Architecture — Data Access Rules](legacy/architecture/data-access-rules.mdc)
- [Architecture — Microservices Best Practices](legacy/architecture/ms_best_practices_rules.mdc)
- [Architecture — Naming Conventions](legacy/architecture/naming_conventions.mdc)
- [Services — FastAPI Rules](legacy/services/fastapi_rules.mdc)
- [Services — Aiogram Rules](legacy/services/aiogram_rules.mdc)
- [Services — AsyncIO Rules](legacy/services/asyncio_rules.mdc)
- [Infrastructure — Redis Rules](legacy/infrastructure/redis_rules.mdc)
- [Infrastructure — RabbitMQ Rules](legacy/infrastructure/rabbitmq_rules.mdc)
- [Infrastructure — MongoDB Rules](legacy/infrastructure/mongodb_rules.mdc)
- [Observability — Logging Rules](legacy/observability/logging_rules.mdc)
- [Observability — Metrics Rules](legacy/observability/metrics_rules.mdc)
- [Observability — Tracing Rules](legacy/observability/tracing_rules.mdc)
- [Observability — ELK Rules](legacy/observability/elk_rules.mdc)
- [Observability — General Rules](legacy/observability/observability_rules.mdc)
- [Quality — Testing Standards](legacy/quality/testing-standards.mdc)

## Maintenance

- Add new guidance to the appropriate `docs/atomic/` module and keep files atomic in scope.
- Update this index whenever a new atomic topic is created or archived.
- Archive superseded `.mdc` materials in `docs/legacy/` without modification for audit purposes.
- Validate internal links as part of CI to avoid regressions in navigation.
