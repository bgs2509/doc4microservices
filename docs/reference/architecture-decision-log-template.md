# Architecture Decision Log Template

> **Purpose**: Standardize the way agents capture significant architecture decisions taken during planning or execution phases.

## Metadata

- **ADR ID**: `ADR-YYYYMMDD-##`
- **Title**: Concise decision statement
- **Date**: YYYY-MM-DD
- **Authors**: Names or agent identifiers
- **Status**: Proposed / Accepted / Deprecated / Superseded

## Context

- Business drivers and functional requirements (link to `docs/guides/requirements-intake-template.md`).
- Non-functional constraints impacting the decision (refer to `docs/guides/architecture-guide.md` and `docs/atomic/architecture/`).
- Existing system assumptions or limitations.

## Decision

- Detailed description of the selected approach.
- How the decision aligns with the Improved Hybrid Approach and mandatory rules.
- References to any implementation plan stages (`docs/guides/implementation-plan-template.md`).

## Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| Example | ... | ... | ... |

## Consequences

- Positive impacts (e.g., scalability, maintainability).
- Negative trade-offs or mitigations required.
- Required updates to documentation or deliverables (e.g., `docs/reference/deliverables-catalog.md`).

## Follow-Up Actions

- Tasks needed to implement or monitor the decision.
- Links to code changes, tickets, or implementation plan updates.
- Notes on future evaluation criteria.

## References

- `docs/guides/architecture-guide.md`
- `docs/atomic/architecture/improved-hybrid-overview.md`
- `docs/atomic/architecture/data-access-architecture.md`
- `docs/atomic/architecture/naming/README.md`
- `docs/guides/implementation-plan-template.md`

## Maintenance

- Store ADRs in a dedicated directory (e.g., `artifacts/adr/`).
- Update status when decisions evolve or are superseded.
- Keep the index aligned with `docs/INDEX.md` and `docs/reference/agent-context-summary.md`.
