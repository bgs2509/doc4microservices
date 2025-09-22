# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Documentation Hierarchy

> **🎯 NAVIGATION GUIDE**: This project follows a clear documentation structure. Each file has a specific purpose and avoids duplication.

### Primary Documentation (Essential Reading)

1. **[CLAUDE.md](CLAUDE.md)** (this file) - **MAIN ENTRY POINT**
   - 🏗️ Project overview and navigation guide
   - 🚀 Development workflow and setup instructions
   - 📋 Links to specialized documentation

2. **[docs/reference/tech_stack.md](docs/reference/tech_stack.md)** - **TECHNOLOGY AUTHORITY**
   - 🔧 Complete technology specifications and versions
   - 📦 Library compatibility and requirements
   - ⚙️ Infrastructure configuration details

3. **[README.md](README.md)** - **PROJECT INTRODUCTION**
   - 📖 High-level project description
   - ⚡ Quick start instructions
   - 🔗 Links to detailed documentation

### Implementation Guides

4. **[docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md)** - **ARCHITECTURE AUTHORITY**
   - 🏗️ Improved Hybrid Approach architecture
   - ⚠️ Mandatory constraints and principles
   - 🔧 Service types and communication patterns

5. **[docs/guides/DEVELOPMENT_COMMANDS.md](docs/guides/DEVELOPMENT_COMMANDS.md)** - **COMMANDS AUTHORITY**
   - 📋 Complete development commands reference
   - 🐳 Docker operations and service management
   - 🔍 Troubleshooting and diagnostic commands

6. **[docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md](docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md)** - **USE CASE CREATION**
   - 📋 Step-by-step use case development
   - ✅ Compliance checklists and templates
   - 🏗️ Production-ready implementation patterns

### Reference Materials

7. **[docs/reference/tech_stack.md](docs/reference/tech_stack.md)** - **TECHNOLOGY AUTHORITY**
   - 🔧 Complete technology specifications and versions
   - 📦 Library compatibility and requirements
   - ⚙️ Infrastructure configuration details

8. **[docs/reference/service-examples.md](docs/reference/service-examples.md)** - **WORKING EXAMPLES**
   - 💻 Complete, runnable service implementations
   - 🎯 Real-world patterns and best practices
   - 🧪 Testing examples and patterns

9. **[docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)** - **PROBLEM SOLVING**
   - 🐛 Common issues and solutions
   - 🔍 Diagnostic procedures
   - 🚨 Emergency troubleshooting steps

### Specialized Documentation

10. **[docs/](docs/)** - **IDE RULES & PATTERNS** (architecture, services, infrastructure, observability, quality)
   - 🤖 Automated code generation rules
   - 📏 Service-specific implementation patterns
   - 🔧 Technology-specific guidelines

10. **[use_cases/](use_cases/)** - **CONCRETE EXAMPLES**
    - 🎯 Real working use case implementations
    - 📚 Domain-specific documentation
    - 🚀 Deployment and usage examples

### Quick Navigation

| Need | Go To |
|------|-------|
| 🏁 **Get started quickly** | [README.md](README.md) → [CLAUDE.md - Development Commands](#development-commands) |
| 🏗️ **Understand architecture** | [docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md) |
| 📋 **Run commands** | [docs/guides/DEVELOPMENT_COMMANDS.md](docs/guides/DEVELOPMENT_COMMANDS.md) |
| 🎯 **Create new use case** | [docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md](docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md) |
| 🔧 **Check versions/config** | [docs/reference/tech_stack.md](docs/reference/tech_stack.md) |
| 💻 **See working examples** | [docs/reference/service-examples.md](docs/reference/service-examples.md) |
| 🐛 **Solve problems** | [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md) |
| 🤖 **IDE rules & patterns** | [docs/INDEX.md#ide-rules--patterns](docs/INDEX.md#ide-rules--patterns) |

## Project Overview

This is a microservices architecture project using Python 3.12+ with the **Improved Hybrid Approach** for data access. The project includes:

- **Infrastructure**: Complete observability stack with Prometheus, Grafana, Jaeger, ELK, and dual database infrastructure (PostgreSQL + MongoDB)
- **Data Services**: Centralized data access services (db_postgres_service, db_mongo_service) implementing the Database Service pattern
- **Business Services**: Business logic services (api_service, bot_service, worker_service) that access data via HTTP APIs only
- **Architecture**: DDD/Hexagonal patterns with clear separation between data access and business logic

**Current Status**: Complete Improved Hybrid Approach implementation with PostgreSQL and MongoDB data services. Business services access data via HTTP only - no direct database connections.

**CRITICAL ARCHITECTURE CONSTRAINTS**:
1. Different service types (FastAPI, Aiogram, AsyncIO workers) MUST run in separate processes/containers to avoid event loop conflicts
2. Business services MUST access data ONLY via HTTP APIs to data services - direct database connections are PROHIBITED
3. Use RabbitMQ for inter-service communication and event publishing
4. **NAMING CONVENTION**: See [docs/architecture/naming_conventions.mdc](docs/architecture/naming_conventions.mdc) for mandatory naming standards

## Development Commands

> **📋 CANONICAL COMMAND REFERENCE**: For all development commands, see [docs/guides/DEVELOPMENT_COMMANDS.md](docs/guides/DEVELOPMENT_COMMANDS.md). This includes Docker operations, testing, deployment, troubleshooting, and more.

### Quick Reference
```bash
# Quick start (full commands in docs/guides/DEVELOPMENT_COMMANDS.md)
cp .env.example .env
docker-compose up -d
uv sync --dev
curl http://localhost:8000/health
```

**Essential operations:**
- **Docker**: [docs/guides/DEVELOPMENT_COMMANDS.md#docker-compose-operations](docs/guides/DEVELOPMENT_COMMANDS.md#docker-compose-operations)
- **Testing**: [docs/guides/DEVELOPMENT_COMMANDS.md#testing-commands](docs/guides/DEVELOPMENT_COMMANDS.md#testing-commands)
- **Troubleshooting**: [docs/guides/DEVELOPMENT_COMMANDS.md#troubleshooting-commands](docs/guides/DEVELOPMENT_COMMANDS.md#troubleshooting-commands)

## Architecture Guidelines

> **🏗️ ARCHITECTURAL FOUNDATION**: For complete architectural guidelines, constraints, and patterns, see [docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md). This section provides a high-level overview.

### Improved Hybrid Approach Overview

This project implements the **Improved Hybrid Approach** - a microservices architecture pattern that combines centralized data access with distributed business logic.

**Key Principles:**
- **Centralized Data Services**: All database operations handled by dedicated data services
- **HTTP-Only Data Access**: Business services communicate with data services via HTTP APIs only
- **Service Type Separation**: Each service type (FastAPI, Aiogram, AsyncIO) runs in separate processes
- **Event-Driven Communication**: RabbitMQ for inter-service messaging
- **DDD/Hexagonal Architecture**: Clear separation of business logic from infrastructure

**Critical Constraints:**
- ❌ **PROHIBITED**: Direct database connections in business services
- ❌ **PROHIBITED**: Running multiple event loop managers in same process
- ⚠️ **MANDATORY**: Python 3.12+ for all services
- ⚠️ **MANDATORY**: Underscore-only naming convention (no hyphens)

> **📋 COMPLETE ARCHITECTURE DETAILS**: See [docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md) for detailed constraints, patterns, and implementation guidelines.

### Docker Compose Organization

#### RECOMMENDED: Single Root Compose Setup
Use one main `docker-compose.yml` in the project root, not individual compose files per service.

**Project Structure:**
```
boilerplate_microservices/
├── docker-compose.yml               # Main orchestration
├── docker-compose.override.yml      # Development overrides (auto-loaded)
├── docker-compose.prod.yml          # Production config
├── services/
│   ├── db_postgres_service/         # PostgreSQL data access service
│   │   ├── Dockerfile
│   │   └── src/
│   ├── db_mongo_service/            # MongoDB data access service
│   │   ├── Dockerfile
│   │   └── src/
│   ├── api_service/                 # Business logic FastAPI service
│   │   ├── Dockerfile
│   │   └── src/
│   ├── bot_service/                 # Business logic Aiogram service
│   │   ├── Dockerfile
│   │   └── src/
│   └── worker_service/              # Business logic AsyncIO workers
│       ├── Dockerfile
│       └── src/
└── infrastructure/
    ├── nginx/
    ├── postgres/
    ├── mongodb/
    └── rabbitmq/
```

**Benefits:**
- **Data Service Isolation**: Centralized database expertise and optimization
- **Business Logic Focus**: Services contain only business logic, no database concerns
- **Shared Infrastructure**: Redis, RabbitMQ, observability stack shared across all services
- **Proper Service Networking**: HTTP communication between business and data services
- **Unified Environment**: Single command deployment with proper dependency management

### Service Types and Implementation Status
**Complete technology specifications and versions**: [docs/reference/tech_stack.md](docs/reference/tech_stack.md)

**Service Architecture:**
- **Data Services**: PostgreSQL and MongoDB data access services (Ports: 8001, 8002)
- **Business Services**: FastAPI, Aiogram, AsyncIO workers (HTTP-only data access)
- **Infrastructure**: Complete observability and messaging stack

**Current Status**: Infrastructure and service framework complete, ready for business logic implementation.

**Service Implementation Guides:**
- Data access patterns: `docs/architecture/data-access-rules.mdc`
- MongoDB operations: `docs/infrastructure/mongodb_rules.mdc`
- FastAPI patterns: `docs/services/fastapi_rules.mdc`
- Aiogram patterns: `docs/services/aiogram_rules.mdc`
- AsyncIO patterns: `docs/services/asyncio_rules.mdc`

### Service Structure
For detailed service structure and architecture patterns, see [docs/reference/tech_stack.md](docs/reference/tech_stack.md) and `docs/architecture/ms_best_practices_rules.mdc`.

### Service-Specific Patterns

**Implementation patterns available in:**
- **FastAPI Services**: [docs/services/fastapi_rules.mdc](docs/services/fastapi_rules.mdc)
- **Aiogram Services**: [docs/services/aiogram_rules.mdc](docs/services/aiogram_rules.mdc)
- **AsyncIO Workers**: [docs/services/asyncio_rules.mdc](docs/services/asyncio_rules.mdc)
- **Database Access**: [docs/architecture/data-access-rules.mdc](docs/architecture/data-access-rules.mdc)
- **Testing Standards**: [docs/quality/testing-standards.mdc](docs/quality/testing-standards.mdc)

## Cursor Rules Integration

**Comprehensive implementation rules available in [docs/](docs/) organized by category**

See [docs/INDEX.md](docs/INDEX.md) for complete overview of all 15 rule files covering architecture, service patterns, infrastructure, and observability.

## Important Notes

- **Implementation Status**: Infrastructure and service framework are complete. Business logic implementation should follow `docs/` rule patterns
- **Complete Examples**: See [docs/reference/service-examples.md](docs/reference/service-examples.md) for comprehensive, working implementations of all service types
- **Environment Setup**: Copy `.env.example` to `.env` and configure for your environment
- **Service Separation**: Each service type runs in separate containers to avoid event loop conflicts
- **Testing Standards**: Use real database instances (via testcontainers), achieve 100% coverage for critical paths
- **Type Annotations**: All functions must have full type hints (enforced by mypy>=1.8.0)
- **Security Focus**: Implement OAuth2/JWT, HTTPS, rate limiting, and proper error handling
- **Troubleshooting**: For common issues and solutions, see [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)