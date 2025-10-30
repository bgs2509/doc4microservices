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

## Requirements Traceability Matrix

> **PURPOSE**: Explicit mapping between user requirements (from Requirements Intake) and implementation tasks. Ensures 100% coverage by systematically tracking every Req ID through the implementation lifecycle.

> **INSTRUCTIONS**:
> 1. Extract ALL Req IDs (FR-*, UI-*, NF-*) from completed Requirements Intake document
> 2. For EACH Req ID, identify which Phase(s) and Task(s) will implement it
> 3. Fill Evidence column during Stage 4 (Code Generation) with exact file paths
> 4. Update Status as implementation progresses (Pending → In Progress → ✅ Done)

| Req ID | Feature/Element | Mapped to Phase | Mapped to Tasks | Evidence (when implemented) | Status |
|--------|----------------|-----------------|-----------------|----------------------------|--------|
| FR-001 | (example: User registration) | Phase 3 | Task 3.1: Domain entity<br>Task 3.2: API endpoint | (fill during Stage 4: `services/api/src/api/v1/users.py:20`) | Pending |
| FR-002 | (example: Loan creation) | Phase 3 | Task 3.3: Loan entity<br>Task 3.4: Validation logic | (fill during Stage 4) | Pending |
| UI-001 | (example: Registration form) | Phase 5 | Task 5.3: Registration handler with FSM | (fill during Stage 4: `services/bot/src/handlers/register.py:15`) | Pending |

**Requirements Coverage Plan:**
- **Total Requirements:** [X] (from Requirements Intake § Requirements Summary)
- **Distributed across:** [Y] phases
- **Average:** [Z] requirements per phase

> **VERIFICATION**: In Stage 5, AI will verify ALL Req IDs have Status "✅ Done" + Evidence before proceeding to Stage 6. Coverage must be 100% OR descoped requirements must have stakeholder approval documented in QA Report.

> **REFERENCE**: See `docs/guides/requirements-traceability-guide.md` for complete Req ID lifecycle and coverage calculation methodology.

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
