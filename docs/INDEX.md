# Documentation Index

This is the comprehensive documentation index for the microservices project. All documentation is organized into logical categories for easy navigation.

## 📚 Quick Navigation

| Need | Go To |
|------|-------|
| 🏁 **Get started quickly** | [../README.md](LINKS_REFERENCE.md#core-documentation) → [../CLAUDE.md](../CLAUDE.md) |
| 🏗️ **Understand architecture** | [guides/ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md) |
| 📋 **Run commands** | [guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) |
| 🎯 **Create new use case** | [guides/USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md) |
| 🔧 **Check tech specs** | [reference/tech_stack.md](reference/tech_stack.md) |
| 💻 **See working examples** | [examples/index.md](examples/index.md) *(or [.framework/examples/index.md](.framework/examples/index.md) when used as submodule)* |
| 🐛 **Solve problems** | [reference/troubleshooting.md](reference/troubleshooting.md) |
| 🤖 **IDE rules & patterns** | [#ide-rules--patterns](#ide-rules--patterns) |

## 📂 Documentation Structure

### 📖 Core Guides
Essential documentation for development and architecture understanding.

- **[guides/ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md)** - Comprehensive architecture principles and constraints
- **[guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md)** - Complete command reference for development workflow
- **[guides/USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md)** - Step-by-step guide for creating new use cases

### 📑 Reference Materials
Technical specifications, examples, and troubleshooting resources.

- **[reference/tech_stack.md](reference/tech_stack.md)** - Technology specifications and versions
- **[examples/index.md](examples/index.md)** *(or [.framework/examples/index.md](.framework/examples/index.md) when used as submodule)* - Working code examples for all service types
- **[reference/troubleshooting.md](reference/troubleshooting.md)** - Common issues and solutions

## 🤖 IDE Rules & Patterns

IDE rules are organized by category at the docs root level for direct access and better integration.

### 🏗️ Architecture & Design
Core architectural patterns and design principles:

- **[architecture/ms_best_practices_rules.mdc](architecture/ms_best_practices_rules.mdc)** - Microservices best practices (DDD/Hex patterns, project structure, quality requirements)
- **[architecture/data-access-rules.mdc](architecture/data-access-rules.mdc)** - Data access patterns and HTTP-only data service communication
- **[architecture/naming_conventions.mdc](architecture/naming_conventions.mdc)** - Mandatory naming standards and conventions

### 🚀 Service Types
Service-specific implementation patterns:

- **[services/fastapi_rules.mdc](services/fastapi_rules.mdc)** - FastAPI service patterns and dependency injection
- **[services/aiogram_rules.mdc](services/aiogram_rules.mdc)** - Telegram bot service standards and patterns
- **[services/asyncio_rules.mdc](services/asyncio_rules.mdc)** - Background worker service patterns

### 🏗️ Infrastructure
Infrastructure component patterns:

- **[infrastructure/redis_rules.mdc](infrastructure/redis_rules.mdc)** - Redis patterns for caching and idempotency
- **[infrastructure/rabbitmq_rules.mdc](infrastructure/rabbitmq_rules.mdc)** - RabbitMQ standards for inter-service communication
- **[infrastructure/mongodb_rules.mdc](infrastructure/mongodb_rules.mdc)** - MongoDB patterns and operations

### 📊 Observability
Monitoring, logging, and tracing patterns:

- **[observability/logging_rules.mdc](observability/logging_rules.mdc)** - Unified logging with Request ID tracing
- **[observability/metrics_rules.mdc](observability/metrics_rules.mdc)** - Prometheus metrics collection patterns
- **[observability/tracing_rules.mdc](observability/tracing_rules.mdc)** - Distributed tracing with OpenTelemetry
- **[observability/elk_rules.mdc](observability/elk_rules.mdc)** - ELK stack configuration and patterns
- **[observability/observability_rules.mdc](observability/observability_rules.mdc)** - Overall observability strategy

### 🧪 Quality Assurance
Code quality and testing standards:

- **[quality/testing-standards.mdc](quality/testing-standards.mdc)** - Testing standards with 100% coverage requirements

## 🎯 Documentation by Task

### For New Developers
1. Start with [../README.md](../README.md) for project overview
2. Read [../CLAUDE.md](../CLAUDE.md) for development guidance
3. Study [guides/ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md) for architecture understanding
4. Use [guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) for daily commands

### For Service Development
1. Follow [guides/USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md)
2. Check relevant service rules in the `services` directory.
3. Use examples from [examples/index.md](examples/index.md) *(or [.framework/examples/index.md](.framework/examples/index.md) when used as submodule)*
4. Verify setup with [reference/tech_stack.md](reference/tech_stack.md)

### For Infrastructure Setup
1. Use [guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) for Docker operations
2. Follow infrastructure rules in the `infrastructure` directory.
3. Setup observability with the rules in the `observability` directory.
4. Troubleshoot with [reference/troubleshooting.md](reference/troubleshooting.md)

### For Code Quality
1. Follow [quality/testing-standards.mdc](quality/testing-standards.mdc)
2. Use [architecture/naming_conventions.mdc](architecture/naming_conventions.mdc)
3. Apply patterns from [architecture/ms_best_practices_rules.mdc](architecture/ms_best_practices_rules.mdc)

## 🔄 Maintenance

This documentation is organized to avoid duplication and maintain clear separation of concerns:

- **Guides** contain step-by-step instructions
- **Reference** contains specifications and examples
- **Root categories** contain IDE automation patterns organized by domain

When adding new documentation:
- Place guides in `guides/`
- Place technical references in `reference/`
- Place IDE rules in appropriate category folders at root level
- Update this index with new content

### 🔗 Link Validation

To maintain documentation quality, all internal links should be validated:

```bash
# Check for broken internal links (example command)
find docs/ -name "*.md" -exec grep -l "\[.*\](" {} \; | \ # (or find .framework/docs/ when used as submodule)
  xargs grep -n "\[.*\](" | \
  grep -v "http" | \
  awk -F: '{print $1":"$2}' | \
  sort | uniq

# Recommended: Add link checker to CI/CD pipeline
# Example: markdown-link-check or similar tool
```

### 📋 Documentation Standards

- **Always use relative paths** for internal links
- **Update INDEX.md** when adding new documentation
- **Follow naming conventions** from [architecture/naming_conventions.mdc](architecture/naming_conventions.mdc)
- **Avoid duplication** between documentation files
- **Reference canonical sources** for shared information

---

> **📖 Main Entry Point**: For project overview and getting started, see [../CLAUDE.md](../CLAUDE.md)