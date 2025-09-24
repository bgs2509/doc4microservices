# Project Links Reference

> **🔗 CENTRAL REFERENCE**: All project documentation links in one place. Use this table instead of duplicating links in documents.

<a id="core-documentation"></a>
## Core Documentation

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Main Entry Point** | [CLAUDE.md](../CLAUDE.md) | `.framework/CLAUDE.md` | Complete developer guide |
| **Project Overview** | [README.md](../README.md) | `.framework/README.md` | Project introduction and quick start |
| **Architecture Guide** | [guides/ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md) | `.framework/docs/guides/ARCHITECTURE_GUIDE.md` | Canonical source of architectural principles |
| **Technical Specifications** | [reference/tech_stack.md](reference/tech_stack.md) | `.framework/docs/reference/tech_stack.md` | Technology versions and configurations |

<a id="developer-guides"></a>
## Developer Guides

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Development Commands** | [guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) | `.framework/docs/guides/DEVELOPMENT_COMMANDS.md` | All development commands |
| **Use Case Implementation** | [guides/USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md) | `.framework/docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md` | Step-by-step creation of new use cases |
| **Project Structure** | [reference/PROJECT_STRUCTURE.md](reference/PROJECT_STRUCTURE.md) | `.framework/docs/reference/PROJECT_STRUCTURE.md` | Directory and file organization |
| **Troubleshooting** | [reference/troubleshooting.md](reference/troubleshooting.md) | `.framework/docs/reference/troubleshooting.md` | Diagnostics and problem solving |
| **Style Guide** | [STYLE_GUIDE.md](STYLE_GUIDE.md) | `.framework/docs/STYLE_GUIDE.md` | Documentation formatting standards |

<a id="examples-and-templates"></a>
## Examples and Templates

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Examples Index** | [../examples/index.md](../examples/index.md) | `.framework/examples/index.md` | Working code examples |
| **AI Agents** | [../ai_agents/AI_AGENT_FRAMEWORK_README.md](../ai_agents/AI_AGENT_FRAMEWORK_README.md) | `.framework/ai_agents/` | Automated generation |
| **Working Demonstrations** | [../use_cases/README.md](../use_cases/README.md) | `.framework/use_cases/` | Complete applications |

<a id="ide-rules-and-patterns"></a>
## IDE Rules & Patterns

| Category | Document | Direct Path | Submodule Path |
|----------|----------|-------------|----------------|
| **Architecture** | Microservices Best Practices | [architecture/ms_best_practices_rules.mdc](architecture/ms_best_practices_rules.mdc) | `.framework/docs/architecture/ms_best_practices_rules.mdc` |
| **Architecture** | Data Access Rules | [architecture/data-access-rules.mdc](architecture/data-access-rules.mdc) | `.framework/docs/architecture/data-access-rules.mdc` |
| **Architecture** | Naming Conventions | [architecture/naming_conventions.mdc](architecture/naming_conventions.mdc) | `.framework/docs/architecture/naming_conventions.mdc` |
| **Services** | FastAPI Rules | [services/fastapi_rules.mdc](services/fastapi_rules.mdc) | `.framework/docs/services/fastapi_rules.mdc` |
| **Services** | Aiogram Rules | [services/aiogram_rules.mdc](services/aiogram_rules.mdc) | `.framework/docs/services/aiogram_rules.mdc` |
| **Services** | AsyncIO Rules | [services/asyncio_rules.mdc](services/asyncio_rules.mdc) | `.framework/docs/services/asyncio_rules.mdc` |
| **Infrastructure** | Redis Rules | [infrastructure/redis_rules.mdc](infrastructure/redis_rules.mdc) | `.framework/docs/infrastructure/redis_rules.mdc` |
| **Infrastructure** | RabbitMQ Rules | [infrastructure/rabbitmq_rules.mdc](infrastructure/rabbitmq_rules.mdc) | `.framework/docs/infrastructure/rabbitmq_rules.mdc` |
| **Infrastructure** | MongoDB Rules | [infrastructure/mongodb_rules.mdc](infrastructure/mongodb_rules.mdc) | `.framework/docs/infrastructure/mongodb_rules.mdc` |
| **Observability** | Logging Rules | [observability/logging_rules.mdc](observability/logging_rules.mdc) | `.framework/docs/observability/logging_rules.mdc` |
| **Observability** | Metrics Rules | [observability/metrics_rules.mdc](observability/metrics_rules.mdc) | `.framework/docs/observability/metrics_rules.mdc` |
| **Observability** | Tracing Rules | [observability/tracing_rules.mdc](observability/tracing_rules.mdc) | `.framework/docs/observability/tracing_rules.mdc` |
| **Observability** | ELK Rules | [observability/elk_rules.mdc](observability/elk_rules.mdc) | `.framework/docs/observability/elk_rules.mdc` |
| **Observability** | Observability Rules | [observability/observability_rules.mdc](observability/observability_rules.mdc) | `.framework/docs/observability/observability_rules.mdc` |
| **Quality** | Testing Standards | [quality/testing-standards.mdc](quality/testing-standards.mdc) | `.framework/docs/quality/testing-standards.mdc` |

<a id="quick-task-navigation"></a>
## Quick Task Navigation

| Task | Documents |
|------|-----------|
| 🏁 **Quick start** | [README.md](../README.md) → [CLAUDE.md](../CLAUDE.md) |
| 🏗️ **Understand architecture** | [ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md) |
| 📋 **Run commands** | [DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) |
| 🎯 **Create new use case** | [USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md) |
| 🔧 **Check versions** | [tech_stack.md](reference/tech_stack.md) |
| 💻 **See examples** | [../examples/index.md](../examples/index.md) |
| 🐛 **Solve problems** | [troubleshooting.md](reference/troubleshooting.md) |

## Link Templates

For simplified linking in other documents, use these templates:

### Core Documents
```markdown
<!-- Link to architecture guide -->
[Architecture Guide](LINKS_REFERENCE.md#core-documentation)

<!-- Link to technical specifications -->
[Technical Specifications](LINKS_REFERENCE.md#core-documentation)
```

### Usage Examples
```markdown
<!-- Instead of long construction -->
[docs/reference/tech_stack.md](docs/reference/tech_stack.md) *(or `.framework/docs/reference/tech_stack.md` when used as submodule)*

<!-- Use -->
See [technical specifications](LINKS_REFERENCE.md#core-documentation)
```

---

> **📖 Usage**: Reference this table from other documents instead of duplicating links. Update this table when adding new documents.