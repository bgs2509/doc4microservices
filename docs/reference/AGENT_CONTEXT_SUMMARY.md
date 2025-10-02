# Agent Context Summary

> **Purpose**: Provide AI agents with a fast, authoritative orientation to this microservices framework. Use this file before scanning the rest of the documentation tree.

## Core Orientation

- **Framework Model**: Framework-as-submodule (`README.md`). Application code lives outside `.framework/`; the framework supplies patterns, infrastructure, and rules.
- **Architecture Paradigm**: Improved Hybrid Approach with HTTP-only data access, dedicated data services, Nginx API Gateway, and event-driven coordination (`docs/guides/ARCHITECTURE_GUIDE.md`).
- **Primary Entry Point**: `CLAUDE.md` explains how AI agents should traverse documentation and obey mandatory constraints.

## Mandatory References

| Need | Primary Sources |
|------|-----------------|
| Full documentation map | `docs/LINKS_REFERENCE.md`, `docs/INDEX.md` |
| Maturity level selection | `docs/reference/MATURITY_LEVELS.md`, `docs/reference/CONDITIONAL_STAGE_RULES.md` |
| Architecture constraints | `docs/guides/ARCHITECTURE_GUIDE.md`, `docs/atomic/architecture/improved-hybrid-overview.md`, `docs/atomic/architecture/data-access-architecture.md`, `docs/atomic/architecture/naming-conventions.md` |
| Service implementation patterns | `docs/atomic/services/fastapi/`, `docs/atomic/services/aiogram/`, `docs/atomic/services/asyncio-workers/`, `docs/atomic/services/data-services/` |
| Infrastructure integration rules | `docs/atomic/integrations/redis/`, `docs/atomic/integrations/rabbitmq/`, `docs/atomic/integrations/http-communication/` |
| Database patterns | `docs/atomic/databases/postgresql/`, `docs/atomic/databases/postgresql-advanced/`, `docs/atomic/infrastructure/databases/` |
| Observability | `docs/atomic/observability/` (logging, metrics, tracing, error tracking, ELK stack) |
| Quality and testing | `docs/atomic/testing/`, `docs/guides/DEVELOPMENT_COMMANDS.md` |

## Agent-Focused Documents

| Purpose | Document |
|---------|----------|
| Complete workflow process | `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md` |
| Stage-by-stage navigation | `docs/reference/AI_NAVIGATION_MATRIX.md` |
| Prompt validation | `docs/guides/PROMPT_VALIDATION_GUIDE.md` |
| Prompt augmentation snippets | `docs/reference/PROMPT_TEMPLATES.md` |
| Requirements capture | `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` |
| Delivery planning | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| Tooling catalog | `docs/reference/AGENT_TOOLBOX.md` |
| Deliverables inventory | `docs/reference/DELIVERABLES_CATALOG.md` |
| Verification checklist | `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` |
| QA reporting | `docs/quality/QA_REPORT_TEMPLATE.md` |
| Architecture decisions | `docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md` |
| Failure & recovery handling | `docs/reference/FAILURE_SCENARIOS.md` |

## Critical Rules Snapshot

1. **Service Separation**: FastAPI, Aiogram, and AsyncIO workers run in separate processes/containers (`docs/atomic/architecture/service-separation-principles.md`).
2. **Data Access**: Business services must call data services over HTTP; direct database access is prohibited (`docs/atomic/architecture/data-access-architecture.md`).
3. **API Gateway**: Nginx is MANDATORY for production deployments (TLS, load balancing, rate limiting) (`docs/atomic/infrastructure/api-gateway/`).
4. **Eventing**: RabbitMQ is the mandatory broker for asynchronous communication (`docs/atomic/integrations/rabbitmq/`).
5. **Naming**: Follow semantic 3-part naming (`{context}_{domain}_{type}`) from `docs/atomic/architecture/naming-conventions.md` and `docs/guides/SEMANTIC_SHORTENING_GUIDE.md`. Add explicit function (4-part) only when domain is ambiguous.
6. **Quality Gates**: Ruff, mypy, bandit, pytest, and coverage thresholds are non-negotiable (`docs/guides/DEVELOPMENT_COMMANDS.md`).

## Workflow Overview

**Complete 7-stage process**: See `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md`

**Quick summary**:
1. **Stage 0: Initialization** → Load framework context (CLAUDE.md, this file, Master Workflow)
2. **Stage 1: Prompt Validation** → `docs/guides/PROMPT_VALIDATION_GUIDE.md` — **SELECT MATURITY LEVEL (1-4)**
3. **Stage 2: Requirements Intake** → populate `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`
4. **Stage 3: Implementation Planning** → use `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`
5. **Stage 4: Code Generation** → **CONDITIONAL** based on maturity level per `docs/reference/CONDITIONAL_STAGE_RULES.md`
6. **Stage 5: Verification** → `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` (criteria vary by level)
7. **Stage 6: Reporting & Handoff** → `docs/quality/QA_REPORT_TEMPLATE.md`, update `docs/reference/DELIVERABLES_CATALOG.md`

**Navigation**: Use `docs/reference/AI_NAVIGATION_MATRIX.md` for exact document mapping at each stage.

**Maturity Levels**: 4 levels from PoC (~5 min) to Production (~30 min). See `docs/reference/MATURITY_LEVELS.md` for details.

## Maintenance

- Update this summary whenever new mandatory documents are introduced.
- Keep the links aligned with `docs/INDEX.md` and `docs/LINKS_REFERENCE.md`.
- Follow `docs/STYLE_GUIDE.md` for formatting updates.
