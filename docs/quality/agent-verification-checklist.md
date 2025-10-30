# Agent Verification Checklist

> **Purpose**: Enforce mandatory quality gates before delivering artefacts. Complete this checklist at the end of the execution phase.

## Usage Instructions

- Run these checks in the order listed.
- Capture command outputs or links to reports in the Evidence column.
- If a check fails, resolve the issue or document the blocker before proceeding.
- Refer back to `docs/guides/development-commands.md` for detailed command descriptions.

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
| Coverage threshold | `uv run pytest --cov=src --cov-report=html --cov-report=xml` | Coverage meets **level-specific threshold**:<br>• Level 1: ≥ 60%<br>• Level 2: ≥ 75%<br>• Level 3: ≥ 80%<br>• Level 4: ≥ 85%<br><br>**Reference**: See `docs/reference/maturity-levels.md` (SSOT) |  |  |
| Coverage artefacts | Inspect `htmlcov/`, `coverage.xml` | Reports generated |  |  |

**Note**: Coverage thresholds are defined in `docs/reference/maturity-levels.md` (Single Source of Truth). If thresholds change, update only maturity-levels.md; this document references it.

## Artefact Validation

| Check | Action | Expected Result | Evidence | Status |
|-------|--------|-----------------|----------|--------|
| Project structure compliance | Review against `docs/reference/project-structure.md` (§Creating the Project Structure)<br>Verify ALL directories created before file generation | • All `services/*/src/*` directories exist<br>• DDD layers present (`domain/`, `application/`, `infrastructure/`)<br>• `shared/` directory exists with subdirectories<br>• `tests/` subdirectories present (`unit/`, `integration/`)<br>• Conditional directories created per maturity level |  |  |
| Shared components usage | Confirm adherence to `docs/guides/shared_components.md` | No duplication or rule violations |  |  |
| Naming conventions | Spot-check against `docs/atomic/architecture/naming/README.md` | No prohibited names |  |  |
| Documentation updates | Ensure relevant docs updated (plans, ADRs, etc.) | Artefacts listed in `docs/reference/deliverables-catalog.md` |  |  |

## Release Gate

| Check | Action | Expected Result | Evidence | Status |
|-------|--------|-----------------|----------|--------|
| QA report | Draft using `docs/quality/qa-report-template.md` | Report ready for sign-off |  |  |
| Deliverables summary | Update per `docs/reference/deliverables-catalog.md` | Complete deliverable list |  |  |
| Outstanding issues | Record unresolved risks or follow-ups | Stakeholder notified |  |  |

## Failure Handling & Retry Policy

> **Purpose**: Define systematic approach to handling check failures, preventing infinite retry loops while ensuring quality gates are met.

### Retry Procedure

When any check fails, follow this structured retry process:

#### Step 1: Initial Failure Analysis

1. **Capture Failure Details**
   - Record exact error message
   - Identify which check failed (linting, type checking, tests, etc.)
   - Save relevant logs/output

2. **Attempt Fix #1** (Immediate)
   - **Analyze** error output
   - **Apply** most likely fix based on error message
   - **Document** what was changed
   - **Re-run** the failed check only

   **Example**:
   ```
   Failed Check: mypy type checking
   Error: "services/api/use_cases/loan.py:45: error: Argument 1 has incompatible type"

   Fix Applied: Add type annotation to function parameter
   Result: Re-run `uv run mypy .`
   ```

#### Step 2: Troubleshooting Consultation (if Attempt #1 fails)

3. **Attempt Fix #2** (Guided)
   - **Consult** `docs/reference/troubleshooting.md` for symptom
   - **Read** relevant atomic documentation (e.g., `docs/atomic/testing/unit-testing/pytest-setup.md`)
   - **Apply** recommended fix from documentation
   - **Document** fix attempt
   - **Re-run** check

   **Example**:
   ```
   Failed Check: pytest tests
   Error: "FAILED tests/test_loan.py::test_create_loan - AssertionError"

   Troubleshooting: Checked troubleshooting.md → "Mock HTTP client not configured"
   Fix Applied: Added pytest fixture for PostgresHTTPClient mock
   Result: Re-run `uv run pytest tests/test_loan.py`
   ```

#### Step 3: Alternative Approach (if Attempt #2 fails)

4. **Attempt Fix #3** (Creative)
   - **Try alternative solution** (e.g., different implementation approach)
   - **Verify** fix doesn't break other checks
   - **Document** rationale for alternative approach
   - **Re-run** all checks (not just failed one)

   **Example**:
   ```
   Failed Check: coverage threshold (78% < 80% required for Level 3)

   Attempts:
   1. Added more unit tests → 79% (still insufficient)
   2. Added integration tests → 79.5% (still insufficient)
   3. Identified untested error paths, added error case tests → 82% ✅

   Result: Coverage threshold met
   ```

#### Step 4: Escalation (if Attempt #3 fails)

5. **Max Retries Reached** (3 attempts per check)
   - **STOP** automated retry attempts
   - **Document failure** in QA report with full diagnostic information:
     ```markdown
     ## ⚠️ Quality Gate Failure

     **Failed Check**: [Check name]
     **Status**: Unresolved after 3 fix attempts

     **Error Details**:
     ```
     [Full error message and logs]
     ```

     **Attempted Fixes**:
     1. [Attempt 1 description] → Result: [outcome]
     2. [Attempt 2 description] → Result: [outcome]
     3. [Attempt 3 description] → Result: [outcome]

     **Diagnostic Information**:
     • Environment: Python 3.12.1, UV 0.1.5
     • Affected files: [list]
     • Related checks: [any other failing checks]

     **Suggested Next Steps**:
     • [AI's analysis of root cause]
     • [Recommended actions for human developer]
     • [Alternative approaches to consider]

     **User Decision Required**:
     Cannot proceed to Stage 6 (QA Report & Handoff) without resolving this issue
     or obtaining explicit stakeholder sign-off on this deviation.
     ```

   - **Notify user** with actionable diagnostic info
   - **WAIT** for user guidance (one of):
     - User fixes issue manually → AI re-runs verification
     - User approves deviation → AI documents exception in QA report → proceed to Stage 6
     - User cancels workflow → AI terminates gracefully

### Retry Limits by Check Type

| Check Type | Max Retries | Escalation Trigger |
|------------|-------------|-------------------|
| Linting (Ruff) | 3 | Code style issues persist after automated fixes |
| Formatting (Ruff) | 2 | Format conflicts (rare, should auto-fix) |
| Type Checking (Mypy) | 3 | Type inference issues, complex generics |
| Security Scan (Bandit) | 3 | High severity findings remain after mitigation attempts |
| Unit Tests | 3 | Test logic errors, environment issues |
| Integration Tests | 3 | Testcontainer setup issues, flaky tests |
| Coverage Threshold | 3 | Cannot reach required % after adding tests |
| Artifact Validation | 2 | Structural issues, missing files |

### Special Cases

#### Flaky Tests

If a test passes on retry without code changes:
- **Mark as flaky** in QA report
- **Document intermittent failure** for investigation
- **DO NOT** count toward retry limit (not a real failure)
- **Suggest** adding retry logic or test stability improvements

#### Environment Issues

If failure is due to environment (e.g., Docker not running, missing dependencies):
- **Provide clear diagnostic**: "Docker daemon not running. Start with: `sudo systemctl start docker`"
- **DO NOT** count toward retry limit
- **Wait** for user to fix environment
- **Re-run** check once environment is ready

#### Blocker Bugs in Dependencies

If failure is due to bug in external library:
- **Document** the external bug (version, issue tracker link if available)
- **Suggest** workaround or version downgrade
- **Escalate** immediately (no retries, external issue)
- **User decides**: wait for fix, use workaround, or accept deviation

### Preventing Infinite Loops

**Hard Limits**:
- Maximum 3 retry attempts per individual check
- Maximum 10 total fix attempts across all checks in Stage 5
- If 10th fix attempt reached → **FORCE ESCALATION** to user

**Example Scenario**:
```
Check Results:
• Ruff: PASS
• Mypy: FAIL (attempted 3 fixes, still failing)
• Pytest: FAIL (attempted 3 fixes, still failing)
• Bandit: PASS
• Coverage: FAIL (attempted 2 fixes, still failing)

Total fix attempts: 3 + 3 + 2 = 8
Action: Continue with remaining checks, but escalate if total reaches 10
```

### Successful Resolution Criteria

Stage 5 verification is considered **COMPLETE** when:
- ✅ **ALL** checks pass (preferred outcome)
- ✅ **OR** User explicitly approves deviations for failed checks (documented exception)
- ✅ Coverage meets level-specific threshold (60%/75%/80%/85% per `docs/reference/maturity-levels.md`)

### Escalation Output Template

When escalating to user, provide structured output:

```markdown
## 🔴 Stage 5 Verification: Manual Intervention Required

**Summary**: X out of Y checks failed after exhausting automated retry attempts.

**Failed Checks** (details below):
1. [Check name] - [brief error description]
2. [Check name] - [brief error description]

---

### Failed Check #1: [Check Name]

**Status**: ❌ Failed after 3 fix attempts
**Impact**: [Blocker/Warning/Minor]

**Error Message**:
```
[Exact error output]
```

**Fix Attempts**:
| Attempt | Action Taken | Outcome | Logs |
|---------|-------------|---------|------|
| 1 | [Description] | Still failing | [Link/snippet] |
| 2 | [Description] | Still failing | [Link/snippet] |
| 3 | [Description] | Still failing | [Link/snippet] |

**Root Cause Analysis**:
[AI's analysis of why this is failing]

**Recommended Actions** (choose one):
- [ ] Option A: [Suggested fix with steps]
- [ ] Option B: [Alternative approach]
- [ ] Option C: Approve deviation (proceed with known issue)

**Next Steps**:
Please choose an action above, or provide alternative guidance.

---

[Repeat for each failed check]

---

**Workflow Status**: ⏸️ PAUSED at Stage 5 (Verification)
**Next Stage**: Cannot proceed to Stage 6 until checks pass or deviations approved
```

### Integration with Workflow

- This retry policy applies **only** to Stage 5 (Quality Verification)
- After 3 failed attempts or user escalation → workflow PAUSES
- User decision required to proceed or terminate
- If user approves deviations → document in QA report → proceed to Stage 6
- If user provides fix → re-run Stage 5 from beginning

---

## Original Failure Handling Notes

- If any check fails, consult `docs/reference/troubleshooting.md` and rerun the step.
- Document persistent issues in the QA report and notify stakeholders.
- Do not proceed to release without explicit sign-off on known deviations.

## Maintenance

- Align commands with `docs/guides/development-commands.md` if they change.
- Keep coverage targets synchronized with `docs/atomic/testing/`.
- Update link references in `docs/reference/agent-context-summary.md` and `docs/INDEX.md` when modifying this checklist.
