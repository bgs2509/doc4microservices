# Deliverables Catalog

> **Purpose**: Define the standard artefacts produced during an agent-led delivery. Use this catalog to confirm expectations and storage locations.

## Core Deliverables

| Deliverable | Description | Produced During | Validation Method | Storage / Path | Source Template |
|-------------|-------------|-----------------|-------------------|----------------|-----------------|
| Prompt Validation Record | Confirmation that all critical prompt fields are present. | Prompt Validation | Manual check per `docs/guides/prompt-validation-guide.md` | Include in Requirements Intake notes | `docs/guides/prompt-validation-guide.md` |
| Requirements Intake Document | Structured capture of business, functional, and non-functional inputs. | Requirements Intake | Review completeness vs. template | Project docs (e.g., `artifacts/requirements/`) | `docs/guides/requirements-intake-template.md` |
| Implementation Plan | Detailed plan with stages, DoD, and references. | Planning | Reviewer sign-off, alignment with architecture rules | Project docs (e.g., `artifacts/plans/`) | `docs/guides/implementation-plan-template.md` |
| Architecture Decision Record (optional) | Formalised decision for significant architectural choices. | Planning / Execution | Peer review, compliance with architecture guide | Project docs (e.g., `artifacts/adr/`) | `docs/reference/architecture-decision-log-template.md` |
| Generated Code & Config | Service implementations, infrastructure, shared components. | Implementation | Testing & verification gates | Application repository (`src/`, configs) | Framework rules |
| Test Artefacts | Unit/integration tests, coverage reports. | Verification | Thresholds in `docs/atomic/testing/` | `htmlcov/`, `coverage.xml`, CI artefacts | Testing standards |
| Verification Checklist Result | Completed checklist with statuses and evidence. | Verification | Sign-off via `docs/quality/agent-verification-checklist.md` | `artifacts/reports/verification-checklist.md` | `docs/quality/agent-verification-checklist.md` |
| QA Report | Final QA summary with defects and sign-off. | Release | Stakeholder approval | `artifacts/reports/qa-report.md` | `docs/quality/qa-report-template.md` |

## Optional Deliverables

| Deliverable | When Needed | Notes |
|-------------|-------------|-------|
| Change Log Entry | When a release is prepared | Follow the team's changelog policy when available |
| Observability Dashboards Export | When custom dashboards are created | Document queries and panels |
| Post-Incident Report | When failures occur during delivery | Base the write-up on `docs/reference/troubleshooting.md` guidance |

## Versioning & Retention

- Align release notes and version bumps with the team's changelog policy when available.
- Store artefacts in the project repository or associated knowledge base with clear version tags.
- Retain verification reports and QA summaries for auditability per team policy.

## Maintenance

- Update entries whenever templates change or new artefacts are added.
- Cross-check with `docs/reference/agent-context-summary.md` and `docs/INDEX.md` after modifications.
- Use formatting rules from `docs/STYLE_GUIDE.md`.
