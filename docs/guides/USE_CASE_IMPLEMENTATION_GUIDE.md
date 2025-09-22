# Complete Use Case Implementation Guide

This guide provides comprehensive instructions for creating production-ready use cases using the project's microservices architecture. All implementations must follow the established project patterns documented in [../../CLAUDE.md](../../CLAUDE.md) and comply with the mandatory naming conventions.

**CRITICAL**: This guide is specifically designed for the existing microservices architecture. For architectural details, see [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) and [../reference/tech_stack.md](../reference/tech_stack.md). For development commands, see [DEVELOPMENT_COMMANDS.md](DEVELOPMENT_COMMANDS.md).

## Table of Contents

- [Use Case Structure Requirements](#use-case-structure-requirements)
- [Essential File Checklist](#essential-file-checklist)
- [Implementation Phases](#implementation-phases)
- [File Templates and Examples](#file-templates-and-examples)
- [Testing Requirements](#testing-requirements)
- [Deployment and Production Checklist](#deployment-and-production-checklist)
- [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
- [Validation Checklist](#validation-checklist)

---

## ⚠️ MANDATORY ARCHITECTURE CONSTRAINTS

**Before implementing any use case, you MUST understand and comply with these non-negotiable constraints:**

> **⚠️ MANDATORY COMPLIANCE**: All constraints are defined in the [canonical architecture documentation](ARCHITECTURE_GUIDE.md). This section provides implementation-specific guidance.

### 1. **Architecture Compliance (MANDATORY)**
- **Foundation**: Follow the [Improved Hybrid Approach architecture](ARCHITECTURE_GUIDE.md)
- **Data Access**: HTTP-only communication with data services
- **Service Separation**: Each service type in separate containers

### 2. **Development Standards**
- **Commands**: Use [canonical development commands](DEVELOPMENT_COMMANDS.md)
- **Technology**: Follow [complete technology specifications](../reference/tech_stack.md)
- **Architecture**: Follow [comprehensive architecture guide](ARCHITECTURE_GUIDE.md)
- **Naming**: Follow [../architecture/naming_conventions.mdc](../architecture/naming_conventions.mdc)
- **Patterns**: See [../INDEX.md](../INDEX.md) for service-specific implementation patterns in services/, architecture/, infrastructure/, observability/, quality/

**Violation of these constraints will result in non-functional use cases. This guide provides compliant implementation patterns.**

---

## Use Case Structure Requirements

### Directory Organization

Every use case must follow this exact structure:

**CRITICAL**: Use cases integrate with existing root docker_compose.yml, do NOT create separate compose files.

```
use_cases/[use_case_name]/
├── README.md                          # ✅ REQUIRED: Complete documentation
├── service_definitions.yml            # ✅ REQUIRED: Service definitions to add to root compose
├── production_overrides.yml           # ✅ REQUIRED: Production config snippets
├── .env.example                       # ✅ REQUIRED: Environment template
├── .gitignore                         # ✅ REQUIRED: Version control exclusions
├── pyproject.toml                     # ✅ REQUIRED: Python dependencies
├── Makefile                           # ✅ REQUIRED: Development automation
├── shared_dtos.py                     # ✅ REQUIRED: Data transfer objects
├── [service_name]_service.py          # ✅ REQUIRED: Service implementations
├── Dockerfile.[service_name]          # ✅ REQUIRED: Build instructions per service
├── .dockerignore                      # ✅ REQUIRED: Docker build optimization
├── scripts/                           # ✅ REQUIRED: Automation scripts
│   ├── setup.sh                      # Environment setup
│   ├── test.sh                       # Testing automation
│   ├── deploy.sh                     # Deployment automation
│   └── cleanup.sh                    # Cleanup utilities
├── sql/                              # ✅ REQUIRED: Database schemas
│   ├── init_[usecase].sql            # PostgreSQL initialization
│   └── migrations/                   # Alembic migration files
├── mongodb/                          # ✅ REQUIRED: MongoDB setup
│   ├── init-mongo.js                 # Database initialization
│   └── collections/                  # Collection schemas
├── tests/                            # ✅ REQUIRED: Test suite
│   ├── unit/                         # Unit tests per service
│   ├── integration/                  # Integration tests
│   ├── load/                         # Performance tests
│   └── conftest.py                   # Test configuration
├── config/                           # ✅ REQUIRED: Configuration files
│   ├── prometheus/                   # Metrics configuration
│   ├── grafana/                      # Dashboard setup
│   ├── nginx/                        # Reverse proxy config
│   └── logging/                      # Log configuration
├── docs/                             # ✅ REQUIRED: Additional documentation
│   ├── api.md                        # API documentation
│   ├── deployment.md                 # Deployment guide
│   └── troubleshooting.md            # Common issues
└── examples/                         # ✅ REQUIRED: Usage examples
    ├── api_examples.sh               # API usage examples
    ├── bot_examples.md               # Bot command examples
    └── integration_examples.py       # Integration examples
```

---

## Essential File Checklist

### 🔴 CRITICAL FILES (Use Case Won't Work Without These)

#### 1. **Dockerfiles for Each Service**
```bash
# Required for each service type
Dockerfile.api          # FastAPI service build
Dockerfile.bot          # Aiogram service build
Dockerfile.worker       # AsyncIO worker build
Dockerfile.analytics    # Analytics worker build
```

**Template Structure:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN uv pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY [service_files] ./

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run service
CMD ["python", "[service_name]_service.py"]
```

#### 2. **Python Dependencies (pyproject.toml)**
```toml
[project]
name = "[use_case_name]"
version = "1.0.0"
description = "[Use case description]"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "aiogram>=3.22.0",
    "redis>=5.0.1",
    "aio-pika>=9.5.0",
    "httpx>=0.27.0",
    "pydantic>=2.6.3",
    "pydantic-settings>=2.10.1",
    "orjson>=3.9.0",
    "asyncpg>=0.30.0",
    "motor==3.5.0",
    "alembic>=1.13.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "testcontainers>=4.8.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "bandit>=1.8.0",
]

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.mypy]
python_version = "3.12"
strict = true
```

#### 3. **Database Initialization Scripts**

**PostgreSQL (sql/init_[usecase].sql):**
```sql
-- Create database schema for [use_case_name]
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Example table structure
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'todo',
    priority VARCHAR(50) DEFAULT 'medium',
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_users_email ON users(email);
```

**MongoDB (mongodb/init-mongo.js):**
```javascript
// Initialize MongoDB collections for [use_case_name]
db = db.getSiblingDB('[usecase]_analytics_db');

// Create collections
db.createCollection('task_activities');
db.createCollection('user_sessions');
db.createCollection('productivity_stats');

// Create indexes
db.task_activities.createIndex({ "user_id": 1, "timestamp": -1 });
db.task_activities.createIndex({ "task_id": 1 });
db.user_sessions.createIndex({ "user_id": 1 });
db.productivity_stats.createIndex({ "user_id": 1, "period_start": -1 });

// Insert sample data if needed
db.task_activities.insertOne({
    task_id: 0,
    user_id: 0,
    action: "system_init",
    timestamp: new Date(),
    metadata: { "initialized": true }
});
```

#### 4. **Environment Configuration (.env.example)**
```env
# Service Configuration
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@postgres:5432/[usecase]_db
MONGODB_URL=mongodb://mongo:mongo123@mongodb:27017/[usecase]_analytics_db?authSource=admin

# Cache and Message Broker
REDIS_URL=redis://:redis123@redis:6379/0
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/

# Data Services (Improved Hybrid Approach)
DB_POSTGRES_SERVICE_URL=http://db_postgres_service:8000
DB_MONGO_SERVICE_URL=http://db_mongo_service:8000

# Security
SECRET_KEY=your-secret-key-change-in-production-please
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services (if applicable)
BOT_TOKEN=your-telegram-bot-token-here
BOT_USERNAME=your_bot_username

# Performance Settings
MAX_ITEMS_PER_PAGE=50
BATCH_SIZE=100
MAX_CONCURRENT_PROCESSING=10

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

#### 5. **Production Configuration Integration**

**CRITICAL**: Do NOT create separate docker_compose files per use case. Instead, integrate with the existing root-level docker_compose.yml.

**Integration Approach:**
```yaml
# Add service definitions to existing root docker_compose.yml
services:
  [use_case_name]_api:
    build:
      context: ./use_cases/[use_case_name]
      dockerfile: Dockerfile.api
    environment:
      DEBUG: false
      LOG_LEVEL: WARNING
      # Use existing data service URLs
      DB_POSTGRES_SERVICE_URL: http://db_postgres_service:8000
      DB_MONGO_SERVICE_URL: http://db_mongo_service:8000
    depends_on:
      - db_postgres_service
      - db_mongo_service
      - redis
      - rabbitmq
    networks:
      - microservices_network
```

**Production Overrides (docker_compose.prod.yml):**
```yaml
# Only add production-specific overrides to existing docker_compose.prod.yml
version: '3.8'
services:
  [use_case_name]_api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      interval: 15s
      timeout: 5s
      retries: 5
```

### 🟡 IMPORTANT FILES (Needed for Production)

#### 6. **Testing Configuration (tests/conftest.py)**
```python
import pytest
import asyncio
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.compose import DockerCompose

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_database():
    """Setup test database."""
    with PostgresContainer("postgres:16") as postgres:
        connection_url = postgres.get_connection_url()
        # Initialize test data
        yield connection_url

@pytest.fixture(scope="session")
async def test_redis():
    """Setup test Redis."""
    with RedisContainer("redis:7-alpine") as redis:
        redis_url = redis.get_connection_url()
        yield redis_url
```

#### 7. **Development Automation (Makefile)**
```makefile
.PHONY: help setup test build deploy clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Complete development commands available in ../CLAUDE.md
setup: ## Setup development environment
	cp .env.example .env
	uv sync --dev

# For Docker commands, database operations, and testing - see ../CLAUDE.md
```

#### 8. **Monitoring Configuration (config/prometheus/prometheus.yml)**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: '[usecase]-api'
    static_configs:
      - targets: ['[usecase]_api_service:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: '[usecase]-workers'
    static_configs:
      - targets: ['[usecase]_worker_service:8000']
    metrics_path: /metrics
    scrape_interval: 30s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

---

## Implementation Phases

### Phase 1: Project Structure Setup (Day 1)
1. Create directory structure following the template above
2. Set up all required files with basic templates
3. Configure Docker and dependency management
4. Initialize Git repository with proper .gitignore

**Validation:**
```bash
# Directory structure exists
ls -la use_cases/[use_case_name]/
# Docker builds successfully
docker-compose build
# Dependencies install correctly
uv sync --dev
```

### Phase 2: Core Services Implementation (Days 2-3)
1. Implement FastAPI service with all endpoints
2. Implement Aiogram bot service (if applicable)
3. Implement AsyncIO worker services
4. Set up shared DTOs and event schemas

**Validation:**
```bash
# Services start without errors
docker-compose up -d
# Health checks pass
curl http://localhost:8000/health
# Basic API functionality works
curl -X POST http://localhost:8000/api/v1/[resource]
```

### Phase 3: Data Layer Integration (Day 4)
1. Create database schemas and migrations
2. Implement HTTP communication with data services
3. Set up Redis caching and RabbitMQ messaging
4. Test all data flows

**Validation:**
```bash
# Database schema created
docker-compose exec postgres psql -U postgres -d [usecase]_db -c "\dt"
# MongoDB collections exist
docker-compose exec mongodb mongosh [usecase]_analytics_db --eval "show collections"
# Redis connectivity works
docker-compose exec redis redis-cli ping
```

### Phase 4: Testing and Quality Assurance (Day 5)
1. Write comprehensive unit tests
2. Implement integration tests with real databases
3. Set up load testing
4. Configure code quality tools

**Validation:**
```bash
# All tests pass
make test
# Code quality checks pass
uv run ruff check . && uv run mypy . && uv run uv run bandit -r .
# Test coverage is adequate (>80%)
uv run pytest --cov=. --cov-report=term-missing
```

### Phase 5: Production Readiness (Day 6)
1. Set up monitoring and observability
2. Configure production deployment
3. Implement security measures
4. Create deployment documentation

**Validation:**
```bash
# Production deployment works
make deploy-prod
# Monitoring is functional
curl http://localhost:9090/metrics
# Security scan passes
uv run bandit -r .
```

---

## File Templates and Examples

### Service Implementation Template

Every service must implement these standard methods:

```python
"""
[Service Name] Service - [Framework] Implementation.

[Service description and key features]
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Framework-specific imports
from fastapi import FastAPI  # For API services
# OR from aiogram import Bot, Dispatcher  # For bot services

from shared_dtos import [Required DTOs]

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Service configuration."""
    # All configuration options with defaults
    pass

settings = Settings()

# Service implementation
class [ServiceName]Service:
    """Service layer for [functionality]."""

    def __init__(self, redis_client, rabbitmq_channel, ...):
        # Initialize dependencies
        pass

    async def [method_name](self, ...):
        """Method documentation."""
        # Implementation with error handling
        pass

# Framework setup (FastAPI example)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting [Service Name] Service")

    # Setup dependencies
    app.state.redis = redis.from_url(settings.REDIS_URL, ...)
    app.state.rabbitmq_connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, ...)

    # Test connections
    await app.state.redis.ping()
    logger.info("Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down [Service Name] Service")
    await app.state.redis.close()
    await app.state.rabbitmq_connection.close()

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="[Service Name] API",
        description="[Service description]",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add middleware and routes
    return app

app = create_app()

# Health check endpoint (MANDATORY)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "[service_name]"}

# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "[service_name]_service:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

### HTTP Data Client Template

Every business service MUST use HTTP clients to access data services:

```python
"""
HTTP Data Client for [Service Name] - Improved Hybrid Approach.

Provides HTTP-based access to data services following project architecture.
"""

from __future__ import annotations

import httpx
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DataServiceError(Exception):
    """Base exception for data service communication errors."""
    pass

class DataServiceTimeoutError(DataServiceError):
    """Exception for data service timeout errors."""
    pass

class PostgresDataClient:
    """HTTP client for PostgreSQL data service (db_postgres_service)."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    async def get_user(self, user_id: str, request_id: str) -> Optional[Dict[str, Any]]:
        """Get user from PostgreSQL via HTTP."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/{user_id}",
                    headers={"X-Request-ID": request_id},
                    timeout=self.timeout
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                logger.error(f"Timeout getting user {user_id}", extra={"request_id": request_id})
                raise DataServiceTimeoutError(f"User service timeout: {user_id}")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error getting user {user_id}: {e}", extra={"request_id": request_id})
                raise DataServiceError(f"User service error: {e.response.status_code}")

    async def create_user(self, user_data: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Create user via PostgreSQL HTTP API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/users",
                    json=user_data,
                    headers={"X-Request-ID": request_id},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                logger.error(f"Timeout creating user", extra={"request_id": request_id})
                raise DataServiceTimeoutError("User creation timeout")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error creating user: {e}", extra={"request_id": request_id})
                raise DataServiceError(f"User creation error: {e.response.status_code}")

class MongoDataClient:
    """HTTP client for MongoDB data service (db_mongo_service)."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    async def track_event(self, event_data: Dict[str, Any], request_id: str) -> str:
        """Track analytics event via MongoDB HTTP API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/events",
                    json=event_data,
                    headers={"X-Request-ID": request_id},
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()["id"]

            except httpx.TimeoutException:
                logger.error(f"Timeout tracking event", extra={"request_id": request_id})
                raise DataServiceTimeoutError("Event tracking timeout")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error tracking event: {e}", extra={"request_id": request_id})
                raise DataServiceError(f"Event tracking error: {e.response.status_code}")

    async def get_user_analytics(self, user_id: str, request_id: str) -> Dict[str, Any]:
        """Get user analytics via MongoDB HTTP API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/analytics/users/{user_id}",
                    headers={"X-Request-ID": request_id},
                    timeout=self.timeout
                )

                if response.status_code == 404:
                    return {}

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                logger.error(f"Timeout getting analytics for user {user_id}", extra={"request_id": request_id})
                raise DataServiceTimeoutError(f"Analytics service timeout: {user_id}")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error getting analytics: {e}", extra={"request_id": request_id})
                raise DataServiceError(f"Analytics service error: {e.response.status_code}")

# Dependency injection for FastAPI
async def get_postgres_client() -> PostgresDataClient:
    """Dependency injection for PostgreSQL data client."""
    from core.config import settings
    return PostgresDataClient(settings.DB_POSTGRES_SERVICE_URL)

async def get_mongo_client() -> MongoDataClient:
    """Dependency injection for MongoDB data client."""
    from core.config import settings
    return MongoDataClient(settings.DB_MONGO_SERVICE_URL)
```

### Test Template

```python
"""Tests for [Service Name] service."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from [service_name]_service import app

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_[functionality](test_database, test_redis):
    """Test core functionality."""
    # Implementation with real database testing
    pass

class TestIntegration:
    """Integration tests with external services."""

    @pytest.mark.asyncio
    async def test_service_communication(self):
        """Test communication between services."""
        # Test HTTP calls to data services
        pass
```

---

## Testing Requirements

### Mandatory Test Coverage

1. **Unit Tests (80%+ coverage required):**
   - All service methods
   - All API endpoints
   - Error handling scenarios
   - Data validation logic

2. **Integration Tests:**
   - HTTP communication with data services (using real testcontainers)
   - Redis caching functionality
   - RabbitMQ messaging
   - Service-to-service communication via HTTP APIs

3. **End-to-End Tests:**
   - Complete user workflows
   - Multi-service interactions
   - Event processing chains

4. **Performance Tests:**
   - Load testing with expected traffic
   - Database query performance
   - Memory usage validation
   - Response time requirements

### Test Execution Commands

```bash
# Run all tests
make test

# Run with coverage
uv run pytest --cov=. --cov-report=html --cov-report=xml

# Run specific test categories
uv run pytest tests/unit/          # Unit tests only (mock HTTP clients)
uv run pytest tests/integration/   # Integration tests with real data services via testcontainers
uv run pytest tests/load/          # Performance tests

# CRITICAL: Integration tests use real data services via testcontainers
uv run pytest tests/integration/ --testcontainers  # Uses real data services for testing
```

---

## Deployment and Production Checklist

### Pre-Deployment Validation

- [ ] All tests pass with 80%+ coverage
- [ ] Docker images build successfully
- [ ] Environment variables documented and validated
- [ ] Database migrations tested
- [ ] Health checks implemented and working
- [ ] Monitoring endpoints configured
- [ ] Security scan passes (bandit, safety)
- [ ] Load testing completed
- [ ] Documentation complete and accurate

### Production Environment Requirements

- [ ] SSL/TLS certificates configured
- [ ] Secrets management implemented
- [ ] Database backups automated
- [ ] Log aggregation configured
- [ ] Monitoring dashboards created
- [ ] Alerting rules defined
- [ ] Disaster recovery plan documented
- [ ] Performance baseline established

### Security Checklist

- [ ] No secrets in code or Docker images
- [ ] Authentication and authorization implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Dependency vulnerability scan clean
- [ ] Container security scan passed

---

## Common Pitfalls and Solutions

### 1. **Missing Dependencies**
**Problem:** Service fails to start due to missing Python packages
**Solution:** Always include complete `pyproject.toml` with pinned versions

### 2. **Data Service Connection Issues**
**Problem:** Services can't connect to data services
**Solution:**
- Ensure proper HTTP client configuration for data services
- Use health checks for data service endpoints (/health)
- Implement HTTP retry logic with exponential backoff
- Verify data service URLs: DB_POSTGRES_SERVICE_URL, DB_MONGO_SERVICE_URL

### 3. **Event Loop Conflicts**
**Problem:** FastAPI and Aiogram conflict when run together
**Solution:** Always run different service types in separate containers

### 4. **Missing Environment Variables**
**Problem:** Configuration errors at runtime
**Solution:**
- Provide complete .env.example with data service URLs
- Validate environment variables at startup
- Use Pydantic Settings for configuration
- MANDATORY: Include DB_POSTGRES_SERVICE_URL and DB_MONGO_SERVICE_URL

### 5. **Docker Build Failures**
**Problem:** Docker images fail to build
**Solution:**
- Use proper base images (python:3.12-slim)
- Include .dockerignore to optimize builds
- Layer dependencies separately from source code

### 6. **Testing Data Service Integration Issues**
**Problem:** Tests fail due to data service communication
**Solution:**
- Use testcontainers to spin up real data services for integration tests
- Mock HTTP clients only in unit tests, use real services in integration tests
- Implement proper test fixtures for data service clients
- Test HTTP error handling scenarios (timeouts, 404s, 500s)
- Follow testing standards in `testing-standards.mdc`

---

## Validation Checklist

Use this checklist to ensure your use case is complete and production-ready:

### ✅ File Structure Validation

- [ ] All required directories exist
- [ ] All mandatory files present
- [ ] Dockerfiles for each service
- [ ] Database initialization scripts
- [ ] Environment configuration files
- [ ] Testing infrastructure complete

### ✅ Service Implementation Validation

- [ ] Health check endpoints implemented
- [ ] Error handling comprehensive
- [ ] Logging configured properly
- [ ] Authentication implemented (if required)
- [ ] Input validation on all endpoints
- [ ] Proper async/await usage

### ✅ Infrastructure Validation

- [ ] Docker Compose integrates with existing stack
- [ ] Data service HTTP APIs accessible (ports 8001, 8002)
- [ ] Redis connectivity working
- [ ] RabbitMQ messaging functional
- [ ] HTTP communication with data services working
- [ ] NO direct database connections in business services

### ✅ Testing Validation

- [ ] Unit tests cover 100% of critical paths
- [ ] Integration tests with real data services via testcontainers
- [ ] Performance tests show acceptable HTTP response times to data services
- [ ] All tests pass consistently with 100% critical path coverage
- [ ] Code quality tools configured and passing (UV only, Ruff, Mypy)
- [ ] NO direct database dependencies in business service code or tests

### ✅ Production Readiness Validation

- [ ] Production configuration files present
- [ ] Monitoring and metrics configured
- [ ] Security measures implemented
- [ ] Documentation complete and accurate
- [ ] Deployment automation working
- [ ] Backup and recovery procedures documented

---

## Conclusion

A complete use case implementation using the **Improved Hybrid Approach** requires adherence to established architectural patterns. The most common failure points when not following project constraints are:

1. **Architecture Violations** (70% of failures)
   - Direct database connections in business services
   - Mixing service types in same containers
   - Ignoring HTTP-only data access pattern

2. **Naming Convention Violations** (15% of failures)
   - Using hyphens instead of underscores
   - Inconsistent file and identifier naming

3. **Technology Stack Deviations** (10% of failures)
   - Wrong Python versions or package managers
   - Incompatible dependency versions

4. **Integration Issues** (5% of failures)
   - Creating separate infrastructure instead of integrating with existing stack
   - Missing HTTP client configurations for data services

**Key Success Factors:**
- **Follow Existing Patterns**: The project infrastructure is complete - integrate, don't rebuild
- **HTTP-Only Data Access**: Business services communicate with data services via HTTP APIs only
- **Naming Consistency**: Use underscores everywhere, no exceptions
- **Service Separation**: Each service type runs in its own container

**Estimated Implementation Time:** 2-4 days for business logic implementation when following established patterns and integrating with existing infrastructure, vs 6-10 days if trying to create separate infrastructure.

**Next Steps:**
1. Study `../../CLAUDE.md` and `../reference/tech_stack.md` thoroughly
2. Examine existing service implementations in `services/` directory
3. Follow `../services/` patterns for your service type
4. Implement business logic using HTTP clients for data access
5. Test using HTTP mocking, not direct database access