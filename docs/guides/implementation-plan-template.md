# Implementation Plan Template

> **Instructions**: Populate this template after completing the Requirements Intake. Use it to obtain approval before writing code.

## Plan Metadata

- **Request ID**:
- **Plan Version**:
- **Date**:
- **Prepared By (Agent)**:
- **Reviewed / Approved By**:

## Summary

- Problem & objective recap (link to `docs/guides/requirements-intake-template.md` artefact):
- High-level solution concept:
- **Maturity Level**: [1-PoC / 2-Development / 3-Pre-Production / 4-Production]
- **Optional Modules**: [List selected modules: Workers, Bot, MongoDB, etc.]
- **Estimated Generation Time**: [Based on level and modules]
- Key assumptions:

## Maturity Level Features

### ✅ Included at Selected Level

| Category | Feature | Justification |
|----------|---------|---------------|
| Example | Structured logging | Level ≥ 2 requirement |
| Example | Nginx API Gateway | Level ≥ 3 requirement |
| Example | OAuth/JWT | Level 4 requirement |

> **Reference**: See `docs/reference/maturity-levels.md` for complete feature matrix.

### ❌ Skipped Features (Available at Higher Levels)

| Feature | Available At Level | Upgrade Impact |
|---------|-------------------|----------------|
| Example | ELK Stack | Level 4 | ~1 day to add |
| Example | CI/CD Pipelines | Level 4 | ~2 days to add |

## Architecture Impact

| Area | Description | Relevant Rules / Docs |
|------|-------------|-----------------------|
| Services | | `docs/atomic/services/`, `docs/guides/architecture-guide.md` |
| Data access | | `docs/atomic/architecture/data-access-architecture.md`, `docs/atomic/infrastructure/` |
| Observability | | `docs/atomic/observability/` |
| Security / compliance | | `docs/atomic/testing/`, policy docs |

## Work Plan

| Stage | Purpose | Key Tasks | Tooling / Owners | Definition of Done | References |
|-------|---------|-----------|------------------|--------------------|------------|
| 1 | | | | | |
| 2 | | | | | |

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy | Owner |
|------|--------|------------|---------------------|-------|
|      |        |            |                     |       |

## Verification Strategy

- Linting & formatting commands (`docs/guides/development-commands.md`):
- Type checking & security tools:
- Test suites and coverage targets (`docs/atomic/testing/`):
- Observability validation (if applicable):

## Deliverables & Acceptance

- Expected artefacts (`docs/reference/deliverables-catalog.md`):
- Acceptance criteria alignment:
- Additional documentation requirements (ADR, diagrams, etc.):

## Dependencies & Schedule

- External dependencies / handoffs:
- Milestones with target dates:

## Sign-Off

- Agent signature & date:
- Reviewer signature & date:
- Requester confirmation:

## References

- Requirements Intake document:
- Relevant ADRs or historical decisions:
