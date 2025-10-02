# Conditional Stage Rules

> **Purpose**: Define which workflow stages and atomic documents AI must read/generate based on the selected Maturity Level. This document ensures AI generates only the appropriate complexity for each level, avoiding over-engineering while maintaining clear upgrade paths.

## Overview

The AI code generation workflow (Stages 0-6) remains the same across all Maturity Levels, but **Stage 4 (Code Generation)** becomes **conditional** based on the selected level. This document provides exact rules for what to include/skip at each level.

---

## Core Principle

```
ALL Levels include:
  ├─ Stage 0: Initialization (MANDATORY)
  ├─ Stage 1: Prompt Validation (MANDATORY)
  ├─ Stage 2: Requirements Intake (MANDATORY)
  ├─ Stage 3: Implementation Planning (MANDATORY)
  ├─ Stage 4: Code Generation (CONDITIONAL — see below)
  ├─ Stage 5: Quality Verification (MANDATORY, criteria vary)
  └─ Stage 6: QA Report & Handoff (MANDATORY)

The ONLY difference between levels is Stage 4 sub-phases.
```

---

## Stage 4 Breakdown by Maturity Level

### Level 1: Proof of Concept (PoC)

#### Sub-Stages to Execute

| Sub-Stage | Phase | Action |
|-----------|-------|--------|
| **4.1** | Infrastructure | **EXECUTE** (Basic) |
| **4.2** | Data Layer | **EXECUTE** (PostgreSQL only) |
| **4.3** | Business Logic | **EXECUTE** (Core only) |
| **4.4** | Background Workers | **CONDITIONAL** (if user requested) |
| **4.5** | Telegram Bot | **CONDITIONAL** (if user requested) |
| **4.6** | Testing | **EXECUTE** (Basic tests, 60% coverage) |

#### 4.1: Infrastructure (Basic)

**Documents to Read:**
- `docs/atomic/infrastructure/containerization/docker-compose-setup.md`
- `docs/atomic/infrastructure/containerization/dockerfile-patterns.md` (single-stage only)
- `docs/atomic/infrastructure/configuration/environment-variables.md`

**Generate:**
- `docker-compose.yml` (dev only, no production config)
- `.env.example`
- `Makefile` (basic commands: up, down, logs)
- Simple Dockerfiles (single-stage builds)

**Skip:**
- ❌ Nginx configuration
- ❌ SSL/TLS setup
- ❌ Multi-stage Docker builds
- ❌ Production deployment configs
- ❌ Health check probes

#### 4.2: Data Layer (PostgreSQL only)

**Documents to Read:**
- `docs/atomic/services/data-services/postgres-service-setup.md`
- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/services/data-services/http-api-design.md`
- `docs/atomic/databases/postgresql/sqlalchemy-integration.md`

**Generate:**
- PostgreSQL data service (models, repositories, HTTP API)
- Alembic migrations (basic)

**Skip:**
- ❌ MongoDB service
- ❌ Database replication
- ❌ Advanced PostgreSQL features (partitioning, etc.)
- ❌ Connection pooling optimization

#### 4.3: Business Logic (Core only)

**Documents to Read:**
- `docs/atomic/services/fastapi/application-factory.md`
- `docs/atomic/services/fastapi/routing-patterns.md`
- `docs/atomic/services/fastapi/dependency-injection.md`
- `docs/atomic/services/fastapi/schema-validation.md`
- `docs/atomic/integrations/http-communication/business-to-data-calls.md`

**Generate:**
- FastAPI service (routers, use cases, domain entities)
- HTTP client to data service
- Basic error handling

**Skip:**
- ❌ Structured logging (use print/console logs)
- ❌ Health check endpoints
- ❌ Prometheus metrics
- ❌ Request ID middleware
- ❌ Error tracking integration (Sentry)
- ❌ OpenAPI customization (use defaults)

#### 4.6: Testing (Basic)

**Documents to Read:**
- `docs/atomic/testing/unit-testing/pytest-setup.md`
- `docs/atomic/testing/unit-testing/fixture-patterns.md`

**Generate:**
- `pytest.ini`
- Unit tests (core logic only)

**Skip:**
- ❌ Integration tests with testcontainers
- ❌ Service tests (end-to-end)
- ❌ Load tests
- ❌ Security tests

**Quality Criteria (Stage 5):**
- Coverage ≥ 60% (relaxed)
- Ruff + Mypy pass
- No Bandit requirement

---

### Level 2: Development Ready

#### Sub-Stages to Execute

| Sub-Stage | Phase | Action |
|-----------|-------|--------|
| **4.1** | Infrastructure | **EXECUTE** (+ Dev overrides) |
| **4.2** | Data Layer | **EXECUTE** (PostgreSQL only) |
| **4.3** | Business Logic | **EXECUTE** (+ Observability) |
| **4.4** | Background Workers | **CONDITIONAL** (if user requested) |
| **4.5** | Telegram Bot | **CONDITIONAL** (if user requested) |
| **4.6** | Testing | **EXECUTE** (+ Integration tests) |

#### 4.1: Infrastructure (+ Dev Overrides)

**Additional Documents:**
- `docs/atomic/infrastructure/configuration/settings-patterns.md`

**Additional Generation:**
- `docker-compose.dev.yml` (dev overrides: hot reload, debug mode)
- `docker-compose.test.yml` (test environment)
- Docker health checks (basic)

**Still Skip:**
- ❌ Nginx
- ❌ SSL
- ❌ Production configs

#### 4.3: Business Logic (+ Observability)

**Additional Documents:**
- `docs/atomic/observability/logging/structured-logging.md`
- `docs/atomic/observability/logging/request-id-tracking.md`
- `docs/atomic/observability/error-tracking/sentry-integration.md`
- `docs/atomic/services/fastapi/middleware-setup.md`

**Additional Generation:**
- Structured logging (JSON format)
- Request ID middleware
- Health check endpoints (`/health`, `/ready`)
- Error tracking integration (Sentry-ready, not deployed)
- Custom OpenAPI metadata

**Still Skip:**
- ❌ Prometheus metrics
- ❌ Distributed tracing
- ❌ ELK stack

#### 4.6: Testing (+ Integration Tests)

**Additional Documents:**
- `docs/atomic/testing/integration-testing/testcontainers-setup.md`
- `docs/atomic/testing/integration-testing/database-testing.md`

**Additional Generation:**
- Integration tests (with testcontainers)
- `conftest.py` (shared fixtures)

**Quality Criteria (Stage 5):**
- Coverage ≥ 75%
- Ruff + Mypy + Bandit pass

---

### Level 3: Pre-Production

#### Sub-Stages to Execute

| Sub-Stage | Phase | Action |
|-----------|-------|--------|
| **4.1** | Infrastructure | **EXECUTE** (+ Nginx + SSL + Metrics) |
| **4.2** | Data Layer | **EXECUTE** (PostgreSQL only) |
| **4.3** | Business Logic | **EXECUTE** (+ Metrics) |
| **4.4** | Background Workers | **CONDITIONAL** (if user requested) |
| **4.5** | Telegram Bot | **CONDITIONAL** (if user requested) |
| **4.6** | Testing | **EXECUTE** (+ Service tests + Load tests) |

#### 4.1: Infrastructure (+ Nginx + SSL + Metrics)

**Additional Documents:**
- `docs/atomic/infrastructure/api-gateway/nginx-setup.md`
- `docs/atomic/infrastructure/api-gateway/ssl-configuration.md`
- `docs/atomic/infrastructure/api-gateway/load-balancing.md`
- `docs/atomic/infrastructure/api-gateway/security-hardening.md` (basic)
- `docs/atomic/infrastructure/containerization/multi-stage-builds.md`
- `docs/atomic/observability/metrics/prometheus-setup.md`
- `docs/atomic/observability/metrics/grafana-dashboards.md`

**Additional Generation:**
- Nginx configuration (reverse proxy, rate limiting, CORS)
- SSL/TLS setup (Let's Encrypt instructions)
- Multi-stage Dockerfiles (optimized images)
- `docker-compose.prod.yml` (production config)
- Prometheus + Grafana stack
- Basic dashboards (API overview)
- Alerting rules (basic thresholds)

**Still Skip:**
- ❌ Jaeger tracing
- ❌ ELK stack
- ❌ Advanced security (OAuth, RBAC)
- ❌ Database replication

#### 4.3: Business Logic (+ Metrics)

**Additional Documents:**
- `docs/atomic/observability/metrics/application-metrics.md`
- `docs/atomic/services/fastapi/metrics-integration.md`

**Additional Generation:**
- Prometheus metrics endpoints
- Custom metrics (request duration, error rates)
- Metrics middleware

**Still Skip:**
- ❌ Distributed tracing
- ❌ OAuth/JWT
- ❌ RBAC
- ❌ Circuit breakers

#### 4.6: Testing (+ Service Tests + Load Tests)

**Additional Documents:**
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md`
- `docs/atomic/testing/end-to-end-testing/user-journey-testing.md`
- `docs/atomic/testing/end-to-end-testing/performance-testing.md`

**Additional Generation:**
- Service tests (end-to-end)
- Load test scripts (basic)

**Quality Criteria (Stage 5):**
- Coverage ≥ 80%
- Ruff + Mypy + Bandit pass
- Load test baseline established

---

### Level 4: Production

#### Sub-Stages to Execute (ALL)

| Sub-Stage | Phase | Action |
|-----------|-------|--------|
| **4.1** | Infrastructure | **EXECUTE** (Full: Nginx + SSL + ELK + Jaeger + HA) |
| **4.2** | Data Layer | **EXECUTE** (+ Replication) |
| **4.3** | Business Logic | **EXECUTE** (Full: OAuth + RBAC + Tracing + Resilience) |
| **4.4** | Background Workers | **CONDITIONAL** (if user requested) |
| **4.5** | Telegram Bot | **CONDITIONAL** (if user requested) |
| **4.6** | Testing | **EXECUTE** (Full: Security + E2E + Load) |
| **4.7** | CI/CD | **EXECUTE** (NEW: Automated pipelines) |
| **4.8** | Documentation | **EXECUTE** (NEW: ADRs + Runbooks) |

#### 4.1: Infrastructure (Full Stack)

**Additional Documents:**
- `docs/atomic/observability/elk-stack/elasticsearch-setup.md`
- `docs/atomic/observability/elk-stack/logstash-configuration.md`
- `docs/atomic/observability/elk-stack/kibana-dashboards.md`
- `docs/atomic/observability/tracing/jaeger-setup.md`
- `docs/atomic/infrastructure/databases/postgresql-replication.md`
- `docs/atomic/infrastructure/deployment/production-deployment.md`

**Additional Generation:**
- ELK Stack configuration
- Jaeger distributed tracing
- Database replication setup (master-slave)
- Backup scripts (automated)
- Disaster recovery documentation

#### 4.2: Data Layer (+ Replication)

**Additional Documents:**
- `docs/atomic/databases/postgresql-advanced/replication-strategies.md`
- `docs/atomic/databases/postgresql-advanced/backup-restore.md`

**Additional Generation:**
- PostgreSQL replication config
- Automated backup scripts
- Point-in-time recovery setup

#### 4.3: Business Logic (Full Security + Tracing)

**Additional Documents:**
- `docs/atomic/security/authentication-authorization-guide.md`
- `docs/atomic/security/authorization-patterns.md` (RBAC)
- `docs/atomic/security/session-management-patterns.md`
- `docs/atomic/observability/tracing/jaeger-integration.md`
- `docs/atomic/services/fastapi/security-patterns.md`
- `docs/atomic/integrations/cross-service/circuit-breaker-patterns.md`

**Additional Generation:**
- OAuth 2.0 / JWT authentication
- RBAC implementation (roles, permissions)
- Session management (distributed)
- Distributed tracing integration
- Circuit breakers
- Security headers middleware
- Secrets management integration (Vault-ready)
- Audit logging

#### 4.6: Testing (Full Suite)

**Additional Documents:**
- `docs/atomic/security/security-testing-guide.md`
- All testing documents (comprehensive coverage)

**Additional Generation:**
- Security tests (OWASP)
- Performance tests (comprehensive)
- Chaos engineering tests (basic)

**Quality Criteria (Stage 5):**
- Coverage ≥ 85%
- Ruff + Mypy + Bandit (strict) pass
- Security scan (0 high severity)
- Load tests pass (defined SLAs)

#### 4.7: CI/CD (NEW)

**Documents to Read:**
- `docs/atomic/infrastructure/deployment/ci-cd-patterns.md`

**Generate:**
- `.github/workflows/ci.yml` (or `.gitlab-ci.yml`)
- Automated testing pipeline
- Security scanning pipeline
- Deployment pipelines (staging + production)
- Rollback procedures

#### 4.8: Documentation (NEW)

**Documents to Read:**
- `docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md`

**Generate:**
- ADRs (for major decisions made during generation)
- Runbooks (incident response procedures)
- Deployment guide (comprehensive)
- Monitoring guide (alert responses)

---

## Decision Tree for AI

```
1. User selects Maturity Level → Store in Requirements Intake

2. At Stage 3 (Planning):
   - Read MATURITY_LEVELS.md
   - Read this document (CONDITIONAL_STAGE_RULES.md)
   - Generate Implementation Plan with ONLY relevant phases

3. At Stage 4 (Code Generation):
   FOR each sub-stage (4.1, 4.2, 4.3, etc.):
     IF sub-stage is MANDATORY for this level:
       - Read documents listed for this level
       - Generate artifacts listed for this level
       - Run validation checks
     ELSE IF sub-stage is CONDITIONAL:
       IF user requested this module (e.g., Workers, Bot):
         - Execute sub-stage
       ELSE:
         - Skip sub-stage, mark as "Not Requested"
     ELSE:
       - Skip sub-stage entirely

4. At Stage 5 (Verification):
   - Use quality criteria specific to this level
   - Adjust coverage thresholds
   - Run security scans only if Level ≥ 2

5. At Stage 6 (QA Report):
   - Document which level was generated
   - List upgrade path to next level
```

---

## Stage Transition Rules (Updated)

### When to Proceed to Next Sub-Stage

| From | To | Condition |
|------|----| |
| 4.1 → 4.2 | Infrastructure → Data | Docker services healthy |
| 4.2 → 4.3 | Data → Business | Data service HTTP APIs functional |
| 4.3 → 4.4 | Business → Workers | API endpoints working **OR** Workers not needed (skip to 4.5) |
| 4.4 → 4.5 | Workers → Bot | Workers functional **OR** Bot not needed (skip to 4.6) |
| 4.5 → 4.6 | Bot → Testing | Bot functional **OR** Bot not needed |
| 4.6 → 4.7 | Testing → CI/CD | All tests pass **AND** Level = 4 **OR** Level < 4 (skip to Stage 5) |
| 4.7 → 4.8 | CI/CD → Documentation | Pipelines configured **AND** Level = 4 **OR** skip to Stage 5 |
| 4.8 → 5 | Documentation → Verification | ADRs + Runbooks created **OR** Level < 4 |

---

## Examples: Stage 4 Execution by Level

### Example 1: Level 1 (PoC) — Simple REST API

**User Selection:**
- Maturity Level: 1 (PoC)
- Optional Modules: None

**Stage 4 Execution:**
```
✅ 4.1: Infrastructure (Basic)
   - Generated: docker-compose.yml, .env, Makefile, simple Dockerfiles
   - Skipped: Nginx, SSL, multi-stage builds

✅ 4.2: Data Layer (PostgreSQL)
   - Generated: PostgreSQL service, models, repositories, API
   - Skipped: MongoDB, replication

✅ 4.3: Business Logic (Core)
   - Generated: FastAPI service, routers, domain logic, HTTP client
   - Skipped: Structured logging, metrics, health checks

⏭️  4.4: SKIPPED (Workers not requested)

⏭️  4.5: SKIPPED (Bot not requested)

✅ 4.6: Testing (Basic)
   - Generated: Unit tests
   - Skipped: Integration tests, load tests

→ Proceed to Stage 5 (Verification with 60% coverage target)
```

**Total Time:** ~5 minutes

---

### Example 2: Level 3 (Pre-Production) + Workers + RabbitMQ

**User Selection:**
- Maturity Level: 3 (Pre-Production)
- Optional Modules: Background Workers, RabbitMQ

**Stage 4 Execution:**
```
✅ 4.1: Infrastructure (Full for Level 3)
   - Generated: docker-compose.yml, docker-compose.prod.yml, Nginx, SSL,
                multi-stage Dockerfiles, Prometheus, Grafana
   - Skipped: ELK, Jaeger, CI/CD

✅ 4.2: Data Layer (PostgreSQL)
   - Generated: PostgreSQL service with optimization
   - Skipped: Replication (Level 4 only)

✅ 4.3: Business Logic (+ Observability + Metrics)
   - Generated: FastAPI, structured logging, health checks, Prometheus metrics,
                RabbitMQ publisher
   - Skipped: OAuth, RBAC, tracing, circuit breakers

✅ 4.4: Background Workers (User requested)
   - Generated: AsyncIO workers, RabbitMQ consumers, task management
   - Read: docs/atomic/services/asyncio-workers/*
   - Read: docs/atomic/integrations/rabbitmq/*

⏭️  4.5: SKIPPED (Bot not requested)

✅ 4.6: Testing (+ Service tests + Load tests)
   - Generated: Unit, integration, service, load tests
   - Skipped: Security tests (Level 4 only)

→ Proceed to Stage 5 (Verification with 80% coverage target)
```

**Total Time:** ~17 minutes

---

### Example 3: Level 4 (Production) — Full Stack

**User Selection:**
- Maturity Level: 4 (Production)
- Optional Modules: All available

**Stage 4 Execution:**
```
✅ 4.1: Infrastructure (Full Stack)
   - Generated: Everything from Level 3 + ELK + Jaeger + DB replication + backups

✅ 4.2: Data Layer (+ Replication)
   - Generated: PostgreSQL service with master-slave replication, automated backups

✅ 4.3: Business Logic (Full Security + Tracing)
   - Generated: Everything from Level 3 + OAuth + RBAC + tracing + circuit breakers

✅ 4.4: Background Workers (if requested)
   - Generated: Full workers with resilience patterns

✅ 4.5: Telegram Bot (if requested)
   - Generated: Full bot with security

✅ 4.6: Testing (Full Suite)
   - Generated: Unit + integration + service + security + load + chaos tests

✅ 4.7: CI/CD (NEW at Level 4)
   - Generated: GitHub Actions workflows (CI + security + deploy)

✅ 4.8: Documentation (NEW at Level 4)
   - Generated: ADRs + Runbooks + Deployment guides

→ Proceed to Stage 5 (Verification with 85% coverage target + strict security)
```

**Total Time:** ~32 minutes

---

## Maintenance

- Update this document when new sub-stages are added to Stage 4.
- Keep synchronized with `MATURITY_LEVELS.md` feature matrix.
- Ensure atomic documentation paths are accurate.
- Follow `STYLE_GUIDE.md` for formatting.
