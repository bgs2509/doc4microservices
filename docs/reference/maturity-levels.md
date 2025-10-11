# Maturity Levels

> **Purpose**: Define four incremental maturity levels for AI-generated applications, from proof-of-concept to production-ready enterprise systems. Each level adds specific infrastructure, observability, and security layers on top of the previous level.

## Overview

When starting a new project, users must select a **Target Maturity Level** that matches their current needs. The AI will generate only the features and infrastructure appropriate for that level, avoiding over-engineering while maintaining a clear upgrade path.

```
Level 1 (PoC)  →  Level 2 (Development)  →  Level 3 (Pre-Production)  →  Level 4 (Production)
    Core              + Observability           + Infrastructure              + Security & HA
```

---

## Level 1: Proof of Concept (PoC) 🧪

### Goal
Validate business idea, build MVP, demonstrate to stakeholders.

### Target Audience
- Solo developers testing an idea
- Startups building first prototype
- Teams creating demo for investors
- Learning projects

### Time to Generate
**~5-7 minutes**

### What's Included

#### Core Services (MANDATORY)
- ✅ **FastAPI** (REST API business service)
- ✅ **PostgreSQL Data Service** (single database)
- ✅ **Docker Compose** (local development only)
- ✅ **Basic Configuration** (`.env` file)
- ✅ **Pytest** (unit tests, minimal coverage)

#### Infrastructure
- ✅ Docker Compose for local dev
- ✅ Simple Dockerfiles (single-stage builds)
- ❌ No Nginx
- ❌ No SSL/TLS
- ❌ No production deployment configs

#### Observability
- ❌ Console logs only (print statements OK)
- ❌ No structured logging
- ❌ No metrics
- ❌ No tracing
- ❌ No error tracking

#### Security
- ❌ No authentication (or basic hardcoded tokens only)
- ❌ No authorization
- ❌ No security headers
- ❌ No secrets management

#### Quality
- ✅ Basic linting (Ruff)
- ✅ Basic type checking (Mypy)
- ✅ Unit tests (low coverage OK, ~60%)
- ❌ No security scanning
- ❌ No integration tests

### Generated Structure

```
project/
├── services/
│   ├── template_business_api/              # FastAPI
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── domain/
│   │   └── tests/
│   └── template_data_postgres_api/      # Data service
│       ├── main.py
│       ├── models/
│       ├── repositories/
│       └── tests/
├── docker-compose.yml            # Local dev only
├── .env.example
├── Makefile
└── README.md
```

### Use Cases
- MVP for investors
- Proof of concept
- Learning microservices
- Hackathon projects
- Internal tools (low traffic)

---

## Level 2: Development Ready 🛠️

### Goal
Enable active team development with proper observability and debugging tools.

### Target Audience
- Small teams (2-5 developers)
- Startups preparing for beta launch
- Projects transitioning from PoC to active development
- Staging environments

### Time to Generate
**~10-12 minutes**

### What's Added to Level 1

#### Observability (+++)
- ✅ **Structured Logging** (JSON format, request IDs)
- ✅ **Health Check Endpoints** (`/health`, `/ready`)
- ✅ **Error Tracking Integration** (Sentry-ready, not deployed)
- ✅ **OpenAPI Documentation** (Swagger UI auto-generated)
- ❌ No Prometheus metrics yet
- ❌ No distributed tracing
- ❌ No ELK stack

#### Development Experience
- ✅ **Hot Reload** (dev mode)
- ✅ **Debug Mode** (detailed error pages)
- ✅ **Docker Compose Dev Overrides** (`docker-compose.dev.yml`)
- ✅ **Environment Separation** (dev/test configs)

#### Quality
- ✅ **Integration Tests** (with testcontainers)
- ✅ **Coverage Target** (≥ 75%)
- ✅ **Pre-commit Hooks** (optional)

### Generated Structure (Additional Files)

```
services/
├── template_business_api/
│   ├── logging_config.py         # NEW: Structured logging
│   ├── middleware/                # NEW: Request ID, error handling
│   │   ├── request_id.py
│   │   └── error_handler.py
│   └── observability/             # NEW: Health checks
│       └── health.py
├── shared/
│   └── logging/                   # NEW: Shared logging utils
│       └── formatters.py
docker-compose.dev.yml             # NEW: Dev overrides
docker-compose.test.yml            # NEW: Test environment
```

### Use Cases
- Active development teams
- Beta testing (closed)
- Staging environments
- Internal demos

---

## Level 3: Pre-Production (Staging) 🚀

### Goal
Prepare for public access with production-like infrastructure and basic security.

### Target Audience
- Startups launching to public beta
- Scale-ups preparing production release
- Projects needing public staging environment
- Teams with < 10,000 users

### Time to Generate
**~15-18 minutes**

### What's Added to Level 2

#### Infrastructure (+++)
- ✅ **Nginx API Gateway** (reverse proxy, load balancing)
- ✅ **SSL/TLS Support** (Let's Encrypt or self-signed)
- ✅ **Multi-Stage Docker Builds** (optimized images)
- ✅ **Production Docker Compose** (`docker-compose.prod.yml`)
- ✅ **Health Check Probes** (Docker healthchecks)

#### Observability (+++)
- ✅ **Prometheus Metrics** (request rate, latency, errors)
- ✅ **Basic Grafana Dashboards** (pre-configured)
- ✅ **Alerting Rules** (basic threshold alerts)
- ❌ No distributed tracing yet
- ❌ No ELK stack yet

#### Security (+)
- ✅ **Rate Limiting** (Nginx-based, per IP)
- ✅ **CORS Configuration** (for frontend)
- ✅ **Security Headers** (basic: CSP, X-Frame-Options)
- ✅ **Basic Secrets Management** (Docker secrets)
- ❌ No OAuth/JWT yet (can use API keys)
- ❌ No RBAC

#### Quality
- ✅ **Security Scanning** (Bandit, Safety)
- ✅ **Service Tests** (end-to-end tests)
- ✅ **Coverage Target** (≥ 80%)
- ✅ **Load Testing Scripts** (basic)

### Generated Structure (Additional Files)

```
infrastructure/
├── nginx/                         # NEW: API Gateway
│   ├── nginx.conf
│   ├── ssl/
│   │   └── README.md
│   └── rate_limit.conf
├── prometheus/                    # NEW: Metrics
│   ├── prometheus.yml
│   └── rules.yml
└── grafana/                       # NEW: Dashboards
    ├── provisioning/
    └── dashboards/
        └── api_overview.json
services/
├── template_business_api/
│   ├── metrics.py                 # NEW: Prometheus metrics
│   └── Dockerfile.prod            # NEW: Multi-stage build
docker-compose.prod.yml            # NEW: Production config
scripts/
└── load_test.sh                   # NEW: Load testing
```

### Use Cases
- Public beta launch
- Staging for production
- Small-scale production (< 10K users)
- Client demos

---

## Level 4: Production 🏢

### Goal
Enterprise-grade system with full security, high availability, and operational excellence.

### Target Audience
- Production deployments
- Enterprise applications
- Scale-ups (> 10,000 users)
- Compliance-sensitive industries (fintech, healthcare)
- Teams requiring SLA guarantees

### Time to Generate
**~25-35 minutes**

### What's Added to Level 3

#### Security (+++)
- ✅ **OAuth 2.0 / JWT Authentication** (full implementation)
- ✅ **Role-Based Access Control (RBAC)** (permissions system)
- ✅ **Session Management** (secure, distributed)
- ✅ **Input Validation** (comprehensive sanitization)
- ✅ **Secrets Management** (Vault-ready integration)
- ✅ **Security Headers** (full suite: CSP, HSTS, etc.)
- ✅ **Encryption at Rest** (database encryption)
- ✅ **Audit Logging** (security events)

#### Observability (+++)
- ✅ **ELK Stack** (Elasticsearch, Logstash, Kibana)
- ✅ **Distributed Tracing** (Jaeger)
- ✅ **Full Grafana Suite** (advanced dashboards)
- ✅ **Alerting** (Prometheus Alertmanager + PagerDuty/Slack)
- ✅ **APM Integration** (Application Performance Monitoring)
- ✅ **Log Aggregation** (centralized, searchable)

#### High Availability (+++)
- ✅ **Database Replication** (master-slave PostgreSQL)
- ✅ **Service Redundancy** (multiple instances)
- ✅ **Graceful Shutdown** (signal handling)
- ✅ **Rolling Updates** (zero-downtime deployments)
- ✅ **Circuit Breakers** (resilience patterns)
- ✅ **Health Checks** (advanced liveness/readiness)

#### CI/CD (+++)
- ✅ **GitHub Actions / GitLab CI** (full pipelines)
- ✅ **Automated Testing** (unit, integration, e2e)
- ✅ **Security Scanning** (SAST, dependency scanning)
- ✅ **Automated Deployment** (staging + production)
- ✅ **Rollback Procedures** (automated)
- ✅ **Version Tagging** (semantic versioning)

#### Backup & Recovery (+++)
- ✅ **Automated DB Backups** (scheduled, encrypted)
- ✅ **Disaster Recovery Plan** (documented)
- ✅ **Point-in-Time Recovery** (PostgreSQL PITR)
- ✅ **Backup Monitoring** (alerts on failures)

#### Documentation (+++)
- ✅ **Architecture Decision Records (ADRs)** (major decisions documented)
- ✅ **Runbooks** (incident response procedures)
- ✅ **API Documentation** (comprehensive, versioned)
- ✅ **Deployment Guide** (step-by-step)
- ✅ **Monitoring Guide** (alert responses)

### Generated Structure (Additional Files)

```
infrastructure/
├── elk/                           # NEW: Log aggregation
│   ├── elasticsearch.yml
│   ├── logstash.conf
│   └── kibana.yml
├── jaeger/                        # NEW: Distributed tracing
│   └── jaeger.yml
├── monitoring/                    # NEW: Full observability
│   ├── prometheus.yml
│   ├── alertmanager.yml
│   └── grafana/
│       └── dashboards/            # Advanced dashboards
├── security/                      # NEW: Security configs
│   ├── vault/
│   └── secrets/
└── databases/                     # NEW: Replication
    └── postgres-replication/
services/
├── template_business_api/
│   ├── security/                  # NEW: Auth & RBAC
│   │   ├── oauth.py
│   │   ├── jwt.py
│   │   └── rbac.py
│   ├── observability/
│   │   ├── tracing.py             # NEW: Jaeger integration
│   │   └── apm.py
│   └── resilience/                # NEW: Circuit breakers
│       └── circuit_breaker.py
.github/                           # NEW: CI/CD
└── workflows/
    ├── ci.yml
    ├── security-scan.yml
    ├── deploy-staging.yml
    └── deploy-production.yml
docs/
├── adr/                           # NEW: Architecture decisions
│   └── 001-use-improved-hybrid.md
├── runbooks/                      # NEW: Incident response
│   ├── database-failover.md
│   ├── high-memory-usage.md
│   └── service-degradation.md
└── deployment/
    ├── deployment-guide.md
    └── rollback-procedure.md
scripts/
├── backup.sh                      # NEW: Automated backups
├── restore.sh
└── health-check.sh
```

### Use Cases
- Production deployments (any scale)
- Enterprise applications
- Regulated industries (fintech, healthcare, government)
- SaaS platforms
- High-traffic systems (> 10K users)

---

## Feature Comparison Matrix

| Feature | PoC (L1) | Development (L2) | Pre-Production (L3) | Production (L4) |
|---------|----------|------------------|---------------------|-----------------|
| **Core Services** |
| FastAPI + PostgreSQL | ✅ | ✅ | ✅ | ✅ |
| Docker Compose | ✅ | ✅ | ✅ | ✅ |
| Basic Tests | ✅ | ✅ | ✅ | ✅ |
| **Observability** |
| Console Logs | ✅ | ❌ | ❌ | ❌ |
| Structured Logging | ❌ | ✅ | ✅ | ✅ |
| Health Endpoints | ❌ | ✅ | ✅ | ✅ |
| Prometheus Metrics | ❌ | ❌ | ✅ | ✅ |
| Grafana Dashboards | ❌ | ❌ | ✅ | ✅ |
| Distributed Tracing | ❌ | ❌ | ❌ | ✅ |
| ELK Stack | ❌ | ❌ | ❌ | ✅ |
| **Infrastructure** |
| Nginx Gateway | ❌ | ❌ | ✅ | ✅ |
| SSL/TLS | ❌ | ❌ | ✅ | ✅ |
| Multi-Stage Builds | ❌ | ❌ | ✅ | ✅ |
| **Security** |
| Rate Limiting | ❌ | ❌ | ✅ | ✅ |
| CORS | ❌ | ❌ | ✅ | ✅ |
| OAuth/JWT | ❌ | ❌ | ❌ | ✅ |
| RBAC | ❌ | ❌ | ❌ | ✅ |
| Secrets Management | ❌ | ❌ | ❌ | ✅ |
| Encryption at Rest | ❌ | ❌ | ❌ | ✅ |
| **High Availability** |
| DB Replication | ❌ | ❌ | ❌ | ✅ |
| Service Redundancy | ❌ | ❌ | ❌ | ✅ |
| Circuit Breakers | ❌ | ❌ | ❌ | ✅ |
| **CI/CD** |
| Automated Pipelines | ❌ | ❌ | ❌ | ✅ |
| Security Scanning | ❌ | ❌ | ✅ | ✅ |
| Automated Deployment | ❌ | ❌ | ❌ | ✅ |
| **Backup & Recovery** |
| Automated Backups | ❌ | ❌ | ❌ | ✅ |
| Disaster Recovery | ❌ | ❌ | ❌ | ✅ |
| **Documentation** |
| Basic README | ✅ | ✅ | ✅ | ✅ |
| ADRs | ❌ | ❌ | ❌ | ✅ |
| Runbooks | ❌ | ❌ | ❌ | ✅ |
| **Test Coverage** | ≥ 60% | ≥ 75% | ≥ 80% | ≥ 85% |
| **Generation Time** | ~5 min | ~10 min | ~15 min | ~30 min |

---

## Upgrade Path

Projects naturally evolve from one level to the next. The framework supports incremental upgrades:

### PoC → Development
**Typical trigger**: Team grows, need debugging tools
**Upgrade effort**: ~2 hours
**Key additions**: Logging, health checks, integration tests

### Development → Pre-Production
**Typical trigger**: Public beta launch
**Upgrade effort**: ~1 day
**Key additions**: Nginx, SSL, metrics, alerting

### Pre-Production → Production
**Typical trigger**: Enterprise contract, compliance requirements
**Upgrade effort**: ~1 week
**Key additions**: OAuth, RBAC, ELK, CI/CD, HA, backups

---

## Selection Guide

**Choose Level 1 (PoC)** if:
- You're validating a business idea
- Building an MVP for investors
- Learning microservices architecture
- Budget/time constrained (< 1 week delivery)

**Choose Level 2 (Development)** if:
- You have a small team (2-5 developers)
- Need observability for debugging
- Preparing for beta launch
- Transitioning from prototype to product

**Choose Level 3 (Pre-Production)** if:
- Launching public beta
- Need SSL and basic security
- Expecting moderate traffic (< 10K users)
- Staging environment for production

**Choose Level 4 (Production)** if:
- Enterprise deployment
- Compliance requirements (GDPR, HIPAA, PCI-DSS)
- High traffic (> 10K users)
- Need SLA guarantees
- Mission-critical application

---

## Maintenance

- Update this matrix when new features are added to atomic documentation.
- Keep generation time estimates accurate based on testing.
- Cross-reference with `conditional-stage-rules.md` for implementation details.
- Follow `STYLE_GUIDE.md` for formatting consistency.
