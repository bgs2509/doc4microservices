# Failure Scenarios & Recovery Guide

> **Purpose**: Provide AI agents with clear decision trees and recovery procedures for handling failures, blockers, and unexpected situations during the 7-stage code generation workflow.

## Overview

This document covers **edge cases** and **failure scenarios** that can occur at any stage of the workflow. For each scenario, AI must follow the specified recovery procedure and communicate clearly with the user.

---

## Quick Navigation

| Scenario Type | When It Happens | Jump To |
|---------------|-----------------|---------|
| Validation failures | Stage 1 | [Incomplete or Invalid Prompts](#scenario-1-incomplete-or-invalid-prompts) |
| Requirement conflicts | Stage 2-3 | [Architecture Conflicts](#scenario-2-architecture-conflicts) |
| Test failures | Stage 4-5 | [Test Failures During Generation](#scenario-3-test-failures-during-generation) |
| Quality gate failures | Stage 5 | [Quality Gate Failures](#scenario-4-quality-gate-failures) |
| User changes mind | Any stage | [Mid-Workflow Requirement Changes](#scenario-5-mid-workflow-requirement-changes) |
| External blockers | Any stage | [External Dependency Failures](#scenario-6-external-dependency-failures) |
| Rollback requests | Stage 3-6 | [Rollback to Previous Stage](#scenario-7-rollback-to-previous-stage) |

---

## Core Principles

1. **Transparency**: Always communicate failures clearly to the user
2. **No Silent Failures**: Never skip checks or ignore errors
3. **User Decision**: When uncertain, ask the user rather than making assumptions
4. **Document Recovery**: Log all recovery actions for QA report
5. **Graceful Degradation**: Offer alternatives when strict requirements can't be met

---

## Scenario 1: Incomplete or Invalid Prompts

**Stage**: 1 (Prompt Validation)

**Symptoms**:
- Missing mandatory fields (business context, maturity level, functional requirements)
- Contradictory requirements
- Vague or ambiguous descriptions

### Recovery Procedure

```
1. STOP immediately — do NOT proceed to Stage 2
2. Identify ALL missing fields using PROMPT_VALIDATION_GUIDE.md
3. Use PROMPT_TEMPLATES.md to formulate clarification questions
4. Send clarification request to user with:
   - List of missing fields
   - Why each field is needed
   - Expected format/examples
5. WAIT for user response
6. Re-validate prompt
7. If still incomplete → repeat steps 2-6
8. If complete → proceed to Stage 2
```

### Example

**Bad Response** ❌:
> "Proceeding with assumptions since business context is missing..."

**Good Response** ✅:
> "## 🔍 Prompt Validation: Missing Information
>
> I cannot proceed without the following mandatory fields:
>
> **Missing**:
> 1. **Target maturity level** (1-4): This determines infrastructure complexity and generation time.
> 2. **Expected user load**: Need RPS, DAU to size infrastructure.
>
> Please provide these details to continue."

### References
- `docs/guides/PROMPT_VALIDATION_GUIDE.md`
- `docs/reference/PROMPT_TEMPLATES.md`

---

## Scenario 2: Architecture Conflicts

**Stage**: 2-3 (Requirements Intake / Planning)

**Symptoms**:
- User requests direct database access (violates HTTP-only rule)
- User wants FastAPI + Aiogram in same process (violates service separation)
- User wants features incompatible with Improved Hybrid Approach

### Recovery Procedure

```
1. STOP immediately — do NOT generate conflicting architecture
2. Identify the specific constraint violation
3. Explain the architectural constraint to the user:
   - What they requested
   - Why it violates framework rules
   - What the correct approach is
4. Propose compliant alternative
5. WAIT for user approval of alternative
6. Update Requirements Intake document
7. Proceed with compliant architecture
```

### Example

**User Request** (violates rules):
> "FastAPI service should connect directly to PostgreSQL for better performance"

**AI Response** ✅:
> "## ⚠️ Architecture Conflict Detected
>
> **Your requirement**: FastAPI service with direct PostgreSQL connection
>
> **Framework constraint**: Improved Hybrid Approach requires HTTP-only data access through dedicated data services.
>
> **Why**:
> - Centralized data access ensures consistency
> - Easier to scale data layer independently
> - Single source of truth for data operations
>
> **Compliant solution**:
> FastAPI service → HTTP calls → `template_data_postgres_api` (Port 8001) → PostgreSQL
>
> Performance impact is negligible (<5ms overhead for internal HTTP calls).
>
> **Do you approve this approach?**"

### References
- `docs/guides/ARCHITECTURE_GUIDE.md`
- `docs/atomic/architecture/improved-hybrid-overview.md`
- `docs/atomic/architecture/data-access-architecture.md`

---

## Scenario 3: Test Failures During Generation

**Stage**: 4 (Code Generation)

**Symptoms**:
- Unit tests fail after generating new code
- Integration tests fail due to configuration issues
- Type checking errors from Mypy
- Linting errors from Ruff

### Recovery Procedure

```
1. Capture the error output (full stack trace)
2. Analyze the root cause:
   - Code bug? → Fix the code
   - Test bug? → Fix the test
   - Configuration issue? → Fix config
   - Missing dependency? → Add to requirements
3. Apply fix
4. Re-run the failing check
5. If still failing → repeat steps 2-4 (max 3 attempts)
6. If still failing after 3 attempts:
   - Document the blocker
   - Ask user for guidance
   - Offer alternatives (skip feature, change approach)
7. Once fixed → commit with clear message
8. Continue to next sub-stage
```

### Example

**Scenario**: Test fails after generating payment integration

**AI Response** ✅:
> "## ⚠️ Test Failure: Payment Integration
>
> **Failed test**: `test_payment_creation_idempotency`
>
> **Error**:
> ```
> AssertionError: Expected 1 payment, got 2 (idempotency key not working)
> ```
>
> **Root cause**: Missing Redis connection in test fixtures.
>
> **Fix applied**: Added Redis testcontainer to `conftest.py`
>
> **Re-running test**: ✅ PASS
>
> Continuing to next sub-stage."

### References
- `docs/reference/troubleshooting.md`
- `docs/atomic/testing/unit-testing/pytest-setup.md`

---

## Scenario 4: Quality Gate Failures

**Stage**: 5 (Verification)

**Symptoms**:
- Coverage below threshold for maturity level
- Security vulnerabilities found by Bandit
- Type errors in critical paths
- Linting issues

### Recovery Procedure

```
1. Review AGENT_VERIFICATION_CHECKLIST.md
2. Identify which quality gate(s) failed
3. For EACH failed gate:
   a. Capture evidence (logs, reports)
   b. Determine if fixable:
      - Yes → Apply fix, re-run check
      - No → Document blocker
   c. If blocker → ask user for decision:
      - Add exception/waiver?
      - Change requirement?
      - Delay release?
4. If ALL gates pass → proceed to Stage 6
5. If ANY gate blocked → WAIT for user decision
```

### Example: Coverage Below Threshold

**Scenario**: Level 3 requires 80% coverage, but achieved only 76%

**AI Response** ✅:
> "## ⚠️ Quality Gate Failure: Coverage Below Threshold
>
> **Required**: ≥ 80% (Level 3 - Pre-Production)
> **Achieved**: 76%
>
> **Uncovered areas**:
> - `payment_service/refund_handler.py`: 45% coverage
> - `template_business_api/webhooks/stripe.py`: 62% coverage
>
> **Options**:
> 1. **Add tests** (recommended): I can generate tests for these areas (~15 minutes)
> 2. **Lower threshold**: Accept 76% (not recommended for Level 3)
> 3. **Defer to next iteration**: Mark as technical debt
>
> **Your decision**: _____"

### References
- `docs/quality/AGENT_VERIFICATION_CHECKLIST.md`
- `docs/reference/MATURITY_LEVELS.md` (for thresholds)

---

## Scenario 5: Mid-Workflow Requirement Changes

**Stage**: Any (typically 3-5)

**Symptoms**:
- User requests new feature during code generation
- User changes maturity level mid-workflow
- User removes previously approved feature

### Recovery Procedure

```
1. Acknowledge the change request
2. Assess impact:
   - Stage 1-2: Easy — update Requirements Intake, continue
   - Stage 3: Moderate — update Implementation Plan, get re-approval
   - Stage 4-5: High — may require rollback or separate iteration
3. Communicate impact to user:
   - Estimated time to incorporate change
   - Which stages need rework
   - Risk of introducing bugs
4. Offer options:
   - Option A: Incorporate now (with rework time)
   - Option B: Complete current plan, add change in next iteration
   - Option C: Rollback to earlier stage
5. WAIT for user decision
6. Execute chosen option
```

### Example: User Adds Feature at Stage 4

**User Request** (mid-generation):
> "Can we add real-time chat feature?"

**AI Response** ✅:
> "## 🔄 Change Request: Add Real-Time Chat
>
> **Current stage**: 4.3 (Business Logic generation - 60% complete)
>
> **Impact analysis**:
> - Requires WebSocket support (new module)
> - Needs Redis pub/sub (new infrastructure)
> - Chat message storage (new PostgreSQL tables)
> - Estimated additional time: ~20 minutes
>
> **Options**:
> 1. **Add now** (recommended if critical):
>    - Pause at current sub-stage
>    - Generate WebSocket module (4.Y)
>    - Resume remaining sub-stages
>    - Total delay: ~20 min
>
> 2. **Add in next iteration** (recommended if not urgent):
>    - Complete current plan first
>    - Deliver working app without chat
>    - Add chat as Phase 2 (~25 min total)
>
> **Your decision**: _____"

---

## Scenario 6: External Dependency Failures

**Stage**: Any (typically 4-5)

**Symptoms**:
- Docker registry unavailable
- Package registry (PyPI) down
- External API (Stripe, Twilio) unavailable
- Git submodule fetch fails

### Recovery Procedure

```
1. Detect the external failure (timeout, 404, 500 error)
2. Classify severity:
   - BLOCKER: Cannot proceed without it
   - WORKAROUND: Can use alternative temporarily
   - INFORMATIONAL: Doesn't affect current stage
3. For BLOCKERS:
   - Document the issue
   - Notify user immediately
   - Provide workaround if available
   - WAIT until dependency is restored
4. For WORKAROUNDS:
   - Use alternative (cached, local, mock)
   - Document temporary solution
   - Add TODO to switch back
5. For INFORMATIONAL:
   - Log for later
   - Continue workflow
```

### Example: PyPI Unavailable

**AI Response** ✅:
> "## 🚫 External Dependency Failure: PyPI Unavailable
>
> **Issue**: Cannot install `fastapi==0.115.0` from PyPI (timeout after 60s)
>
> **Impact**: BLOCKER for Stage 4 (cannot generate FastAPI service)
>
> **Workarounds**:
> 1. Use cached packages (if available locally)
> 2. Use alternative PyPI mirror (e.g., Alibaba mirror)
> 3. Wait for PyPI to restore (typically < 30 min)
>
> **Recommended action**: Try alternative mirror first. If fails, wait for PyPI.
>
> **Your decision**: _____"

---

## Scenario 7: Rollback to Previous Stage

**Stage**: 3-6 (any stage after planning)

**Symptoms**:
- User realizes requirements were wrong
- Major defect found during verification
- User wants to change approach

### Recovery Procedure

```
1. Confirm rollback request with user (explain data loss)
2. Identify target stage for rollback
3. Execute rollback:
   - Stage 3 → 2: Discard Implementation Plan, update Requirements Intake
   - Stage 4 → 3: Discard generated code, revise Implementation Plan
   - Stage 5 → 4: Keep code, re-run specific sub-stages
   - Stage 6 → 5: Re-run verification with adjusted criteria
4. Document reason for rollback (for QA report)
5. Resume workflow from target stage
6. Update delivery timeline estimate
```

### Example: Rollback from Stage 4 to Stage 3

**User Request**:
> "I realized we don't need MongoDB, only PostgreSQL. Can we simplify?"

**AI Response** ✅:
> "## 🔄 Rollback Request: Stage 4 → Stage 3
>
> **Current progress**:
> - ✅ Infrastructure (4.1) — completed
> - ✅ PostgreSQL data service (4.2) — completed
> - ⏸️ MongoDB data service (4.2b) — 50% complete
> - ⏸️ Business Logic (4.3) — not started
>
> **Rollback impact**:
> - Discard MongoDB service code
> - Update Implementation Plan (remove MongoDB phases)
> - Time saved: ~5 minutes
> - Time lost: ~2 minutes (MongoDB work done)
> - Net benefit: ~3 minutes faster delivery
>
> **Proceeding**:
> 1. Rollback to Stage 3 (planning)
> 2. Update Implementation Plan (remove MongoDB)
> 3. Get your approval
> 4. Resume Stage 4 with simplified plan
>
> **Confirmed?**"

---

## Scenario 8: User Aborts Workflow

**Stage**: Any

**Symptoms**:
- User explicitly says "stop", "cancel", "abort"
- User stops responding for extended period

### Recovery Procedure

```
1. Confirm abort intent with user:
   - "Do you want to abort the workflow?"
   - Explain current progress
   - Explain what will be saved/lost
2. If confirmed abort:
   - Stop all work immediately
   - Save current progress (if any code generated)
   - Generate partial QA report:
     - What was completed
     - What was in progress
     - Reason for abort
   - Provide handoff package (partial deliverables)
3. If user wants pause (not abort):
   - Save state
   - Document stopping point
   - Provide resume instructions
4. Close session gracefully
```

### Example

**User Says**: "Stop, I need to rethink this."

**AI Response** ✅:
> "## ⏸️ Workflow Pause Requested
>
> **Current stage**: 4.3 (Business Logic - 40% complete)
>
> **Completed so far**:
> - ✅ Infrastructure setup (Docker Compose, Nginx)
> - ✅ PostgreSQL data service (fully functional)
> - ⏸️ FastAPI business service (2 of 5 endpoints done)
>
> **Options**:
> 1. **Pause**: Save current state, you can resume later
> 2. **Abort**: Discard all work, start fresh next time
> 3. **Continue**: I can keep going while you think
>
> **If pausing**: I'll provide:
> - Partial codebase (zipped)
> - Progress report (where we stopped)
> - Resume instructions (how to continue)
>
> **Your choice**: _____"

---

## Scenario 9: Conflicting Quality Requirements

**Stage**: 5 (Verification)

**Symptoms**:
- User wants high coverage but minimal tests
- User wants production readiness but chose Level 1 (PoC)
- User wants compliance but no audit logging

### Recovery Procedure

```
1. Identify the contradiction
2. Explain the conflict to user with evidence:
   - What they requested
   - What maturity level provides
   - The gap between them
3. Offer resolution options:
   - Option A: Upgrade maturity level (recommended)
   - Option B: Accept lower quality (document risk)
   - Option C: Add specific features a-la-carte
4. WAIT for user decision
5. Update Requirements Intake / Implementation Plan
6. Re-run verification with adjusted criteria
```

### Example

**Conflict**: User wants GDPR compliance but chose Level 1 (PoC)

**AI Response** ✅:
> "## ⚠️ Conflicting Requirements Detected
>
> **Your requirements**:
> - GDPR compliance (audit logging, encryption, right to deletion)
> - Maturity Level: 1 (PoC)
>
> **Conflict**:
> Level 1 (PoC) does NOT include:
> - ❌ Audit logging
> - ❌ Encryption at rest
> - ❌ RBAC / access controls
> - ❌ GDPR deletion workflows
>
> **GDPR compliance requires at minimum Level 4 (Production).**
>
> **Options**:
> 1. **Upgrade to Level 4** (recommended for GDPR):
>    - Full compliance features
>    - Time: ~30 min (instead of ~5 min)
>
> 2. **Stay at Level 1, defer GDPR**:
>    - Accept that app is NOT GDPR compliant
>    - Add compliance in future iteration
>    - Risk: Cannot deploy in EU
>
> 3. **Hybrid approach** (Level 2 + manual GDPR):
>    - Generate Level 2 base (~10 min)
>    - You manually add GDPR features later
>
> **Your decision**: _____"

---

## Scenario 10: Infinite Loop / Stuck State

**Stage**: Any

**Symptoms**:
- AI keeps asking same question
- Test fails repeatedly with same fix attempts
- User and AI disagree on requirements

### Recovery Procedure

```
1. Detect loop (if same action repeated > 3 times)
2. STOP immediately
3. Escalate to user:
   - "I'm unable to proceed due to [issue]"
   - Summarize what was attempted
   - Ask for explicit guidance or decision
4. Offer to:
   - Rollback to previous stage
   - Skip problematic component
   - Defer to manual implementation
5. WAIT for user decision (do NOT continue loop)
```

### Example: Test Keeps Failing

**After 3 failed fix attempts**:

**AI Response** ✅:
> "## 🔄 Unable to Fix Test Failure
>
> **Issue**: `test_user_authentication` keeps failing
>
> **Attempts made**:
> 1. Fixed JWT token generation → still failed
> 2. Updated test fixtures → still failed
> 3. Changed timing (added delays) → still failed
>
> **Root cause**: Unclear. Possibly environment-specific issue.
>
> **I'm stuck. Options**:
> 1. **Skip this test** (not recommended): Mark as known failure, document in QA report
> 2. **Simplify auth** (recommended): Use simpler auth mechanism for now
> 3. **Debug together**: Share full logs, you help identify issue
> 4. **Rollback auth feature**: Remove authentication, add later
>
> **Your decision**: _____"

---

## Decision Tree Reference

Use this flowchart when any failure occurs:

```
                           [Failure Detected]
                                  |
                    +-------------+-------------+
                    |                           |
          [Can I fix automatically?]   [Need user decision?]
                    |                           |
              +-----+-----+                     |
              |           |                     |
          [YES]        [NO]               [Ask user]
              |           |                     |
         [Fix it]   [Try alternative]     [WAIT for input]
              |           |                     |
         [Re-run]         |              +------+------+
              |           |              |             |
        +-----+-----+     |          [Proceed]    [Rollback]
        |           |     |              |             |
    [PASS]      [FAIL]   |         [Continue]   [Go back]
        |           |     |              |             |
   [Continue] [Escalate] |         [Next stage]  [Fix & retry]
                    |     |
                    +-----+
                          |
                   [User decides]
                          |
                   [Document & proceed]
```

---

## Maintenance

- Update this document when new failure patterns are identified
- Keep aligned with `AI_CODE_GENERATION_MASTER_WORKFLOW.md`
- Reference from `AGENT_CONTEXT_SUMMARY.md`
- Follow `STYLE_GUIDE.md` for formatting

---

**Last Updated**: 2025-10-02
