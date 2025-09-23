# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this microservices framework.

> **📍 CONTEXT**: This framework can be used in two ways:
> - **Direct**: Working in this repository directly (use paths like `docs/`, `examples/`)
> - **Submodule**: Added as `.framework/` submodule to your project (use paths like `.framework/docs/`, `.framework/examples/`)
>
> The paths below assume **direct usage**. When used as submodule, prefix all paths with `.framework/`.

## 📚 Documentation Hierarchy

> **🎯 NAVIGATION GUIDE**: This project follows a clear documentation structure. Each file has a specific purpose and avoids duplication.

### Primary Documentation (Essential Reading)

1. **[CLAUDE.md](CLAUDE.md)** (this file) - **MAIN ENTRY POINT**
   - 🏗️ Project overview and navigation guide
   - 🚀 Development workflow and setup instructions
   - 📋 Links to specialized documentation

2. **[Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation)** - **TECHNOLOGY AUTHORITY**
   - 🔧 Complete technology specifications and versions
   - 📦 Library compatibility and requirements
   - ⚙️ Infrastructure configuration details

3. **[README.md](README.md)** - **PROJECT INTRODUCTION**
   - 📖 High-level project description
   - ⚡ Quick start instructions
   - 🔗 Links to detailed documentation

### Implementation Guides

4. **[Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation)** - **ARCHITECTURE AUTHORITY**
   - 🏗️ Improved Hybrid Approach architecture
   - ⚠️ Mandatory constraints and principles
   - 🔧 Service types and communication patterns

5. **[Development Commands](docs/LINKS_REFERENCE.md#developer-guides)** - **COMMANDS AUTHORITY**
   - 📋 Complete development commands reference
   - 🐳 Docker operations and service management
   - 🔍 Troubleshooting and diagnostic commands

6. **[Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides)** - **USE CASE CREATION**
   - 📋 Step-by-step use case development
   - ✅ Compliance checklists and templates
   - 🏗️ Production-ready implementation patterns

### Reference Materials

7. **[Examples Index](docs/LINKS_REFERENCE.md#examples-and-templates)** - **WORKING EXAMPLES**
   - 💻 Complete, runnable service implementations
   - 🎯 Real-world patterns and best practices
   - 🧪 Testing examples and patterns

8. **[Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)** - **PROBLEM SOLVING**
   - 🐛 Common issues and solutions
   - 🔍 Diagnostic procedures
   - 🚨 Emergency troubleshooting steps

### Specialized Documentation

10. **[IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules--patterns)** - **IDE RULES & PATTERNS** (architecture, services, infrastructure, observability, quality)
   - 🤖 Automated code generation rules
   - 📏 Service-specific implementation patterns
   - 🔧 Technology-specific guidelines

11. **[Working Demonstrations](docs/LINKS_REFERENCE.md#examples-and-templates)** - **CONCRETE EXAMPLES**
    - 🎯 Real working use case implementations
    - 📚 Domain-specific documentation
    - 🚀 Deployment and usage examples

### Quick Navigation

| Need | Go To |
|------|-------|
| 🏁 **Get started quickly** | [README.md](README.md) → [CLAUDE.md - Development Commands](#development-commands) |
| 🏗️ **Understand architecture** | [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) |
| 📋 **Run commands** | [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) |
| 🎯 **Create new use case** | [Use Case Implementation](docs/LINKS_REFERENCE.md#developer-guides) |
| 🔧 **Check versions/config** | [Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation) |
| 💻 **See working examples** | [Examples Index](docs/LINKS_REFERENCE.md#examples-and-templates) |
| 🐛 **Solve problems** | [Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides) |
| 🤖 **IDE rules & patterns** | [IDE Rules & Patterns](docs/LINKS_REFERENCE.md#ide-rules--patterns) |

## 📚 Documentation Types Guide

> **🎯 UNDERSTANDING THE THREE-TIER APPROACH**: This project uses three complementary documentation approaches serving different audiences and purposes.

### Quick Reference
| Need | Documentation Type | Location | Target Users |
|------|-------------------|----------|--------------|
| 🎓 **Learn to code properly** | Educational Examples | [Examples Index](docs/LINKS_REFERENCE.md#examples-and-templates) | Human developers, teams |
| 🤖 **AI-generated applications** | Automation Framework | [AI Agents](docs/LINKS_REFERENCE.md#examples-and-templates) | AI systems, AI developers |
| 💻 **See working solutions** | Live Demonstrations | [Working Demonstrations](docs/LINKS_REFERENCE.md#examples-and-templates) | Business stakeholders, QA teams |

### 📊 **DOCUMENTATION TYPE COMPARISON**

#### **1. `examples/` *(or `.framework/examples/` when used as submodule)* - EDUCATIONAL DOCUMENTATION**

**🎯 Primary Purpose:**
- Teaching developers HOW to implement services correctly
- Demonstrating best practices and architectural patterns
- Providing production-ready code examples with explanations

**👥 Target Users:**
- Human developers learning the architecture
- Senior developers implementing new services
- Teams establishing coding standards
- Code reviewers verifying compliance

**🛠️ Way of Working:**
- Study-oriented: Read → Understand → Apply
- Pattern-based: Shows ideal implementations
- Educational: Explains WHY things are done certain ways
- Reference: Developers copy and adapt patterns

**📋 Key Characteristics:**
- Format: Markdown documentation with code snippets
- Scope: Individual service patterns and practices
- Detail Level: Deep technical explanations
- Code Style: Commented, explained, educational
- Updates: When architectural patterns evolve

#### **2. `ai_agents/` *(or `.framework/ai_agents/` when used as submodule)* - AI AUTOMATION FRAMEWORK**

**🎯 Primary Purpose:**
- Enabling AI to automatically generate complete applications
- Providing systematic rules and templates for code generation
- Validating business requirements against architecture constraints

**👥 Target Users:**
- AI systems (Claude, GPT, etc.) for autonomous coding
- AI developers building agentic coding systems
- Business analysts validating feasibility
- DevOps engineers for automated deployment

**🛠️ Way of Working:**
- Generation-oriented: Requirements → Validation → Generate → Deploy
- Template-based: Variable substitution in code templates
- Systematic: Follows strict validation and generation workflow
- Autonomous: Minimal human intervention required

**📋 Key Characteristics:**
- Format: YAML configs + Python templates with {{variables}}
- Scope: Complete application generation (all services)
- Detail Level: Systematic rules and constraints
- Code Style: Template variables, generation-focused
- Updates: When adding new business domains or patterns

#### **3. `use_cases/` *(or `.framework/use_cases/` when used as submodule)* - WORKING DEMONSTRATIONS**

**🎯 Primary Purpose:**
- Demonstrating complete, functional applications
- Proving the architecture works in real scenarios
- Providing reference implementations for specific domains

**👥 Target Users:**
- Business stakeholders seeing working solutions
- Developers needing complete examples
- QA teams for testing and validation
- Product managers understanding capabilities

**🛠️ Way of Working:**
- Demonstration-oriented: Deploy → Use → Learn → Adapt
- Domain-specific: Real business logic implementations
- Functional: Actually runs and provides value
- Inspirational: Shows what's possible with the architecture

**📋 Key Characteristics:**
- Format: Complete Python applications with Docker configs
- Scope: Full business applications (Task Management, E-commerce, etc.)
- Detail Level: Production-ready implementations
- Code Style: Business logic, real-world complexity
- Updates: When adding new use case domains

### 🔄 **HOW THEY WORK TOGETHER**

#### **For Human Developers:**
1. **Learn** from `examples/` *(or `.framework/examples/` when used as submodule)* (HOW to code properly)
2. **Reference** `use_cases/` *(or `.framework/use_cases/` when used as submodule)* (WHAT working solutions look like)
3. **Ignore** `ai_agents/` *(or `.framework/ai_agents/` when used as submodule)* (Not needed for manual development)

#### **For AI Systems:**
1. **Validate** using `ai_agents/business_validation/` *(or `.framework/ai_agents/business_validation/` when used as submodule)* (CAN it be built?)
2. **Generate** using `ai_agents/generators/` *(or `.framework/ai_agents/generators/` when used as submodule)* (TEMPLATE-based creation)
3. **Reference** `use_cases/` *(or `.framework/use_cases/` when used as submodule)* (WHAT the end result should be)
4. **Learn patterns** from `examples/` *(or `.framework/examples/` when used as submodule)* (HOW to implement correctly)

#### **For Business Users:**
1. **See working examples** in `use_cases/` *(or `.framework/use_cases/` when used as submodule)* (PROOF of capability)
2. **Request new features** via `ai_agents/` *(or `.framework/ai_agents/` when used as submodule)* (AUTOMATED generation)
3. **Understand technical approach** via `examples/` *(or `.framework/examples/` when used as submodule)* (EDUCATION)

### ✅ **RECOMMENDATION: ALL THREE ARE ESSENTIAL**

Each serves a distinct and valuable purpose:
- **`examples/`** *(or `.framework/examples/` when used as submodule)*: Human education and standards
- **`ai_agents/`** *(or `.framework/ai_agents/` when used as submodule)*: AI automation and generation
- **`use_cases/`** *(or `.framework/use_cases/` when used as submodule)*: Working demonstrations and proof-of-concept

The overlap is intentional and beneficial - they reinforce each other while serving different primary purposes.

## Framework Overview

This is a **Framework-as-Submodule** for microservices architecture using Python 3.12+ with the **Improved Hybrid Approach** for data access. When added as a Git submodule (`.framework/`), it provides:

- **Centralized Framework**: Proven patterns, AI agents, and complete documentation
- **Separation of Concerns**: Framework code separate from your application code
- **Automatic Updates**: `git submodule update --remote` gets latest improvements
- **AI Compatibility**: AI systems automatically scan the framework for patterns and rules

The framework includes:

- **Infrastructure**: Complete observability stack with Prometheus, Grafana, Jaeger, ELK, and dual database infrastructure (PostgreSQL + MongoDB)
- **Data Services**: Centralized data access services (db_postgres_service, db_mongo_service) implementing the Database Service pattern
- **Business Services**: Business logic services (api_service, bot_service, worker_service) that access data via HTTP APIs only
- **Architecture**: DDD/Hexagonal patterns with clear separation between data access and business logic

**Current Status**: Complete Improved Hybrid Approach implementation with PostgreSQL and MongoDB data services. Business services access data via HTTP only - no direct database connections.

**CRITICAL ARCHITECTURE CONSTRAINTS**:
1. Different service types (FastAPI, Aiogram, AsyncIO workers) MUST run in separate processes/containers to avoid event loop conflicts
2. Business services MUST access data ONLY via HTTP APIs to data services - direct database connections are PROHIBITED
3. Use RabbitMQ for inter-service communication and event publishing
4. **NAMING CONVENTION**: See [naming conventions](docs/LINKS_REFERENCE.md#ide-rules--patterns) for mandatory naming standards

## Development Commands

> **📋 CANONICAL COMMAND REFERENCE**: For all development commands, see [development commands](docs/LINKS_REFERENCE.md#developer-guides). This includes Docker operations, testing, deployment, troubleshooting, and more.

### Quick Reference for Framework Usage
```bash
# 1. Add framework as submodule to your project
mkdir my_awesome_app && cd my_awesome_app && git init
git submodule add <framework-repo-url> .framework
git submodule init && git submodule update

# 2. Generate application with AI (AI reads framework patterns)
# Ask AI: "Create [your app] using framework patterns"

# 3. Quick start your generated application
cp .env.example .env
docker-compose up -d
uv sync --dev
curl http://localhost:8000/health
```

**Essential operations:**
- **Framework Update**: `git submodule update --remote .framework`
- **Docker**: [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) (Docker operations)
- **Testing**: [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) (Testing commands)
- **Troubleshooting**: [Development Commands](docs/LINKS_REFERENCE.md#developer-guides) (Troubleshooting commands)

## Architecture Guidelines

> **🏗️ ARCHITECTURAL FOUNDATION**: For complete architectural guidelines, constraints, and patterns, see [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation). This section provides a high-level overview.

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

> **📋 COMPLETE ARCHITECTURE DETAILS**: See [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) for detailed constraints, patterns, and implementation guidelines.

### Docker Compose Organization

#### RECOMMENDED: Single Root Compose Setup
Use one main `docker-compose.yml` in the project root, not individual compose files per service.

**Project Organization:**
When used as submodule, projects follow a clean separation pattern: framework provides patterns, user code stays in `src/`.

> **📋 COMPLETE PROJECT STRUCTURE**: See [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md) *(or [.framework/docs/reference/PROJECT_STRUCTURE.md](.framework/docs/reference/PROJECT_STRUCTURE.md) when used as submodule)* for detailed directory organization, service types, and development workflow.

**Benefits:**
- **Data Service Isolation**: Centralized database expertise and optimization
- **Business Logic Focus**: Services contain only business logic, no database concerns
- **Shared Infrastructure**: Redis, RabbitMQ, observability stack shared across all services
- **Proper Service Networking**: HTTP communication between business and data services
- **Unified Environment**: Single command deployment with proper dependency management

### Service Types and Implementation Status
**Complete technology specifications and versions**: [docs/reference/tech_stack.md](docs/reference/tech_stack.md) *(or [.framework/docs/reference/tech_stack.md](.framework/docs/reference/tech_stack.md) when used as submodule)*

**Service Architecture:**
- **Data Services**: PostgreSQL and MongoDB data access services (Ports: 8001, 8002)
- **Business Services**: FastAPI, Aiogram, AsyncIO workers (HTTP-only data access)
- **Infrastructure**: Complete observability and messaging stack

**Current Status**: Infrastructure and service framework complete, ready for business logic implementation.

**Service Implementation Guides:**
- Data access patterns: `docs/architecture/data-access-rules.mdc` *(or `.framework/docs/architecture/data-access-rules.mdc` when used as submodule)*
- MongoDB operations: `docs/infrastructure/mongodb_rules.mdc` *(or `.framework/docs/infrastructure/mongodb_rules.mdc` when used as submodule)*
- FastAPI patterns: `docs/services/fastapi_rules.mdc` *(or `.framework/docs/services/fastapi_rules.mdc` when used as submodule)*
- Aiogram patterns: `docs/services/aiogram_rules.mdc` *(or `.framework/docs/services/aiogram_rules.mdc` when used as submodule)*
- AsyncIO patterns: `docs/services/asyncio_rules.mdc` *(or `.framework/docs/services/asyncio_rules.mdc` when used as submodule)*

### Service Structure
For detailed service structure and architecture patterns, see [docs/reference/tech_stack.md](docs/reference/tech_stack.md) *(or [.framework/docs/reference/tech_stack.md](.framework/docs/reference/tech_stack.md) when used as submodule)* and `docs/architecture/ms_best_practices_rules.mdc` *(or `.framework/docs/architecture/ms_best_practices_rules.mdc` when used as submodule)*.

### Service-Specific Patterns

**Implementation patterns available in:**
- **FastAPI Services**: [docs/services/fastapi_rules.mdc](docs/services/fastapi_rules.mdc) *(or [.framework/docs/services/fastapi_rules.mdc](.framework/docs/services/fastapi_rules.mdc) when used as submodule)*
- **Aiogram Services**: [docs/services/aiogram_rules.mdc](docs/services/aiogram_rules.mdc) *(or [.framework/docs/services/aiogram_rules.mdc](.framework/docs/services/aiogram_rules.mdc) when used as submodule)*
- **AsyncIO Workers**: [docs/services/asyncio_rules.mdc](docs/services/asyncio_rules.mdc) *(or [.framework/docs/services/asyncio_rules.mdc](.framework/docs/services/asyncio_rules.mdc) when used as submodule)*
- **Database Access**: [docs/architecture/data-access-rules.mdc](docs/architecture/data-access-rules.mdc) *(or [.framework/docs/architecture/data-access-rules.mdc](.framework/docs/architecture/data-access-rules.mdc) when used as submodule)*
- **Testing Standards**: [docs/quality/testing-standards.mdc](docs/quality/testing-standards.mdc) *(or [.framework/docs/quality/testing-standards.mdc](.framework/docs/quality/testing-standards.mdc) when used as submodule)*

## Cursor Rules Integration

**Comprehensive implementation rules available in [docs/](docs/) *(or [.framework/docs/](.framework/docs/) when used as submodule)* organized by category**

See [docs/INDEX.md](docs/INDEX.md) *(or [.framework/docs/INDEX.md](.framework/docs/INDEX.md) when used as submodule)* for complete overview of all 15 rule files covering architecture, service patterns, infrastructure, and observability.

## Important Notes

- **Implementation Status**: Infrastructure and service framework are complete. Business logic implementation should follow `docs/` *(or `.framework/docs/` when used as submodule)* rule patterns
- **Complete Examples**: See [examples/index.md](examples/index.md) *(or [.framework/examples/index.md](.framework/examples/index.md) when used as submodule)* for comprehensive, working implementations of all service types
- **Environment Setup**: Create `.env.example` template (if not auto-generated by AI), then copy to `.env` and configure for your environment
- **Service Separation**: Each service type runs in separate containers to avoid event loop conflicts
- **Testing Standards**: Use real database instances (via testcontainers), achieve 100% coverage for critical paths
- **Type Annotations**: All functions must have full type hints (enforced by mypy>=1.8.0)
- **Security Focus**: Implement OAuth2/JWT, HTTPS, rate limiting, and proper error handling
- **Troubleshooting**: For common issues and solutions, see [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md) *(or [.framework/docs/reference/troubleshooting.md](.framework/docs/reference/troubleshooting.md) when used as submodule)*

## Framework Management

### Framework Submodule Operations
> **📋 COMPLETE SUBMODULE GUIDE**: See [README.md#framework-management](README.md#framework-management) and [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md) *(or [.framework/docs/reference/PROJECT_STRUCTURE.md](.framework/docs/reference/PROJECT_STRUCTURE.md) when used as submodule)* for detailed submodule operations and project setup.

```bash
# Quick reference - Update framework
git submodule update --remote .framework
```

### AI Development Guidelines
1. **Automatically scan framework** for patterns, rules, and examples
2. **Generate user code in `src/`** - never modify framework content when used as submodule
3. **Follow `docs/` *(or `.framework/docs/` when used as submodule)* guidelines** for architecture compliance
4. **Use `ai_agents/` *(or `.framework/ai_agents/` when used as submodule)*** for validation and generation tools
5. **Reference `examples/` *(or `.framework/examples/` when used as submodule)*** for implementation patterns
6. **Validate against `use_cases/` *(or `.framework/use_cases/` when used as submodule)*** for working examples
