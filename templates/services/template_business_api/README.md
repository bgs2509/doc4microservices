# FastAPI Business Service Template

**Status**: 🚧 In Development
**Purpose**: Business logic API service following the Improved Hybrid Approach

## Overview

This template provides a FastAPI-based business service that implements business logic, orchestrates data access via HTTP calls to data services, and publishes events to RabbitMQ.

## Key Features

- Business logic orchestration
- HTTP-only data access (calls data services via HTTP)
- Event publishing to RabbitMQ
- Redis for caching and idempotency
- RESTful API design with OpenAPI documentation
- Health check endpoints
- Dependency injection with dishka

## Architecture Compliance

Following the mandatory Improved Hybrid Approach:
- Business logic separated from data access
- HTTP calls to data services (no direct DB access)
- Event-driven communication via RabbitMQ
- Redis for cross-service state management
- Stateless API design

## Service Structure

```
template_business_api/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection setup
│   ├── services/            # Business logic services
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── clients/             # HTTP clients for data services
│   └── events/              # Event publishing logic
├── tests/                   # Unit and integration tests
├── Dockerfile               # Container definition
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Usage

When using this template:

1. **Rename the service**: Replace `template_business_api` with your actual service name (e.g., `finance_lending_api`)
2. **Configure integrations**: Update settings for Redis, RabbitMQ, and data services
3. **Define business entities**: Create Pydantic schemas for your domain
4. **Implement business logic**: Add service classes with business rules
5. **Create API endpoints**: Define routers for your use cases
6. **Set up event publishing**: Configure events for your domain

## Example Endpoints

- `GET /health` - Service health check
- `GET /ready` - Dependencies readiness check
- `POST /api/v1/{resource}` - Create resource (business logic)
- `GET /api/v1/{resource}/{id}` - Get resource with business rules applied
- `PUT /api/v1/{resource}/{id}` - Update with validation
- `DELETE /api/v1/{resource}/{id}` - Delete with business checks
- `POST /api/v1/{action}` - Execute business action

## Environment Variables

```env
SERVICE_PORT=8000
LOG_LEVEL=INFO

# Data service URLs
DATA_SERVICE_URL=http://data-postgres-api:8001

# Redis configuration
REDIS_URL=redis://redis:6379/0

# RabbitMQ configuration
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# API settings
API_TIMEOUT_SECONDS=30
MAX_RETRY_ATTEMPTS=3
```

## Dependencies

Key dependencies in requirements.txt:
- FastAPI for web framework
- dishka for dependency injection
- httpx for HTTP client
- aio-pika for RabbitMQ
- redis for caching
- pydantic for validation

## Related Documentation

- [Architecture Guide](../../../docs/guides/architecture-guide.md)
- [Business Service Patterns](../../../docs/atomic/services/fastapi/)
- [HTTP Communication](../../../docs/atomic/integrations/http-communication/)
- [Event Publishing](../../../docs/atomic/integrations/rabbitmq/)

---

**Note**: This is a template. Full implementation coming soon.