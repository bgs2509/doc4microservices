# Project Structure Guide

This document provides comprehensive guidance on organizing projects when using the microservices framework as a Git submodule.

## Framework Usage Patterns

This framework can be used in two ways:
- **Direct**: Working in this repository directly (use paths like `docs/`)
- **Submodule**: Added as `.framework/` submodule to your project (use paths like `.framework/docs/`)

## Recommended Project Structure

When you add this framework as a submodule, your project structure should follow this pattern:

```
my_awesome_app/                      # Your project repository
├── .framework/                      # Git submodule (this repository)
│   ├── docs/                       # Atomic knowledge base and guides
│   └── CLAUDE.md                   # AI instructions
├── services/                        # All microservices (independent deployable units)
│   ├── api-service/                # FastAPI REST API service (port 8000)
│   │   ├── src/                    # Service source code (DDD/Hexagonal structure)
│   │   │   ├── api/                # Transport adapters (FastAPI routers)
│   │   │   ├── application/        # Use cases, orchestrators
│   │   │   ├── domain/             # Entities, value objects
│   │   │   ├── infrastructure/     # Repositories, HTTP clients
│   │   │   ├── schemas/            # Pydantic DTOs
│   │   │   └── core/               # Configuration, logging, settings
│   │   ├── tests/                  # Service-specific tests
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── Dockerfile              # Service-specific container
│   │   ├── requirements.txt        # Service dependencies
│   │   └── pyproject.toml          # Service Python config
│   ├── bot-service/                # Aiogram Telegram bot service
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── worker-service/             # AsyncIO background workers
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── db-postgres-service/        # PostgreSQL data access service (port 8001)
│   │   ├── src/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── db-mongo-service/           # MongoDB data access service (port 8002)
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
├── shared/                          # Shared components across services
│   ├── dtos/                       # Shared Data Transfer Objects
│   ├── events/                     # Shared Event Schemas
│   └── utils/                      # Shared stateless utility functions
├── nginx/                           # API Gateway / Reverse Proxy
│   ├── nginx.conf                  # Main nginx configuration
│   ├── conf.d/                     # Configuration modules
│   │   ├── api-gateway.conf        # Routing rules for all services
│   │   ├── upstream.conf           # Upstream service definitions
│   │   └── ssl.conf                # SSL/TLS configuration
│   ├── Dockerfile                  # Nginx container
│   └── certs/                      # SSL certificates (gitignored)
├── infrastructure/                  # Infrastructure and observability (optional)
│   ├── monitoring/                 # Prometheus, Grafana configs
│   │   ├── prometheus/
│   │   └── grafana/
│   └── logging/                    # ELK stack configs
│       ├── elasticsearch/
│       ├── logstash/
│       └── kibana/
├── docker-compose.yml               # Orchestration for all services
├── .env.example                     # Configuration template
├── pyproject.toml                   # Root-level Python config (optional)
├── Makefile                         # Development automation commands
├── .gitignore                       # Version control exclusions
└── README.md                        # Project documentation
```

## Directory Structure Explanation

### Framework Directory (`.framework/`)
- **Immutable**: Never modify framework content when used as submodule
- **Patterns**: Contains atomic rules, implementation guides, and automation rule sets
- **Legacy**: Archived `.mdc` sources live in `docs/legacy/` for historical reference
- **Updates**: Use `git submodule update --remote .framework` to get latest improvements

### Root-Level Configuration
- **`docker-compose.yml`**: Single orchestration file for all services, nginx, databases, and infrastructure
- **`pyproject.toml`**: Optional root-level Python config for shared tooling
- **`Makefile`**: Development automation commands (build, test, deploy)
- **`.gitignore`**: Version control exclusions
- **`.env.example`**: Environment configuration template with all variables

### Services Directory (`services/`)
- **Purpose**: All microservices as independent deployable units
- **Structure**: Each service has its own `src/`, `tests/`, `Dockerfile`, and dependencies
- **Isolation**: Services can be extracted to separate repositories without refactoring
- **DDD/Hexagonal**: Each service follows layered architecture (see [Project Structure Patterns](../atomic/architecture/project-structure-patterns.md))

### Service Types

#### Business Services
- **`api-service/`**: FastAPI REST API service (Port: 8000)
- **`bot-service/`**: Aiogram Telegram bot service
- **`worker-service/`**: AsyncIO background workers
- **Purpose**: Business logic only, HTTP-only data access

#### Data Services
- **`db-postgres-service/`**: PostgreSQL data access service (Port: 8001)
- **`db-mongo-service/`**: MongoDB data access service (Port: 8002)
- **Purpose**: Centralized database operations, no business logic

### Shared Components (`shared/`)
- **Cross-Service Code**: DTOs, events, and utilities used across multiple services
- **Ownership**: Clear ownership and versioning for shared contracts
- **Stateless**: Utilities remain pure functions without side effects

### Nginx Directory (`nginx/`)
- **Purpose**: API Gateway and reverse proxy for all services
- **SSL/TLS**: Centralized certificate management and termination
- **Routing**: Path-based routing to internal services
- **Security**: Rate limiting, CORS, security headers
- **Single Instance**: One nginx serves all microservices

### Infrastructure Directory (`infrastructure/`)
- **Optional**: Observability and monitoring configurations
- **Monitoring**: Prometheus, Grafana, alerting rules
- **Logging**: ELK stack (Elasticsearch, Logstash, Kibana) configurations
- **Separation**: Infrastructure concerns isolated from business services

### Service File Structure
The structure below is a simplified overview for quick setup. For the complete, mandatory source code organization inside a service (including the `src/` layout, DDD/Hexagonal layers, and testing directories), see [Project Structure Patterns](../atomic/architecture/project-structure-patterns.md) for the mandatory layout.

Each service contains at a minimum:
- **`Dockerfile`**: Service-specific container configuration
- **`main.py`**: Service implementation
- **`requirements.txt`**: Service dependencies
- **`config.py`**: Service-specific configuration

### Test Organization
- **`tests/unit/`**: Individual test files per service (e.g., `test_api_service.py`)
- **`tests/integration/`**: Cross-service communication tests
- **`conftest.py`**: Centralized test fixtures and configuration

## Docker Compose Organization

### Single Root Compose Setup (Mandatory)
Use one main `docker-compose.yml` in the project root, not individual compose files per service.

**Example Structure:**
```yaml
services:
  # API Gateway
  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api-service
      - bot-service
    networks:
      - app-network

  # Business Services (no exposed ports, internal only)
  api-service:
    build: ./services/api-service
    networks:
      - app-network

  bot-service:
    build: ./services/bot-service
    networks:
      - app-network

  worker-service:
    build: ./services/worker-service
    networks:
      - app-network

  # Data Services (internal ports only)
  db-postgres-service:
    build: ./services/db-postgres-service
    networks:
      - app-network

  db-mongo-service:
    build: ./services/db-mongo-service
    networks:
      - app-network

  # Infrastructure
  postgres:
    image: postgres:16
    networks:
      - app-network

  mongodb:
    image: mongo:7
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

  rabbitmq:
    image: rabbitmq:3-management
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

**Benefits:**
- **Single Entry Point**: Nginx handles all external traffic, services isolated internally
- **Service Isolation**: Business services never expose ports directly
- **Data Service Isolation**: Centralized database expertise and optimization
- **Shared Infrastructure**: Redis, RabbitMQ, observability stack shared across all services
- **Proper Service Networking**: HTTP communication between business and data services via internal network
- **Unified Environment**: Single command deployment with proper dependency management
- **Security**: Only nginx is exposed; services communicate via internal Docker network

## Framework Management

### Submodule Operations
```bash
# Update framework to latest version
git submodule update --remote .framework
git add .framework && git commit -m "Update framework"

# Clone project with framework
git clone --recursive <your-project-repo>

# If you forgot --recursive
git submodule init && git submodule update
```

### Development Workflow
1. **Add framework as submodule** to your project
2. **Generate application code** in `services/`, `shared/`, and `nginx/` using AI or manual development
3. **Follow framework patterns** from `docs/` *(or `.framework/docs/` when used as submodule)*
4. **Never modify** `.framework/` content
5. **Update framework** periodically with `git submodule update --remote`

**Key Principles:**
- Services at root level (`services/`), not buried in `src/`
- Each service is self-contained with own `src/`, `tests/`, and dependencies
- Nginx at root level for API Gateway functionality
- Infrastructure concerns (monitoring, logging) separated in `infrastructure/`

## Quick Setup Guide

```bash
# 1. Create your project
mkdir my_awesome_app && cd my_awesome_app && git init

# 2. Add framework as submodule
git submodule add <framework-repo-url> .framework
git submodule init && git submodule update

# 3. Generate application with AI (AI reads framework patterns)
# Ask AI: "Create [your app] using .framework/ patterns"

# 4. Deploy ready application
docker-compose up -d
```

## Architecture Compliance

When organizing your project:

### Critical Constraints
- **PROHIBITED**: Direct database connections in business services
- **PROHIBITED**: Running multiple event loop managers in same process
- **MANDATORY**: Python 3.12+ for all services
- **MANDATORY**: Underscore-only naming convention (no hyphens)

### Service Communication
- **Business → Data**: HTTP APIs only
- **Inter-service**: RabbitMQ for events
- **Service Isolation**: Each service type in separate containers

### Documentation References
- **Architecture Details**: [Architecture Guide](../LINKS_REFERENCE.md#core-documentation)
- **Development Commands**: [Development Commands](../LINKS_REFERENCE.md#developer-guides)
- **Technology Stack**: [Technical Specifications](../LINKS_REFERENCE.md#core-documentation)
