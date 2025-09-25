# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this microservices framework.

> **CONTEXT**: This framework can be used in two ways:
> - **Direct**: Working in this repository directly (use paths like `docs/`)
> - **Submodule**: Added as `.framework/` submodule to your project (use paths like `.framework/docs/`)
>
> The paths below assume **direct usage**. When used as submodule, prefix all paths with `.framework/`.

## Documentation Hierarchy

> **NAVIGATION GUIDE**: Each document has a single purpose. Use the references below instead of duplicating content.

### Primary Documentation (Essential Reading)

- **[README.md](docs/LINKS_REFERENCE.md#core-documentation)** — intro, quick start, value proposition.
- **[Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation)** — technology versions and configurations.
- **[Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation)** — mandatory architecture principles and communication patterns.
- **[Development Commands](docs/LINKS_REFERENCE.md#developer-guides)** — canonical command catalog for local/dev/CI operations.
- **[Agent Workflow](docs/INDEX.md#documentation-pillars)** — end-to-end process for AI agents.

### Reference Materials

- **[Agent Context Summary](docs/INDEX.md#reference-materials)** — fastest orientation for agents; links to critical rules.
- **[Agent Toolbox](docs/INDEX.md#reference-materials)** — machine-friendly command lookup.
- **[Deliverables Catalog](docs/INDEX.md#reference-materials)** — required artefacts and storage locations.
- **[Prompt Templates](docs/INDEX.md#reference-materials)** — reusable prompts for clarification and reporting.
- **[Project Structure](docs/LINKS_REFERENCE.md#developer-guides)** — canonical repository layout when the framework is a submodule.
- **[Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)** — symptom-based diagnostics and recovery playbook.

### Agent Templates & Checklists

- **[Prompt Validation Guide](docs/INDEX.md#agent-templates-checklists)** — ensure user prompt completeness before any work.
- **[Requirements Intake Template](docs/INDEX.md#agent-templates-checklists)** — structured capture of inputs.
- **[Implementation Plan Template](docs/INDEX.md#agent-templates-checklists)** — planning artefact for approval.
- **[Agent Verification Checklist](docs/INDEX.md#agent-templates-checklists)** — mandatory quality gates.
- **[QA Report Template](docs/INDEX.md#agent-templates-checklists)** — final summary for stakeholders.
- **[Architecture Decision Log Template](docs/INDEX.md#reference-materials)** — standardized ADR format when major decisions arise.

### IDE Rules & Patterns

- See `docs/LINKS_REFERENCE.md#ide-rules-and-patterns` for machine-readable rules covering architecture, services, infrastructure, observability, and quality.

### Quick Navigation

| Need | Go To |
|------|-------|
| Validate a new prompt | [Prompt Validation Guide](docs/INDEX.md#agent-templates-checklists) |
| Prepare requirements | [Requirements Intake Template](docs/INDEX.md#agent-templates-checklists) |
| Build a plan | [Implementation Plan Template](docs/INDEX.md#agent-templates-checklists) |
| Execute tasks | [Agent Workflow](docs/INDEX.md#documentation-pillars) + [Agent Toolbox](docs/INDEX.md#reference-materials) |
| Verify quality | [Agent Verification Checklist](docs/INDEX.md#agent-templates-checklists) |
| Report results | [QA Report Template](docs/INDEX.md#agent-templates-checklists) |

## Framework Overview

This framework implements the **Improved Hybrid Approach** with FastAPI, Aiogram, and AsyncIO services, strict HTTP-only data access, and RabbitMQ eventing.

> **COMPLETE ARCHITECTURE DETAILS**: See [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) for detailed principles, constraints, service types, and implementation guidelines.

## Agent Workflow (High-Level)

1. Prompt Validation → [Prompt Validation Guide](docs/guides/PROMPT_VALIDATION_GUIDE.md)
2. Requirements Intake → fill [Requirements Intake Template](docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md)
3. Implementation Planning → populate [Implementation Plan Template](docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md)
4. Execution → follow [Agent Workflow](docs/guides/AGENT_WORKFLOW.md), using [Agent Toolbox](docs/reference/AGENT_TOOLBOX.md)
5. Verification → run [Agent Verification Checklist](docs/quality/AGENT_VERIFICATION_CHECKLIST.md)
6. Release Handoff → summarise with [QA Report Template](docs/quality/QA_REPORT_TEMPLATE.md) and update deliverables ([Deliverables Catalog](docs/reference/DELIVERABLES_CATALOG.md))

## Important Notes

- Never modify framework files when used as submodule; generate application code under the host project ([README.md](README.md)).
- Maintain `.env` files, Docker configurations, and shared components per [Shared Components Guide](docs/guides/shared_components.md).
- Use ADR template for significant decisions impacting architecture or infrastructure.
- Reference [Technical Specifications](docs/reference/tech_stack.md) when selecting technologies or versions.
- Update documentation and changelog (when available) in tandem with code changes.

## Framework Management

- See [Project Structure Guide](docs/LINKS_REFERENCE.md#developer-guides) for complete submodule operations and development workflow.
- Keep documentation synchronized: update `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md` when new files are added.
- Follow [Style Guide](docs/STYLE_GUIDE.md) for formatting and wording.
