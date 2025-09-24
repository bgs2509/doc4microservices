# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this microservices framework.

> **📍 CONTEXT**: This framework can be used in two ways:
> - **Direct**: Working in this repository directly (use paths like `docs/`)
> - **Submodule**: Added as `.framework/` submodule to your project (use paths like `.framework/docs/`)
>
> The paths below assume **direct usage**. When used as submodule, prefix all paths with `.framework/`.

## 📚 Documentation Hierarchy

> **🎯 NAVIGATION GUIDE**: This project follows a clear documentation structure. Each file has a specific purpose and avoids duplication.

### Primary Documentation (Essential Reading)

- **[CLAUDE.md](docs/LINKS_REFERENCE.md#core-documentation)** (this file) — main entry point with project overview, workflow guidance, and navigation tips.
- **[Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation)** — authoritative source on technology versions, compatibility, and infrastructure configuration.
- **[README.md](docs/LINKS_REFERENCE.md#core-documentation)** — introductory summary with quick-start instructions and value proposition.

### Implementation Guides

- **[Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation)** — mandatory architecture principles, constraints, and communication patterns.
- **[Development Commands](docs/LINKS_REFERENCE.md#developer-guides)** — complete command reference for local development, Docker workflows, and diagnostics.
- **[Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides)** — structured process for designing and delivering new business capabilities.

### Reference Materials

- **[Project Structure](docs/LINKS_REFERENCE.md#developer-guides)** — canonical layout for repositories using this framework.
- **[Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation)** — quick lookup for stack details and configuration expectations.
- **[Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)** — playbook for resolving common operational and development issues.

### Specialized Documentation

- **[IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules-and-patterns)** — machine-readable rulesets for architecture, services, infrastructure, observability, and quality.

### Quick Navigation

| Need | Go To |
|------|-------|
| 🏁 **Get started quickly** | [README.md](docs/LINKS_REFERENCE.md#core-documentation) → [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) |
| 🏗️ **Understand architecture** | [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) |
| 📋 **Run commands** | [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) |
| 🎯 **Create new use case** | [Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides) |
| 🔧 **Check versions/config** | [Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation) |
| 🐛 **Solve problems** | [Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides) |
| 🤖 **IDE rules & patterns** | [IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules-and-patterns) |

## 📚 Documentation Categories

> **🎯 ORIENT BY PURPOSE**: Group documentation by the job you need to accomplish and follow the corresponding sources below.

| Focus | Primary Docs | What You Gain |
|-------|--------------|---------------|
| Architecture alignment | [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) | Constraints, service roles, communication rules |
| Daily development | [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) | Command recipes, environment management, troubleshooting steps |
| Delivering features | [Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides) | Step-by-step blueprint, validation checkpoints, deployment tips |
| Repository layout | [Project Structure](docs/LINKS_REFERENCE.md#developer-guides) | Expected folders, naming rules, separation of concerns |
| Operational support | [Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides) | Symptom-based diagnostics, recovery paths, escalation points |
| Automated enforcement | [IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules-and-patterns) | Machine-consumable checks for consistency and compliance |

## Framework Overview

This is a **Framework-as-Submodule** for microservices architecture using Python 3.12+ with the **Improved Hybrid Approach** for data access. It provides a centralized, updatable framework with proven patterns, AI agents, and comprehensive documentation to accelerate development.

> **🏗️ For a complete overview of the architecture, see the [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation).**

**CRITICAL ARCHITECTURE CONSTRAINTS**:
1. Different service types (FastAPI, Aiogram, AsyncIO workers) MUST run in separate processes/containers to avoid event loop conflicts
2. Business services MUST access data ONLY via HTTP APIs to data services - direct database connections are PROHIBITED
3. Use RabbitMQ for inter-service communication and event publishing
4. **NAMING CONVENTION**: See [naming conventions](docs/LINKS_REFERENCE.md#ide-rules-and-patterns) for mandatory naming standards

## Development Commands

> **📋 CANONICAL COMMAND REFERENCE**: For all development commands, see [Development Commands](docs/LINKS_REFERENCE.md#developer-guides). This includes Docker operations, testing, deployment, troubleshooting, and more.

## Architecture Guidelines

> **🏗️ ARCHITECTURAL FOUNDATION**: For complete architectural guidelines, constraints, and patterns, see [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation). This section provides a high-level overview.

This project implements the **Improved Hybrid Approach**, a microservices architecture that combines centralized data access with distributed business logic. Key principles include HTTP-only data access, strict service type separation, and event-driven communication.


## Cursor Rules Integration

**Comprehensive implementation rules available organized by category**

See [IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules-and-patterns) for complete overview of all 15 rule files covering architecture, service patterns, infrastructure, and observability.

## Important Notes

- **Implementation Status**: Infrastructure and service framework are complete. Business logic implementation should follow rule patterns
- **Environment Setup**: Create `.env.example` template (if not auto-generated by AI), then copy to `.env` and configure for your environment
- **Service Separation**: Each service type runs in separate containers to avoid event loop conflicts
- **Testing Standards**: Use real database instances (via testcontainers), achieve 100% coverage for critical paths
- **Type Annotations**: All functions must have full type hints (enforced by mypy>=1.8.0)
- **Security Focus**: Implement OAuth2/JWT, HTTPS, rate limiting, and proper error handling
- **Troubleshooting**: For common issues and solutions, see [Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)

## Framework Management

### Framework Submodule Operations
> **📋 COMPLETE SUBMODULE GUIDE**: See [README.md#framework-management](README.md#framework-management) and [Project Structure](docs/LINKS_REFERENCE.md#developer-guides) for detailed submodule operations and project setup.

```bash
# Quick reference - Update framework
git submodule update --remote .framework
```

### AI Development Guidelines
1. **Automatically scan framework** for patterns and rules documented in `docs/`
2. **Generate user code in `src/`** — never modify framework content when used as submodule
3. **Follow guidelines** for architecture compliance — see [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation)
4. **Apply checklists** from [Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides) to validate coverage of business requirements
5. **Cross-check commands and verification steps** via [Development Commands](docs/LINKS_REFERENCE.md#developer-guides)
