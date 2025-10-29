# Microservices Framework

<div align="center">

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](./docs/INDEX.md)
[![Framework](https://img.shields.io/badge/type-framework--as--submodule-orange.svg)](./docs/guides/architecture-guide.md)
[![AI Ready](https://img.shields.io/badge/AI-ready-purple.svg)](./docs/guides/ai-code-generation-master-workflow.md)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](./templates/infrastructure/docker-compose.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

</div>

> **Framework-as-Submodule** - Centralised microservices architecture framework designed to be used as a Git submodule in your projects. Provides proven patterns, AI agents, and complete documentation for rapid development.

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

## ⚡ Quick Start

```bash
# 1. Create your project
mkdir my_awesome_app && cd my_awesome_app && git init

# 2. Add framework as submodule
git submodule add https://github.com/yourusername/doc4microservices .framework
git submodule init && git submodule update

# 3. Generate with AI (AI reads .framework/docs/ automatically)
# Ask AI: "Create [your app] using .framework/ patterns"

# 4. Use documentation
# Apply patterns from docs/atomic/ when setting up your environment in the working project.
# See:
# - docs/atomic/infrastructure/containerization/docker-compose-setup.md
# - docs/reference/project-structure.md
```

## 🚀 Features

### Architecture & Patterns
- ✅ **Improved Hybrid Approach** - Centralized data services with business logic separation
- ✅ **HTTP-only data access** - No direct database connections in business services
- ✅ **Event-driven architecture** - RabbitMQ for async communication
- ✅ **Service separation** - Clear boundaries between service types
- ✅ **4 Maturity Levels** - From PoC (5 min) to Production (30 min)

### Technology Stack
- 🐍 **Python 3.11+** with type hints and async/await
- ⚡ **FastAPI** for high-performance REST APIs
- 🤖 **Aiogram** for Telegram bot development
- 🔄 **AsyncIO** workers for background tasks
- 🐘 **PostgreSQL** with SQLAlchemy ORM
- 🍃 **MongoDB** for document storage
- 🐰 **RabbitMQ** for message queuing
- 🔴 **Redis** for caching and sessions
- 🐳 **Docker & Docker Compose** for containerization
- 📊 **Prometheus + Grafana** for monitoring

### AI & Automation
- 🤖 **AI-ready documentation** - Structured for LLM consumption
- 📝 **7-stage workflow** - Complete AI agent guidance
- 🎯 **Navigation matrix** - Stage-by-stage documentation mapping
- 📋 **Templates & checklists** - Ready-to-use patterns
- 🔄 **Auto-generation** - From requirements to working code

### Documentation
- 📚 **200+ documentation files** - Comprehensive coverage
- 🔍 **172 atomic modules** - Focused, single-purpose docs
- 🗺️ **Clear navigation** - INDEX.md as entry point
- 🎓 **Learning path** - Progressive complexity levels
- 💡 **Real examples** - Working code samples

## 📖 Documentation Structure

```
docs/
├── INDEX.md                    # Main entry point
├── guides/                     # Step-by-step guides
│   ├── architecture-guide.md   # Architecture overview
│   └── ai-code-generation-master-workflow.md
├── atomic/                     # Atomic documentation modules
│   ├── architecture/           # Architecture patterns
│   ├── services/               # Service implementations
│   ├── databases/              # Database patterns
│   ├── infrastructure/         # Infrastructure setup
│   └── ...                     # 10+ categories
├── reference/                  # Reference materials
│   ├── tech_stack.md          # Technology versions
│   ├── maturity-levels.md     # 4 maturity levels
│   └── agent-toolbox.md       # AI agent commands
└── checklists/                # Validation checklists
```

## 🏗️ Project Structure

When using as submodule:

```
your_project/
├── .framework/                 # This framework as submodule
│   ├── docs/                   # All documentation
│   ├── templates/              # Service templates
│   └── ...
├── services/                   # Your microservices
│   ├── finance_lending_api/    # Business API service
│   ├── finance_lending_bot/    # Telegram bot service
│   └── data_postgres_api/      # Data access service
├── docker-compose.yml          # Your compose configuration
└── .env.example               # Your environment variables
```

## 🔧 Requirements

- Python 3.11 or higher
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.34+
- 8GB RAM minimum (16GB recommended)
- 20GB disk space

## 💻 Installation

### As Framework User

```bash
# Clone with submodule
git clone --recurse-submodules https://github.com/your-org/your-project
cd your-project

# Or add to existing project
git submodule add https://github.com/yourusername/doc4microservices .framework
git submodule init && git submodule update

# Copy templates
cp -r .framework/templates/infrastructure/* .
cp .framework/templates/services/template_business_api services/your_service_api

# Start development
docker-compose up -d
```

### For Framework Development

```bash
# Clone repository
git clone https://github.com/yourusername/doc4microservices
cd doc4microservices

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run documentation audit
python scripts/audit_docs.py
```

## 🤝 Contributing

We love your input! We want to make contributing to this project as easy and transparent as possible. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Quick ways to contribute:
- Report bugs via [GitHub Issues](https://github.com/yourusername/doc4microservices/issues)
- Suggest features and improvements
- Submit pull requests with bug fixes
- Improve documentation
- Share your success stories

## 📋 Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/yourusername/doc4microservices/tags).

Current stable version: **1.0.0**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This means you can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

## 🔒 Security

For security issues, please see our [Security Policy](SECURITY.md). Please do NOT open public issues for security vulnerabilities.

## 🙏 Acknowledgments

- Thanks to all [contributors](https://github.com/yourusername/doc4microservices/graphs/contributors)
- Inspired by microservices best practices from Netflix, Uber, and Spotify
- Built with love for the Python community

## 📞 Support

- 📖 [Documentation](./docs/INDEX.md)
- 💬 [Discussions](https://github.com/yourusername/doc4microservices/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/doc4microservices/issues)
- 📧 Email: your-email@example.com

## 🗺️ Roadmap

See our [public roadmap](https://github.com/yourusername/doc4microservices/projects) for planned features.

### Coming Soon
- [ ] Kubernetes deployment templates
- [ ] AWS/GCP/Azure terraform modules
- [ ] GraphQL API support
- [ ] gRPC service templates
- [ ] More AI agent integrations

## 📊 Stats

- 📁 **200+** documentation files
- 🏗️ **5** service templates
- 📚 **172** atomic documentation modules
- ⏱️ **5-30 min** from idea to deployment
- 🎯 **95.9/100** documentation health score

---

<div align="center">

**Built with ❤️ for the microservices community**

[Report Bug](https://github.com/yourusername/doc4microservices/issues) · [Request Feature](https://github.com/yourusername/doc4microservices/issues) · [Documentation](./docs/INDEX.md)

</div>