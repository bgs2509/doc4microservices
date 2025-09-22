# Technology Stack

> **🔧 CANONICAL TECHNOLOGY REFERENCE**: This document is the single source of truth for all technology versions, configurations, and specifications used in the project. All other documentation references this file.

> **📖 Related Documentation**: For development guidance, see [../../CLAUDE.md](../../CLAUDE.md). For service-specific patterns, see [../INDEX.md](../INDEX.md) (architecture/, services/, infrastructure/, observability/, quality/). For complete working examples, see [service-examples.md](service-examples.md). For troubleshooting, see [troubleshooting.md](troubleshooting.md).

## Table of Contents
- [Architecture](#architecture)
- [Service Types and Event Loop Separation](#service-types-and-event-loop-separation)
- [Version Control and Tools](#version-control-and-tools)
- [Asynchronous Frameworks](#asynchronous-frameworks)
- [Microservices and Infrastructure](#microservices-and-infrastructure)
- [Observability and Monitoring](#observability-and-monitoring)
- [Servers and Deployment](#servers-and-deployment)
- [Asynchronous Libraries](#asynchronous-libraries)
- [Implementation Guidelines](#implementation-guidelines)

---

## Architecture

### Architectural Patterns
- **Technology**: DDD/Hexagonal architecture, Test Driven Design
- **Comment**: DDD/Hex works well with FastAPI, SQLAlchemy repositories and queues (RabbitMQ), isolating domain from infrastructure. Suitable for asynchronous code (port/adapter separation), Python 3.12+ compatible. Compatible with other libraries (Pydantic v2, Uvicorn, Alembic), simplifies testing (pytest-asyncio, testcontainers) and scaling in Docker Compose.
- **Detailed implementation**: See `../architecture/ms_best_practices_rules.mdc` for complete DDD/Hex architecture guide.

---

## Architecture Overview

> **📖 ARCHITECTURE**: For complete architectural guidelines, see [ARCHITECTURE_GUIDE.md](../guides/ARCHITECTURE_GUIDE.md). This section provides technology-specific implementation details.

### Improved Hybrid Approach - Technology Implementation

The project implements the **Improved Hybrid Approach** with centralized data services. For architectural principles and rules, see the [canonical architecture documentation](../guides/ARCHITECTURE_GUIDE.md).

#### Technology Stack Summary
- **Data Services**: FastAPI + SQLAlchemy 2.x (PostgreSQL) / Motor (MongoDB)
- **Business Services**: FastAPI + httpx for HTTP-only data access
- **Communication**: RabbitMQ for events, HTTP for data access
- **Runtime**: Python 3.12+ unified across all services

---

## Service Types and Event Loop Separation

### Critical Architecture Constraints
- **MANDATORY**: Each service type must run in separate processes/containers to avoid event loop conflicts
- **PROHIBITED**: Running FastAPI and Aiogram in the same process - this creates conflicting event loop claims
- **MANDATORY**: Use RabbitMQ or other message brokers for communication between different service types

### Microservice Types and Technologies

#### HTTP API Services
- **Technology**: FastAPI + Uvicorn
- **Event Loop**: Managed by FastAPI/Uvicorn
- **Integration**: Redis and RabbitMQ via dependency injection
- **Process**: Separate container/process
- **Guide**: See `../services/fastapi_rules.mdc`

#### Telegram Bot Services
- **Technology**: Aiogram
- **Event Loop**: Managed by Aiogram via `asyncio.run(dp.start_polling(bot))`
- **Integration**: Redis and RabbitMQ via dependency injection in Dispatcher
- **Process**: Separate container/process
- **Guide**: See `../services/aiogram_rules.mdc`

#### Background Worker Services
- **Technology**: AsyncIO + aio-pika + redis.asyncio
- **Event Loop**: `asyncio.run(main())` in separate process
- **Integration**: Direct use of async libraries
- **Process**: Separate container/process
- **Guide**: See `../services/asyncio_rules.mdc`

### Inter-service Communication
- **Synchronous**: HTTP API between services (FastAPI ↔ FastAPI)
- **Asynchronous**: RabbitMQ events between all service types
- **Caching**: Redis for all service types (idempotency, cache, sessions)
- **Tracing**: Request ID and OpenTelemetry trace propagation

---

## Version Control and Tools

### Version Control System
- **Technology**: Git
- **Comment**: Standard for code management and CI/CD. Fully compatible with any stack and workflows, independent of sync/async and Python version. Fits perfectly into microservice development and GitOps.

### Package Manager
- **Technology**: UV
- **Comment**: Fast environment/dependency manager. Compatible with Python 3.12+, works with Docker and CI pipeline, supports reproducible builds (lock files). No conflicts with FastAPI/SQLAlchemy/Pydantic.

### Linter
- **Technology**: Ruff
- **Libraries**: ruff>=0.1.0
- **Comment**: Ruff provides fast PEP8/style and formatting. Compatible with Python 3.12+, async-independent. Works well in CI and doesn't conflict with other libraries.

- **Technology**: Bandit
- **Libraries**: bandit>=1.8.0
- **Comment**: Bandit performs static security analysis. Compatible with Python 3.12+, async-independent. Complements Ruff, integrates easily into CI/CD.

### Type Annotation Checking
- **Technology**: Mypy
- **Libraries**: mypy>=1.8.0
- **Comment**: Static type checking improves reliability. Compatible with Python 3.12+ and Pydantic v2 (via typed models), suitable for async code and entire used stack.

---

## Asynchronous Frameworks

### Async Library for REST API
- **Technology**: FastAPI
- **Libraries**: fastapi>=0.115.0
- **Comment**: Native async/await, works excellently with Uvicorn, Pydantic v2, SQLAlchemy asyncio, Redis and RabbitMQ. Full compatibility with Python 3.12+ and DDD/Hex architecture (routers/services/repositories).

### Async Library for Telegram
- **Technology**: Aiogram
- **Libraries**: aiogram>=3.22.0
- **Comment**: Fully asynchronous, compatible with Python 3.12+. Integrates well with Redis (cache/FSM), RabbitMQ (background processing) and FastAPI (webhooks). Fits DDD/Hex via bot adapters.

### Async Framework
- **Technology**: AsyncIO
- **Libraries**: asyncio
- **Comment**: Base event loop for entire stack. Full compatibility with Python 3.12+, used by Uvicorn, httpx, aio-pika, aiogram and others. Foundation of async architecture.

### LLM Framework
- **Technology**: LangChain
- **Libraries**: langchain>=0.2.11, langchain-core>=0.2.22, langchain-openai>=0.2.5
- **Comment**: Supports integrations with OpenAI and ChromaDB, has async API. Compatible with Python 3.12+, applicable as separate domain module (DDD) and adapter to LLM providers.

### Async Code Testing
- **Technology**: Pytest-asyncio
- **Libraries**: pytest>=8.3.0, pytest-asyncio>=0.24.0, pytest-cov>=6.0.0, testcontainers>=4.8.0
- **Comment**: Provides async tests and coverage. Compatible with Python 3.12+. Testcontainers allows spinning up real PostgreSQL/Redis/RabbitMQ/ChromaDB for integration tests.

### ORM (Object-Relational Mapping)
- **Technology**: SQLAlchemy
- **Libraries**: sqlalchemy[asyncio]>=2.0.36
- **Comment**: Native asyncio support in 2.x branch. Compatible with Python 3.12+, asyncpg, Alembic and DDD (repositories/unit of work). Works well in UoW patterns.

### SQLAlchemy Migrations
- **Technology**: Alembic
- **Libraries**: alembic>=1.13.2
- **Comment**: De-facto migration standard, compatible with SQLAlchemy 2.x and Python 3.12+. Suitable for microservices (separate schemas/DBs) and CI/CD.

### AI Providers
- **Technologies**: OpenAI, OpenRouter
- **Libraries**: openai>=1.0.0
- **Comment**: Compatible with Python 3.12+, supports async client. Integrates with LangChain and used via ENV/secrets configuration. Works in Docker/Compose.

---

## Microservices and Infrastructure

### Application Containerization
- **Technology**: Docker
- **Image/Version**: Docker version 27.0.0+, base image: python:3.12-slim
- **Comment**: Foundation for service packaging. Base image with Python 3.12 compatible with entire stack. Supports multi-layer builds, caching, healthchecks and network isolation.

### Container Orchestration
- **Technology**: Docker Compose
- **Version**: v2.29.0+
- **Comment**: Describes multi-service environment (Postgres, Redis, RabbitMQ, ChromaDB, ELK, Prometheus/Grafana, Nginx). Compatible with async services and dependencies.

### Web Server
- **Technology**: Nginx
- **Image**: nginx:1.26.1
- **Comment**: Reverse proxy and static files. Compatible with Uvicorn/Gunicorn, TLS/HTTP2, rate limiting. Integrates well with Prometheus exporters and ELK logging.

### Python Interpreter
- **Technology**: Python
- **Version**: 3.12+ (STANDARD for all services)
- **Image**: python:3.12-slim (builder stage)
- **Comment**: Single version for all microservices. Compatible with all libraries, optimal for slim builds. Supports async/await, Pydantic v2, SQLAlchemy 2.x etc. All services MUST use Python 3.12+.

### Relational Database
- **Technology**: PostgreSQL
- **Image**: postgres:16
- **Comment**: Primary relational database for structured data, transactions, and business entities. Accessed ONLY via db_postgres_service in the Improved Hybrid Approach. Supports complex queries, joins, and ACID transactions.
- **Integration**: Business services access PostgreSQL data via HTTP calls to db_postgres_service (Port: 8001).
- **Use Cases**: Users, products, orders, payments, structured business data requiring transactions.

### PostgreSQL Driver
- **Technology**: asyncpg
- **Libraries**: asyncpg>=0.30.0
- **Comment**: Used ONLY in db_postgres_service for direct database access. Native asyncio driver with superior performance. Fully compatible with SQLAlchemy 2.x, Python 3.12+. Business services MUST NOT use asyncpg directly - use HTTP client instead.

### Message Broker
- **Technology**: RabbitMQ
- **Image**: rabbitmq:3.13-management
- **Comment**: Critical component for inter-service communication. MANDATORY for communication between different service types (FastAPI ↔ Aiogram ↔ AsyncIO). Ensures reliable event delivery and service decoupling.
- **Integration**:
  - FastAPI: via `app.state.rabbitmq` and dependency injection
  - Aiogram: via `dp.startup.register()` and dependency injection
  - AsyncIO: via global client in `main()` function
- **Detailed implementation**: See `../infrastructure/rabbitmq_rules.mdc`

### RabbitMQ Driver
- **Technology**: aio-pika (ONLY async version)
- **Libraries**: aio-pika>=9.5.0
- **Comment**: Only acceptable client for async services. Mandatory use of `connect_robust()` for reliability. Key requirements: Request ID in headers (`x-request-id`), Pydantic DTOs for validation, idempotency via Redis.
- **CRITICAL**: CANNOT create separate event loops when using with FastAPI/Aiogram.
- **PROHIBITED**: Using synchronous `pika` library in async services.

### NoSQL Database
- **Technology**: MongoDB
- **Image**: mongo:7.0.9
- **Comment**: Document-oriented storage for analytics, user behavior, and flexible schemas. Accessed ONLY via db_mongo_service in the Improved Hybrid Approach. Supports aggregation pipelines and real-time analytics.
- **Integration**: Business services access MongoDB data via HTTP calls to db_mongo_service (Port: 8002).
- **Use Cases**: Analytics events, user behavior tracking, application logs, flexible document storage.

### MongoDB Driver
- **Technology**: Motor
- **Libraries**: motor==3.5.0 (async library)
- **Comment**: Used ONLY in db_mongo_service for direct database access. Fully async driver over pymongo, compatible with Python 3.12+. Business services MUST NOT use Motor directly - use HTTP client instead.

### Cache and Idempotency
- **Technology**: Redis
- **Image**: redis:7-alpine
- **Comment**: In-memory cache/sessions/locks/idempotency. Critical for avoiding operation duplication between services. Integrates via dependency injection in all service types.
- **Integration**:
  - FastAPI: via `app.state.redis` and dependency injection
  - Aiogram: via `dp.startup.register()` and dependency injection
  - AsyncIO: via global client in `main()` function
- **Detailed implementation**: See `../infrastructure/redis_rules.mdc`

### Redis Driver
- **Technology**: redis.asyncio
- **Libraries**: redis>=5.0.1
- **Comment**: Only acceptable client for all async services. Connection pooling via `from_url()`. Key patterns: idempotency via `SETNX`, unified key naming (`context:entity:id`), Request ID integration.
- **CRITICAL**: CANNOT create separate event loops when using with FastAPI/Aiogram.

### RAG Database
- **Technology**: ChromaDB
- **Image**: chromadb/chroma:0.5.0
- **Comment**: Vector storage for RAG. Used as HTTP API; compatible with LangChain and Python 3.12+. For async applications used via httpx.

### ChromaDB Driver
- **Technology**: chromadb
- **Libraries**: chromadb==0.5.0
- **Comment**: Client for ChromaDB. Synchronous API, in async applications used via httpx or thread pools. Combines with LangChain.

### Log Database
- **Technology**: Elasticsearch
- **Image**: docker.elastic.co/elasticsearch/elasticsearch:8.15.0
- **Comment**: Log search and analytics. Updated to v8.x for security support. Compatible with Logstash/Kibana and Python clients, deployed in Compose.

### Elasticsearch Driver
- **Technology**: elasticsearch-async
- **Libraries**: elasticsearch>=8.15.0
- **Comment**: Updated to ES8 with async support, compatible with Python 3.12. Integrates with FastAPI for logging/search.

### Log Collector
- **Technology**: Logstash
- **Image**: docker.elastic.co/logstash/logstash:8.15.0
- **Comment**: Log ingestion/enrichment/routing. Compatible with Elasticsearch/Kibana and container environment; easily connects to Nginx and applications.

### Log Dashboard
- **Technology**: Kibana
- **Image**: docker.elastic.co/kibana/kibana:8.15.0
- **Comment**: Log and metrics visualization. Compatible with Elasticsearch 8.x, deployed in Compose, integrates with SSO/Reverse proxy.

### Metrics
- **Technology**: Prometheus
- **Image**: prom/prometheus:v2.53.0
- **Comment**: Service and infrastructure metrics collection. Integrates with Python `prometheus_client`, Nginx exporters and Grafana. Compatible with Docker Compose.

### Prometheus Driver
- **Technology**: prometheus_client
- **Libraries**: prometheus_client>=0.20.0
- **Comment**: Metrics export from FastAPI/Uvicorn. Compatible with Python 3.12 and async applications (metric endpoints/middleware), displayed in Grafana.

### Dashboards
- **Technology**: Grafana
- **Image**: grafana/grafana:11.2.0
- **Comment**: Universal metrics/logs dashboards. Integration with Prometheus/Elasticsearch, deployment in Compose, compatible with rest of stack.

### Error Tracker
- **Technology**: Sentry
- **Image**: sentry/sentry:24.10.0
- **Comment**: Error monitoring/tracing. SDK compatible with FastAPI/ASGI and Python 3.12+. Easily integrates with Docker and CI/CD.

### Sentry Driver
- **Technology**: sentry-sdk
- **Libraries**: sentry-sdk>=2.11.0
- **Comment**: ASGI middleware support, logging integration. Compatible with Python 3.12+ and other dependencies; no conflicts with Prometheus/ELK.

---

## Observability and Monitoring

### Metrics Collection and Visualization
- **Technology**: Prometheus + Grafana
- **Image**: prom/prometheus:v2.53.0, grafana/grafana:11.2.0
- **Libraries**: prometheus_client>=0.20.0
- **Comment**: Complete metrics collection using Golden Signals methodology. Prometheus scrapes metrics from all services, Grafana provides visualization and alerting. Integrates with existing Request ID system from `logging_rules.mdc`.
- **Detailed implementation**: See `../observability/metrics_rules.mdc` for service-specific patterns.

### Distributed Tracing
- **Technology**: Jaeger + OpenTelemetry
- **Image**: jaegertracing/all-in-one:1.50
- **Libraries**: opentelemetry-api>=1.21.0, opentelemetry-sdk>=1.21.0, opentelemetry-instrumentation-fastapi>=0.42b0
- **Comment**: End-to-end request tracing across microservices. Builds on existing OpenTelemetry setup in `logging_rules.mdc`. Automatic correlation with Request ID system for complete observability.
- **Detailed implementation**: See `../observability/tracing_rules.mdc` for comprehensive setup.

### Log Aggregation and Analysis
- **Technology**: ELK Stack (Elasticsearch + Logstash + Kibana + Filebeat)
- **Image**: docker.elastic.co/elasticsearch/elasticsearch:8.15.0, docker.elastic.co/logstash/logstash:8.15.0, docker.elastic.co/kibana/kibana:8.15.0, docker.elastic.co/beats/filebeat:8.15.0
- **Comment**: Centralized log aggregation and analysis. Enhances existing structured logging from `logging_rules.mdc` with powerful search, visualization, and alerting capabilities. Replaces Loki+Promtail approach for better complex log analysis.
- **Detailed implementation**: See `../observability/elk_rules.mdc` for complete ELK setup.

### Error Tracking and Performance Monitoring
- **Technology**: Sentry
- **Image**: sentry/sentry:24.10.0
- **Libraries**: sentry-sdk>=2.11.0
- **Comment**: Application error tracking with automatic grouping, performance monitoring, and release tracking. ASGI middleware support for FastAPI integration. Compatible with existing logging and tracing systems.
- **Integration**: Correlates with Request ID and trace context from existing observability foundation.

### Infrastructure Monitoring
- **Technology**: Exporters (PostgreSQL, Redis, RabbitMQ, Node)
- **Images**: Various community exporters
- **Comment**: Infrastructure-level metrics for databases, message brokers, and system resources. Integrates with Prometheus for unified monitoring and alerting.

### Comprehensive Observability Strategy
- **Foundation**: Builds on excellent `logging_rules.mdc` with Request ID correlation
- **Four Pillars**: Logs (ELK), Metrics (Prometheus), Traces (Jaeger), Errors (Sentry)
- **Integration**: Unified Request ID correlation across all observability data
- **Deployment**: Docker Compose integration with existing infrastructure
- **Detailed architecture**: See `../observability/observability_rules.mdc` for complete strategy

---

## Servers and Deployment

### WSGI Server
- **Technology**: Gunicorn
- **Libraries/Version**: gunicorn==23.0.0
- **Comment**: Used as process manager with Uvicorn workers (`uvicorn.workers.UvicornWorker`). Compatible with Python 3.12+ and containers.

### ASGI Server
- **Technology**: Uvicorn
- **Libraries**: uvicorn>=0.30.0
- **Comment**: High-performance ASGI server, fully async. Compatible with FastAPI, Python 3.12+, Prometheus metrics and Nginx as frontend.

### Deployment
- **Technology**: VPS
- **Comment**: Deployment via Docker Compose on VPS. Compatible with reverse-proxy Nginx, TLS, monitoring (Prometheus/Grafana) and logging (ELK).

---

## Asynchronous Libraries

### Async Photo Compression
- **Technology**: Pillow
- **Libraries**: Pillow>=11.3.0
- **Comment**: Synchronous library; in async code runs in thread pools. Compatible with Python 3.12+ and containers.

### Async HTTP Requests
- **Technology**: httpx
- **Libraries**: httpx>=0.27.0
- **Comment**: Native async client, supports timeouts/retries. Compatible with Python 3.12+, FastAPI, Sentry, Prometheus and Nginx proxy.

### High-Performance JSON
- **Technology**: orjson
- **Libraries**: orjson>=3.9.0
- **Comment**: Very fast serializer, compatible with Python 3.12+. Integrates with Pydantic v2 and FastAPI for response acceleration.

### Data Validation
- **Technology**: Pydantic
- **Libraries**: pydantic>=2.6.3
- **Comment**: Validation/schemas, foundation for FastAPI. Full compatibility with Python 3.12+, dataclass/typing support and high-performance in v2.

### Settings Management
- **Technology**: pydantic-settings
- **Libraries**: pydantic-settings>=2.10.1
- **Comment**: Configuration loading from ENV/files. Compatible with Python 3.12+, works with Docker/Compose and secrets.

### UUIDv6 Generation
- **Technology**: uuid6
- **Libraries**: uuid6>=0.6.0
- **Comment**: Time-ordered UUID (v6) generation for DB/logs. Compatible with Python 3.12+ and PostgreSQL, async-independent.

### Async File Operations
- **Technology**: aiofiles
- **Libraries**: aiofiles>=24.1.0
- **Comment**: Async file I/O. Compatible with Python 3.12+ and FastAPI (file upload/serve), works well under Uvicorn.

### Async Web Framework/Client
- **Technology**: aiohttp
- **Libraries**: aiohttp>=3.9.0
- **Comment**: Async HTTP server/client. Compatible with Python 3.12+, alternative to httpx/Starlette stack; can be used as adapter in DDD.

---

## Implementation Guidelines

### Cursor Rules (Mandatory Study)

This technology stack must be implemented according to detailed guides in docs root categories (architecture/, services/, infrastructure/, observability/, quality/). These rules contain specific patterns, requirements and code examples.

#### Core Architecture Rules
- **`../architecture/ms_best_practices_rules.mdc`** - Main guide for microservice architecture, DDD/Hex patterns, project structure and quality requirements
- **`../quality/testing-standards.mdc`** - Testing standards with mandatory 100% coverage for critical paths

#### Service Type Rules
- **`../services/fastapi_rules.mdc`** - Detailed rules for HTTP API services on FastAPI
- **`../services/aiogram_rules.mdc`** - Standards for Telegram Bot services on Aiogram
- **`../services/asyncio_rules.mdc`** - Rules for Background Worker services on AsyncIO

#### Infrastructure Rules
- **`../observability/logging_rules.mdc`** - Unified logging standard with Request ID tracing
- **`../infrastructure/redis_rules.mdc`** - Redis patterns for caching and idempotency
- **`../infrastructure/rabbitmq_rules.mdc`** - RabbitMQ standards for inter-service communication

### Critical Implementation Principles

#### 1. Event Loop Separation
- Each service type (FastAPI, Aiogram, AsyncIO) MUST run in separate process
- PROHIBITED to mix FastAPI and Aiogram in same process
- Use RabbitMQ for communication between service types

#### 2. Dependency Injection Patterns
- **FastAPI**: `app.state.redis`, `app.state.rabbitmq` + dependency injection
- **Aiogram**: `dp.startup.register()` + dependency injection in handlers
- **AsyncIO**: global clients in `main()` + pass as arguments

#### 3. Tracing and Idempotency
- Request ID MUST be generated and passed through all services
- Redis MUST be used for idempotency checking
- All operations MUST be idempotent

#### 4. Testing
- 100% coverage for critical paths
- Use testcontainers for integration tests
- Real databases instead of mocks in integration tests

### Development Commands Reference

> **📋 COMMANDS**: For all development commands, see the [canonical command reference in DEVELOPMENT_COMMANDS.md](../guides/DEVELOPMENT_COMMANDS.md). This includes Docker, testing, linting, and deployment commands.

### Working Examples Reference

For comprehensive, working implementations of all service types with real-world scenarios:
- **FastAPI Service**: Complete user management API with authentication, caching, and events
- **Aiogram Bot**: Media processing bot with file handling and RabbitMQ integration
- **AsyncIO Worker**: Background processing with retry logic and status tracking
- **Inter-Service Communication**: HTTP API calls and event-driven patterns
- **Testing Examples**: Unit, integration, and end-to-end testing patterns

See [service-examples.md](service-examples.md) for detailed implementations.

### Troubleshooting Reference

For common issues and solutions including:
- Development environment setup problems
- Docker and service connectivity issues
- Event loop and async conflicts
- Database and migration problems
- Observability stack configuration

See [troubleshooting.md](troubleshooting.md) for diagnostic steps and solutions.

### Project Structure (Current Implementation)

**Status**: ✅ Implemented - Infrastructure and service framework complete

```
try_microservices/                    # Root project directory
├── docker-compose.yml               # ✅ Main orchestration with full stack
├── docker-compose.override.yml      # ✅ Development overrides (auto-loaded)
├── docker-compose.prod.yml          # ✅ Production configuration
├── .env.example                     # ✅ Environment configuration template
├── services/                        # ✅ All microservices (framework ready)
│   ├── api_service/                 # ✅ FastAPI service (placeholder ready)
│   │   ├── Dockerfile               # ✅ Production-ready container
│   │   ├── pyproject.toml           # ✅ Dependencies configured
│   │   └── src/main.py              # ✅ Basic FastAPI app + health check
│   ├── bot_service/                 # ✅ Aiogram service (placeholder ready)
│   │   ├── Dockerfile               # ✅ Production-ready container
│   │   └── src/main.py              # ✅ Basic asyncio framework
│   └── worker_service/              # ✅ AsyncIO workers (placeholder ready)
│       ├── Dockerfile               # ✅ Production-ready container
│       └── src/main.py              # ✅ Basic worker framework
├── infrastructure/                  # ✅ Infrastructure configurations
│   ├── nginx/nginx.conf             # ✅ API routing configuration
│   ├── postgres/init.sql            # ✅ Database initialization
│   └── observability/              # ✅ Complete observability stack
│       ├── prometheus/              # ✅ Metrics collection
│       ├── grafana/                 # ✅ Dashboards and visualization
│       ├── elk/                     # ✅ Log aggregation (ELK stack)
│       └── jaeger/                  # ✅ Distributed tracing
├── docs/                            # ✅ Complete rule set (15 files) in architecture/, services/, infrastructure/, observability/, quality/
├── docs/tech_stack.md               # ✅ Technology specifications
├── CLAUDE.md                        # ✅ Development guidance
└── logs/                            # ✅ Application logs directory
```

**Next Steps**: Implement business logic in services according to docs rule patterns (architecture/, services/, infrastructure/, observability/, quality/).

### Docker Compose Organization

#### RECOMMENDED: Single Root Compose File
- **Primary file**: `docker-compose.yml` in project root
- **Development overrides**: `docker-compose.override.yml` (auto-loaded)
- **Production config**: `docker-compose.prod.yml` (explicit)

#### Benefits of Root-Level Compose:
- **Shared Infrastructure**: All services share Redis, RabbitMQ, PostgreSQL, and observability stack
- **Inter-service Communication**: Proper Docker networks between services and monitoring
- **Dependency Management**: Correct startup order (infrastructure → observability → services)
- **Environment Consistency**: Unified environment variables and secrets
- **Simplified Development**: Single `docker-compose up` starts entire stack including monitoring

#### Deployment Commands:
See [CLAUDE.md](../CLAUDE.md#development-commands) for complete command reference including development, production, and observability operations.

### Compliance Verification

All implementations MUST comply with cursor rules. For verification:

1. Study relevant `../*/*.mdc` files
2. Follow code examples from rules
3. Use verification commands from each rule
4. Achieve 100% test coverage for critical paths

**IMPORTANT**: Cursor rules are the source of truth for implementation. In case of conflicts between tech_stack.md and cursor rules, cursor rules take priority.