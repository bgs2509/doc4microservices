# Prompt Validation Guide

> **Purpose**: Ensure every user prompt entering the agent workflow contains the minimum context required to follow the microservices framework rules and produce production-ready deliverables.

## When to Run This Checklist

Run prompt validation immediately after receiving a new user request and before starting the Requirements Intake step (Stage 2 in `ai-code-generation-master-workflow.md`). If any mandatory field is missing, pause all further actions and ask the requester for clarification using the prompt augmentation templates.

## Critical Input Checklist

| Field | Why It Matters | Primary References |
|-------|----------------|--------------------|
| **Business Context** | Anchors the solution in a clear problem statement, target users, and success metrics. | `README.md`, `docs/reference/tech_stack.md`, `docs/reference/agent-context-summary.md` |
| **Target Maturity Level** | Determines infrastructure complexity, observability, security, and generation time. Prevents over-engineering for MVPs and ensures production readiness for enterprise deployments. | `docs/reference/maturity-levels.md`, `docs/reference/conditional-stage-rules.md` |
| **Functional Requirements** | Defines the capabilities the generated services must expose. | `docs/guides/use-case-implementation-guide.md`, `docs/reference/project-structure.md` |
| **Optional Modules** | Identifies additional services beyond core (Workers, Bot, MongoDB, Redis, etc.). Available at any maturity level. | `docs/reference/maturity-levels.md` (modules section) |
| **Non-Functional Constraints** | Ensures compliance with architecture, performance, and security requirements. | `docs/guides/architecture-guide.md`, `docs/atomic/architecture/`, `docs/atomic/observability/` |
| **Dependencies & Integrations** | Identifies external systems, queues, or data flows that must be modeled. | `docs/atomic/infrastructure/`, `docs/atomic/services/`, `docs/reference/deliverables-catalog.md` |
| **Scope Boundaries** | Prevents unplanned features from entering the delivery plan. | `docs/guides/implementation-plan-template.md` |
| **Expected Deliverables** | Aligns produced artefacts with framework expectations. | `docs/reference/deliverables-catalog.md`, `docs/reference/architecture-decision-log-template.md` |
| **Acceptance Criteria** | Adds measurable success checks that feed the verification stage. | `docs/quality/agent-verification-checklist.md`, `docs/atomic/testing/` |
| **Open Questions & Risks** | Triggers early clarification to avoid rework. | `docs/reference/troubleshooting.md`, `docs/reference/prompt-templates.md` |

## Validation Procedure

1. **Collect Prompt**
   - Store the raw user prompt in the working notes.
   - Confirm the prompt language and conventions comply with `docs/STYLE_GUIDE.md` if it will be referenced in documentation.
2. **Inspect Each Field**
   - For every row in the checklist above, verify the prompt contains explicit information.
   - If a field is partially filled, treat it as missing.
3. **Request Clarifications When Needed**
   - Use the relevant prompt augmentation snippet from `docs/reference/prompt-templates.md`.
   - Clearly state which field is missing and why it is required.
   - Do not continue until the requester provides the missing context.
4. **Record Validation Outcome**
   - When all mandatory fields are satisfied, capture a short confirmation note to include in the Requirements Intake artefact.
   - If the requester cancels or cannot supply the data, terminate the workflow and log the reason.

## Decision Matrix

| Missing Information | Required Action | Blocker? |
|---------------------|-----------------|----------|
| Business context or overall goal | Ask the requester to restate the problem, target users, and success metrics. | Yes |
| Target maturity level | Ask: "Choose maturity level: 1=PoC (~5 min), 2=Development (~10 min), 3=Pre-Production (~15 min), 4=Production (~30 min)". See `prompt-templates.md` for full prompt. | Yes |
| Optional modules | If not mentioned, ask explicitly: "Do you need any optional modules (Workers, Bot, MongoDB, RabbitMQ, Redis) or just core (FastAPI + PostgreSQL)?" **MUST be explicitly stated** (default: "none" if user confirms core-only). | No (defaults to "none" if user confirms, but must ask) |
| Functional requirements | Request a prioritized feature list or user stories. | Yes |
| Architecture and quality constraints | Ask for performance/security expectations or confirm adherence to framework defaults. | Yes |
| Dependencies or integrations | Clarify external systems, message queues, and data sources. | Yes |
| Scope boundaries | Request explicit exclusions to avoid over-delivery. | Yes |
| Deliverables or acceptance criteria | Confirm which artefacts and checks are expected (tests, coverage, reports). | Yes |
| Open questions/risks | Capture known unknowns; recommend a follow-up session if unresolved. | No, but must be tracked |

## Retry Policy for Unresponsive Users

> **Purpose**: Define how AI handles cases where users don't provide required clarifications, preventing indefinite workflow suspension.

### Retry Sequence

When AI requests clarification for missing mandatory fields:

1. **First Attempt** (immediate)
   - Send clarification request using templates from `prompt-templates.md`
   - Clearly list all missing fields
   - Provide examples for each field
   - Set expectations: "Please provide this information to proceed with Stage 2"

2. **Wait Period**
   - Monitor for user response
   - If no valid response received, proceed to second attempt

3. **Second Attempt** (after first timeout)
   - Resend clarification with simplified format
   - Highlight most critical missing fields (e.g., Maturity Level, Business Context)
   - Offer options/defaults where applicable:
     ```
     Quick Decision Guide:
     • Maturity Level: Choose 1 (PoC) if unsure - can upgrade later
     • Optional Modules: Choose "none" if uncertain - can add later
     ```
   - Final warning: "Without this information, workflow cannot proceed"

4. **Third Attempt Decision**
   - If still no valid response after second attempt:
     - **TERMINATE** workflow gracefully
     - Log termination reason: "Workflow terminated: User did not provide required information after 2 clarification attempts"
     - Send termination summary to user:
       ```
       ## ⚠️ Workflow Terminated

       **Reason**: Missing mandatory information after multiple clarification requests

       **Missing Fields**:
       • Target Maturity Level (1-4)
       • Business Context (problem, users, metrics)
       [... list all still-missing fields ...]

       **Next Steps**:
       To restart the workflow, please provide a complete prompt including all mandatory fields.
       See docs/guides/prompt-validation-guide.md for requirements.
       ```

### Handling Ambiguous Responses

If user provides **partial** or **ambiguous** information:

| Scenario | AI Action | Example |
|----------|-----------|---------|
| User says "I don't know" for non-critical field | Use framework default, document assumption in Requirements Intake | User: "I don't know auth method"<br>AI: "Defaulting to JWT (framework standard), can change later" |
| User says "I don't know" for **critical** field (Maturity Level, Business Context) | Cannot proceed → retry with more guidance | User: "I don't know which level"<br>AI: "Cannot proceed without level. For quick prototype, choose Level 1 (PoC). For production, choose Level 4." |
| User provides invalid value | Reject, ask for correction with valid options | User: "Maturity Level = 7"<br>AI: "Invalid level. Valid options: 1, 2, 3, or 4" |

### DO NOT Assume Defaults for Critical Fields

**NEVER** auto-select these without explicit user confirmation:
- ❌ Target Maturity Level (1-4)
- ❌ Business Context
- ❌ Functional Requirements

**MAY** auto-select these with user notification:
- ✅ Optional Modules (default: "none" if user confirms core-only is sufficient)
- ✅ Authentication method (default: JWT if user approves)
- ✅ Coverage threshold (use level-appropriate default from `maturity-levels.md`)

### Timeout Configuration

| Attempt | Wait Time | Notes |
|---------|-----------|-------|
| After 1st request | Implementation-dependent | In interactive CLI: wait for user input<br>In async environments: configurable timeout |
| After 2nd request | Implementation-dependent | Shorter than first timeout<br>Signal urgency to user |

**Note**: Exact timeout values are implementation-specific (CLI vs web UI vs API). The principle is: 2 clarification attempts maximum, then terminate gracefully.

## Integration With Agent Workflow

- This guide is executed at **Stage 1** in `docs/guides/ai-code-generation-master-workflow.md`.
- Only after successful validation should the agent proceed to Stage 2 (Requirements Intake) and populate `docs/guides/requirements-intake-template.md`.
- The validated prompt becomes part of the project artefacts referenced in `docs/reference/deliverables-catalog.md`.

## Maintenance

- Update this checklist whenever new artefacts are added or requirements change.
- Ensure references stay aligned with `docs/INDEX.md` and `docs/reference/agent-context-summary.md`.
- Follow `docs/STYLE_GUIDE.md` when editing this guide.
