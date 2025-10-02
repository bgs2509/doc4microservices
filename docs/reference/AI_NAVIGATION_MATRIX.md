# AI Navigation Matrix

> **PURPOSE**: Quick-lookup table showing exactly which documents AI should read at each workflow stage and what outputs are expected.

## How to Use This Matrix

1. **Find your current stage** (0-6) in the leftmost column
2. **Read the "Documents to Read" column** - these are MANDATORY reading for that stage
3. **Generate outputs** listed in "AI Generates" column
4. **Use tools** from "Templates/Tools" column
5. **Verify success** using "Success Criteria" column

---

## Complete Navigation Matrix

| Stage | Phase | Documents to Read | AI Generates | Templates/Tools | Success Criteria |
|-------|-------|-------------------|--------------|-----------------|------------------|
| **0** | **Initialization** | • `CLAUDE.md`<br>• `docs/reference/AGENT_CONTEXT_SUMMARY.md`<br>• `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md` | Nothing (loading phase) | None | AI has complete framework context:<br>• Improved Hybrid Approach understood<br>• Mandatory constraints loaded<br>• Documentation structure mapped |
| **1** | **Prompt Validation** | • `docs/guides/PROMPT_VALIDATION_GUIDE.md`<br>• `docs/reference/PROMPT_TEMPLATES.md` (if clarification needed) | • Validation confirmation note<br>OR<br>• Clarification request to user | • `PROMPT_TEMPLATES.md` (augmentation snippets) | All mandatory fields present:<br>✅ Business context<br>✅ Functional requirements<br>✅ Non-functional constraints<br>✅ Dependencies<br>✅ Scope boundaries<br>✅ Deliverables<br>✅ Acceptance criteria |
| **2** | **Requirements Clarification & Intake** | • `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`<br>• `docs/guides/ARCHITECTURE_GUIDE.md`<br>• `docs/reference/tech_stack.md`<br>• `docs/atomic/architecture/improved-hybrid-overview.md`<br>• `docs/atomic/architecture/service-separation-principles.md`<br>• `docs/atomic/architecture/data-access-architecture.md` | • Completed Requirements Intake document<br>• Architecture compatibility analysis<br>• Service mapping (FastAPI/Aiogram/Workers/Data) | • `REQUIREMENTS_INTAKE_TEMPLATE.md`<br>• `PROMPT_TEMPLATES.md` (if follow-up questions) | • Requirements doc approved by user<br>• Architecture alignment confirmed<br>• Service types identified<br>• No architectural conflicts |
| **3** | **Architecture Mapping & Planning** | • `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`<br>• `docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md`<br>• `docs/atomic/services/**/*` (based on services needed)<br>• `docs/atomic/integrations/**/*` (based on integrations needed)<br>• `docs/reference/AGENT_TOOLBOX.md` | • Detailed Implementation Plan<br>• Optional Architecture Decision Records (ADRs) | • `IMPLEMENTATION_PLAN_TEMPLATE.md`<br>• `ARCHITECTURE_DECISION_LOG_TEMPLATE.md` (if major decisions)<br>• `AGENT_TOOLBOX.md` | • Plan approved by user<br>• All phases defined with DoD<br>• Risks identified<br>• Atomic docs mapped to each phase |
| **4.1** | **Code Generation: Infrastructure** | • `docs/atomic/infrastructure/containerization/docker-compose-setup.md`<br>• `docs/atomic/infrastructure/containerization/dockerfile-patterns.md`<br>• `docs/atomic/infrastructure/configuration/environment-variables.md`<br>• `docs/atomic/infrastructure/configuration/settings-patterns.md` | • `docker-compose.yml`<br>• `docker-compose.prod.yml`<br>• `.env.example`<br>• `Makefile`<br>• Service directories with Dockerfiles | • `AGENT_TOOLBOX.md` (Docker commands)<br>• `docs/reference/PROJECT_STRUCTURE.md` | • `docker-compose up -d` succeeds<br>• All services show "healthy" status<br>• Ports correctly mapped |
| **4.2** | **Code Generation: Data Layer** | • `docs/atomic/services/data-services/postgres-service-setup.md`<br>• `docs/atomic/services/data-services/mongo-service-setup.md`<br>• `docs/atomic/services/data-services/repository-patterns.md`<br>• `docs/atomic/services/data-services/http-api-design.md`<br>• `docs/atomic/services/data-services/transaction-management.md`<br>• `docs/atomic/databases/postgresql/sqlalchemy-integration.md`<br>• `docs/atomic/databases/postgresql-advanced/*` (if complex models) | **PostgreSQL Service**:<br>• SQLAlchemy models<br>• Repositories (CRUD)<br>• HTTP API routers<br>• Alembic migrations<br><br>**MongoDB Service**:<br>• Motor models<br>• Repositories<br>• HTTP API routers | • `AGENT_TOOLBOX.md` (DB commands)<br>• `docs/atomic/architecture/naming-conventions.md` | • Data services respond to health checks<br>• HTTP APIs functional:<br>&nbsp;&nbsp;• `curl localhost:8001/health` → 200<br>&nbsp;&nbsp;• `curl localhost:8002/health` → 200<br>• Migrations apply successfully |
| **4.3** | **Code Generation: Business Logic** | • `docs/atomic/services/fastapi/application-factory.md`<br>• `docs/atomic/services/fastapi/routing-patterns.md`<br>• `docs/atomic/services/fastapi/dependency-injection.md`<br>• `docs/atomic/services/fastapi/schema-validation.md`<br>• `docs/atomic/services/fastapi/error-handling.md`<br>• `docs/atomic/architecture/ddd-hexagonal-principles.md`<br>• `docs/atomic/integrations/http-communication/business-to-data-calls.md`<br>• `docs/atomic/integrations/http-communication/timeout-retry-patterns.md` | **Domain Layer**:<br>• Entities<br>• Value objects<br>• Domain services<br><br>**Application Layer**:<br>• Use cases<br>• DTOs<br>• Application services<br><br>**Infrastructure Layer**:<br>• HTTP clients (to data services)<br>• RabbitMQ publishers<br><br>**API Layer**:<br>• FastAPI routers<br>• Request/response schemas | • `AGENT_TOOLBOX.md` (quality commands)<br>• `docs/atomic/architecture/naming-conventions.md` | • API endpoints functional<br>• HTTP-only data access verified (no direct DB)<br>• DDD layers properly separated<br>• OpenAPI docs generated |
| **4.4** | **Code Generation: Background Workers** | • `docs/atomic/services/asyncio-workers/basic-setup.md`<br>• `docs/atomic/services/asyncio-workers/main-function-patterns.md`<br>• `docs/atomic/services/asyncio-workers/signal-handling.md`<br>• `docs/atomic/services/asyncio-workers/task-management.md`<br>• `docs/atomic/services/asyncio-workers/error-handling.md`<br>• `docs/atomic/integrations/rabbitmq/message-consuming.md`<br>• `docs/atomic/integrations/rabbitmq/asyncio-integration.md` | • Worker implementations<br>• RabbitMQ consumers<br>• Task orchestration<br>• Main entrypoint with signal handling | • `AGENT_TOOLBOX.md`<br>• `docs/atomic/integrations/rabbitmq/dto-contracts.md` | • Workers start successfully<br>• Event consumption working<br>• Graceful shutdown functional<br>• Error handling tested |
| **4.5** | **Code Generation: Telegram Bot** | • `docs/atomic/services/aiogram/basic-setup.md`<br>• `docs/atomic/services/aiogram/bot-initialization.md`<br>• `docs/atomic/services/aiogram/handler-patterns.md`<br>• `docs/atomic/services/aiogram/middleware-setup.md`<br>• `docs/atomic/services/aiogram/state-management.md`<br>• `docs/atomic/integrations/rabbitmq/aiogram-integration.md` | • Bot handlers (commands, messages)<br>• FSM states (if needed)<br>• Middleware<br>• RabbitMQ event listeners<br>• Main entrypoint | • `AGENT_TOOLBOX.md` | • Bot responds to commands<br>• Event-based notifications working<br>• State management functional (if used) |
| **4.6** | **Code Generation: Testing** | • `docs/atomic/testing/unit-testing/pytest-setup.md`<br>• `docs/atomic/testing/unit-testing/fixture-patterns.md`<br>• `docs/atomic/testing/unit-testing/mocking-strategies.md`<br>• `docs/atomic/testing/integration-testing/testcontainers-setup.md`<br>• `docs/atomic/testing/service-testing/fastapi-testing-patterns.md`<br>• `docs/atomic/testing/service-testing/data-service-testing.md` | • `pytest.ini`<br>• `conftest.py`<br>• Unit tests (all layers)<br>• Integration tests (with testcontainers)<br>• Service tests<br>• Test fixtures | • `AGENT_TOOLBOX.md` (testing commands) | • All tests pass:<br>&nbsp;&nbsp;`uv run pytest`<br>• Coverage ≥ 80%:<br>&nbsp;&nbsp;`pytest --cov=services`<br>• No test errors |
| **5** | **Quality Verification** | • `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`<br>• `docs/reference/AGENT_TOOLBOX.md`<br>• `docs/reference/troubleshooting.md` (if issues) | • Completed verification checklist<br>• Coverage reports (HTML + XML)<br>• Evidence logs/screenshots | • `AGENT_TOOLBOX.md` (quality commands):<br>&nbsp;&nbsp;• `uv run ruff check .`<br>&nbsp;&nbsp;• `uv run ruff format . --check`<br>&nbsp;&nbsp;• `uv run mypy .`<br>&nbsp;&nbsp;• `uv run bandit -r .`<br>&nbsp;&nbsp;• `uv run pytest --cov` | **ALL checks must pass**:<br>✅ Linting (Ruff): 0 errors<br>✅ Formatting: No drift<br>✅ Type checking (Mypy): 0 errors<br>✅ Security (Bandit): 0 high severity<br>✅ Tests: All pass<br>✅ Coverage: ≥ 80%<br>✅ Project structure: Compliant<br>✅ Naming: Follows conventions |
| **6** | **QA Report & Handoff** | • `docs/quality/QA_REPORT_TEMPLATE.md`<br>• `docs/reference/DELIVERABLES_CATALOG.md` | • Final QA Report<br>• Deliverables summary<br>• Deployment guide<br>• Updated DELIVERABLES_CATALOG | • `QA_REPORT_TEMPLATE.md` | • QA report approved by stakeholder<br>• All deliverables documented<br>• Deployment instructions verified<br>• Sign-off obtained |

---

## Stage Transition Rules

### When to Proceed to Next Stage

| From Stage | To Stage | Transition Criteria |
|------------|----------|---------------------|
| 0 → 1 | Initialization → Validation | AI has loaded all framework context |
| 1 → 2 | Validation → Intake | All mandatory prompt fields present |
| 2 → 3 | Intake → Planning | Requirements document approved by user |
| 3 → 4 | Planning → Generation | Implementation plan approved by user |
| 4.1 → 4.2 | Infrastructure → Data | `docker-compose up -d` succeeds, all services healthy |
| 4.2 → 4.3 | Data → Business | Data service health checks pass, HTTP APIs functional |
| 4.3 → 4.4 | Business → Workers | API endpoints working, tests pass |
| 4.4 → 4.5 | Workers → Bot | Workers processing events correctly |
| 4.5 → 4.6 | Bot → Testing | Bot responding to commands |
| 4.6 → 5 | Testing → Verification | All tests written and passing |
| 5 → 6 | Verification → Handoff | All quality checks pass |
| 6 → END | Handoff → Complete | Stakeholder sign-off obtained |

### When to Go Back

| Failure Point | Go Back To | Reason |
|---------------|------------|--------|
| Stage 2 | Stage 1 | Architecture conflict detected → need clarification |
| Stage 3 | Stage 2 | Requirements incomplete/unclear |
| Stage 4 | Stage 3 | Plan needs adjustment (e.g., missing services) |
| Stage 5 | Stage 4 | Tests fail, type errors, security issues |
| Stage 6 | Stage 5 | Verification criteria not met |

---

## Document Categories Reference

### Atomic Documents by Domain

| Domain | Path Pattern | When to Read |
|--------|-------------|--------------|
| **Architecture** | `docs/atomic/architecture/*.md` | Stage 2 (Requirements)<br>Stage 3 (Planning) |
| **FastAPI Services** | `docs/atomic/services/fastapi/*.md` | Stage 3 (Planning)<br>Stage 4.3 (Business Logic) |
| **Aiogram Services** | `docs/atomic/services/aiogram/*.md` | Stage 3 (Planning)<br>Stage 4.5 (Bot) |
| **AsyncIO Workers** | `docs/atomic/services/asyncio-workers/*.md` | Stage 3 (Planning)<br>Stage 4.4 (Workers) |
| **Data Services** | `docs/atomic/services/data-services/*.md` | Stage 3 (Planning)<br>Stage 4.2 (Data Layer) |
| **Redis Integration** | `docs/atomic/integrations/redis/*.md` | Stage 3 (if Redis needed)<br>Stage 4 (during implementation) |
| **RabbitMQ Integration** | `docs/atomic/integrations/rabbitmq/*.md` | Stage 3 (Planning)<br>Stage 4.3, 4.4, 4.5 (eventing) |
| **HTTP Communication** | `docs/atomic/integrations/http-communication/*.md` | Stage 4.3 (Business Logic) |
| **Infrastructure** | `docs/atomic/infrastructure/**/*.md` | Stage 4.1 (Infrastructure) |
| **Observability** | `docs/atomic/observability/**/*.md` | Stage 4 (all phases - logging, metrics) |
| **Testing** | `docs/atomic/testing/**/*.md` | Stage 4.6 (Testing)<br>Stage 5 (Verification) |

---

## Quick Lookup: "I Need To..."

| Task | Read These Documents | Generate This | Use This Tool |
|------|---------------------|---------------|---------------|
| **Validate a user prompt** | `PROMPT_VALIDATION_GUIDE.md` | Validation note or clarification | `PROMPT_TEMPLATES.md` |
| **Understand architecture** | `ARCHITECTURE_GUIDE.md`<br>`atomic/architecture/improved-hybrid-overview.md` | Nothing (learning) | None |
| **Structure requirements** | `REQUIREMENTS_INTAKE_TEMPLATE.md` | Completed intake doc | `PROMPT_TEMPLATES.md` |
| **Plan implementation** | `IMPLEMENTATION_PLAN_TEMPLATE.md`<br>`USE_CASE_IMPLEMENTATION_GUIDE.md` | Implementation plan | `AGENT_TOOLBOX.md` |
| **Setup Docker** | `atomic/infrastructure/containerization/docker-compose-setup.md` | docker-compose.yml | `AGENT_TOOLBOX.md` |
| **Create PostgreSQL service** | `atomic/services/data-services/postgres-service-setup.md`<br>`atomic/databases/postgresql/sqlalchemy-integration.md` | Models, repositories, API | `AGENT_TOOLBOX.md` |
| **Create FastAPI endpoint** | `atomic/services/fastapi/routing-patterns.md`<br>`atomic/services/fastapi/dependency-injection.md` | Router + use case | `AGENT_TOOLBOX.md` |
| **Call data service from business service** | `atomic/integrations/http-communication/business-to-data-calls.md` | HTTP client code | None |
| **Publish RabbitMQ event** | `atomic/integrations/rabbitmq/message-publishing.md` | Event publisher code | None |
| **Consume RabbitMQ event** | `atomic/integrations/rabbitmq/message-consuming.md` | Consumer code | None |
| **Create background worker** | `atomic/services/asyncio-workers/main-function-patterns.md` | Worker main.py | `AGENT_TOOLBOX.md` |
| **Create Telegram bot** | `atomic/services/aiogram/bot-initialization.md`<br>`atomic/services/aiogram/handler-patterns.md` | Bot handlers | `AGENT_TOOLBOX.md` |
| **Write tests** | `atomic/testing/unit-testing/pytest-setup.md`<br>`atomic/testing/service-testing/fastapi-testing-patterns.md` | Test files | `AGENT_TOOLBOX.md` |
| **Run quality checks** | `AGENT_VERIFICATION_CHECKLIST.md` | Checklist results | `AGENT_TOOLBOX.md` |
| **Create QA report** | `QA_REPORT_TEMPLATE.md` | QA report | None |
| **Troubleshoot issues** | `troubleshooting.md` | Nothing (diagnosis) | `AGENT_TOOLBOX.md` |

---

## Reading Optimization Tips

### Do NOT Read Everything Upfront

❌ **Anti-pattern**: AI reads all 157 atomic documents at start
✅ **Correct approach**: AI reads documents **on-demand** based on current stage

### Example: P2P Lending Platform

**Stage 0-2** (Init, Validation, Intake):
- Read: 5 documents (~500 lines)
- Time: 2 minutes

**Stage 3** (Planning):
- Read: 10 documents (~1500 lines) - only relevant services
- Time: 5 minutes

**Stage 4.3** (Business Logic - FastAPI):
- Read: 15 FastAPI atomic docs (~2000 lines)
- Time: 7 minutes

**Total reading**: ~30 documents out of 157 (82% saved!)

### How to Decide What to Read

Use this decision tree:

```
┌─ Does project need FastAPI service?
│  ├─ YES → Read atomic/services/fastapi/* during Stage 4.3
│  └─ NO → Skip FastAPI docs entirely
│
┌─ Does project need Telegram bot?
│  ├─ YES → Read atomic/services/aiogram/* during Stage 4.5
│  └─ NO → Skip Aiogram docs entirely
│
┌─ Does project use Redis?
│  ├─ YES → Read atomic/integrations/redis/* during Stage 3-4
│  └─ NO → Skip Redis docs entirely
│
... and so on for each technology
```

---

## Maintenance

### Updating This Matrix

When framework documentation changes:

1. **New atomic documents added** → Add row to "Document Categories Reference"
2. **Workflow stages change** → Update main matrix rows
3. **Templates change** → Update "Templates/Tools" column
4. **Success criteria change** → Update "Success Criteria" column

### Cross-References

Keep aligned with:
- `AI_CODE_GENERATION_MASTER_WORKFLOW.md` (source of truth for process)
- `AGENT_CONTEXT_SUMMARY.md` (critical rules)
- `INDEX.md` (full documentation map)
- All atomic documentation (implementation rules)

---

**Last Updated**: 2025-10-01
