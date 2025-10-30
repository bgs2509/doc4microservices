# Requirements Traceability Guide

> **PURPOSE**: Establish a systematic approach to track every requirement from initial user prompt through implementation to final delivery, guaranteeing 100% coverage without exceptions. Critical for large, detailed UX/UI prompts with 50+ requirements.

## Table of Contents

- [What is Requirements Traceability?](#what-is-requirements-traceability)
- [Why RTM is Critical](#why-rtm-is-critical)
- [Req ID Format Standards](#req-id-format-standards)
- [Lifecycle Through Workflow](#lifecycle-through-workflow)
- [Coverage Calculation](#coverage-calculation)
- [Implementation Guide](#implementation-guide)
- [Complete Example](#complete-example-p2p-lending)
- [Common Pitfalls](#common-pitfalls)

---

## What is Requirements Traceability?

**Requirements Traceability Matrix (RTM)** is a document that maps each user requirement to its implementation in code, tests, and deliverables. It ensures **bidirectional traceability**:

- **Forward**: Requirement → Design → Implementation → Testing → Delivery
- **Backward**: Code → Test → Requirement (proving every line serves a purpose)

### Key Benefits

1. **100% Coverage Guarantee**: No requirement left unimplemented
2. **Auditability**: Stakeholders can verify every requirement was addressed
3. **Change Impact Analysis**: Identify which code to modify when requirements change
4. **Quality Gate**: Block delivery if coverage < 100% (unless explicitly approved)
5. **UX/UI Completeness**: Essential for UI-heavy projects with 50+ UI elements

---

## Why RTM is Critical

### Problem Without RTM

When AI generates code from a large user prompt:
- ❌ **Memory limits**: AI may forget requirements from early in prompt
- ❌ **Implicit tracking**: No systematic verification of completeness
- ❌ **Easy to miss**: One missing button, modal, or error message = incomplete product
- ❌ **No evidence**: Cannot prove to stakeholders that everything was built

### Solution With RTM

- ✅ **Explicit tracking**: Every requirement gets unique Req ID (FR-001, UI-001)
- ✅ **Systematic verification**: Stage 5 checks 100% coverage before delivery
- ✅ **Evidence-based**: QA Report shows exact code location for each requirement
- ✅ **Stakeholder confidence**: Coverage matrix proves completeness

### Critical for Large Prompts

**Example**: UX/UI prompt with 50 requirements
- 20 UI screens (Login, Dashboard, Profile, Settings, etc.)
- 30 UI elements (buttons, forms, modals, dropdowns, etc.)
- 15 user flows (registration → verification → onboarding)
- 25 validation rules (email format, password strength, etc.)
- 30 error messages (field empty, wrong format, etc.)

**Without RTM**: High risk of missing 5-10% of requirements
**With RTM**: 100% coverage guaranteed by systematic Stage 5 verification

---

## Req ID Format Standards

### ID Structure

```
[PREFIX]-[NUMBER]

PREFIX:
- FR = Functional Requirement
- UI = UI/UX Requirement
- NF = Non-Functional Requirement

NUMBER: 001, 002, 003, ... (zero-padded, 3 digits)
```

### Examples

| Req ID | Type | Description |
|--------|------|-------------|
| FR-001 | Functional | User registration with email/password |
| FR-002 | Functional | Loan creation with validation rules |
| UI-001 | UI/UX | Registration form (email, password, confirm fields) |
| UI-002 | UI/UX | Login screen with "Forgot password?" link |
| UI-003 | UI/UX | Dashboard showing active loans + stats |
| NF-001 | Non-Functional | API latency < 200ms p95 |
| NF-002 | Non-Functional | 99.9% uptime SLA |

### Numbering Rules

1. **Sequential**: Assign IDs in order as requirements are documented (FR-001, FR-002, FR-003)
2. **Immutable**: Once assigned, Req ID never changes (even if requirement is descoped)
3. **No reuse**: Never reuse Req ID from deleted requirement
4. **Separate sequences**: FR, UI, NF have independent numbering (FR-001 ≠ UI-001)

### When to Assign IDs

**Stage 2: Requirements Intake** (MANDATORY)
- As AI documents requirements in `requirements-intake-template.md`
- EVERY requirement in Functional Requirements table gets Req ID
- EVERY UI element/screen gets Req ID (for UI-heavy projects)
- EVERY measurable non-functional constraint gets Req ID

---

## Lifecycle Through Workflow

### Stage 0: AI Initialization
- **RTM Status**: Not yet created
- **AI Action**: Read this guide to understand RTM concept

### Stage 1: Prompt Validation
- **RTM Status**: Not yet created
- **AI Action**: Ensure prompt contains detailed requirements (foundation for RTM)

### Stage 2: Requirements Intake
- **RTM Status**: ✅ **CREATED**
- **AI Action**:
  1. Extract all requirements from user prompt
  2. Assign unique Req ID to each requirement (FR-*, UI-*, NF-*)
  3. Document in `requirements-intake-template.md` with columns:
     - Req ID
     - Feature/Capability
     - Priority (Must/Should/Could)
     - Description
     - Acceptance Criteria
     - Implementation Status = **Pending**
  4. Count total requirements for coverage tracking

### Stage 3: Architecture Mapping & Planning
- **RTM Status**: ✅ **MAPPED TO TASKS**
- **AI Action**:
  1. Create Requirements Traceability Matrix in `implementation-plan-template.md`
  2. Map EVERY Req ID → Phase → Specific Tasks
  3. Example:
     ```
     FR-001 (User registration) → Phase 3 → Task 3.1, 3.2
     UI-001 (Registration form) → Phase 5 → Task 5.3
     ```
  4. Verify all Req IDs from Stage 2 appear in mapping (no orphaned requirements)

### Stage 4: Code Generation
- **RTM Status**: ✅ **IMPLEMENTATION IN PROGRESS**
- **AI Action**:
  1. As each requirement is implemented, update RTM:
     - Change Status from "Pending" → "In Progress" → "✅ Done"
     - Add Evidence (code file location: `services/api/src/api/v1/users.py:20`)
  2. Add comments in code linking back to Req ID:
     ```python
     # Implements: FR-001 (User registration)
     @router.post("/users", status_code=201)
     async def create_user(...):
     ```

### Stage 5: Quality Verification
- **RTM Status**: ✅ **COVERAGE VERIFIED**
- **AI Action**:
  1. Run Requirements Coverage Verification check (NEW in `agent-verification-checklist.md`)
  2. For EACH Req ID in Stage 2:
     - Verify Status = "✅ Done" in RTM
     - Verify Evidence (code location) exists
     - Verify tests exist for requirement
  3. Calculate coverage: `implemented / total * 100%`
  4. **GATE**: If coverage < 100% → BLOCK Stage 6 (unless stakeholder approves descope)

### Stage 6: QA Report & Handoff
- **RTM Status**: ✅ **DOCUMENTED IN QA REPORT**
- **AI Action**:
  1. Generate Requirements Coverage Matrix in `qa-report-template.md`
  2. Include full table with ALL Req IDs:
     - Status (✅ Done / ⚠️ Descoped / ❌ Missing)
     - Evidence (code + tests)
     - Notes
  3. Include Overall Coverage Summary:
     ```
     Total Requirements: 50
     Implemented: 50 (100%)
     Descoped: 0
     Outstanding: 0
     Status: ✅ 100% COVERAGE ACHIEVED
     ```

---

## Coverage Calculation

### Formula

```
Coverage (%) = (Implemented Requirements / Total Requirements) × 100%

Where:
- Implemented = Req IDs with Status "✅ Done" AND Evidence exists
- Total = All Req IDs assigned in Stage 2 (FR-* + UI-* + NF-*)
```

### Coverage Thresholds

| Coverage | Status | Action |
|----------|--------|--------|
| **100%** | ✅ **PASS** | Proceed to Stage 6 (QA Report) |
| **95-99%** | ⚠️ **WARNING** | Review missing requirements, consider descope with stakeholder approval |
| **< 95%** | ❌ **FAIL** | BLOCK Stage 6, implement missing requirements OR get explicit descope approval |

### Descope Process

If stakeholder approves descoping requirements:
1. Update Req ID Status: "Pending" → "⚠️ Descoped (Approved by [Name] on [Date])"
2. Document reason in QA Report § Defects & Risks
3. Recalculate coverage excluding descoped:
   ```
   Adjusted Coverage = Implemented / (Total - Descoped) × 100%
   ```
4. Adjusted coverage MUST be 100% to proceed

---

## Implementation Guide

### For AI Agents

#### **Step 1: Stage 2 - Create RTM Foundation**

When filling `requirements-intake-template.md`:

```markdown
## Functional Requirements
| **Req ID** | Feature / Capability | Priority | Description | Acceptance Criteria | **Implementation Status** |
|------------|---------------------|----------|-------------|---------------------|--------------------------|
| FR-001 | User registration | Must | Email/password signup | POST /users endpoint works, email verification sent | **Pending** |
| FR-002 | Loan creation | Must | Borrower creates loan request | POST /loans validates amount/duration, stores in DB | **Pending** |
| FR-003 | Payment automation | Must | Monthly payments via Stripe | Worker processes payments, updates loan status | **Pending** |

## UI/UX Requirements (for UI-heavy projects)
| **Req ID** | UI Element / Screen | Priority | Description | Acceptance Criteria | **Implementation Status** |
|------------|-------------------|----------|-------------|---------------------|--------------------------|
| UI-001 | Registration form | Must | Email, password, confirm password fields | Form validation works, error messages shown | **Pending** |
| UI-002 | Login screen | Must | Email/password with "Forgot password?" link | Redirect to /dashboard on success | **Pending** |
| UI-003 | Dashboard | Must | Show active loans + statistics | Data loads from API, responsive layout | **Pending** |

## Requirements Summary
- **Total Functional (FR-*):** 3
- **Total UI/UX (UI-*):** 3
- **Total Non-Functional (NF-*):** 0
- **Grand Total:** 6
```

#### **Step 2: Stage 3 - Map Requirements to Tasks**

In `implementation-plan-template.md`:

```markdown
## Requirements Traceability Matrix

| Req ID | Feature/Element | Mapped to Phase | Mapped to Tasks | Evidence (when implemented) | Status |
|--------|----------------|-----------------|-----------------|----------------------------|--------|
| FR-001 | User registration | Phase 3 | Task 3.1: Domain entity, Task 3.2: API endpoint | TBD | Pending |
| FR-002 | Loan creation | Phase 3 | Task 3.3: Loan entity, Task 3.4: Validation logic | TBD | Pending |
| FR-003 | Payment automation | Phase 4 | Task 4.1: Payment worker, Task 4.2: Stripe integration | TBD | Pending |
| UI-001 | Registration form | Phase 5 | Task 5.3: Registration handler with FSM | TBD | Pending |
| UI-002 | Login screen | Phase 5 | Task 5.4: Auth handler | TBD | Pending |
| UI-003 | Dashboard | Phase 5 | Task 5.5: Dashboard handler with API calls | TBD | Pending |

**Requirements Coverage Plan:**
- Total Requirements: 6
- Distributed across 3 phases (Phase 3, 4, 5)
- Average 2 requirements per phase
```

#### **Step 3: Stage 4 - Update RTM During Implementation**

As you implement each task, update the RTM Evidence column:

```markdown
| Req ID | Evidence (when implemented) | Status |
|--------|----------------------------|--------|
| FR-001 | `services/api/src/api/v1/users.py:20` | ✅ Done |
| FR-002 | `services/api/src/api/v1/loans.py:15` | ✅ Done |
| UI-001 | `services/bot/src/handlers/register.py:15` | In Progress |
```

#### **Step 4: Stage 5 - Verify Coverage**

Run Requirements Coverage Verification:

```bash
# 1. Extract all Req IDs from Requirements Intake
grep "FR-\|UI-\|NF-" docs/artifacts/requirements-intake.md

# 2. For each Req ID, verify implementation exists
# (Manual or automated check)

# 3. Calculate coverage
Total: 6
Implemented: 6
Coverage: 100%
```

#### **Step 5: Stage 6 - Document in QA Report**

Include full Coverage Matrix:

```markdown
## Requirements Coverage Matrix

### Functional Requirements (FR-*)
| Req ID | Feature | Status | Evidence (Code Location) | Tests | Notes |
|--------|---------|--------|--------------------------|-------|-------|
| FR-001 | User registration | ✅ Done | `services/api/src/api/v1/users.py:20` | ✅ 5 tests | Fully implemented |
| FR-002 | Loan creation | ✅ Done | `services/api/src/api/v1/loans.py:15` | ✅ 8 tests | Complete with validations |
| FR-003 | Payment automation | ✅ Done | `services/worker/src/workers/payment.py:30` | ✅ 6 tests | Worker operational |

**Functional Coverage:** 3/3 requirements (100%)

### Overall Coverage Summary
- **Total Requirements:** 6 (3 functional + 3 UI + 0 non-functional)
- **Implemented:** 6 (100%)
- **Descoped:** 0
- **Outstanding:** 0

**Status:** ✅ **ALL REQUIREMENTS COVERED**
```

---

## Complete Example: P2P Lending

### User Prompt (Simplified)

```
Build a P2P lending platform with:
1. User registration with KYC verification
2. Loan marketplace (browse/search loans)
3. Automated monthly payments via Stripe
4. Credit scoring algorithm
5. Telegram bot for notifications
```

### Stage 2: Requirements Intake (Excerpt)

```markdown
## Functional Requirements
| Req ID | Feature | Priority | Description | Acceptance Criteria | Status |
|--------|---------|----------|-------------|---------------------|--------|
| FR-001 | User registration | Must | Email/password + KYC | POST /users, Onfido integration | Pending |
| FR-002 | Loan marketplace | Must | Browse/filter loans | GET /loans with pagination | Pending |
| FR-003 | Automated payments | Must | Monthly via Stripe | Worker + webhook handler | Pending |
| FR-004 | Credit scoring | Must | 3-factor algorithm | Score calculation in worker | Pending |

## UI/UX Requirements
| Req ID | Element | Priority | Description | Acceptance Criteria | Status |
|--------|---------|----------|-------------|---------------------|--------|
| UI-001 | Registration form | Must | Email, password, confirm | Validation + error messages | Pending |
| UI-002 | Login screen | Must | Email/password + "Forgot?" | Redirect to dashboard | Pending |
| UI-003 | Loan list | Must | Cards with amount/rate/term | Clickable to view details | Pending |
| UI-004 | Notification setup | Must | Enable/disable Telegram | Toggle in settings | Pending |

**Total:** 8 requirements (4 FR + 4 UI)
```

### Stage 3: Requirements Traceability Matrix

```markdown
| Req ID | Feature | Phase | Tasks | Evidence | Status |
|--------|---------|-------|-------|----------|--------|
| FR-001 | User registration | Phase 3 | 3.1, 3.2 | TBD | Pending |
| FR-002 | Loan marketplace | Phase 3 | 3.3, 3.4 | TBD | Pending |
| FR-003 | Automated payments | Phase 4 | 4.1, 4.2 | TBD | Pending |
| FR-004 | Credit scoring | Phase 4 | 4.3 | TBD | Pending |
| UI-001 | Registration form | Phase 5 | 5.1 | TBD | Pending |
| UI-002 | Login screen | Phase 5 | 5.2 | TBD | Pending |
| UI-003 | Loan list | Phase 5 | 5.3 | TBD | Pending |
| UI-004 | Notification setup | Phase 5 | 5.4 | TBD | Pending |
```

### Stage 5: Coverage Verification

```
Total Requirements: 8
Implemented: 8
Coverage: 8/8 = 100% ✅
```

### Stage 6: QA Report (Excerpt)

```markdown
## Requirements Coverage Matrix

### Functional Requirements (4 total)
| Req ID | Feature | Status | Evidence | Tests |
|--------|---------|--------|----------|-------|
| FR-001 | User registration | ✅ Done | `api/v1/users.py:20` | ✅ 5 tests |
| FR-002 | Loan marketplace | ✅ Done | `api/v1/loans.py:15` | ✅ 8 tests |
| FR-003 | Automated payments | ✅ Done | `worker/payment.py:30` | ✅ 6 tests |
| FR-004 | Credit scoring | ✅ Done | `worker/credit_score.py:45` | ✅ 4 tests |

**Functional Coverage:** 4/4 (100%)

### UI/UX Requirements (4 total)
| Req ID | Element | Status | Evidence | Tests |
|--------|---------|--------|----------|-------|
| UI-001 | Registration form | ✅ Done | `bot/handlers/register.py:15` | ✅ e2e |
| UI-002 | Login screen | ✅ Done | `bot/handlers/auth.py:30` | ✅ e2e |
| UI-003 | Loan list | ✅ Done | `bot/handlers/loans.py:40` | ✅ e2e |
| UI-004 | Notification setup | ✅ Done | `bot/handlers/settings.py:25` | ✅ e2e |

**UI/UX Coverage:** 4/4 (100%)

### Overall Coverage
- **Total:** 8 requirements
- **Implemented:** 8 (100%)
- **Status:** ✅ ALL REQUIREMENTS COVERED
```

---

## Common Pitfalls

### ❌ Pitfall 1: Forgetting to Assign Req IDs in Stage 2

**Problem**: Requirements documented without Req IDs
```markdown
| Feature | Description |
|---------|-------------|
| User registration | Email/password signup |
```

**Solution**: ALWAYS include Req ID column
```markdown
| **Req ID** | Feature | Description |
|------------|---------|-------------|
| FR-001 | User registration | Email/password signup |
```

### ❌ Pitfall 2: Partial Requirements Mapping in Stage 3

**Problem**: Some Req IDs missing from RTM
```markdown
RTM shows FR-001, FR-002, but FR-003 is missing
```

**Solution**: Verify ALL Req IDs from Stage 2 appear in RTM
- Use checklist: grep all Req IDs from Requirements Intake
- Ensure each Req ID has Phase + Tasks mapping

### ❌ Pitfall 3: No Evidence Links in Stage 4

**Problem**: RTM says "Done" but no code location
```markdown
| Req ID | Status | Evidence |
|--------|--------|----------|
| FR-001 | Done | ??? |
```

**Solution**: ALWAYS include file path + line number
```markdown
| Req ID | Status | Evidence |
|--------|--------|----------|
| FR-001 | ✅ Done | `services/api/src/api/v1/users.py:20` |
```

### ❌ Pitfall 4: Skipping Coverage Verification in Stage 5

**Problem**: Proceeding to Stage 6 without verifying 100% coverage

**Solution**: MANDATORY check in `agent-verification-checklist.md`
- Extract all Req IDs from Stage 2
- Verify each has Status "✅ Done" + Evidence
- Calculate coverage (must be 100% or descope approved)

### ❌ Pitfall 5: Missing Coverage Matrix in QA Report

**Problem**: QA Report lacks RTM table

**Solution**: Use `qa-report-template.md` Requirements Coverage Matrix section
- Include full table with ALL Req IDs
- Show Overall Coverage Summary
- Provide evidence links

---

## Integration Points

### With Other Framework Documents

| Document | How RTM Integrates |
|----------|-------------------|
| `prompt-validation-guide.md` | Stage 1 ensures prompt has detailed requirements (foundation for RTM) |
| `requirements-intake-template.md` | Stage 2 creates RTM with Req IDs |
| `implementation-plan-template.md` | Stage 3 maps Req IDs to tasks |
| `agent-verification-checklist.md` | Stage 5 verifies 100% coverage |
| `qa-report-template.md` | Stage 6 documents final coverage |
| `ai-code-generation-master-workflow.md` | All stages reference RTM lifecycle |

### With Maturity Levels

RTM is **MANDATORY for ALL maturity levels** (Level 1-4):
- Level 1 (PoC): Fewer requirements, but 100% coverage of selected requirements
- Level 4 (Production): More requirements, but same 100% coverage rule

**Key Principle**: Maturity Level = Scope Selector (how many requirements), NOT coverage target

---

## Maintenance

- Update examples when workflow changes
- Keep Req ID format consistent with new requirement types
- Align with `STYLE_GUIDE.md` for formatting
- Cross-reference with `ai-code-generation-master-workflow.md` for lifecycle accuracy

---

## Quick Reference Card

| Question | Answer |
|----------|--------|
| When to create RTM? | Stage 2 (Requirements Intake) |
| Req ID format? | FR-001, UI-001, NF-001 (PREFIX-NUMBER) |
| When to map requirements? | Stage 3 (Planning) |
| When to verify coverage? | Stage 5 (Verification) |
| Required coverage? | 100% (or descope with approval) |
| Where to document final RTM? | Stage 6 (QA Report § Requirements Coverage Matrix) |
| How to handle missing requirements? | BLOCK Stage 6, implement OR get descope approval |

---

> **NAVIGATION**: This guide is referenced by [Requirements Intake Template](requirements-intake-template.md), [Implementation Plan Template](implementation-plan-template.md), [Agent Verification Checklist](../quality/agent-verification-checklist.md), and [QA Report Template](../quality/qa-report-template.md).
