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
- **[Agent Workflow](docs/INDEX.md#documentation-structure)** — end-to-end process for AI agents.

### Reference Materials

- **[Agent Context Summary](docs/INDEX.md#reference-materials)** — fastest orientation for agents; links to critical rules.
- **[Agent Toolbox](docs/INDEX.md#reference-materials)** — machine-friendly command lookup.
- **[Deliverables Catalog](docs/INDEX.md#reference-materials)** — required artefacts and storage locations.
- **[Prompt Templates](docs/INDEX.md#reference-materials)** — reusable prompts for clarification and reporting.
- **[Project Structure](docs/LINKS_REFERENCE.md#developer-guides)** — canonical repository layout when the framework is a submodule.
- **[Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)** — symptom-based diagnostics and recovery playbook.

### Agent Templates & Checklists

- **[Prompt Validation Guide](docs/INDEX.md#agent-templates)** — ensure user prompt completeness before any work.
- **[Requirements Intake Template](docs/INDEX.md#agent-templates)** — structured capture of inputs.
- **[Implementation Plan Template](docs/INDEX.md#agent-templates)** — planning artefact for approval.
- **[Agent Verification Checklist](docs/INDEX.md#agent-templates)** — mandatory quality gates.
- **[QA Report Template](docs/INDEX.md#agent-templates)** — final summary for stakeholders.
- **[Architecture Decision Log Template](docs/INDEX.md#reference-materials)** — standardized ADR format when major decisions arise.

### IDE Rules & Patterns

- See `docs/LINKS_REFERENCE.md#ide-rules-and-patterns` for machine-readable rules covering architecture, services, infrastructure, observability, and quality.

### Quick Navigation

| Need | Go To |
|------|-------|
| Validate a new prompt | [Prompt Validation Guide](docs/INDEX.md#agent-templates) |
| Prepare requirements | [Requirements Intake Template](docs/INDEX.md#agent-templates) |
| Build a plan | [Implementation Plan Template](docs/INDEX.md#agent-templates) |
| Execute tasks | [Agent Workflow](docs/INDEX.md#documentation-structure) + [Agent Toolbox](docs/INDEX.md#reference-materials) |
| Verify quality | [Agent Verification Checklist](docs/INDEX.md#agent-templates) |
| Report results | [QA Report Template](docs/INDEX.md#agent-templates) |

## Framework Overview

- **Architecture**: Improved Hybrid Approach, strict HTTP-only data services, RabbitMQ eventing.
- **Service Types**: FastAPI (API), Aiogram (bot), AsyncIO workers, dedicated data services (PostgreSQL, MongoDB).
- **Quality**: Enforced via Ruff, mypy, bandit, pytest, coverage thresholds (`docs/guides/DEVELOPMENT_COMMANDS.md`, `docs/quality/testing-standards.mdc`).

**Critical Constraints**
1. Separate containers/processes for each service type (`docs/architecture/ms_best_practices_rules.mdc`).
2. Business services must use HTTP to access data services (`docs/architecture/data-access-rules.mdc`).
3. Use RabbitMQ for cross-service eventing (`docs/infrastructure/rabbitmq_rules.mdc`).
4. Adhere to naming conventions (`docs/architecture/naming_conventions.mdc`).

## Agent Workflow (High-Level)

1. Prompt Validation → `docs/guides/PROMPT_VALIDATION_GUIDE.md`
2. Requirements Intake → fill `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`
3. Implementation Planning → populate `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`
4. Execution → follow `docs/guides/AGENT_WORKFLOW.md`, using `docs/reference/AGENT_TOOLBOX.md`
5. Verification → run `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`
6. Release Handoff → summarise with `docs/quality/QA_REPORT_TEMPLATE.md` and update deliverables (`docs/reference/DELIVERABLES_CATALOG.md`)

## Important Notes

- Never modify framework files when used as submodule; generate application code under the host project (`README.md`).
- Maintain `.env` files, Docker configurations, and shared components per `docs/guides/shared_components.md`.
- Use ADR template for significant decisions impacting architecture or infrastructure.
- Reference `docs/reference/tech_stack.md` when selecting technologies or versions.
- Update documentation and changelog (when available) in tandem with code changes.

## Framework Management

- Update the framework submodule with `git submodule update --remote .framework` as needed.
- Keep documentation synchronized: update `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md` when new files are added.
- Follow `docs/STYLE_GUIDE.md` for formatting and wording.
