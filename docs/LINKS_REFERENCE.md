# Project Links Reference

> **CENTRAL REFERENCE**: All project documentation links in one place. Use this table instead of duplicating links in documents.

<a id="core-documentation"></a>
## Core Documentation

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Main Entry Point** | [AGENTS.md](../AGENTS.md) | `.framework/AGENTS.md` | Complete developer guide |
| **Project Overview** | [README.md](../README.md) | `.framework/README.md` | Project introduction and quick start |
| **Architecture Guide** | [guides/architecture-guide.md](guides/architecture-guide.md) | `.framework/docs/guides/architecture-guide.md` | Canonical source of architectural principles |
| **Technical Specifications** | [reference/tech_stack.md](reference/tech_stack.md) | `.framework/docs/reference/tech_stack.md` | Technology versions and configurations |

<a id="developer-guides"></a>
## Developer Guides

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **AI Code Generation Master Workflow** | [guides/ai-code-generation-master-workflow.md](guides/ai-code-generation-master-workflow.md) | `.framework/docs/guides/ai-code-generation-master-workflow.md` | Complete 7-stage AI process (unified workflow) |
| **Development Commands** | [guides/development-commands.md](guides/development-commands.md) | `.framework/docs/guides/development-commands.md` | All development commands |
| **Use Case Implementation** | [guides/use-case-implementation-guide.md](guides/use-case-implementation-guide.md) | `.framework/docs/guides/use-case-implementation-guide.md` | Step-by-step creation of new use cases |
| **Prompt Validation Guide** | [guides/prompt-validation-guide.md](guides/prompt-validation-guide.md) | `.framework/docs/guides/prompt-validation-guide.md` | Mandatory intake checklist before work starts |
| **Requirements Intake Template** | [guides/requirements-intake-template.md](guides/requirements-intake-template.md) | `.framework/docs/guides/requirements-intake-template.md` | Structured capture of inputs |
| **Implementation Plan Template** | [guides/implementation-plan-template.md](guides/implementation-plan-template.md) | `.framework/docs/guides/implementation-plan-template.md` | Planning artefact for approval |
| **Project Structure** | [reference/project-structure.md](reference/project-structure.md) | `.framework/docs/reference/project-structure.md` | Directory and file organization |
| **Troubleshooting** | [reference/troubleshooting.md](reference/troubleshooting.md) | `.framework/docs/reference/troubleshooting.md` | Diagnostics and problem solving |
| **Style Guide** | [STYLE_GUIDE.md](STYLE_GUIDE.md) | `.framework/docs/STYLE_GUIDE.md` | Documentation formatting standards |

<a id="agent-references"></a>
## Agent References

| Document | Direct Path | Submodule Path | Purpose |
|----------|-------------|----------------|---------|
| **Agent Context Summary** | [reference/agent-context-summary.md](reference/agent-context-summary.md) | `.framework/docs/reference/agent-context-summary.md` | Quick orientation for AI agents |
| **Maturity Levels** | [reference/maturity-levels.md](reference/maturity-levels.md) | `.framework/docs/reference/maturity-levels.md` | 4 incremental levels from PoC to Production |
| **Conditional Stage Rules** | [reference/conditional-stage-rules.md](reference/conditional-stage-rules.md) | `.framework/docs/reference/conditional-stage-rules.md` | Stage skipping rules per maturity level |
| **AI Navigation Matrix** | [reference/ai-navigation-matrix.md](reference/ai-navigation-matrix.md) | `.framework/docs/reference/ai-navigation-matrix.md` | Exact document mapping per workflow stage |
| **Agent Toolbox** | [reference/agent-toolbox.md](reference/agent-toolbox.md) | `.framework/docs/reference/agent-toolbox.md` | Machine-friendly command catalog |
| **Deliverables Catalog** | [reference/deliverables-catalog.md](reference/deliverables-catalog.md) | `.framework/docs/reference/deliverables-catalog.md` | Required artefacts and storage rules |
| **Prompt Templates** | [reference/prompt-templates.md](reference/prompt-templates.md) | `.framework/docs/reference/prompt-templates.md` | Reusable prompts for clarification and reporting |
| **Architecture Decision Log Template** | [reference/architecture-decision-log-template.md](reference/architecture-decision-log-template.md) | `.framework/docs/reference/architecture-decision-log-template.md` | Standardised ADR format |
| **Semantic Shortening Guide** | [guides/semantic-shortening-guide.md](guides/semantic-shortening-guide.md) | `.framework/docs/guides/semantic-shortening-guide.md` | 3-part service naming formula and decision tree |

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
| **Agent Verification Checklist** | [quality/agent-verification-checklist.md](quality/agent-verification-checklist.md) | `.framework/docs/quality/agent-verification-checklist.md` | Mandatory quality gates |
| **QA Report Template** | [quality/qa-report-template.md](quality/qa-report-template.md) | `.framework/docs/quality/qa-report-template.md` | Final QA summary |

<a id="quick-task-navigation"></a>
## Quick Task Navigation

| Task | Documents |
|------|-----------|
| **Quick start** | [README.md](../README.md) → [AGENTS.md](../AGENTS.md) |
| **Understand architecture** | [architecture-guide.md](guides/architecture-guide.md) |
| **Run commands** | [development-commands.md](guides/development-commands.md) |
| **Create new use case** | [use-case-implementation-guide.md](guides/use-case-implementation-guide.md) |
| **AI-led code generation** | [ai-code-generation-master-workflow.md](guides/ai-code-generation-master-workflow.md) → [ai-navigation-matrix.md](reference/ai-navigation-matrix.md) |
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
  - Link OK: reference/tech_stack.md
<!-- Use -->
See [technical specifications](LINKS_REFERENCE.md#core-documentation)
```

---

> **Usage**: Reference this table from other documents instead of duplicating links. Update this table when adding new documents.
