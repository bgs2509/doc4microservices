# Documentation for Microservices

> **📚 Comprehensive Documentation Project** - Architecture patterns, guidelines, and best practices for Python 3.12+ microservices using the Improved Hybrid Approach.

## 📖 What This Is

A **comprehensive documentation project** providing architectural patterns, implementation guidelines, and best practices for building production-ready Python microservices.

**This is NOT a runnable application** - it's a curated collection of documentation, patterns, and examples for microservices architecture.

### What's Included

- **🏗 Improved Hybrid Architecture Patterns** - Centralized data services with HTTP-only business logic
- **📡 Event-Driven Communication Guidelines** - Complete RabbitMQ integration patterns
- **📊 Production Observability Stack** - Prometheus, Grafana, Jaeger, ELK configuration and patterns
- **🧪 Real-World Testing Standards** - Testcontainers patterns for database testing
- **💻 Working Code Examples** - Complete, runnable service implementations
- **🤖 AI-Ready Documentation** - Optimized for Claude Code and modern development workflows

### Target Audience

- **Software Architects** designing microservices systems
- **Python Developers** building distributed applications
- **DevOps Engineers** implementing observability and deployment patterns
- **Development Teams** adopting microservices architecture

### What's NOT Included

- Business logic or domain-specific functionality
- Ready-to-deploy applications
- Framework-specific tutorials (covered in official docs)

## 🏗 Architecture Overview

### Improved Hybrid Approach

```mermaid
graph TB
    subgraph "Business Services"
        API[FastAPI Service :8000]
        BOT[Aiogram Bot]
        WORKER[AsyncIO Workers]
    end

    subgraph "Data Services"
        PG[PostgreSQL Service :8001]
        MONGO[MongoDB Service :8002]
    end

    subgraph "Infrastructure"
        POSTGRES[(PostgreSQL)]
        MONGODB[(MongoDB)]
        REDIS[(Redis)]
        RABBIT[RabbitMQ]
    end

    API -->|HTTP only| PG
    API -->|HTTP only| MONGO
    BOT -->|HTTP only| PG
    BOT -->|HTTP only| MONGO
    WORKER -->|HTTP only| PG
    WORKER -->|HTTP only| MONGO

    PG --> POSTGRES
    MONGO --> MONGODB

    API -.->|Events| RABBIT
    BOT -.->|Events| RABBIT
    WORKER -.->|Events| RABBIT
```

### Key Principles

- **Data Access**: HTTP-only communication to centralized data services
- **Service Separation**: Each service type runs in separate containers
- **Event-Driven**: RabbitMQ for asynchronous inter-service communication
- **Observability**: Complete monitoring and tracing stack
- **Type Safety**: Full type annotations with mypy validation

## 📚 Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[CLAUDE.md](CLAUDE.md)** | Main development guide | Start here - architecture, commands, setup |
| **[docs/reference/tech_stack.md](docs/reference/tech_stack.md)** | Technology specifications | Check versions, configurations |
| **[docs/reference/service-examples.md](docs/reference/service-examples.md)** | Working code examples | Implement new services |
| **[docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)** | Problem solving | Fix issues, debug problems |
| **[docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md](docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md)** | Create use cases | Build production features |

## 📋 Technology Stack

This project uses a carefully selected technology stack optimized for microservices architecture with the Improved Hybrid Approach.

**Key Technologies:**
- **Python 3.12+** - Unified runtime across all services
- **FastAPI + Aiogram + AsyncIO** - Service type separation
- **PostgreSQL + MongoDB** - Dual database strategy
- **Redis + RabbitMQ** - Caching and messaging
- **Docker Compose** - Service orchestration
- **Complete Observability Stack** - Prometheus, Grafana, Jaeger, ELK

### Benefits for Teams

- **Reduced Architecture Decisions** - Pre-validated patterns and technology choices
- **Faster Development** - Working examples and implementation templates
- **Production Readiness** - Complete observability, testing, and deployment patterns
- **Team Alignment** - Consistent patterns and coding standards
- **Risk Mitigation** - Battle-tested architectural constraints and best practices

> **📋 COMPLETE TECHNOLOGY SPECIFICATIONS**: For detailed versions, configurations, compatibility matrix, and implementation guidelines, see [docs/reference/tech_stack.md](docs/reference/tech_stack.md).

## 🔗 Links

- **📚 Complete Documentation**: [CLAUDE.md](CLAUDE.md)
- **🏗️ Architecture Guide**: [docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md)
- **📋 Development Commands**: [docs/guides/DEVELOPMENT_COMMANDS.md](docs/guides/DEVELOPMENT_COMMANDS.md)
- **🔧 Technology Specifications**: [docs/reference/tech_stack.md](docs/reference/tech_stack.md)
- **💻 Working Examples**: [docs/reference/service-examples.md](docs/reference/service-examples.md)
- **🐛 Troubleshooting**: [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**📚 Ready to explore microservices documentation?** Start with [CLAUDE.md](CLAUDE.md) for complete guidance!