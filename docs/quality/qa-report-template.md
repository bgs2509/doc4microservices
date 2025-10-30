# QA Report Template

> **Instructions**: Complete this report after running the verification checklist. Provide links to evidence wherever possible.

## Report Metadata

- **Project / Service**:
- **Request ID**:
- **Report Version**:
- **Date**:
- **Prepared By (Agent)**:
- **Reviewed By**:

## Executive Summary

- Overall status (Ready / Blocked):
- Key accomplishments:
- Outstanding issues:
- Recommendation:

## Verification Checklist Summary

| Check Category | Status | Evidence Link | Notes |
|----------------|--------|---------------|-------|
| Environment |  |  |  |
| Static analysis |  |  |  |
| Testing & coverage |  |  |  |
| **Requirements coverage** | **[✅ 100% / ⚠️ Partial / ❌ Incomplete]** | **RTM below** | **[Coverage %]** |
| Artefact validation |  |  |  |
| Release gate |  |  |  |

> Reference: Completed `docs/quality/agent-verification-checklist.md`.

## Requirements Coverage Matrix

> **PURPOSE**: Evidence that ALL requirements from original user prompt were implemented. This is the **PRIMARY deliverable** proving completeness.

> **INSTRUCTIONS**: Extract Req IDs from Requirements Intake (Stage 2) and Implementation Plan RTM (Stage 3), verify implementation, and document evidence below.

### Functional Requirements (FR-*)

| Req ID | Feature | Status | Evidence (Code Location) | Tests | Notes |
|--------|---------|--------|--------------------------|-------|-------|
| FR-001 | (example: User registration) | ✅ Done | `services/api/src/api/v1/users.py:20` | ✅ 5 unit tests<br>✅ 2 integration tests | Fully implemented with email verification |
| FR-002 | (example: Loan creation) | ✅ Done | `services/api/src/api/v1/loans.py:15` | ✅ 8 unit tests<br>✅ 3 integration tests | Complete with validation rules |
| FR-003 | (example: Payment automation) | ✅ Done | `services/worker/src/workers/payment.py:30` | ✅ 6 unit tests<br>✅ 2 e2e tests | Worker operational with Stripe integration |

**Functional Coverage:** [X]/[X] requirements ([100]%)

### UI/UX Requirements (UI-*) — *For UI-heavy projects only*

> **NOTE**: This section applies ONLY to projects with detailed UI/UX requirements (Telegram bots, web frontends, mobile apps). Skip if project is API-only.

| Req ID | UI Element/Screen | Status | Evidence (Code + Screenshot) | Tests | Notes |
|--------|------------------|--------|------------------------------|-------|-------|
| UI-001 | (example: Registration form) | ✅ Done | **Code**: `services/bot/src/handlers/register.py:15`<br>**Screenshot**: `screenshots/register.png` | ✅ e2e test<br>✅ FSM states verified | All fields present: email, password, confirm |
| UI-002 | (example: Login screen) | ✅ Done | **Code**: `services/bot/src/handlers/auth.py:30`<br>**Screenshot**: `screenshots/login.png` | ✅ e2e test | "Forgot password" link functional |
| UI-003 | (example: Dashboard) | ✅ Done | **Code**: `services/bot/src/handlers/dashboard.py:40`<br>**Screenshot**: `screenshots/dashboard.png` | ✅ e2e test | Stats displayed correctly, responsive |

**UI/UX Coverage:** [Y]/[Y] requirements ([100]%)

### Non-Functional Requirements (NF-*) — *For measurable constraints only*

> **NOTE**: This section applies ONLY to projects with measurable non-functional constraints (performance SLAs, uptime targets, etc.). Skip if no NF requirements in Requirements Intake.

| Req ID | Constraint | Target / SLA | Status | Evidence | Verification Method | Notes |
|--------|-----------|--------------|--------|----------|---------------------|-------|
| NF-001 | (example: API latency) | < 200ms p95 | ✅ Met | Load test results: p95 = 145ms | Apache Bench / k6 load testing | Performance acceptable |
| NF-002 | (example: Uptime) | 99.9% | ✅ Met | Healthcheck + monitoring config | Prometheus + alerting rules | HA configured (Level 4 only) |
| NF-003 | (example: Test coverage) | ≥ 80% (Level 3) | ✅ Met | Coverage report: 82% | pytest --cov | Threshold met |

**Non-Functional Coverage:** [Z]/[Z] requirements ([100]%)

---

### **Overall Coverage Summary**

> **CRITICAL METRICS**: These numbers determine whether project can proceed to deployment or requires additional work.

- **Total Requirements:** [X+Y+Z] = [sum] requirements
  - Functional (FR-*): [X]
  - UI/UX (UI-*): [Y] *(or N/A if API-only)*
  - Non-Functional (NF-*): [Z] *(or 0 if none)*

- **Implemented:** [count] requirements ([percentage]%)
- **Descoped:** [count] requirements *(with stakeholder approval — see § Defects & Risks)*
- **Outstanding:** [count] requirements *(BLOCKER if > 0 without approval)*

**Coverage Status:**
- ✅ **100% COVERAGE ACHIEVED** — All requirements implemented, ready for deployment
- ⚠️ **PARTIAL COVERAGE ([percentage]%)** — Requires stakeholder approval (see Descoped Requirements below)
- ❌ **INCOMPLETE ([percentage]%)** — Cannot proceed to deployment until missing requirements implemented

### Descoped Requirements (if any)

> **NOTE**: Fill this section ONLY if coverage < 100% and stakeholder approved descoping certain requirements.

| Req ID | Feature/Element | Reason for Descope | Approved By | Approval Date | Planned for Version |
|--------|----------------|-------------------|-------------|---------------|---------------------|
| FR-015 | (example: Advanced search filters) | Low priority for MVP, defer to v2 | John Doe (Product Owner) | 2025-10-30 | v2.0 (Q2 2026) |
| UI-007 | (example: Dark mode theme) | Nice-to-have, not critical for launch | Jane Smith (Stakeholder) | 2025-10-30 | v1.1 (Q4 2025) |

**Adjusted Coverage** (excluding descoped): [implemented] / ([total] - [descoped]) × 100% = **100%**

### Coverage Verification Evidence

- **Requirements Intake Document**: [link to artifacts/requirements-intake.md]
- **Implementation Plan RTM**: [link to artifacts/implementation-plan.md § Requirements Traceability Matrix]
- **Verification Checklist**: [link to artifacts/verification-checklist.md § Requirements Coverage Verification]

> **REFERENCE**: See `docs/guides/requirements-traceability-guide.md` for RTM methodology and coverage calculation formula.

---

## Test & Coverage Details

- Test command(s) executed:
- Coverage percentage (compare with `docs/atomic/testing/`):
- Location of reports (`htmlcov/`, `coverage.xml`, CI artifacts):

## Defects & Risks

| ID | Description | Severity | Status | Owner | Mitigation / Next Steps |
|----|-------------|----------|--------|-------|--------------------------|
|    |             |          |        |       |                          |

## Deliverables Summary

- Updated deliverables list reference (`docs/reference/deliverables-catalog.md`):
- ADRs created or updated (`docs/reference/architecture-decision-log-template.md`):
- Documentation updates (requirements, plans, guides):

## Sign-Off

- Agent signature & date:
- Reviewer signature & date:
- Requester acknowledgement:

## References

- Requirements Intake document:
- Implementation Plan:
- Verification Checklist artefact:
- Additional notes:
