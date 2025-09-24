# Agent Workflow

> **Purpose**: Define the end-to-end execution path for AI agents delivering production-ready applications with this framework.

## Process Summary

| Step | Goal | Primary Inputs | Key Outputs | References |
|------|------|---------------|-------------|------------|
| 0. Prompt Validation | Ensure the user prompt is complete | User prompt | Validation note | `docs/guides/PROMPT_VALIDATION_GUIDE.md` |
| 1. Requirements Intake | Capture structured requirements | Validated prompt | Requirements Intake document | `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` |
| 2. Implementation Planning | Design stages, tooling, and risks | Intake artefact | Implementation Plan | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| 3. Execution | Generate code & config per rules | Plan, architecture docs | Code, configs, ADRs | `docs/reference/AGENT_TOOLBOX.md`, architecture/service rules |
| 4. Verification | Validate quality gates | Generated artefacts | Completed checklist, reports | `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` |
| 5. Release Handoff | Summarize deliverables & readiness | Verified artefacts | QA report, deliverable links | `docs/quality/QA_REPORT_TEMPLATE.md`, `docs/reference/DELIVERABLES_CATALOG.md` |

## Step 0 – Prompt Validation

- **Entry Criteria**: User prompt received.
- **Mandatory Actions**:
  - Execute the checklist in `docs/guides/PROMPT_VALIDATION_GUIDE.md`.
  - Request missing information using `docs/reference/PROMPT_TEMPLATES.md`.
- **Allowed Tools**: Prompt templates only.
- **Expected Deliverables**: Validation confirmation or clarification request.
- **Exit Criteria**: All mandatory fields confirmed; otherwise halt workflow.

## Step 1 – Requirements Intake

- **Entry Criteria**: Prompt validation completed.
- **Mandatory Actions**:
  - Populate `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` with detailed context.
  - Cross-check architecture compatibility via `docs/reference/tech_stack.md` and `docs/guides/ARCHITECTURE_GUIDE.md`.
- **Allowed Tools**: Prompt templates for follow-up questions, technical references.
- **Expected Deliverables**: Completed intake document, open issues list.
- **Exit Criteria**: Stakeholder-confirmed requirements, identified risks logged.

## Step 2 – Implementation Planning

- **Entry Criteria**: Intake document approved.
- **Mandatory Actions**:
  - Draft the plan with `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`.
  - Map each stage to relevant architecture/service/infrastructure rules.
  - Identify required tooling from `docs/reference/AGENT_TOOLBOX.md`.
- **Allowed Tools**: Toolbox commands (planning sections use them descriptively), architecture references.
- **Expected Deliverables**: Implementation plan, optional ADR stubs (`docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md`).
- **Exit Criteria**: Plan approved by requester or reviewer.

## Step 3 – Execution

- **Entry Criteria**: Implementation plan approved.
- **Mandatory Actions**:
  - Implement tasks stage by stage, adhering to the plan.
  - Follow service-specific rules (`docs/services/*.mdc`) and shared component guidance (`docs/guides/shared_components.md`).
  - Document major decisions in ADRs as needed.
- **Allowed Tools**: Commands from `docs/reference/AGENT_TOOLBOX.md`, infrastructure/observability rules, troubleshooting guide.
- **Expected Deliverables**: Source code, configurations, ADRs, updated plan status.
- **Exit Criteria**: All planned tasks marked complete, no open blockers.

## Step 4 – Verification

- **Entry Criteria**: Execution tasks finished.
- **Mandatory Actions**:
  - Run the full verification suite defined in `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`.
  - Ensure test coverage meets `docs/quality/testing-standards.mdc`.
  - Capture evidence (logs, reports) for the QA report.
- **Allowed Tools**: Toolbox quality commands, observability checks, troubleshooting as needed.
- **Expected Deliverables**: Completed verification checklist, coverage reports, defect list if any.
- **Exit Criteria**: All mandatory checks pass or issues documented with remediation plan.

## Step 5 – Release Handoff

- **Entry Criteria**: Verification results available.
- **Mandatory Actions**:
  - Assemble the QA report (`docs/quality/QA_REPORT_TEMPLATE.md`).
  - Update deliverable listings per `docs/reference/DELIVERABLES_CATALOG.md`.
  - Provide final summary to stakeholders using `docs/reference/PROMPT_TEMPLATES.md`.
- **Allowed Tools**: Documentation templates, repository artifacts.
- **Expected Deliverables**: QA report, deliverable index, release readiness statement.
- **Exit Criteria**: Stakeholder acceptance or queued follow-up actions.

## Escalation & Fallback

- For missing inputs at any stage, revert to the applicable prompt templates.
- For technical failures, consult `docs/reference/troubleshooting.md` and rerun necessary commands.
- Escalate unresolved blockers with a clear summary of impact and requested decision.

## Maintenance

- Keep this workflow aligned with the templates and checklists referenced above.
- Update `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md` after modifications.
- Follow `docs/STYLE_GUIDE.md` when editing.
