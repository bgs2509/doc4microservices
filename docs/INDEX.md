# Documentation Index

This is the comprehensive documentation index for the microservices project. All documentation is organized into logical categories for easy navigation.

## 📚 Quick Navigation

| Need | Go To |
|------|-------|
| 🏁 **Get started quickly** | [Project Overview][link-project-overview] → [Main Entry Point][link-main-entry-point] |
| 🏗️ **Understand architecture** | [Architecture Guide][link-architecture-guide] |
| 📋 **Run commands** | [Development Commands][link-development-commands] |
| 🎯 **Create new use case** | [Use Case Implementation Guide][link-use-case-guide] |
| 🔧 **Check tech specs** | [Technical Specifications][link-tech-specs] |
| 💻 **See working examples** | [Examples Index][link-examples-index] |
| 🐛 **Solve problems** | [Troubleshooting Guide][link-troubleshooting-guide] |
| 🤖 **IDE rules & patterns** | [IDE Rules & Patterns][link-ide-rules] |

## 📂 Documentation Structure

### 📖 Core Guides
Essential documentation for development and architecture understanding.

- **[Architecture Guide][link-architecture-guide]** - Comprehensive architecture principles and constraints
- **[Development Commands][link-development-commands]** - Complete command reference for development workflow
- **[Use Case Implementation Guide][link-use-case-guide]** - Step-by-step guide for creating new use cases

### 📑 Reference Materials
Technical specifications, examples, and troubleshooting resources.

- **[Technical Specifications][link-tech-specs]** - Technology specifications and versions
- **[Examples Index][link-examples-index]** - Working code examples for all service types
- **[Troubleshooting Guide][link-troubleshooting-guide]** - Common issues and solutions

## 🤖 IDE Rules & Patterns

IDE rules are organized by category at the docs root level for direct access and better integration.

### 🏗️ Architecture & Design
Core architectural patterns and design principles:

- **[Microservices Best Practices][link-ms-best-practices]** - DDD/Hex patterns, project structure, quality requirements
- **[Data Access Rules][link-data-access-rules]** - Data access patterns and HTTP-only data service communication
- **[Naming Conventions][link-naming-conventions]** - Mandatory naming standards and conventions

### 🚀 Service Types
Service-specific implementation patterns:

- **[FastAPI Rules][link-fastapi-rules]** - FastAPI service patterns and dependency injection
- **[Aiogram Rules][link-aiogram-rules]** - Telegram bot service standards and patterns
- **[AsyncIO Rules][link-asyncio-rules]** - Background worker service patterns

### 🏗️ Infrastructure
Infrastructure component patterns:

- **[Redis Rules][link-redis-rules]** - Redis patterns for caching and idempotency
- **[RabbitMQ Rules][link-rabbitmq-rules]** - RabbitMQ standards for inter-service communication
- **[MongoDB Rules][link-mongodb-rules]** - MongoDB patterns and operations

### 📊 Observability
Monitoring, logging, and tracing patterns:

- **[Logging Rules][link-logging-rules]** - Unified logging with Request ID tracing
- **[Metrics Rules][link-metrics-rules]** - Prometheus metrics collection patterns
- **[Tracing Rules][link-tracing-rules]** - Distributed tracing with OpenTelemetry
- **[ELK Rules][link-elk-rules]** - ELK stack configuration and patterns
- **[Observability Rules][link-observability-rules]** - Overall observability strategy

### 🧪 Quality Assurance
Code quality and testing standards:

- **[Testing Standards][link-testing-standards]** - Testing standards with 100% coverage requirements

## 🎯 Documentation by Task

### For New Developers
1. Start with [Project Overview][link-project-overview] for project overview
2. Read [Main Entry Point][link-main-entry-point] for development guidance
3. Study [Architecture Guide][link-architecture-guide] for architecture understanding
4. Use [Development Commands][link-development-commands] for daily commands

### For Service Development
1. Follow [Use Case Implementation Guide][link-use-case-guide]
2. Check relevant service rules in the `services` directory.
3. Use examples from [Examples Index][link-examples-index]
4. Verify setup with [Technical Specifications][link-tech-specs]

### For Infrastructure Setup
1. Use [Development Commands][link-development-commands] for Docker operations
2. Follow infrastructure rules in the `infrastructure` directory.
3. Setup observability with the rules in the `observability` directory.
4. Troubleshoot with [Troubleshooting Guide][link-troubleshooting-guide]

### For Code Quality
1. Follow [Testing Standards][link-testing-standards]
2. Use [Naming Conventions][link-naming-conventions]
3. Apply patterns from [Microservices Best Practices][link-ms-best-practices]

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
  awk -F: \'{print $1":"$2}\' | \
  sort | uniq

# Recommended: Add link checker to CI/CD pipeline
# Example: markdown-link-check or similar tool
```

### 📋 Documentation Standards

- **Always use relative paths** for internal links
- **Update INDEX.md** when adding new documentation
- **Follow naming conventions** from [Naming Conventions][link-naming-conventions]
- **Avoid duplication** between documentation files
- **Reference canonical sources** for shared information

---

> **📖 Main Entry Point**: For project overview and getting started, see [Main Entry Point][link-main-entry-point]

[link-main-entry-point]: LINKS_REFERENCE.md#core-documentation
[link-project-overview]: LINKS_REFERENCE.md#core-documentation
[link-architecture-guide]: LINKS_REFERENCE.md#core-documentation
[link-tech-specs]: LINKS_REFERENCE.md#core-documentation
[link-development-commands]: LINKS_REFERENCE.md#developer-guides
[link-use-case-guide]: LINKS_REFERENCE.md#developer-guides
[link-troubleshooting-guide]: LINKS_REFERENCE.md#developer-guides
[link-examples-index]: LINKS_REFERENCE.md#examples-and-templates
[link-ide-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-ms-best-practices]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-data-access-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-naming-conventions]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-fastapi-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-aiogram-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-asyncio-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-redis-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-rabbitmq-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-mongodb-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-logging-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-metrics-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-tracing-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-elk-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-observability-rules]: LINKS_REFERENCE.md#ide-rules-and-patterns
[link-testing-standards]: LINKS_REFERENCE.md#ide-rules-and-patterns