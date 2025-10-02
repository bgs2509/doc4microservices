# Prompt Validation Guide

> **Purpose**: Ensure every user prompt entering the agent workflow contains the minimum context required to follow the microservices framework rules and produce production-ready deliverables.

## When to Run This Checklist

Run prompt validation immediately after receiving a new user request and before starting the Requirements Intake step (Stage 2 in `AI_CODE_GENERATION_MASTER_WORKFLOW.md`). If any mandatory field is missing, pause all further actions and ask the requester for clarification using the prompt augmentation templates.

## Critical Input Checklist

| Field | Why It Matters | Primary References |
|-------|----------------|--------------------|
| **Business Context** | Anchors the solution in a clear problem statement, target users, and success metrics. | `README.md`, `docs/reference/tech_stack.md`, `docs/reference/AGENT_CONTEXT_SUMMARY.md` |
| **Target Maturity Level** | Determines infrastructure complexity, observability, security, and generation time. Prevents over-engineering for MVPs and ensures production readiness for enterprise deployments. | `docs/reference/MATURITY_LEVELS.md`, `docs/reference/CONDITIONAL_STAGE_RULES.md` |
| **Functional Requirements** | Defines the capabilities the generated services must expose. | `docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md`, `docs/reference/PROJECT_STRUCTURE.md` |
| **Optional Modules** | Identifies additional services beyond core (Workers, Bot, MongoDB, Redis, etc.). Available at any maturity level. | `docs/reference/MATURITY_LEVELS.md` (modules section) |
| **Non-Functional Constraints** | Ensures compliance with architecture, performance, and security requirements. | `docs/guides/ARCHITECTURE_GUIDE.md`, `docs/atomic/architecture/`, `docs/atomic/observability/` |
| **Dependencies & Integrations** | Identifies external systems, queues, or data flows that must be modeled. | `docs/atomic/infrastructure/`, `docs/atomic/services/`, `docs/reference/DELIVERABLES_CATALOG.md` |
| **Scope Boundaries** | Prevents unplanned features from entering the delivery plan. | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| **Expected Deliverables** | Aligns produced artefacts with framework expectations. | `docs/reference/DELIVERABLES_CATALOG.md`, `docs/reference/ARCHITECTURE_DECISION_LOG_TEMPLATE.md` |
| **Acceptance Criteria** | Adds measurable success checks that feed the verification stage. | `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`, `docs/atomic/testing/` |
| **Open Questions & Risks** | Triggers early clarification to avoid rework. | `docs/reference/troubleshooting.md`, `docs/reference/PROMPT_TEMPLATES.md` |

## Validation Procedure

1. **Collect Prompt**
   - Store the raw user prompt in the working notes.
   - Confirm the prompt language and conventions comply with `docs/STYLE_GUIDE.md` if it will be referenced in documentation.
2. **Inspect Each Field**
   - For every row in the checklist above, verify the prompt contains explicit information.
   - If a field is partially filled, treat it as missing.
3. **Request Clarifications When Needed**
   - Use the relevant prompt augmentation snippet from `docs/reference/PROMPT_TEMPLATES.md`.
   - Clearly state which field is missing and why it is required.
   - Do not continue until the requester provides the missing context.
4. **Record Validation Outcome**
   - When all mandatory fields are satisfied, capture a short confirmation note to include in the Requirements Intake artefact.
   - If the requester cancels or cannot supply the data, terminate the workflow and log the reason.

## Decision Matrix

| Missing Information | Required Action | Blocker? |
|---------------------|-----------------|----------|
| Business context or overall goal | Ask the requester to restate the problem, target users, and success metrics. | Yes |
| Target maturity level | Ask: "Choose maturity level: 1=PoC (~5 min), 2=Development (~10 min), 3=Pre-Production (~15 min), 4=Production (~30 min)". See `PROMPT_TEMPLATES.md` for full prompt. | Yes |
| Optional modules | If applicable, clarify: "Need Telegram Bot? Background Workers? MongoDB? RabbitMQ? Redis?" | No (defaults to core only) |
| Functional requirements | Request a prioritized feature list or user stories. | Yes |
| Architecture and quality constraints | Ask for performance/security expectations or confirm adherence to framework defaults. | Yes |
| Dependencies or integrations | Clarify external systems, message queues, and data sources. | Yes |
| Scope boundaries | Request explicit exclusions to avoid over-delivery. | Yes |
| Deliverables or acceptance criteria | Confirm which artefacts and checks are expected (tests, coverage, reports). | Yes |
| Open questions/risks | Capture known unknowns; recommend a follow-up session if unresolved. | No, but must be tracked |

## Integration With Agent Workflow

- This guide is executed at **Stage 1** in `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md`.
- Only after successful validation should the agent proceed to Stage 2 (Requirements Intake) and populate `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`.
- The validated prompt becomes part of the project artefacts referenced in `docs/reference/DELIVERABLES_CATALOG.md`.

## Maintenance

- Update this checklist whenever new artefacts are added or requirements change.
- Ensure references stay aligned with `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md`.
- Follow `docs/STYLE_GUIDE.md` when editing this guide.
