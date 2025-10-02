# Project Links Reference

> **CENTRAL REFERENCE**: All project documentation links in one place. Use this table instead of duplicating links in documents.

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
| **AI Code Generation Master Workflow** | [guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md](guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md) | `.framework/docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md` | Complete 7-stage AI process (unified workflow) |
| **Development Commands** | [guides/DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) | `.framework/docs/guides/DEVELOPMENT_COMMANDS.md` | All development commands |
| **Use Case Implementation** | [guides/USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md) | `.framework/docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md` | Step-by-step creation of new use cases |
| **Prompt Validation Guide** | [guides/PROMPT_VALIDATION_GUIDE.md](guides/PROMPT_VALIDATION_GUIDE.md) | `.framework/docs/guides/PROMPT_VALIDATION_GUIDE.md` | Mandatory intake checklist before work starts |
| **Requirements Intake Template** | [guides/REQUIREMENTS_INTAKE_TEMPLATE.md](guides/REQUIREMENTS_INTAKE_TEMPLATE.md) | `.framework/docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` | Structured capture of inputs |
| **Implementation Plan Template** | [guides/IMPLEMENTATION_PLAN_TEMPLATE.md](guides/IMPLEMENTATION_PLAN_TEMPLATE.md) | `.framework/docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` | Planning artefact for approval |
| **Project Structure** | [reference/PROJECT_STRUCTURE.md](reference/PROJECT_STRUCTURE.md) | `.framework/docs/reference/PROJECT_STRUCTURE.md` | Directory and file organization |
| **Troubleshooting** | [reference/troubleshooting.md](reference/troubleshooting.md) | `.framework/docs/reference/troubleshooting.md` | Diagnostics and problem solving |
| **Style Guide** | [STYLE_GUIDE.md](STYLE_GUIDE.md) | `.framework/docs/STYLE_GUIDE.md` | Documentation formatting standards |

<a id="agent-references"></a>
## Agent References

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Agent Context Summary** | [reference/AGENT_CONTEXT_SUMMARY.md](reference/AGENT_CONTEXT_SUMMARY.md) | `.framework/docs/reference/AGENT_CONTEXT_SUMMARY.md` | Quick orientation for AI agents |
| **Maturity Levels** | [reference/MATURITY_LEVELS.md](reference/MATURITY_LEVELS.md) | `.framework/docs/reference/MATURITY_LEVELS.md` | 4 incremental levels from PoC to Production |
| **Conditional Stage Rules** | [reference/CONDITIONAL_STAGE_RULES.md](reference/CONDITIONAL_STAGE_RULES.md) | `.framework/docs/reference/CONDITIONAL_STAGE_RULES.md` | Stage skipping rules per maturity level |
| **AI Navigation Matrix** | [reference/AI_NAVIGATION_MATRIX.md](reference/AI_NAVIGATION_MATRIX.md) | `.framework/docs/reference/AI_NAVIGATION_MATRIX.md` | Exact document mapping per workflow stage |
| **Agent Toolbox** | [reference/AGENT_TOOLBOX.md](reference/AGENT_TOOLBOX.md) | `.framework/docs/reference/AGENT_TOOLBOX.md` | Machine-friendly command catalog |
| **Deliverables Catalog** | [reference/DELIVERABLES_CATALOG.md](reference/DELIVERABLES_CATALOG.md) | `.framework/docs/reference/DELIVERABLES_CATALOG.md` | Required artefacts and storage rules |
| **Prompt Templates** | [reference/PROMPT_TEMPLATES.md](reference/PROMPT_TEMPLATES.md) | `.framework/docs/reference/PROMPT_TEMPLATES.md` | Reusable prompts for clarification and reporting |
| **Architecture Decision Log Template** | [reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md](reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md) | `.framework/docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md` | Standardised ADR format |
| **Semantic Shortening Guide** | [guides/SEMANTIC_SHORTENING_GUIDE.md](guides/SEMANTIC_SHORTENING_GUIDE.md) | `.framework/docs/guides/SEMANTIC_SHORTENING_GUIDE.md` | 3-part service naming formula and decision tree |

<a id="ide-rules-and-patterns"></a>
## Atomic Knowledge Base

Centralised atomic documentation for domain-specific rules. See [INDEX.md](INDEX.md) for the full topic list.

| Domain | Entry Point | Example Topics |
|--------|-------------|----------------|
| Architecture | [atomic/architecture/](atomic/architecture/) | hybrid approach, service separation, naming conventions |
| Services | [atomic/services/](atomic/services/) | FastAPI, Aiogram, AsyncIO workers, data services |
| Integrations | [atomic/integrations/](atomic/integrations/) | Redis, RabbitMQ, HTTP, cross-service coordination |
| Infrastructure | [atomic/infrastructure/](atomic/infrastructure/) | databases, containerisation, configuration, deployment |
| Observability | [atomic/observability/](atomic/observability/) | logging, metrics, tracing, error tracking, ELK |
| Testing | [atomic/testing/](atomic/testing/) | unit, integration, service, end-to-end, QA |

<a id="quality-assets"></a>
## Quality Assets

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Agent Verification Checklist** | [quality/AGENT_VERIFICATION_CHECKLIST.md](quality/AGENT_VERIFICATION_CHECKLIST.md) | `.framework/docs/quality/AGENT_VERIFICATION_CHECKLIST.md` | Mandatory quality gates |
| **QA Report Template** | [quality/QA_REPORT_TEMPLATE.md](quality/QA_REPORT_TEMPLATE.md) | `.framework/docs/quality/QA_REPORT_TEMPLATE.md` | Final QA summary |

<a id="quick-task-navigation"></a>
## Quick Task Navigation

| Task | Documents |
|------|-----------|
| **Quick start** | [README.md](../README.md) → [CLAUDE.md](../CLAUDE.md) |
| **Understand architecture** | [ARCHITECTURE_GUIDE.md](guides/ARCHITECTURE_GUIDE.md) |
| **Run commands** | [DEVELOPMENT_COMMANDS.md](guides/DEVELOPMENT_COMMANDS.md) |
| **Create new use case** | [USE_CASE_IMPLEMENTATION_GUIDE.md](guides/USE_CASE_IMPLEMENTATION_GUIDE.md) |
| **AI-led code generation** | [AI_CODE_GENERATION_MASTER_WORKFLOW.md](guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md) → [AI_NAVIGATION_MATRIX.md](reference/AI_NAVIGATION_MATRIX.md) |
| **Check versions** | [tech_stack.md](reference/tech_stack.md) |
| **Solve problems** | [troubleshooting.md](reference/troubleshooting.md) |

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
  - Ссылка OK: reference/tech_stack.md
<!-- Use -->
See [technical specifications](LINKS_REFERENCE.md#core-documentation)
```

---

> **Usage**: Reference this table from other documents instead of duplicating links. Update this table when adding new documents.
