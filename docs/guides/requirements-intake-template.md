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

| Feature / Capability | Priority (Must / Should / Could) | Description | Acceptance Notes |
|----------------------|----------------------------------|-------------|------------------|
|                      |                                  |             |                  |

## Non-Functional Constraints

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
