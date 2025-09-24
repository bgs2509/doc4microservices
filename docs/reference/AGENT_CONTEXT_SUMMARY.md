# Agent Context Summary

> **Purpose**: Provide AI agents with a fast, authoritative orientation to this microservices framework. Use this file before scanning the rest of the documentation tree.

## Core Orientation

- **Framework Model**: Framework-as-submodule (`README.md`). Application code lives outside `.framework/`; the framework supplies patterns, infrastructure, and rules.
- **Architecture Paradigm**: Improved Hybrid Approach with HTTP-only data access, dedicated data services, and event-driven coordination (`docs/guides/ARCHITECTURE_GUIDE.md`).
- **Primary Entry Point**: `CLAUDE.md` explains how AI agents should traverse documentation and obey mandatory constraints.

## Mandatory References

| Need | Primary Sources |
|------|-----------------|
| Full documentation map | `docs/LINKS_REFERENCE.md`, `docs/INDEX.md` |
| Architecture constraints | `docs/architecture/ms_best_practices_rules.mdc`, `docs/architecture/data-access-rules.mdc`, `docs/architecture/naming_conventions.mdc` |
| Service implementation patterns | `docs/services/fastapi_rules.mdc`, `docs/services/aiogram_rules.mdc`, `docs/services/asyncio_rules.mdc` |
| Infrastructure rules | `docs/infrastructure/redis_rules.mdc`, `docs/infrastructure/rabbitmq_rules.mdc`, `docs/infrastructure/mongodb_rules.mdc` |
| Observability | `docs/observability/` folder (logging, metrics, tracing, ELK, observability strategy) |
| Quality and testing | `docs/quality/testing-standards.mdc`, `docs/guides/DEVELOPMENT_COMMANDS.md` |

## Agent-Focused Documents

| Purpose | Document |
|---------|----------|
| Prompt validation | `docs/guides/PROMPT_VALIDATION_GUIDE.md` |
| Prompt augmentation snippets | `docs/reference/PROMPT_TEMPLATES.md` |
| Requirements capture | `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` |
| Delivery planning | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| Execution workflow | `docs/guides/AGENT_WORKFLOW.md` |
| Tooling catalog | `docs/reference/AGENT_TOOLBOX.md` |
| Deliverables inventory | `docs/reference/DELIVERABLES_CATALOG.md` |
| Verification checklist | `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` |
| QA reporting | `docs/quality/QA_REPORT_TEMPLATE.md` |
| Architecture decisions | `docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md` |

## Critical Rules Snapshot

1. **Service Separation**: FastAPI, Aiogram, and AsyncIO workers run in separate processes/containers (`docs/architecture/ms_best_practices_rules.mdc`).
2. **Data Access**: Business services must call data services over HTTP; direct database access is prohibited (`docs/architecture/data-access-rules.mdc`).
3. **Eventing**: RabbitMQ is the mandatory broker for asynchronous communication (`docs/infrastructure/rabbitmq_rules.mdc`).
4. **Naming**: Follow the naming standards in `docs/architecture/naming_conventions.mdc` for all files, modules, and identifiers.
5. **Quality Gates**: Ruff, mypy, bandit, pytest, and coverage thresholds are non-negotiable (`docs/guides/DEVELOPMENT_COMMANDS.md`, `docs/quality/testing-standards.mdc`).

## Workflow Overview (High-Level)

1. **Prompt Validation** → `docs/guides/PROMPT_VALIDATION_GUIDE.md`
2. **Requirements Intake** → populate `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`
3. **Implementation Planning** → use `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`
4. **Execution** → follow `docs/guides/AGENT_WORKFLOW.md` and tooling from `docs/reference/AGENT_TOOLBOX.md`
5. **Verification** → `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`
6. **Reporting & Hand-off** → `docs/quality/QA_REPORT_TEMPLATE.md`, update deliverables per `docs/reference/DELIVERABLES_CATALOG.md`

## Maintenance

- Update this summary whenever new mandatory documents are introduced.
- Keep the links aligned with `docs/INDEX.md` and `docs/LINKS_REFERENCE.md`.
- Follow `docs/STYLE_GUIDE.md` for formatting updates.
