# Microservices Framework

> **🏗️ Framework-as-Submodule** - Centralised microservices architecture framework designed to be used as a Git submodule in your projects. Provides proven patterns, AI agents, and complete documentation for rapid development.

## 🎯 What This Solves and Who It's For

### **The Problem**
Creating microservices architecture is a complex task requiring:
- Deep understanding of architectural patterns
- Proper infrastructure setup (databases, monitoring, queues)
- Following numerous rules and standards
- Months of development time "from scratch"

### **The Solution: Framework-as-Submodule**
This is not just documentation, but a **living framework** that:

1. **Connects as Git submodule** to your project - framework separate, your code separate
2. **Provides ready architecture** - proven "Improved Hybrid Approach" with PostgreSQL, MongoDB, RabbitMQ, full monitoring
3. **Updates centrally** - `git submodule update` and all projects get improvements
4. **AI reads rules automatically** from `.framework/docs/` - generates applications from business requirements
5. **Ready patterns** - for FastAPI, Aiogram, AsyncIO workers, PostgreSQL, MongoDB, RabbitMQ, Redis, Docker Compose, monitoring stack

### **Target Users:**
- **Python developers** - want to quickly create microservices applications
- **Development teams** - need standardized architectural solutions
- **AI systems** - for automatic application generation
- **Business analysts** - validate idea feasibility within the architecture

### **Result:**
Instead of months of architecture development - get production-ready applications in minutes/hours using standardized, updatable framework with AI automation.

## 🚀 Quick Start

```bash
# 1. Create your project
mkdir my_awesome_app && cd my_awesome_app && git init

# 2. Add framework as submodule
git submodule add <https://github.com/bgs2509/doc4microservices> .framework
git submodule init && git submodule update

# 3. Generate with AI (AI reads .framework/docs/ automatically)
# Ask AI: "Create [your app] using .framework/ patterns"

# 4. Deploy ready application
docker-compose up -d
```

### **Key Benefits:**
- **Separation** - Framework separate, your code separate
- **Updates** - `git submodule update --remote` gets new features
- **Standardization** - All projects use same rules
- **AI compatibility** - AI automatically finds patterns in `.framework/`

This transforms microservices application creation into a standardized, repeatable process.

## 🏗️ Project Structure

When you add this framework as a submodule, your project follows a clean separation pattern where the framework provides proven architecture patterns while your application code stays completely separate.

> **📋 DETAILED PROJECT STRUCTURE**: See [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md) *(or [.framework/docs/reference/PROJECT_STRUCTURE.md](.framework/docs/reference/PROJECT_STRUCTURE.md) when used as submodule)* for comprehensive directory organization, service types, and setup guidance.

## 💻 AI Generation Examples

**Example AI Prompts:**
```
Create a task management application using the .framework/ patterns:
- FastAPI service for REST API
- Telegram bot service for notifications
- AsyncIO workers for background tasks
- Follow the Improved Hybrid Approach from .framework/docs/
```

```
Build an e-commerce platform with .framework/ architecture:
- Product catalog and search (FastAPI)
- Order processing workers (AsyncIO)
- Customer notifications (Aiogram bot)
- Use PostgreSQL and MongoDB data services
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

The framework implements the **Improved Hybrid Approach** - a microservices pattern combining centralized data access with distributed business logic.

### Key Characteristics
- **Centralized Data Services**: Two dedicated services handle ALL database operations
- **Business Logic Separation**: Business services contain ONLY business logic
- **HTTP-Only Data Access**: No direct database connections in business services
- **Event-Driven Communication**: RabbitMQ for inter-service messaging
- **Service Type Isolation**: Each service type runs in separate processes

> **📖 COMPLETE ARCHITECTURE DETAILS**: See [Architecture Guide](docs/LINKS_REFERENCE.md#основная-документация) for detailed principles, constraints, diagrams, and implementation guidelines.

## 📚 Documentation and AI Knowledge Base

This repository contains comprehensive documentation designed for both AI agents and human developers:

### For AI Agents
| Component | Purpose | Location |
|-----------|---------|----------|
| **🏗️ Main Entry Point** | Complete development guide and navigation | [CLAUDE.md](CLAUDE.md) |
| **🤖 AI Framework** | Automated application generation | [ai_agents/](ai_agents/) *(or [.framework/ai_agents/](.framework/ai_agents/) when used as submodule)* |
| **📋 Implementation Rules** | Service-specific patterns and constraints | [docs/](docs/) *(or [.framework/docs/](.framework/docs/) when used as submodule)* |
| **💻 Working Examples** | Complete reference implementations | [examples/](examples/) *(or [.framework/examples/](.framework/examples/) when used as submodule)* |

### For Human Developers
| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[CLAUDE.md](CLAUDE.md)** | Complete development guide | Start here - setup, architecture, commands |
| **[docs/reference/tech_stack.md](docs/reference/tech_stack.md)** *(or [.framework/docs/reference/tech_stack.md](.framework/docs/reference/tech_stack.md) when used as submodule)* | Technology specifications | Check versions, configurations |
| **[examples/index.md](examples/index.md)** *(or [.framework/examples/index.md](.framework/examples/index.md) when used as submodule)* | Working code examples | Understand implementation patterns |
| **[docs/reference/troubleshooting.md](docs/reference/troubleshooting.md)** *(or [.framework/docs/reference/troubleshooting.md](.framework/docs/reference/troubleshooting.md) when used as submodule)* | Problem solving | Debug issues, find solutions |

## 📋 Technology Stack

**Carefully selected technologies optimized for the Improved Hybrid Approach:**

### Core Technologies
- **Python 3.12+** - Unified runtime with advanced type system
- **FastAPI + Aiogram + AsyncIO** - Service type separation and specialization
- **PostgreSQL + MongoDB** - Dual database strategy for different data needs
- **Redis + RabbitMQ** - High-performance caching and messaging
- **Docker Compose** - Simple but powerful service orchestration

### Observability Stack
- **Prometheus** - Metrics collection, alerting rules, and performance monitoring
- **Grafana** - Rich visualization dashboards, alerting, and data exploration
- **Jaeger** - Distributed tracing, request flow analysis, and performance bottleneck identification
- **ELK Stack** (Elasticsearch, Logstash, Kibana) - Centralized logging, log analysis, and search
- **Node Exporter** - System metrics collection (CPU, memory, disk, network)
- **cAdvisor** - Container metrics and resource usage monitoring
- **AlertManager** - Alert routing, grouping, and notification management
- **Health Checks** - Service health endpoints and readiness probes

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

## 🔧 Framework Management

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

> **📋 COMPLETE SETUP GUIDE**: See [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md) *(or [.framework/docs/reference/PROJECT_STRUCTURE.md](.framework/docs/reference/PROJECT_STRUCTURE.md) when used as submodule)* for detailed project organization and development workflow.

### For AI Agents
1. **Automatically scan `.framework/`** for patterns, rules, and examples
2. **Generate user code in `src/`** - never modify `.framework/` content
3. **Follow `.framework/docs/` guidelines** for architecture compliance
4. **Use `.framework/ai_agents/`** for validation and generation tools

### Quick Links (within .framework/)
- **🏗️ Architecture Guide**: `.framework/docs/guides/ARCHITECTURE_GUIDE.md`
- **📋 Development Commands**: `.framework/docs/guides/DEVELOPMENT_COMMANDS.md`
- **🎯 Use Case Implementation**: `.framework/docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md`
- **🔧 Technology Stack**: `.framework/docs/reference/tech_stack.md`
- **💻 Working Examples**: `.framework/examples/index.md`
- **🐛 Troubleshooting**: `.framework/docs/reference/troubleshooting.md`
- **🚀 Live Demonstrations**: `.framework/use_cases/`

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**🚀 Ready to use this framework?** Add it as a submodule to your project: `git submodule add <repo-url> .framework`
