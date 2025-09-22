# Development Commands Reference

> **📋 CANONICAL COMMAND REFERENCE**: This document is the single source of truth for all development commands. All other documentation should reference this file instead of duplicating commands.

## Table of Contents
- [Docker Compose Operations](#docker-compose-operations)
- [Observability Operations](#observability-operations)
- [Data Service Operations](#data-service-operations)
- [Production Deployment](#production-deployment)
- [Package Management (UV)](#package-management-uv)
- [Code Quality Commands](#code-quality-commands)
- [Testing Commands](#testing-commands)
- [Configuration and Validation](#configuration-and-validation)
- [Development Workflow](#development-workflow)
- [Troubleshooting Commands](#troubleshooting-commands)

---

## 🐳 Docker Compose Operations

### Basic Operations
```bash
# Start entire stack
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop and remove containers
docker-compose down

# Stop and remove volumes (⚠️ Data loss)
docker-compose down -v
```

### Build Operations
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build <service_name>

# Force rebuild without cache
docker-compose build --no-cache

# Build and start
docker-compose up --build
```

### Service Management
```bash
# Follow logs for specific service
docker-compose logs -f <service_name>

# Enter service container
docker-compose exec <service_name> bash

# Restart specific service
docker-compose restart <service_name>

# Scale specific service
docker-compose up --scale <service_name>=3

# Check service status
docker-compose ps
```

---

## 📊 Observability Operations

### Start Monitoring Stack
```bash
# Start with all monitoring services
docker-compose --profile monitoring up -d

# Start only specific monitoring services
docker-compose up prometheus grafana jaeger elasticsearch logstash kibana filebeat -d
```

### Access Monitoring Dashboards
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Jaeger**: http://localhost:16686
- **Kibana**: http://localhost:5601
- **Prometheus**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

### Monitoring Commands
```bash
# Follow ELK logs
docker-compose logs -f elasticsearch logstash kibana

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health

# Check RabbitMQ queues
docker-compose exec rabbitmq rabbitmqctl list_queues
```

---

## 🗄️ Data Service Operations

### Service URLs and Health Checks
```bash
# External Access (from host machine)
curl http://localhost:8001/health    # PostgreSQL Data Service
curl http://localhost:8002/health    # MongoDB Data Service
curl http://localhost:8000/health    # Business API Service

# API Documentation
open http://localhost:8001/docs      # PostgreSQL Data Service API
open http://localhost:8002/docs      # MongoDB Data Service API
open http://localhost:8000/docs      # Business API Service API
```

### Inter-Service Communication (inside Docker network)
- **PostgreSQL Data Service**: `http://db_postgres_service:8000`
- **MongoDB Data Service**: `http://db_mongo_service:8000`
- **Business API Service**: `http://api_service:8000`

> **💡 Port Mapping Strategy**: All services run on port 8000 inside containers. Docker Compose maps them to different host ports (8000, 8001, 8002) to avoid conflicts.

### Database Connectivity Checks
```bash
# PostgreSQL connectivity
docker-compose exec postgres pg_isready -U postgres
docker-compose exec postgres psql -U postgres -d microservices_db

# MongoDB connectivity
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Redis connectivity
docker-compose exec redis redis-cli ping
```

---

## 🚀 Production Deployment

### Production Commands
```bash
# Deploy with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services for production
docker-compose up --scale api_service=3 --scale worker_service=2 -d

# Production build with optimizations
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Health Checks in Production
```bash
# Check all service health
./scripts/health-check.sh

# Validate configuration consistency
./scripts/validate-config.sh
```

---

## 📦 Package Management (UV)

### Dependency Management
```bash
# Add new dependencies
uv add <package>

# Add development dependencies
uv add --dev <package>

# Update lock file
uv lock

# Install dependencies from lock file
uv sync

# Install with dev dependencies
uv sync --dev

# Run application
uv run python main.py
```

---

## 🔍 Code Quality Commands

### Linting and Formatting
```bash
# Run linter (follows PEP8 compliance)
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check formatting without applying
uv run ruff format . --check
```

### Type Checking and Security
```bash
# Type checking (requires mypy>=1.8.0)
uv run mypy .

# Security analysis
uv run bandit -r .

# Run all quality checks
uv run ruff check . && uv run ruff format . --check && uv run mypy . && uv run bandit -r .
```

---

## 🧪 Testing Commands

### Test Execution
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html --cov-report=xml

# Run specific test categories
uv run pytest tests/unit/              # Unit tests only
uv run pytest tests/integration/       # Integration tests only
uv run pytest tests/ -k "test_api"     # Filter by test name

# Run tests with verbose output
uv run pytest -v

# Run tests in parallel (with pytest-xdist)
uv run pytest -n auto
```

### Coverage Analysis
```bash
# Generate HTML coverage report
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html

# Coverage with missing lines
uv run pytest --cov=app --cov-report=term-missing

# Set coverage threshold
uv run pytest --cov=app --cov-fail-under=80
```

> **🎯 Target**: 100% test coverage for critical paths

---

## ⚙️ Configuration and Validation

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Validate Docker Compose configuration
docker-compose config

# Validate environment variables
docker-compose config --quiet && echo "✅ Configuration valid"
```

### Service Health and Connectivity Checks
```bash
# Check all service health
curl http://localhost:8000/health  # Business API
curl http://localhost:8001/health  # PostgreSQL Data Service
curl http://localhost:8002/health  # MongoDB Data Service

# Database connectivity checks
docker-compose exec postgres pg_isready -U postgres
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose exec redis redis-cli ping
```

---

## 🛠️ Development Workflow

### Quick Start
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your settings

# 2. Start development stack
docker-compose up -d

# 3. Install dependencies
uv sync --dev

# 4. Run quality checks
uv run ruff check . && uv run mypy . && uv run pytest

# 5. View logs
docker-compose logs -f
```

### Common Development Tasks
```bash
# Start only infrastructure (for local development)
docker-compose up postgres mongodb redis rabbitmq -d

# Rebuild after dependency changes
docker-compose down && docker-compose up --build -d

# Reset everything (⚠️ Data loss)
docker-compose down -v && docker-compose up --build -d

# Debug specific service
docker-compose logs -f <service_name>
docker-compose exec <service_name> bash
```

---

## 🔍 Troubleshooting Commands

### Service Diagnostics
```bash
# Check services status and logs
docker-compose ps
docker-compose logs -f [service_name]

# Test connectivity
curl http://localhost:8000/health  # API service
curl http://localhost:8001/health  # PostgreSQL data service
curl http://localhost:8002/health  # MongoDB data service
```

### Infrastructure Diagnostics
```bash
# Check Docker system status
docker system df
docker system prune -a  # Clean up unused resources

# Check network connectivity
docker network ls
docker network inspect try_microservices_default

# Check port usage
sudo netstat -tulpn | grep :5432
```

### Database Diagnostics
```bash
# PostgreSQL diagnostics
docker-compose exec postgres pg_isready -U postgres
docker-compose logs postgres

# MongoDB diagnostics
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
docker-compose logs mongodb

# Redis diagnostics
docker-compose exec redis redis-cli -a redis123 ping
docker-compose exec redis redis-cli -a redis123 info memory
```

### Service Communication Diagnostics
```bash
# RabbitMQ diagnostics
docker-compose logs rabbitmq
open http://localhost:15672  # Management UI

# Check message queues
docker-compose exec rabbitmq rabbitmqctl list_queues

# Test HTTP communication between services
docker-compose exec api_service curl http://db_postgres_service:8000/health
```

### Performance Diagnostics
```bash
# Monitor resource usage
docker stats

# Check logs for performance issues
docker-compose logs -f --timestamps

# Database query performance
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

---

## 🎯 Use Case Specific Commands

### Task Management Use Case
```bash
# Navigate to use case
cd use_cases/task_management

# Start task management system
docker-compose up -d

# Test task management API
curl http://localhost:8000/docs    # API documentation
curl http://localhost:8000/health  # Health check

# Check task management logs
docker-compose logs -f task_api_service
docker-compose logs -f task_bot_service
```

---

## 📚 Related Documentation

- **Architecture Details**: [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)
- **Technology Specifications**: [../reference/tech_stack.md](../reference/tech_stack.md)
- **Working Examples**: [../examples/index.md](../examples/index.md)
- **Troubleshooting Guide**: [../reference/troubleshooting.md](../reference/troubleshooting.md)
- **Main Development Guide**: [../../CLAUDE.md](../../CLAUDE.md)

---

## 🚨 Emergency Procedures

### Service Recovery
```bash
# Emergency restart all services
docker-compose down && docker-compose up -d

# Reset with data loss (last resort)
docker-compose down -v
docker system prune -a
docker-compose up --build -d
```

### Data Recovery
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U postgres microservices_db > backup.sql

# MongoDB backup
docker-compose exec mongodb mongodump --db microservices_analytics_db --out /backup/

# Redis backup
docker-compose exec redis redis-cli -a redis123 BGSAVE
```

---

> **📖 Documentation Hierarchy**: For complete project guidance, see [../../CLAUDE.md](../../CLAUDE.md). For architectural details, see [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md). For technology specifications, see [../reference/tech_stack.md](../reference/tech_stack.md).