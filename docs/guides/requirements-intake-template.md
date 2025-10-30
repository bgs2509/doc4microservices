# Requirements Intake Template

> **Instructions**: Copy this template when documenting user requirements. Provide explicit answers for each section. Reference `docs/guides/prompt-validation-guide.md` for mandatory content.

## Request Metadata

- **Request ID**:
- **Requester / Stakeholders**:
- **Date**:
- **Communication Channel**:

## Target Configuration

- **Maturity Level**: [1-PoC / 2-Development / 3-Pre-Production / 4-Production]
- **Optional Modules**: [None / Workers / Bot / MongoDB / RabbitMQ / Redis / File Storage / Real-Time]
- **Estimated Generation Time**: [~5 min / ~10 min / ~15 min / ~30 min based on level]
- **Reference**: See `docs/reference/maturity-levels.md` for level details

## Business Context & Objectives

- Problem statement:
- Target users / personas:
- Success metrics / KPIs:
- Strategic alignment notes (see `README.md` for framework positioning):

## Functional Requirements

| **Req ID** | Feature / Capability | Priority (Must / Should / Could) | Description | Acceptance Criteria | **Implementation Status** |
|------------|----------------------|----------------------------------|-------------|---------------------|--------------------------|
| FR-001     | (example)            | Must                             | (example)   | (example)           | **Pending** |

> **NOTE**: Assign unique Req ID (FR-001, FR-002, ...) to EVERY functional requirement for traceability. See `docs/guides/requirements-traceability-guide.md` for Req ID lifecycle.

## UI/UX Requirements (for UI-heavy projects)

> **WHEN TO USE**: For projects with detailed UI/UX specifications (Telegram bots, web frontends, mobile apps). Skip this section if project has minimal UI (API-only services).

| **Req ID** | UI Element / Screen | Priority (Must / Should / Could) | Description | Acceptance Criteria | **Implementation Status** |
|------------|-------------------|----------------------------------|-------------|---------------------|--------------------------|
| UI-001     | (example: Login screen) | Must                          | (example: Email/password with "Forgot?" link) | (example: Redirect to /dashboard on success) | **Pending** |

> **NOTE**: Assign unique Req ID (UI-001, UI-002, ...) to EVERY UI element, screen, modal, button, or form. Critical for ensuring 100% UI coverage in large UX/UI prompts.

## Non-Functional Requirements (measurable constraints)

> **WHEN TO USE**: For performance, security, compliance, or availability requirements that can be objectively measured and verified.

| **Req ID** | Constraint Type | Target / SLA | Description | Acceptance Criteria | **Implementation Status** |
|------------|----------------|--------------|-------------|---------------------|--------------------------|
| NF-001     | (example: Performance) | (example: < 200ms p95) | (example: API latency) | (example: Load test confirms < 200ms) | **Pending** |

> **NOTE**: Assign Req ID (NF-001, NF-002, ...) only to measurable constraints that can be verified (e.g., latency < 200ms, uptime > 99.9%). Skip subjective constraints.

## Requirements Summary

> **PURPOSE**: Track total requirement count for coverage calculation in Stage 5 (Verification) and Stage 6 (QA Report).

- **Total Functional (FR-*):** [count]
- **Total UI/UX (UI-*):** [count or "N/A" if API-only]
- **Total Non-Functional (NF-*):** [count or "0" if none]
- **Grand Total:** [sum]

> **TRACEABILITY**: See `docs/guides/requirements-traceability-guide.md` for Req ID lifecycle through all workflow stages. Coverage verification mandatory in Stage 5.

## Non-Functional Constraints (general)

- Performance / SLA expectations:
- Security / compliance requirements:
- Reliability & availability targets:
- Architecture alignment confirmation (Improved Hybrid Approach, HTTP-only data access, service separation; see `docs/guides/architecture-guide.md` and `docs/atomic/architecture/`):
- Observability expectations (logging, metrics, tracing; see `docs/atomic/observability/`):

## Dependencies & Integrations

| External System / Service | Interaction Pattern | Protocol / API | Notes |
|---------------------------|----------------------|----------------|-------|
|                           |                      |                |       |

## Data & Storage Considerations

- Primary data sources:
- Expected data volume / growth:
- Data retention or compliance rules:
- Mapping to data services (`docs/reference/project-structure.md`, `docs/atomic/infrastructure/`):

## Scope Boundaries

- In scope:
- Out of scope:

## Expected Deliverables

- Code / services:
- Configuration / infrastructure artefacts:
- Documentation (ADR, QA report, others per `docs/reference/deliverables-catalog.md`):

## Acceptance Criteria

- Functional validation steps:
- Quality gates (linting, typing, security, tests, coverage per `docs/quality/agent-verification-checklist.md`):
- Deployment / release expectations:

## Risks & Open Questions

| Item | Description | Owner | Resolution Path |
|------|-------------|-------|-----------------|
|      |             |       |                 |

## Next Steps

- Agreed decisions:
- Pending clarifications:
- Target date for implementation plan review:

## References

- Link to original prompt:
- Related documents / tickets:
