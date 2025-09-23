# Microservices Framework

> **🏗️ Framework-as-Submodule** - Centralised microservices architecture framework designed to be used as a Git submodule in your projects. Provides proven patterns, AI agents, and complete documentation for rapid development.

## 🎯 What This Is

A **centralised microservices framework** designed to be included as a Git submodule in your projects, providing:

- **📚 Architecture Documentation** - Complete patterns, rules, and best practices
- **🤖 AI Agent Framework** - Automated code generation and validation tools
- **💻 Working Examples** - Production-ready service implementations
- **🏗️ Project Templates** - Standardised structure for microservices applications

### Framework-as-Submodule Workflow

1. **📁 Create your project repository** - `mkdir my_awesome_app && cd my_awesome_app && git init`
2. **🔗 Add framework as submodule** - `git submodule add <framework-repo-url> .framework`
3. **🤖 AI reads framework rules** - AI agents automatically find patterns in `.framework/docs/`
4. **🚀 Generate your application** - AI creates services in `src/` following framework guidelines
5. **⚡ Deploy and iterate** - Framework provides infrastructure and development tools

## 🏗️ Project Structure with Framework Submodule

When you add this framework as a submodule, your project structure becomes:

```
my_awesome_app/                    # Your project repository
├── .framework/                    # Git submodule (this repository)
│   ├── docs/                     # Architecture rules and patterns
│   ├── ai_agents/                # AI generators and validators
│   ├── examples/                 # Reference implementations
│   ├── use_cases/                # Working applications
│   └── CLAUDE.md                 # AI instructions
├── README.md                      # Your project documentation
├── docker-compose.yml             # Your project infrastructure
├── .env.example                   # Your project configuration
└── src/                          # Your application code
    ├── services/                 # Microservices
    │   ├── api_service/          # FastAPI REST API service
    │   │   ├── Dockerfile        # Service-specific container
    │   │   ├── main.py           # Service implementation
    │   │   └── requirements.txt  # Service dependencies
    │   ├── bot_service/          # Aiogram Telegram bot service
    │   │   ├── Dockerfile
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── worker_service/       # AsyncIO background workers
    │   │   ├── Dockerfile
    │   │   ├── main.py
    │   │   └── requirements.txt
    │   ├── db_postgres_service/  # PostgreSQL data access service
    │   │   ├── Dockerfile
    │   │   └── main.py
    │   └── db_mongo_service/     # MongoDB data access service
    │       ├── Dockerfile
    │       └── main.py
    ├── shared/                   # Shared components
    │   ├── dtos.py              # Data transfer objects
    │   ├── events.py            # Event schemas
    │   └── utils.py             # Common utilities
    ├── config/                   # Configuration management
    │   ├── settings.py          # Centralized settings
    │   └── logging.py           # Logging configuration
    └── tests/                   # Test suites
        ├── unit/                # Unit tests per service
        ├── integration/         # Integration tests
        └── conftest.py          # Test configuration
```

## 🚀 How to Use This Framework

### Step 1: Add Framework to Your Project
```bash
# Create your project repository
mkdir my_awesome_app
cd my_awesome_app
git init

# Add this framework as a submodule
git submodule add https://github.com/your-org/microservices-framework.git .framework
git submodule init
git submodule update
```

### Step 2: Generate Your Application with AI
AI agents automatically find framework rules in `.framework/` directory:

**Example AI Prompt:**
```
Create a task management application using the .framework/ patterns:
- FastAPI service for REST API
- Telegram bot service for notifications
- AsyncIO workers for background tasks
- Follow the Improved Hybrid Approach from .framework/docs/
```

### Step 3: Deploy and Run
```bash
# AI generates your code in src/
cp .framework/templates/.env.example .env
# Edit .env with your configuration
docker-compose up -d
```

## 🤖 AI Agent Framework

This project includes a comprehensive AI framework for generating applications:

### Business Validation
- **Feasibility Checker** - Validates business ideas against architectural constraints
- **Domain Classifier** - Identifies business patterns and optimal service allocation
- **Constraint Validator** - Ensures compliance with Improved Hybrid Approach

### Code Generation
- **Service Templates** - Production-ready templates for FastAPI, Aiogram, AsyncIO workers
- **Variable Substitution** - Business-specific customization of proven patterns
- **Quality Validation** - Automated code quality and architecture compliance checks

### Deployment Automation
- **Docker Compose Generator** - Complete infrastructure and service orchestration
- **Environment Configuration** - Secure configuration templates and examples
- **Health Monitoring** - Production-ready observability and health checks

## 🏗 Architecture Overview

### Improved Hybrid Approach

```mermaid
graph TB
    subgraph "Business Services (src/services/)"
        API[FastAPI Service :8000]
        BOT[Aiogram Bot]
        WORKER[AsyncIO Workers]
    end

    subgraph "Data Services (src/services/)"
        PG[PostgreSQL Service :8001]
        MONGO[MongoDB Service :8002]
    end

    subgraph "Infrastructure (Docker Compose)"
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

### Key Architectural Principles

- **🔗 HTTP-Only Data Access** - Business services communicate with data services via HTTP APIs only
- **🏗️ Service Type Separation** - FastAPI, Aiogram, and AsyncIO services run in separate containers
- **📡 Event-Driven Communication** - RabbitMQ for asynchronous inter-service messaging
- **📊 Complete Observability** - Prometheus, Grafana, Jaeger, and ELK stack integration
- **🧪 Production-Ready Testing** - Real database testing with testcontainers
- **🔒 Security First** - OAuth2/JWT authentication, HTTPS, rate limiting

## 📚 Documentation and AI Knowledge Base

This repository contains comprehensive documentation designed for both AI agents and human developers:

### For AI Agents
| Component | Purpose | Location |
|-----------|---------|----------|
| **🤖 AI Framework** | Automated application generation | [ai_agents/](ai_agents/) |
| **📋 Implementation Rules** | Service-specific patterns and constraints | [docs/](docs/) |
| **💻 Working Examples** | Complete reference implementations | [examples/](examples/) |

### For Human Developers
| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[CLAUDE.md](CLAUDE.md)** | Complete development guide | Start here - setup, architecture, commands |
| **[docs/reference/tech_stack.md](docs/reference/tech_stack.md)** | Technology specifications | Check versions, configurations |
| **[examples/index.md](examples/index.md)** | Working code examples | Understand implementation patterns |
| **[docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)** | Problem solving | Debug issues, find solutions |

## 📋 Technology Stack

**Carefully selected technologies optimized for the Improved Hybrid Approach:**

### Core Technologies
- **Python 3.12+** - Unified runtime with advanced type system
- **FastAPI + Aiogram + AsyncIO** - Service type separation and specialization
- **PostgreSQL + MongoDB** - Dual database strategy for different data needs
- **Redis + RabbitMQ** - High-performance caching and messaging
- **Docker Compose** - Simple but powerful service orchestration

### Observability Stack
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Jaeger** - Distributed tracing
- **ELK Stack** - Centralized logging and search

### Development Tools
- **UV** - Fast Python package management
- **Ruff** - Lightning-fast Python linting
- **MyPy** - Static type checking
- **Testcontainers** - Real database testing

## ✨ Benefits for Development Teams

### For AI-Assisted Development
- **🎯 Zero Architecture Decisions** - Pre-validated patterns and technology choices
- **⚡ Rapid Prototyping** - From business idea to running application in minutes
- **🔄 Consistent Quality** - AI generates production-ready code following best practices
- **📈 Scalable Patterns** - Applications can grow from prototype to production

### For Traditional Development
- **📚 Comprehensive Patterns** - Working examples and implementation guidelines
- **🛡️ Risk Mitigation** - Battle-tested architectural constraints and best practices
- **🔧 Developer Experience** - Complete tooling and automation setup
- **👥 Team Alignment** - Consistent coding standards and patterns

## 🎯 Example Applications AI Can Generate

✅ **E-commerce Platform** - Product catalog, orders, payments, user management, analytics
✅ **Project Management Tool** - Tasks, projects, time tracking, team collaboration, reporting
✅ **Content Management System** - Articles, media, user permissions, publishing workflows
✅ **Social Platform** - User profiles, posts, messaging, engagement analytics
✅ **IoT Data Platform** - Device management, real-time data ingestion, analytics dashboards
✅ **Financial Application** - Account management, transactions, reporting, compliance

## 🔗 Getting Started

### For Project Creators
1. **Create new repository** - `mkdir my_project && cd my_project && git init`
2. **Add framework submodule** - `git submodule add <this-repo-url> .framework`
3. **Initialize submodule** - `git submodule init && git submodule update`
4. **Use AI to generate code** - AI will automatically read `.framework/` rules

### For AI Agents
1. **Automatically scan `.framework/`** for patterns, rules, and examples
2. **Generate user code in `src/`** - never modify `.framework/` content
3. **Follow `.framework/docs/` guidelines** for architecture compliance
4. **Use `.framework/ai_agents/`** for validation and generation tools

### Framework Submodule Management
```bash
# Update framework to latest version
git submodule update --remote .framework
git add .framework && git commit -m "Update framework"

# Clone project with framework
git clone --recursive <your-project-repo>

# If you forgot --recursive
git submodule init && git submodule update
```

### Quick Links (within .framework/)
- **🏗️ Architecture Guide**: `.framework/docs/guides/ARCHITECTURE_GUIDE.md`
- **📋 Development Commands**: `.framework/docs/guides/DEVELOPMENT_COMMANDS.md`
- **🔧 Technology Stack**: `.framework/docs/reference/tech_stack.md`
- **💻 Examples**: `.framework/examples/`

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**🚀 Ready to use this framework?** Add it as a submodule to your project: `git submodule add <repo-url> .framework`