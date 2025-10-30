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

> **NEW**: Each sub-stage now includes "Required At Level" to support adaptive generation based on maturity level selection. See `docs/reference/maturity-levels.md` for level definitions.

| Stage | Phase | Required At Level | Documents to Read | AI Generates | Success Criteria |
|-------|-------|-------------------|-------------------|--------------|------------------|
| **0** | **Initialization** | **ALL** | • `AGENTS.md`<br>• `docs/reference/agent-context-summary.md`<br>• `docs/guides/ai-code-generation-master-workflow.md`<br>• `docs/reference/maturity-levels.md` | Nothing (loading phase) | AI has complete framework context |
| **1** | **Prompt Validation** | **ALL** | • `docs/guides/prompt-validation-guide.md`<br>• `docs/reference/prompt-templates.md`<br>• `docs/reference/maturity-levels.md` (for level selection) | • Validation confirmation<br>• **Selected maturity level (1-4)**<br>• **Selected optional modules** | All mandatory fields present:<br>✅ Business context<br>✅ **Target maturity level**<br>✅ Functional requirements<br>✅ Dependencies |
| **2** | **Requirements Clarification & Intake** | **ALL** | • `docs/guides/requirements-intake-template.md`<br>• `docs/guides/architecture-guide.md`<br>• `docs/reference/tech_stack.md`<br>• `docs/atomic/architecture/improved-hybrid-overview.md` | • Completed Requirements Intake<br>• **Maturity level confirmed**<br>• Architecture compatibility analysis | • Requirements approved<br>• Maturity level documented<br>• Architecture aligned |
| **3** | **Architecture Mapping & Planning** | **ALL** | • `docs/guides/implementation-plan-template.md`<br>• `docs/reference/conditional-stage-rules.md`<br>• `docs/checklists/service-naming-checklist.md`<br>• `docs/atomic/architecture/naming/README.md` (Section 2.3)<br>• `docs/atomic/services/**/*` (based on level + modules)<br>• `docs/atomic/integrations/**/*` (if needed) | • Implementation Plan with:<br>&nbsp;&nbsp;• **Included features list**<br>&nbsp;&nbsp;• **Skipped features list**<br>&nbsp;&nbsp;• Conditional sub-stages<br>• Service names (DEFAULT TO 3-PART) | • Plan approved<br>• Features clearly marked<br>• Sub-stages identified<br>• Naming follows conventions |
| **4.1** | **Infrastructure (Basic)** | **ALL** | • `docs/reference/project-structure.md` (§Creating the Project Structure)<br>• `docs/atomic/architecture/project-structure-patterns.md`<br>• `docs/atomic/infrastructure/containerization/docker-compose-setup.md`<br>• `docs/atomic/infrastructure/containerization/dockerfile-patterns.md` | • **Complete directory structure** (per project-structure.md)<br>• `docker-compose.yml`<br>• `.env.example`<br>• `Makefile` | • All directories created and verified<br>• Docker services healthy |
| **4.1b** | **+ Dev Overrides** | **≥ Level 2** | • `docs/atomic/infrastructure/configuration/settings-patterns.md` | • `docker-compose.dev.yml`<br>• Docker healthchecks | • Dev environment working |
| **4.1c** | **+ Nginx + SSL + Metrics** | **≥ Level 3** | • `docs/atomic/infrastructure/api-gateway/nginx-setup.md`<br>• `docs/atomic/infrastructure/api-gateway/ssl-configuration.md`<br>• `docs/atomic/observability/metrics/prometheus-setup.md` | • Nginx config<br>• SSL setup<br>• Prometheus + Grafana<br>• `docker-compose.prod.yml` | • Nginx reverse proxy working<br>• SSL functional<br>• Metrics exposed |
| **4.1d** | **+ ELK + Replication** | **Level 4 only** | • `docs/atomic/observability/elk-stack/*`<br>• `docs/atomic/infrastructure/databases/postgresql-replication.md` | • ELK Stack config<br>• DB replication<br>• Backup scripts | • Centralized logging<br>• DB replication active |
| **4.2** | **Data Layer (PostgreSQL)** | **ALL** | • `docs/atomic/services/data-services/postgres-service-setup.md`<br>• `docs/atomic/databases/postgresql/sqlalchemy-integration.md` | • PostgreSQL service<br>• Models, repositories<br>• HTTP API<br>• Migrations | • Data service health checks pass<br>• HTTP API functional |
| **4.2b** | **+ MongoDB (optional)** | **IF user requested** | • `docs/atomic/services/data-services/mongo-service-setup.md` | • MongoDB service | • MongoDB API functional |
| **4.3** | **Business Logic (Core)** | **ALL** | • `docs/atomic/services/fastapi/application-factory.md`<br>• `docs/atomic/services/fastapi/routing-patterns.md`<br>• `docs/atomic/services/fastapi/dependency-injection.md`<br>• `docs/atomic/services/fastapi/schema-validation.md`<br>• `docs/atomic/services/fastapi/error-handling.md`<br>• `docs/atomic/architecture/ddd-hexagonal-principles.md`<br>• `docs/atomic/integrations/http-communication/business-to-data-calls.md` | **Domain Layer**:<br>• Entities, Value objects<br><br>**Application Layer**:<br>• Use cases, DTOs<br><br>**Infrastructure Layer**:<br>• HTTP clients (to data services)<br><br>**API Layer**:<br>• FastAPI routers<br>• Request/response schemas | • API endpoints functional<br>• HTTP-only data access verified |
| **4.3b** | **+ Structured Logging** | **≥ Level 2** | • `docs/atomic/observability/logging/structured-logging.md`<br>• `docs/atomic/observability/logging/log-correlation.md` | • Logger setup<br>• Request ID propagation<br>• Error logging | • Logs are structured JSON<br>• Correlation IDs present |
| **4.3c** | **+ Prometheus Metrics** | **≥ Level 3** | • `docs/atomic/observability/metrics/prometheus-setup.md`<br>• `docs/atomic/observability/metrics/custom-metrics.md` | • Metrics endpoints<br>• Custom business metrics | • `/metrics` endpoint works<br>• Grafana dashboards |
| **4.3d** | **+ OAuth/JWT + Tracing** | **Level 4 only** | • `docs/atomic/services/fastapi/oauth-jwt.md` *(TODO: not yet created)*<br>• `docs/atomic/observability/tracing/jaeger-configuration.md` | • OAuth 2.0 / JWT auth<br>• RBAC middleware<br>• Distributed tracing | • Auth functional<br>• Traces visible in Jaeger |
| **4.4** | **Background Workers (optional)** | **IF user requested** | • `docs/atomic/services/asyncio-workers/basic-setup.md`<br>• `docs/atomic/services/asyncio-workers/main-function-patterns.md`<br>• `docs/atomic/services/asyncio-workers/signal-handling.md`<br>• `docs/atomic/integrations/rabbitmq/message-consuming.md` | • Worker implementations<br>• RabbitMQ consumers<br>• Main entrypoint with signal handling | • Workers start successfully<br>• Event consumption working |
| **4.4b** | **+ Structured Logging (Workers)** | **≥ Level 2 AND Workers requested** | • `docs/atomic/observability/logging/structured-logging.md` *(adapted for workers)* | • Worker logger setup | • Worker logs structured |
| **4.5** | **Telegram Bot (optional)** | **IF user requested** | • `docs/atomic/services/aiogram/basic-setup.md`<br>• `docs/atomic/services/aiogram/bot-initialization.md`<br>• `docs/atomic/services/aiogram/handler-patterns.md`<br>• `docs/atomic/integrations/rabbitmq/aiogram-integration.md` | • Bot handlers (commands, messages)<br>• RabbitMQ event listeners<br>• Main entrypoint | • Bot responds to commands<br>• Event-based notifications working |
| **4.5b** | **+ Structured Logging (Bot)** | **≥ Level 2 AND Bot requested** | • `docs/atomic/observability/logging/structured-logging.md` *(adapted for bots)* | • Bot logger setup | • Bot logs structured |
| **4.6** | **Testing (Basic)** | **ALL** | • `docs/atomic/testing/unit-testing/pytest-setup.md`<br>• `docs/atomic/testing/unit-testing/fixture-patterns.md`<br>• `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` | • `pytest.ini`<br>• `conftest.py`<br>• Unit tests (core layers)<br>• Service tests | • All tests pass<br>• Coverage ≥ 60% (Level 1) |
| **4.6b** | **+ Integration Tests** | **≥ Level 2** | • `docs/atomic/testing/integration-testing/testcontainers-setup.md`<br>• `docs/atomic/testing/unit-testing/mocking-strategies.md` | • Integration tests (with testcontainers)<br>• Enhanced mocking | • Coverage ≥ 75% |
| **4.6c** | **+ E2E Tests** | **≥ Level 3** | • `docs/atomic/testing/end-to-end-testing/e2e-test-setup.md` | • End-to-end API tests | • Coverage ≥ 80% |
| **4.6d** | **+ Security Tests** | **Level 4 only** | • `docs/atomic/testing/quality-assurance/linting-standards.md` *(includes Bandit)*<br>• `docs/atomic/testing/end-to-end-testing/performance-testing.md` | • Security test suite<br>• Bandit config | • Coverage ≥ 85%<br>• Security tests pass |
| **5** | **Quality Verification** | **ALL** (criteria vary by level) | • `docs/quality/agent-verification-checklist.md`<br>• `docs/reference/agent-toolbox.md`<br>• `docs/reference/maturity-levels.md` (for coverage targets)<br>• `docs/reference/troubleshooting.md` (if issues) | • Completed verification checklist<br>• Coverage reports (HTML + XML)<br>• Evidence logs/screenshots | **ALL checks must pass**:<br>✅ Linting (Ruff): 0 errors<br>✅ Formatting: No drift<br>✅ Type checking (Mypy): 0 errors<br>✅ Security (Bandit): 0 high severity<br>✅ Tests: All pass<br>✅ Coverage: **Level-dependent** (60%/75%/80%/85%)<br>✅ Project structure: Compliant<br>✅ Naming: Follows conventions |
| **6** | **QA Report & Handoff** | **ALL** | • `docs/quality/qa-report-template.md`<br>• `docs/reference/deliverables-catalog.md` | • Final QA Report<br>• Deliverables summary<br>• Deployment guide<br>• Updated DELIVERABLES_CATALOG | • QA report approved by stakeholder<br>• All deliverables documented<br>• Deployment instructions verified<br>• Sign-off obtained |

---

## Stage Transition Rules

> **NEW**: Transition rules now account for conditional sub-stages. AI must check maturity level and optional modules before proceeding.

### When to Proceed to Next Stage

| From Stage | To Stage | Transition Criteria |
|------------|----------|---------------------|
| 0 → 1 | Initialization → Validation | AI has loaded all framework context |
| 1 → 2 | Validation → Intake | All mandatory prompt fields present, **maturity level selected** |
| 2 → 3 | Intake → Planning | Requirements document approved by user |
| 3 → 4.1 | Planning → Generation | Implementation plan approved by user |
| 4.1 → 4.1b | Infrastructure (Basic) → Dev Overrides | **IF maturity level ≥ 2** AND 4.1 complete |
| 4.1b → 4.1c | Dev Overrides → Nginx+SSL | **IF maturity level ≥ 3** AND 4.1b complete |
| 4.1c → 4.1d | Nginx+SSL → ELK+Replication | **IF maturity level = 4** AND 4.1c complete |
| 4.1x → 4.2 | Infrastructure → Data | All applicable infrastructure sub-stages complete |
| 4.2 → 4.2b | PostgreSQL → MongoDB | **IF user requested MongoDB** AND 4.2 complete |
| 4.2x → 4.3 | Data → Business Logic | All applicable data sub-stages complete |
| 4.3 → 4.3b | Core Business → Logging | **IF maturity level ≥ 2** AND 4.3 complete |
| 4.3b → 4.3c | Logging → Metrics | **IF maturity level ≥ 3** AND 4.3b complete |
| 4.3c → 4.3d | Metrics → Auth+Tracing | **IF maturity level = 4** AND 4.3c complete |
| 4.3x → 4.4 | Business → Workers | **IF user requested Workers** OR proceed to 4.5 |
| 4.4 → 4.4b | Workers Core → Workers Logging | **IF maturity level ≥ 2** AND 4.4 complete |
| 4.4x → 4.5 | Workers → Bot | **IF user requested Bot** OR proceed to 4.6 |
| 4.5 → 4.5b | Bot Core → Bot Logging | **IF maturity level ≥ 2** AND 4.5 complete |
| 4.5x → 4.6 | Bot → Testing | All applicable service sub-stages complete |
| 4.6 → 4.6b | Basic Tests → Integration Tests | **IF maturity level ≥ 2** AND 4.6 complete |
| 4.6b → 4.6c | Integration → E2E Tests | **IF maturity level ≥ 3** AND 4.6b complete |
| 4.6c → 4.6d | E2E → Security Tests | **IF maturity level = 4** AND 4.6c complete |
| 4.6x → 5 | Testing → Verification | All applicable test sub-stages complete |
| 5 → 6 | Verification → Handoff | All quality checks pass (level-specific criteria) |
| 6 → END | Handoff → Complete | Stakeholder sign-off obtained |

### When to Go Back

| Failure Point | Go Back To | Reason |
|---------------|------------|--------|
| Stage 2 | Stage 1 | Architecture conflict detected → need clarification |
| Stage 3 | Stage 2 | Requirements incomplete/unclear |
| Stage 4 | Stage 3 | Plan needs adjustment (e.g., missing services) |
| Stage 5 | Stage 4 | Tests fail, type errors, security issues |
| Stage 6 | Stage 5 | Verification criteria not met |

### Sub-Stage Execution Logic

**AI Decision Tree at Stage 4**:

```
FOR each sub-stage in [4.1, 4.1b, 4.1c, 4.1d, 4.2, 4.2b, 4.3, 4.3b, 4.3c, 4.3d, 4.4, 4.4b, 4.5, 4.5b, 4.6, 4.6b, 4.6c, 4.6d]:
  READ "Required At Level" column

  IF "Required At Level" = "ALL":
    EXECUTE sub-stage (mandatory for all levels)

  ELSE IF "Required At Level" = "≥ Level X":
    IF user's maturity level >= X:
      EXECUTE sub-stage
    ELSE:
      SKIP sub-stage

  ELSE IF "Required At Level" = "Level X only":
    IF user's maturity level == X:
      EXECUTE sub-stage
    ELSE:
      SKIP sub-stage

  ELSE IF "Required At Level" = "IF user requested [module]":
    IF user selected [module] in optional modules:
      EXECUTE sub-stage
    ELSE:
      SKIP sub-stage

  ELSE IF "Required At Level" contains "AND":
    PARSE compound condition (e.g., "≥ Level 2 AND Workers requested")
    IF all conditions true:
      EXECUTE sub-stage
    ELSE:
      SKIP sub-stage
```

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
| **Validate a user prompt** | `docs/guides/prompt-validation-guide.md` | Validation note or clarification | `docs/reference/prompt-templates.md` |
| **Understand architecture** | `docs/guides/architecture-guide.md`<br>`docs/atomic/architecture/improved-hybrid-overview.md` | Nothing (learning) | None |
| **Structure requirements** | `docs/guides/requirements-intake-template.md` | Completed intake doc | `docs/reference/prompt-templates.md` |
| **Plan implementation** | `docs/guides/implementation-plan-template.md`<br>`docs/guides/use-case-implementation-guide.md` | Implementation plan | `docs/reference/agent-toolbox.md` |
| **Setup Docker** | `docs/atomic/infrastructure/containerization/docker-compose-setup.md` | docker-compose.yml | `docs/reference/agent-toolbox.md` |
| **Create PostgreSQL service** | `docs/atomic/services/data-services/postgres-service-setup.md`<br>`docs/atomic/databases/postgresql/sqlalchemy-integration.md` | Models, repositories, API | `docs/reference/agent-toolbox.md` |
| **Create FastAPI endpoint** | `docs/atomic/services/fastapi/routing-patterns.md`<br>`docs/atomic/services/fastapi/dependency-injection.md` | Router + use case | `docs/reference/agent-toolbox.md` |
| **Call data service from business service** | `docs/atomic/integrations/http-communication/business-to-data-calls.md` | HTTP client code | None |
| **Publish RabbitMQ event** | `docs/atomic/integrations/rabbitmq/message-publishing.md` | Event publisher code | None |
| **Consume RabbitMQ event** | `docs/atomic/integrations/rabbitmq/message-consuming.md` | Consumer code | None |
| **Create background worker** | `docs/atomic/services/asyncio-workers/main-function-patterns.md` | Worker main.py | `docs/reference/agent-toolbox.md` |
| **Create Telegram bot** | `docs/atomic/services/aiogram/bot-initialization.md`<br>`docs/atomic/services/aiogram/handler-patterns.md` | Bot handlers | `docs/reference/agent-toolbox.md` |
| **Write tests** | `docs/atomic/testing/unit-testing/pytest-setup.md`<br>`docs/atomic/testing/service-testing/fastapi-testing-patterns.md` | Test files | `docs/reference/agent-toolbox.md` |
| **Run quality checks** | `docs/quality/agent-verification-checklist.md` | Checklist results | `docs/reference/agent-toolbox.md` |
| **Create QA report** | `docs/quality/qa-report-template.md` | QA report | None |
| **Troubleshoot issues** | `docs/reference/troubleshooting.md` | Nothing (diagnosis) | `docs/reference/agent-toolbox.md` |

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

### Reading Order Within Phase

When multiple atomic documents are listed for a single phase, read them in this recommended order:

**1. Architecture principles first** (understand constraints before implementation)
   - `docs/atomic/architecture/ddd-hexagonal-principles.md`
   - `docs/atomic/architecture/service-separation-principles.md`
   - `docs/atomic/architecture/data-access-architecture.md`
   - `docs/atomic/architecture/naming-conventions.md`

**2. Setup/scaffolding documents** (project structure)
   - `docs/atomic/services/fastapi/basic-setup.md`
   - `docs/atomic/services/fastapi/application-factory.md`
   - `docs/atomic/services/aiogram/bot-initialization.md`
   - `docs/atomic/services/asyncio-workers/main-function-patterns.md`

**3. Core implementation patterns** (business logic)
   - `docs/atomic/services/fastapi/routing-patterns.md`
   - `docs/atomic/services/aiogram/handler-patterns.md`
   - `docs/atomic/services/fastapi/dependency-injection.md`
   - `docs/atomic/services/fastapi/schema-validation.md`
   - `docs/atomic/services/data-services/repository-patterns.md`

**4. Integration patterns** (external communication)
   - `docs/atomic/integrations/http-communication/business-to-data-calls.md`
   - `docs/atomic/integrations/rabbitmq/message-publishing.md`
   - `docs/atomic/integrations/rabbitmq/message-consuming.md`
   - `docs/atomic/integrations/redis/caching-patterns.md` *(TODO: document not yet created)*

**5. Advanced features** (observability, security, error handling)
   - `docs/atomic/services/aiogram/middleware-setup.md`
   - `docs/atomic/services/fastapi/error-handling.md`
   - `docs/atomic/observability/logging/structured-logging.md`
   - `docs/atomic/observability/metrics/custom-metrics.md`
   - `docs/atomic/services/fastapi/oauth-jwt.md` *(TODO: document not yet created)*

**Rationale**: This order ensures AI understands:
- **Why** before **how** (architecture → implementation)
- **Structure** before **details** (setup → patterns)
- **Core** before **advanced** (basic logic → integrations → observability)

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
- `docs/guides/ai-code-generation-master-workflow.md` (source of truth for process)
- `docs/reference/agent-context-summary.md` (critical rules)
- `INDEX.md` (full documentation map)
- All atomic documentation (implementation rules)

---

**Last Updated**: 2025-10-01
