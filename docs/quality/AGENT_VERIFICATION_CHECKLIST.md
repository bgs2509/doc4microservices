# Agent Verification Checklist

> **Purpose**: Enforce mandatory quality gates before delivering artefacts. Complete this checklist at the end of the execution phase.

## Usage Instructions

- Run these checks in the order listed.
- Capture command outputs or links to reports in the Evidence column.
- If a check fails, resolve the issue or document the blocker before proceeding.
- Refer back to `docs/guides/DEVELOPMENT_COMMANDS.md` for detailed command descriptions.

## Pre-Flight Environment Checks

| Check | Command / Action | Expected Result | Evidence | Status |
|-------|------------------|-----------------|----------|--------|
| Python version | `python --version` | >= 3.12 |  |  |
| UV installed | `uv --version` | Command succeeds |  |  |
| Environment configured | `cp .env.example .env` (if not yet copied) | `.env` present |  |  |

## Static Analysis & Security

| Check | Command | Expected Result | Evidence | Status |
|-------|---------|-----------------|----------|--------|
| Linting | `uv run ruff check .` | No errors reported |  |  |
| Formatting | `uv run ruff format . --check` | No format drift |  |  |
| Type checking | `uv run mypy .` | No type errors |  |  |
| Security scan | `uv run bandit -r .` | No high severity findings |  |  |

## Testing & Coverage

| Check | Command | Expected Result | Evidence | Status |
|-------|---------|-----------------|----------|--------|
| Full test suite | `uv run pytest` or plan-specific command | Tests pass |  |  |
| Coverage threshold | `uv run pytest --cov=app --cov-report=html --cov-report=xml` | Coverage meets targets from `docs/atomic/testing/` |  |  |
| Coverage artefacts | Inspect `htmlcov/`, `coverage.xml` | Reports generated |  |  |

## Artefact Validation

| Check | Action | Expected Result | Evidence | Status |
|-------|--------|-----------------|----------|--------|
| Project structure compliance | Review against `docs/reference/PROJECT_STRUCTURE.md` | Files placed correctly |  |  |
| Shared components usage | Confirm adherence to `docs/guides/shared_components.md` | No duplication or rule violations |  |  |
| Naming conventions | Spot-check against `docs/atomic/architecture/naming-conventions.md` | No prohibited names |  |  |
| Documentation updates | Ensure relevant docs updated (plans, ADRs, etc.) | Artefacts listed in `docs/reference/DELIVERABLES_CATALOG.md` |  |  |

## Release Gate

| Check | Action | Expected Result | Evidence | Status |
|-------|--------|-----------------|----------|--------|
| QA report | Draft using `docs/quality/QA_REPORT_TEMPLATE.md` | Report ready for sign-off |  |  |
| Deliverables summary | Update per `docs/reference/DELIVERABLES_CATALOG.md` | Complete deliverable list |  |  |
| Outstanding issues | Record unresolved risks or follow-ups | Stakeholder notified |  |  |

## Failure Handling

- If any check fails, consult `docs/reference/troubleshooting.md` and rerun the step.
- Document persistent issues in the QA report and notify stakeholders.
- Do not proceed to release without explicit sign-off on known deviations.

## Maintenance

- Align commands with `docs/guides/DEVELOPMENT_COMMANDS.md` if they change.
- Keep coverage targets synchronized with `docs/atomic/testing/`.
- Update link references in `docs/reference/AGENT_CONTEXT_SUMMARY.md` and `docs/INDEX.md` when modifying this checklist.
