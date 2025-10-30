# Agent Context Summary

> **Purpose**: Provide AI agents with a fast, authoritative orientation to this microservices framework. Use this file before scanning the rest of the documentation tree.

## Core Orientation

- **Framework Model**: Framework-as-submodule (`README.md`). Application code lives outside `.framework/`; the framework supplies patterns, infrastructure, and rules.
- **Architecture Paradigm**: Improved Hybrid Approach with HTTP-only data access, dedicated data services, Nginx API Gateway, and event-driven coordination (`docs/guides/architecture-guide.md`).
- **Primary Entry Point**: `AGENTS.md` (or `AGENTS.md` symlink) explains how AI agents should traverse documentation and obey mandatory constraints. This follows the industry-standard filename adopted by GitHub Copilot, Cursor, and other AI coding agents.

## Mandatory References

| Need | Primary Sources |
|------|-----------------|
| Full documentation map | `docs/LINKS_REFERENCE.md`, `docs/INDEX.md` |
| Maturity level selection | `docs/reference/maturity-levels.md`, `docs/reference/conditional-stage-rules.md` |
| Architecture constraints | `docs/guides/architecture-guide.md`, `docs/atomic/architecture/improved-hybrid-overview.md`, `docs/atomic/architecture/data-access-architecture.md`, `docs/atomic/architecture/naming/README.md` |
| Service implementation patterns | `docs/atomic/services/fastapi/`, `docs/atomic/services/aiogram/`, `docs/atomic/services/asyncio-workers/`, `docs/atomic/services/data-services/` |
| Infrastructure integration rules | `docs/atomic/integrations/redis/`, `docs/atomic/integrations/rabbitmq/`, `docs/atomic/integrations/http-communication/` |
| Database patterns | `docs/atomic/databases/postgresql/`, `docs/atomic/databases/postgresql-advanced/`, `docs/atomic/infrastructure/databases/` |
| Observability | `docs/atomic/observability/` (logging, metrics, tracing, error tracking, ELK stack) |
| Quality and testing | `docs/atomic/testing/`, `docs/guides/development-commands.md` |

## Agent-Focused Documents

| Purpose | Document |
|---------|----------|
| Complete workflow process | `docs/guides/ai-code-generation-master-workflow.md` |
| Stage-by-stage navigation | `docs/reference/ai-navigation-matrix.md` |
| Prompt validation | `docs/guides/prompt-validation-guide.md` |
| Prompt augmentation snippets | `docs/reference/prompt-templates.md` |
| Requirements capture | `docs/guides/requirements-intake-template.md` |
| **Requirements traceability** | **`docs/guides/requirements-traceability-guide.md`** — **100% coverage methodology** |
| Delivery planning | `docs/guides/implementation-plan-template.md` |
| Tooling catalog | `docs/reference/agent-toolbox.md` |
| Deliverables inventory | `docs/reference/deliverables-catalog.md` |
| Verification checklist | `docs/quality/agent-verification-checklist.md` |
| QA reporting | `docs/quality/qa-report-template.md` |
| Architecture decisions | `docs/reference/architecture-decision-log-template.md` |
| Failure & recovery handling | `docs/reference/failure-scenarios.md` |

## Critical Rules Snapshot

1. **Requirements Coverage**: **100% requirement coverage MANDATORY** — ALL requirements from Stage 2 must be implemented by Stage 5 (or explicitly descoped with approval). Use Req ID tracking (FR-*, UI-*, NF-*) throughout workflow (`docs/guides/requirements-traceability-guide.md`).
2. **Service Separation**: FastAPI, Aiogram, and AsyncIO workers run in separate processes/containers (`docs/atomic/architecture/service-separation-principles.md`).
3. **Data Access**: Business services must call data services over HTTP; direct database access is prohibited (`docs/atomic/architecture/data-access-architecture.md`).
4. **API Gateway**: Nginx is MANDATORY for production deployments (TLS, load balancing, rate limiting) (`docs/atomic/infrastructure/api-gateway/`).
5. **Eventing**: RabbitMQ is the mandatory broker for asynchronous communication (`docs/atomic/integrations/rabbitmq/`).
6. **Naming**: **DEFAULT TO 3-PART** naming (`{context}_{domain}_{type}`). Use 4-part ONLY when domain is ambiguous (burden of proof required). See `docs/atomic/architecture/naming/naming-4part-reasons.md` for 10 serious reasons. Use `docs/checklists/service-naming-checklist.md` for quick decision.
7. **Quality Gates**: Ruff, mypy, bandit, pytest, and test coverage thresholds are non-negotiable (`docs/guides/development-commands.md`).

## Workflow Overview

**Complete 7-stage process**: See `docs/guides/ai-code-generation-master-workflow.md`

**Quick summary**:
1. **Stage 0: Initialization** → Load framework context (AGENTS.md, this file, Master Workflow)
2. **Stage 1: Prompt Validation** → `docs/guides/prompt-validation-guide.md` — **SELECT MATURITY LEVEL (1-4)**
3. **Stage 2: Requirements Intake** → populate `docs/guides/requirements-intake-template.md` — **ASSIGN REQ IDs (FR-*, UI-*, NF-*)**
4. **Stage 3: Implementation Planning** → use `docs/guides/implementation-plan-template.md` — **CREATE RTM (map Req IDs → tasks)**
5. **Stage 4: Code Generation** → **CONDITIONAL** based on maturity level per `docs/reference/conditional-stage-rules.md`
6. **Stage 5: Verification** → `docs/quality/agent-verification-checklist.md` — **VERIFY 100% REQUIREMENTS COVERAGE** (PRIMARY GATE)
7. **Stage 6: Reporting & Handoff** → `docs/quality/qa-report-template.md` with **Requirements Coverage Matrix**, update `docs/reference/deliverables-catalog.md`

**Navigation**: Use `docs/reference/ai-navigation-matrix.md` for exact document mapping at each stage.

**Maturity Levels**: 4 levels from PoC (~5 min) to Production (~30 min). See `docs/reference/maturity-levels.md` for details.

## Maintenance

- Update this summary whenever new mandatory documents are introduced.
- Keep the links aligned with `docs/INDEX.md` and `docs/LINKS_REFERENCE.md`.
- Follow `docs/STYLE_GUIDE.md` for formatting updates.
