# PostgreSQL Data Service Template

**Status**: 🚧 In Development
**Purpose**: HTTP-only data access service for PostgreSQL database

## Overview

This template provides a FastAPI-based HTTP data service that exposes PostgreSQL database operations following the framework's Improved Hybrid Approach architecture.

## Key Features

- HTTP-only data access (no direct DB access from business services)
- RESTful CRUD operations
- Connection pooling with asyncpg
- Schema validation with Pydantic
- Health check endpoints
- Database migration support with Alembic

## Architecture Compliance

Following the mandatory Improved Hybrid Approach:
- Business services call this service via HTTP
- No direct database connections from business layer
- Stateless HTTP API design
- PostgreSQL as primary data store

## Service Structure

```
template_data_postgres_api/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── repositories/        # Data access layer
│   └── routers/             # API endpoints
├── migrations/              # Alembic migrations
├── tests/                   # Unit and integration tests
├── Dockerfile               # Container definition
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Usage

When using this template:

1. **Rename the service**: Replace `template_data_postgres_api` with your actual service name (e.g., `finance_data_postgres_api`)
2. **Configure database**: Update connection settings in config.py
3. **Define models**: Create SQLAlchemy models for your domain
4. **Create migrations**: Use Alembic to manage schema changes
5. **Implement repositories**: Add data access methods
6. **Define API endpoints**: Create routers for your entities

## Example Endpoints

- `GET /health` - Service health check
- `GET /ready` - Database readiness check
- `POST /{entity}` - Create entity
- `GET /{entity}/{id}` - Get entity by ID
- `PUT /{entity}/{id}` - Update entity
- `DELETE /{entity}/{id}` - Delete entity
- `GET /{entity}` - List entities with pagination

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname
SERVICE_PORT=8001
LOG_LEVEL=INFO
MAX_CONNECTIONS=20
```

## Related Documentation

- [Data Access Architecture](../../../docs/atomic/architecture/data-access-architecture.md)
- [PostgreSQL Patterns](../../../docs/atomic/databases/postgresql/)
- [HTTP Communication](../../../docs/atomic/integrations/http-communication/)

---

**Note**: This is a template. Full implementation coming soon.