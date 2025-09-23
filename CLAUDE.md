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

7. **[examples/index.md](examples/index.md)** - **WORKING EXAMPLES**
   - 💻 Complete, runnable service implementations
   - 🎯 Real-world patterns and best practices
   - 🧪 Testing examples and patterns

8. **[docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)** - **PROBLEM SOLVING**
   - 🐛 Common issues and solutions
   - 🔍 Diagnostic procedures
   - 🚨 Emergency troubleshooting steps

### Specialized Documentation

10. **[docs/](docs/)** - **IDE RULES & PATTERNS** (architecture, services, infrastructure, observability, quality)
   - 🤖 Automated code generation rules
   - 📏 Service-specific implementation patterns
   - 🔧 Technology-specific guidelines

11. **[use_cases/](use_cases/)** - **CONCRETE EXAMPLES**
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
| 💻 **See working examples** | [examples/index.md](examples/index.md) |
| 🐛 **Solve problems** | [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md) |
| 🤖 **IDE rules & patterns** | [docs/INDEX.md#ide-rules--patterns](docs/INDEX.md#ide-rules--patterns) |

## 📚 Documentation Types Guide

> **🎯 UNDERSTANDING THE THREE-TIER APPROACH**: This project uses three complementary documentation approaches serving different audiences and purposes.

### Quick Reference
| Need | Documentation Type | Location | Target Users |
|------|-------------------|----------|--------------|
| 🎓 **Learn to code properly** | Educational Examples | [examples/](examples/) | Human developers, teams |
| 🤖 **AI-generated applications** | Automation Framework | [ai_agents/](ai_agents/) | AI systems, AI developers |
| 💻 **See working solutions** | Live Demonstrations | [use_cases/](use_cases/) | Business stakeholders, QA teams |

### 📊 **DOCUMENTATION TYPE COMPARISON**

#### **1. `examples/` - EDUCATIONAL DOCUMENTATION**

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

#### **2. `ai_agents/` - AI AUTOMATION FRAMEWORK**

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

#### **3. `use_cases/` - WORKING DEMONSTRATIONS**

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
1. **Learn** from `examples/` (HOW to code properly)
2. **Reference** `use_cases/` (WHAT working solutions look like)
3. **Ignore** `ai_agents/` (Not needed for manual development)

#### **For AI Systems:**
1. **Validate** using `ai_agents/business_validation/` (CAN it be built?)
2. **Generate** using `ai_agents/generators/` (TEMPLATE-based creation)
3. **Reference** `use_cases/` (WHAT the end result should be)
4. **Learn patterns** from `examples/` (HOW to implement correctly)

#### **For Business Users:**
1. **See working examples** in `use_cases/` (PROOF of capability)
2. **Request new features** via `ai_agents/` (AUTOMATED generation)
3. **Understand technical approach** via `examples/` (EDUCATION)

### ✅ **RECOMMENDATION: ALL THREE ARE ESSENTIAL**

Each serves a distinct and valuable purpose:
- **`examples/`**: Human education and standards
- **`ai_agents/`**: AI automation and generation
- **`use_cases/`**: Working demonstrations and proof-of-concept

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
4. **NAMING CONVENTION**: See [docs/architecture/naming_conventions.mdc](docs/architecture/naming_conventions.mdc) for mandatory naming standards

## Development Commands

> **📋 CANONICAL COMMAND REFERENCE**: For all development commands, see [docs/guides/DEVELOPMENT_COMMANDS.md](docs/guides/DEVELOPMENT_COMMANDS.md). This includes Docker operations, testing, deployment, troubleshooting, and more.

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

**Project Structure with Framework Submodule:**
```
my_awesome_app/                      # Your project repository
├── .framework/                      # Git submodule (this repository)
│   ├── docs/                       # Architecture rules and patterns
│   ├── ai_agents/                  # AI generators and validators
│   ├── examples/                   # Reference implementations
│   ├── use_cases/                  # Working applications
│   └── CLAUDE.md                   # AI instructions
├── README.md                        # Your project documentation
├── docker-compose.yml               # Your project infrastructure
├── .env.example                     # Your project configuration template (created by AI or manually)
└── src/                            # Your application code
    ├── services/                   # Microservices
    │   ├── api_service/            # FastAPI REST API service
    │   │   ├── Dockerfile          # Service-specific container
    │   │   ├── main.py             # Service implementation
    │   │   └── requirements.txt    # Service dependencies
    │   ├── bot_service/            # Aiogram Telegram bot service
    │   │   ├── Dockerfile
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── worker_service/         # AsyncIO background workers
    │   │   ├── Dockerfile
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── db_postgres_service/    # PostgreSQL data access service
    │   │   ├── Dockerfile
    │   │   └── main.py
    │   └── db_mongo_service/       # MongoDB data access service
    │       ├── Dockerfile
    │       └── main.py
    ├── shared/                     # Shared components
    │   ├── dtos.py                # Data transfer objects
    │   ├── events.py              # Event schemas
    │   └── utils.py               # Common utilities
    ├── config/                     # Configuration management
    │   ├── settings.py            # Centralized settings
    │   └── logging.py             # Logging configuration
    └── tests/                     # Test suites
        ├── unit/                  # Unit tests per service
        ├── integration/           # Integration tests
        └── conftest.py            # Test configuration
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
- **Complete Examples**: See [examples/index.md](examples/index.md) for comprehensive, working implementations of all service types
- **Environment Setup**: Create `.env.example` template (if not auto-generated by AI), then copy to `.env` and configure for your environment
- **Service Separation**: Each service type runs in separate containers to avoid event loop conflicts
- **Testing Standards**: Use real database instances (via testcontainers), achieve 100% coverage for critical paths
- **Type Annotations**: All functions must have full type hints (enforced by mypy>=1.8.0)
- **Security Focus**: Implement OAuth2/JWT, HTTPS, rate limiting, and proper error handling
- **Troubleshooting**: For common issues and solutions, see [docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)

## Framework Management

### Framework Submodule Operations
```bash
# Update framework to latest version
git submodule update --remote .framework
git add .framework && git commit -m "Update framework"

# Clone project with framework
git clone --recursive <your-project-repo>

# If you forgot --recursive
git submodule init && git submodule update
```

### AI Development Guidelines
1. **Automatically scan framework** for patterns, rules, and examples
2. **Generate user code in `src/`** - never modify framework content when used as submodule
3. **Follow `docs/` guidelines** for architecture compliance
4. **Use `ai_agents/`** for validation and generation tools
5. **Reference `examples/`** for implementation patterns
6. **Validate against `use_cases/`** for working examples
