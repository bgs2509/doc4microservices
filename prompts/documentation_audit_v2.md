# Documentation Audit Prompt Template

## Purpose

This prompt helps AI agents conduct comprehensive documentation audits to identify and fix structural, consistency, and content issues.

---

## 🔴 EXECUTION PROTOCOL (MANDATORY)

**READ THIS SECTION FIRST BEFORE STARTING ANY AUDIT WORK**

### Critical Execution Rules

1. **DO NOT DELEGATE** this audit to Task agent or any other agent
   - You MUST run ALL validation commands yourself using Bash tool
   - Task agents may interpret "comprehensive" as "sample-based checking"
   - Only direct execution ensures exhaustive validation (checking ALL files, not just samples)
   
2. **READ ENTIRE TEMPLATE** before starting
   - Don't skip to OBJECTIVES and start immediately
   - Read through Automation Script Template section (appears later in this document)
   - Understand the full scope: 14 objectives, validation commands, verification protocol

3. **RUN SMOKE TESTS FIRST** (30 seconds) before deep audit
   - Understand documentation scope and identify critical issues quickly
   - See "Smoke Tests" section below

4. **EXECUTE validation commands** sequentially for each objective
   - Don't just READ objectives - RUN the bash commands provided
   - Each objective has "VALIDATION COMMANDS" section with exact commands to execute
   - Record outputs and analyze results

5. **VERIFY your audit results** with spot checks
   - Pick 3 random issues from your findings
   - Manually verify each one is real (not false positive)
   - Include verification results in your report

### 🧪 Smoke Tests (Run First - 30 Seconds)

**Purpose:** Quick assessment of documentation health to identify critical issues before full audit.

```bash
# ===================================================================
# SMOKE TEST 1: Count total markdown files
# ===================================================================
echo "=== SMOKE TEST 1: Total Markdown Files ==="
find docs -name "*.md" 2>/dev/null | wc -l
# Expected: ~150-250 files
# If < 50 or > 500 → investigate scope

# ===================================================================
# SMOKE TEST 2: Count total markdown links
# ===================================================================
echo "=== SMOKE TEST 2: Total Markdown Links ==="
grep -rho '\[.*\](.*\.md' docs/ 2>/dev/null | wc -l
# Expected: ~500-1500 links
# This gives you scope of link validation task

# ===================================================================
# SMOKE TEST 3: 🚨 CRITICAL - Check legacy/deprecated references
# ===================================================================
echo "=== SMOKE TEST 3: Legacy/Deprecated References (MUST BE 0) ==="
grep -rn "docs/legacy\|/legacy/\|deprecated\|old-docs\|DEPRECATED" docs/ README.md CLAUDE.md 2>/dev/null | wc -l
# Expected: 0
# If > 0 → CRITICAL ISSUE (blocks users/AI agents)

# ===================================================================
# SMOKE TEST 4: Quick sample of broken links (first 10 files only)
# ===================================================================
echo "=== SMOKE TEST 4: Broken Links Sample (first 10 files) ==="
find docs -name "*.md" | head -10 | while read f; do
  grep -Hn '\[.*\](.*\.md' "$f" 2>/dev/null | while IFS=: read -r file line link; do
    path=$(echo "$link" | sed 's/.*(\(.*\.md\).*/\1/')
    [ ! -f "$path" ] && [ ! -f "docs/$path" ] && echo "BROKEN SAMPLE: $file:$line -> $path"
  done
done | head -5
# Expected: 0 broken links
# If > 0 → indicates systemic link problems (need full validation)

# ===================================================================
# SMOKE TEST 5: Check Stage 0 initialization docs exist
# ===================================================================
echo "=== SMOKE TEST 5: Stage 0 Documents (Critical for AI) ==="
for doc in CLAUDE.md \
           docs/reference/agent-context-summary.md \
           docs/guides/ai-code-generation-master-workflow.md \
           docs/reference/maturity-levels.md; do
  if [ -f "$doc" ]; then
    echo "✅ $doc"
  else
    echo "🚨 CRITICAL MISSING: $doc"
  fi
done
```

**DECISION POINT based on smoke test results:**

| Smoke Test | Result | Action |
|------------|--------|--------|
| Test 3 (Legacy refs) | > 0 | **STOP. CRITICAL ISSUE FOUND.** Report immediately, must fix before proceeding. |
| Test 4 (Broken links sample) | > 0 | **HIGH PRIORITY.** Note in report, proceed with full link validation. |
| Test 5 (Stage 0 docs) | Any missing | **CRITICAL.** AI agents cannot work. Report immediately. |
| All tests pass | ✅ | Proceed with full 14-objective audit. |

### ⚠️ Anti-Patterns to Avoid

| ❌ DON'T DO THIS | ✅ DO THIS INSTEAD |
|------------------|-------------------|
| Delegate entire audit to Task agent | Run validation commands yourself using Bash tool |
| Check 10 sample files and extrapolate to all | Use `grep -r` and `find` to check ALL files exhaustively |
| Assume "Related Documents" sections are optional metadata | Explicitly grep for `"legacy\|deprecated"` in all sections |
| Trust "Stage 0 works → everything works" heuristic | Run exhaustive validation (check all 1000+ links individually) |
| Skip Automation Script Template section | Read entire template including script examples |
| Report health score without showing calculation | Show exact formula: `100 - (CRITICAL×3) - (HIGH×1.5) - (MEDIUM×0.5)` |
| Say "several files have issues" (vague) | Provide exact `file:line` locations for EVERY issue |

---

## Full Audit Prompt

```
Conduct a comprehensive documentation audit of this project:

## OBJECTIVES

[Original 14 objectives content will follow, enhanced with VALIDATION COMMANDS sections]
```


## OBJECTIVES

### 1. Understand Project Purpose
   - Read README.md, CLAUDE.md, and docs/INDEX.md
   - Identify main project goals and target users
   - Understand architecture and technology stack

### 2. Link Validation ⚡ MANDATORY COMMANDS

**OBJECTIVE:** Find ALL broken markdown links, including legacy/deprecated references

**VALIDATION COMMANDS** (execute in order, do NOT skip):

```bash
# ========================================
# STEP 1: Check legacy/deprecated refs (CRITICAL)
# ========================================
echo "Step 1: Checking for legacy/deprecated references..."
grep -rn "docs/legacy\|/legacy/\|deprecated\|old-\|DEPRECATED" docs/ README.md CLAUDE.md 2>/dev/null > /tmp/legacy_refs.txt

LEGACY_COUNT=$(wc -l < /tmp/legacy_refs.txt)
echo "Found $LEGACY_COUNT legacy references"

if [ "$LEGACY_COUNT" -gt 0 ]; then
  echo "🚨 CRITICAL: Legacy references found!"
  head -20 /tmp/legacy_refs.txt  # Show first 20
fi

# ========================================
# STEP 2: Extract ALL markdown links
# ========================================
echo "Step 2: Extracting all markdown links..."
grep -rn '\[.*\](.*\.md' docs/ README.md CLAUDE.md 2>/dev/null > /tmp/all_links.txt

TOTAL_LINKS=$(wc -l < /tmp/all_links.txt)
echo "Found $TOTAL_LINKS total markdown links"

# ========================================
# STEP 3: Check each link's target file exists
# ========================================
echo "Step 3: Validating link targets..."
> /tmp/broken_links.txt  # Clear file

grep -rho '\[.*\](.*\.md' docs/ 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | while read -r ref; do
  # Try: exact path, docs/ prefix, relative from docs/
  if [ ! -f "$ref" ] && [ ! -f "docs/$ref" ] && [ ! -f "$(dirname "docs")/$ref" ]; then
    # Find which files reference this broken link
    grep -l "$ref" docs/**/*.md 2>/dev/null | head -3 | while read -r file; do
      line=$(grep -n "$ref" "$file" | head -1 | cut -d: -f1)
      echo "BROKEN: $file:$line -> $ref" >> /tmp/broken_links.txt
    done
  fi
done

BROKEN_COUNT=$(wc -l < /tmp/broken_links.txt)
echo "Found $BROKEN_COUNT broken links"

if [ "$BROKEN_COUNT" -gt 0 ]; then
  echo "⚠️ HIGH PRIORITY: Broken links found!"
  head -30 /tmp/broken_links.txt  # Show first 30
fi

# ========================================
# SUMMARY
# ========================================
echo ""
echo "=== LINK VALIDATION SUMMARY ==="
echo "Total links: $TOTAL_LINKS"
echo "Legacy references: $LEGACY_COUNT (MUST BE 0)"
echo "Broken links: $BROKEN_COUNT (MUST BE 0)"
echo ""
```

**EXPECTED RESULTS:**
- Legacy references: **0** (if >0 → CRITICAL priority)
- Broken links: **0** (if >0 → HIGH priority)

**IF ISSUES FOUND:**

**Priority Assignment:**
- Legacy references: **CRITICAL** (blocks AI agents, confuses users)
- Broken links: **HIGH** (404 errors, navigation fails)
- Broken anchors: **MEDIUM** (UX degradation)

**Impact:**
- Users clicking links get 404 errors
- AI agents fail to navigate documentation
- Broken Stage 0 sequence blocks all AI generation

**Fix (example for legacy links):**
```bash
# Replace all legacy references (example):
sed -i 's|docs/legacy/services/fastapi_rules.md|docs/atomic/services/fastapi/basic-setup.md|g' docs/atomic/**/*.md
sed -i 's|docs/legacy/architecture/data-access-rules.md|docs/atomic/architecture/data-access-architecture.md|g' docs/atomic/**/*.md
```

**Verification:**
```bash
# After fix, re-run Step 1:
grep -rn "docs/legacy" docs/ | wc -l  # Should be 0
```

### 3. File Completeness
   - Find all file references in documentation
   - Verify each referenced file exists
   - Check for missing templates, configs, or resources
   - Identify orphaned documents not referenced anywhere

### 4. Structural Consistency
   - Verify directory structure matches PROJECT_STRUCTURE.md
   - Ensure all documents listed in INDEX.md exist
   - Validate LINKS_REFERENCE.md has correct paths
   - Check navigation consistency across guides

### 5. Content Quality
   - Find contradictions between documents
   - Identify outdated information or version mismatches
   - Detect duplicated content across files
   - Check naming convention consistency

### 6. Code & Configuration
   - Validate .env.example files
   - Check docker-compose configurations
   - Verify requirements.txt or pyproject.toml
   - Test sample code blocks where applicable
   - Run shellcheck on all bash examples
   - Validate Python code examples with pylint/flake8
   - If a required tool is unavailable, record the skipped check and suggest a manual alternative

### 7. Language & Readability
   - Check spelling with aspell/hunspell
   - Verify English-only content (no other languages)
   - Calculate readability scores (Flesch-Kincaid, SMOG)
   - Measure documentation complexity metrics
   - Check technical terminology consistency

### 8. Version Consistency
   - Extract all technology versions mentioned
   - Cross-reference with tech_stack.md
   - Identify version conflicts or mismatches
   - Check dependency compatibility matrix
   - Verify Docker image tags alignment

### 9. AI Navigation & Workflow Validation (NEW - Critical for AI-first framework)
   - Verify Stage 0 initialization sequence (CLAUDE.md → agent-context-summary.md → workflow → maturity-levels.md)
   - Validate Navigation Matrix accuracy (all referenced documents exist)
   - Check workflow coherence (entry/exit criteria alignment)
   - Detect circular dependencies in reading order
   - Ensure maturity levels integrated into workflow stages
   - Update the Stage 0 sequence to match the current repository structure before flagging inconsistencies

### 10. Submodule Path Validation (NEW - Framework-as-submodule model)
   - Ensure documentation works in standalone and submodule modes
   - Detect hardcoded absolute paths that break in submodule
   - Verify examples show both path variants where relevant
   - Check CLAUDE.md guidance mentions both usage modes

### 11. Maturity Levels Consistency (NEW - Core framework concept)
   - Verify features correctly marked per maturity level (✅/❌)
   - Ensure conditional stage rules align with maturity-levels.md
   - Check upgrade paths documented
   - Validate time estimates consistency (5/10/15/30 min)
   - Verify coverage thresholds per level (60%/75%/80%/85%)

### 12. Architectural Constraints Consistency (NEW - Mandatory patterns)
   - Verify HTTP-only data access mentioned consistently
   - Check service separation principles in examples
   - Ensure API Gateway mandatory for production (Level 3+)
   - Validate RabbitMQ mandatory for async communication
   - Check DEFAULT TO 3-PART naming guidance consistency

### 13. Atomic Documentation Coverage (NEW - Implementation patterns)
   - Verify all atomic docs referenced in Navigation Matrix exist
   - Check atomic docs cover all patterns mentioned in workflow
   - Find orphaned atomic docs (not referenced anywhere)
   - Validate atomic docs completeness per service type

### 14. Agent Toolbox Command Validation (NEW - Executable commands)
   - Verify all commands in agent-toolbox.md are executable
   - Check tool versions align with tech_stack.md
   - Ensure development-commands.md consistent with agent-toolbox.md
   - Test sample commands for syntax correctness


## DELIVERABLES (ENHANCED)

Create a detailed report with:

### 1. Executive Summary (MANDATORY FORMAT - SHOW YOUR WORK)

#### Project Purpose
[1-2 paragraphs describing project goals and target users]

#### Health Score Calculation (MUST SHOW CALCULATION)

**Formula:**
```
Health Score = 100 - (CRITICAL_count × 3) - (HIGH_count × 1.5) - (MEDIUM_count × 0.5) - (LOW_count × 0.1)
Min score: 0 (cap negative scores at 0)
```

**Calculation (SHOW THIS IN YOUR REPORT):**
```
Base:                    100 points
CRITICAL issues (X):     X × 3  = -Y points
HIGH issues (Z):         Z × 1.5 = -W points
MEDIUM issues (M):       M × 0.5 = -N points
LOW issues (L):          L × 0.1 = -K points
─────────────────────────────────
FINAL HEALTH SCORE:      max(0, 100 - Y - W - N - K) = SCORE/100
```

Example:
```
Base:                    100 points
CRITICAL issues (64):    64 × 3  = -192 points
HIGH issues (10):        10 × 1.5 = -15 points
MEDIUM issues (5):       5 × 0.5 = -2.5 points
LOW issues (2):          2 × 0.1 = -0.2 points
─────────────────────────────────
Subtotal:                100 - 209.7 = -109.7
FINAL HEALTH SCORE:      max(0, -109.7) = 0/100 (capped at 0)
```

#### Total Issues Found (MANDATORY TABLE)

| Priority | Count | Top 3 Examples (file:line) | Impact |
|----------|-------|---------------------------|--------|
| **CRITICAL** | X | `docs/foo.md:42`, `docs/bar.md:15`, `docs/baz.md:88` | Blocks AI/users |
| **HIGH** | Y | `docs/qux.md:23`, ... | Affects quality |
| **MEDIUM** | Z | `docs/lorem.md:67`, ... | Usability issues |
| **LOW** | W | `docs/ipsum.md:89`, ... | Minor improvements |
| **TOTAL** | X+Y+Z+W | | |

#### Top 3 Critical Issues (MANDATORY DETAILED FORMAT)

For EACH critical issue, provide this exact format:

**CRITICAL-01: [Brief one-line description]**

- **Priority**: CRITICAL
- **Location**: `docs/atomic/architecture/data-access-architecture.md:66` (exact file:line)
- **Description**: Legacy reference to non-existent file `docs/legacy/architecture/data-access-rules.md`
- **Impact**: 
  - Users clicking link get 404 error
  - AI agents attempting to read referenced doc fail
  - Breaks documentation navigation flow
- **How Found**: 
  ```bash
  grep -rn "docs/legacy" docs/atomic/architecture/data-access-architecture.md
  # Output: 66:- Legacy reference: `docs/legacy/architecture/data-access-rules.mdc`
  ```
- **Fix**: 
  ```bash
  sed -i 's|docs/legacy/architecture/data-access-rules.md|docs/atomic/architecture/data-access-architecture.md|g' \
    docs/atomic/architecture/data-access-architecture.md
  ```
- **Verification**: 
  ```bash
  grep -n "docs/legacy" docs/atomic/architecture/data-access-architecture.md
  # Expected output: (nothing - line should be removed/fixed)
  ```

[Repeat exact format for CRITICAL-02, CRITICAL-03]

#### Validation Commands Used (PROOF OF WORK - MANDATORY)

**Smoke tests executed:**
```bash
1. find docs -name "*.md" | wc -l
   Result: 200 markdown files found

2. grep -rho '\[.*\](.*\.md' docs/ | wc -l
   Result: 1247 total markdown links found

3. grep -rn "docs/legacy\|deprecated" docs/ | wc -l
   Result: 64 legacy references found (CRITICAL ISSUE)

4. Broken links sample (first 10 files):
   Result: 5 broken links found in sample → indicates systemic problem
```

**Full validation commands executed:**
```bash
# For Objective 2 (Link Validation):
5. grep -rn "docs/legacy" docs/ > /tmp/legacy_refs.txt
   Result: 64 legacy references (see /tmp/legacy_refs.txt)

6. grep -rho '\[.*\](.*\.md' docs/ | sed 's/.*(\(.*\.md\).*/\1/' | sort -u > /tmp/unique_refs.txt
   Result: 487 unique file references

7. [List OTHER commands you actually executed]
   Result: [actual results]
```

**Spot checks performed (MANDATORY - verify 3+ random issues):**
```bash
# Spot Check 1: Verify docs/atomic/architecture/data-access-architecture.md:66
Command: sed -n '66p' docs/atomic/architecture/data-access-architecture.md
Output: "- Legacy reference: `docs/legacy/architecture/data-access-rules.mdc`"
Verified: ✅ Issue is real (legacy link exists at line 66)

# Spot Check 2: Verify target file doesn't exist
Command: ls docs/legacy/architecture/data-access-rules.md 2>&1
Output: "No such file or directory"
Verified: ✅ Target file does not exist (404 error for users)

# Spot Check 3: [third random issue verification]
Command: [command used]
Output: [actual output]
Verified: ✅ / ❌ [result]
```

### 2. Issue Categories

[Original issue categories from template, keeping them as-is since they're already good]

#### Link & Reference Issues
- Broken internal links
- Invalid anchor references
- Missing referenced files
- **Legacy/deprecated references** (NEW - highest priority)

#### Content Quality Issues
- Spelling errors with corrections
- Duplicate content locations
- Contradictory information

[... rest of original issue categories ...]

For each issue, provide:
- **Priority**: CRITICAL / HIGH / MEDIUM / LOW
- **Location**: Exact file:line (e.g., `docs/path/file.md:123`)
- **Description**: What's broken and why it matters
- **Impact**: How it affects users/AI agents
- **Fix**: Exact bash commands or changes needed (not "update the files" - give EXACT commands)
- **Verification**: Exact bash command to verify fix worked

### 3. TODO List

Organize fixes into phases:
- **Phase 1: Quick Fixes** (< 1 hour) - Critical broken links, legacy refs, typos
- **Phase 2: Content Updates** (1-4 hours) - Missing docs, inconsistencies
- **Phase 3: Structural** (> 4 hours) - Architecture changes, major rewrites

For each task:
- Estimated time
- Priority level
- Dependencies (what must be done first)
- Exact validation command

### 4. Validation Commands

Provide bash commands to:
- Check all markdown links
- Verify file existence
- Test anchor links
- Compare expected vs actual structure

### 5. What's Working Well

Highlight positive findings:
- Good structure and organization
- Consistent patterns
- Comprehensive coverage
- Well-maintained areas

### 6. Recommendations

- Immediate (this week)
- Short-term (this month)
- Long-term (when needed)
- CI/CD automation suggestions


---

## OUTPUT FORMAT

### Structure Requirements

1. **Use Markdown** with clear section hierarchy
2. **Code blocks** with syntax highlighting (```bash, ```python, etc.)
3. **File paths** format: `/path/to/file.md:123` (clickable in most IDEs)
4. **Tables** for large datasets (issue lists, file inventories)
5. **Command examples** showing exact fix commands with expected output

### Example Output Structure

```markdown
## Critical Issues (Priority: CRITICAL)

### Issue 1: Broken Legacy Reference

**File**: `docs/atomic/architecture/data-access-architecture.md:66`  
**Problem**: Reference to non-existent `docs/legacy/architecture/data-access-rules.md`  
**Impact**: Blocks users/AI agents trying to find data access rules  
**Category**: Link Validation

**How Found**:
```bash
grep -rn "docs/legacy" docs/atomic/architecture/data-access-architecture.md
```

**Fix Command**:
```bash
sed -i 's|docs/legacy/architecture/data-access-rules.md|docs/atomic/architecture/data-access-architecture.md|g' \
  docs/atomic/architecture/data-access-architecture.md
```

**Verification**:
```bash
grep -n "docs/legacy" docs/atomic/architecture/data-access-architecture.md
# Expected: no output (issue fixed)
```
```

---

## CONSTRAINTS ⚡ MANDATORY

### Execution Constraints

1. **DO NOT delegate this audit to Task agent**
   - You MUST execute all validation commands yourself using Bash tool
   - Delegation leads to incomplete audits (proven failure mode)

2. **DO NOT use sample-based checking**
   - Check ALL files, not 10% with extrapolation
   - Use `find`, `grep -r`, `xargs -P` for exhaustive scans

3. **DO NOT skip smoke tests**
   - Run all 5 smoke tests before full audit
   - If any smoke test shows critical issues, report immediately

4. **DO NOT estimate health score**
   - Calculate using exact formula: `100 - (CRITICAL×3) - (HIGH×1.5) - (MEDIUM×0.5) - (LOW×0.1)`
   - Show calculation in report

5. **DO NOT trust "Related Documents" sections without verification**
   - These are NOT optional metadata
   - Users/AI agents click these links expecting valid targets
   - Broken "Related Documents" = CRITICAL issue

### Reporting Constraints

1. **MUST show validation commands used** (proof of work)
2. **MUST perform 3+ spot checks** to verify issues are real
3. **MUST include fix commands** for each issue (not just descriptions)
4. **MUST include verification commands** showing how to confirm fix worked
5. **MUST report file:line locations** for all issues (not just filenames)

### Quality Constraints

1. **Accuracy > Speed**: Better to take 10 minutes and find all issues than 2 minutes with 50% false negatives
2. **Explicit > Implicit**: Show commands, outputs, calculations
3. **Reproducible**: Any human/AI should be able to run your commands and get same results
4. **Actionable**: Every issue should have clear fix command

---

## VERIFICATION PROTOCOL ⚡ MANDATORY

After completing the audit, perform these self-checks:

### Automated Verification

```bash
# Check 1: Did you run smoke tests?
grep -q "SMOKE TEST" /tmp/audit_output.md
echo "Smoke tests documented: $?"  # Expected: 0 (yes)

# Check 2: Did you show health score calculation?
grep -q "100 - (CRITICAL" /tmp/audit_output.md
echo "Health score formula shown: $?"  # Expected: 0 (yes)

# Check 3: Did you perform spot checks?
grep -c "Spot Check" /tmp/audit_output.md
# Expected: >= 3

# Check 4: Are all issues tagged with severity?
ISSUES=$(grep -c "^### Issue" /tmp/audit_output.md)
SEVERITIES=$(grep -c "Priority: \(CRITICAL\|HIGH\|MEDIUM\|LOW\)" /tmp/audit_output.md)
echo "Issues: $ISSUES, Tagged: $SEVERITIES"  # Should match

# Check 5: Do all issues have fix commands?
FIX_COMMANDS=$(grep -c "**Fix Command**:" /tmp/audit_output.md)
echo "Issues with fixes: $ISSUES/$FIX_COMMANDS"  # Should match
```

### Manual Spot Checks (Pick 3 Random Issues)

For each spot check:

1. **Copy the "How Found" command** → Run it yourself
2. **Verify the issue exists** at reported file:line
3. **Copy the "Fix Command"** → Run it in test environment
4. **Copy the "Verification Command"** → Confirm fix works
5. **Document result** in audit report

**Example Spot Check Documentation**:

```markdown
#### Spot Check 1: Legacy Reference Verification

**Issue**: docs/atomic/architecture/data-access-architecture.md:66 references non-existent legacy file

**Command Run**:
```bash
sed -n '66p' docs/atomic/architecture/data-access-architecture.md
```

**Output**:
```
- Legacy reference: `docs/legacy/architecture/data-access-rules.md`
```

**Verification**: ✅ Issue confirmed - line 66 contains broken legacy reference

**Fix Tested**: ✅ sed replacement works, file updated correctly
```

### Self-Audit Checklist

Before submitting audit report, confirm:

- [ ] All 5 smoke tests executed and documented
- [ ] Health score calculation shown with formula
- [ ] All validation commands listed (proof of work)
- [ ] 3+ spot checks performed and documented
- [ ] Every issue has: file:line, impact, category, how found, fix command, verification
- [ ] No delegation used (all commands run directly by you)
- [ ] Exhaustive checking used (not sample-based)
- [ ] "Related Documents" sections validated (not skipped)

**If ANY checklist item is unchecked → AUDIT IS INCOMPLETE**

---

## OBJECTIVES (Detailed)

### 1. Documentation Completeness

**Goal**: Ensure every required document exists and is accessible.

**Validation Commands**:

```bash
# Check critical Stage 0 documents
STAGE0_DOCS=(
  "CLAUDE.md"
  "docs/reference/agent-context-summary.md"
  "docs/guides/ai-code-generation-master-workflow.md"
  "docs/reference/maturity-levels.md"
)

for doc in "${STAGE0_DOCS[@]}"; do
  if [ -f "$doc" ]; then
    echo "✅ $doc"
  else
    echo "❌ MISSING (CRITICAL): $doc"
  fi
done

# Check all documents referenced in ai-navigation-matrix.md
grep -oP '\[.*?\]\(\K[^)]+\.md' docs/reference/ai-navigation-matrix.md | while read -r ref; do
  if [ -f "$ref" ] || [ -f "docs/$ref" ]; then
    echo "✅ $ref"
  else
    echo "❌ BROKEN REFERENCE: $ref (referenced in ai-navigation-matrix.md)"
  fi
done
```

**Expected Outcome**: List of missing/broken documents with severity ratings.

### 2. Link Validation ⚡ ALREADY DETAILED ABOVE

(See previous section with step-by-step validation commands)

### 3. Structural Consistency

**Goal**: Verify all documents follow framework structure patterns.

**Validation Commands**:

```bash
# Check atomic/* structure
EXPECTED_ATOMIC_DIRS=(
  "architecture"
  "databases"
  "infrastructure"
  "integrations"
  "observability"
  "services"
  "testing"
)

for dir in "${EXPECTED_ATOMIC_DIRS[@]}"; do
  if [ -d "docs/atomic/$dir" ]; then
    README_COUNT=$(find "docs/atomic/$dir" -name "README.md" | wc -l)
    echo "✅ docs/atomic/$dir exists (READMEs: $README_COUNT)"
  else
    echo "❌ MISSING: docs/atomic/$dir"
  fi
done

# Check service documentation completeness
for svc_dir in docs/atomic/services/*/; do
  svc_name=$(basename "$svc_dir")
  echo "=== Checking $svc_name ==="
  
  # Required files
  [ -f "$svc_dir/README.md" ] && echo "  ✅ README.md" || echo "  ❌ README.md"
  [ -f "$svc_dir/basic-setup.md" ] && echo "  ✅ basic-setup.md" || echo "  ⚠️  basic-setup.md"
  
  # Check for code examples
  if grep -q '```python\|```yaml\|```bash' "$svc_dir"/*.md 2>/dev/null; then
    echo "  ✅ Contains code examples"
  else
    echo "  ⚠️  No code examples found"
  fi
done
```

**Expected Outcome**: Structural consistency report with missing directories/files.

### 4. Content Quality

**Goal**: Validate code examples, check for TODOs, verify English language.

**Validation Commands**:

```bash
# Find TODO markers
grep -rn "TODO\|FIXME\|XXX\|HACK\|WIP" docs/ README.md CLAUDE.md 2>/dev/null > /tmp/todos.txt
TODO_COUNT=$(wc -l < /tmp/todos.txt)
echo "TODO markers found: $TODO_COUNT"
if [ $TODO_COUNT -gt 0 ]; then
  echo "⚠️  Incomplete documentation detected"
  head -10 /tmp/todos.txt
fi

# Validate Python code blocks
grep -rn '```python' docs/ | cut -d: -f1 | sort -u | while read -r file; do
  # Extract Python code blocks and validate syntax
  awk '/```python/,/```/' "$file" | grep -v '```' > /tmp/code_check.py
  if [ -s /tmp/code_check.py ]; then
    python3 -m py_compile /tmp/code_check.py 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "✅ $file - Python syntax valid"
    else
      echo "❌ $file - Python syntax errors"
    fi
  fi
done

# Validate bash code blocks
find docs/ -name "*.md" -exec grep -l '```bash' {} \; | while read -r file; do
  # Extract bash blocks and check with shellcheck (if available)
  if command -v shellcheck &>/dev/null; then
    awk '/```bash/,/```/' "$file" | grep -v '```' > /tmp/code_check.sh
    if [ -s /tmp/code_check.sh ]; then
      shellcheck /tmp/code_check.sh 2>/dev/null && echo "✅ $file - Bash valid" || echo "⚠️  $file - Bash warnings"
    fi
  fi
done

# Check for non-English content (basic heuristic)
grep -rn '[а-яА-ЯёЁ]' docs/ README.md CLAUDE.md 2>/dev/null > /tmp/non_english.txt
NON_ENGLISH=$(wc -l < /tmp/non_english.txt)
if [ $NON_ENGLISH -gt 0 ]; then
  echo "⚠️  Non-English content detected ($NON_ENGLISH instances)"
  head -5 /tmp/non_english.txt
fi
```

**Expected Outcome**: Content quality report with syntax errors, TODOs, language issues.

### 5. AI Navigation Integrity

**Goal**: Verify AI agents can navigate documentation per Master Workflow.

**Validation Commands**:

```bash
# Verify Stage 0 initialization sequence
echo "=== Verifying Stage 0 Initialization Sequence ==="

STAGE0_ORDER=(
  "CLAUDE.md"
  "docs/reference/agent-context-summary.md"
  "docs/guides/ai-code-generation-master-workflow.md"
  "docs/reference/maturity-levels.md"
)

for i in "${!STAGE0_ORDER[@]}"; do
  doc="${STAGE0_ORDER[$i]}"
  if [ -f "$doc" ]; then
    echo "Step $((i+1)): ✅ $doc"
    
    # Check file is readable and non-empty
    if [ ! -s "$doc" ]; then
      echo "  ❌ CRITICAL: File is empty"
    fi
    
    # Check Stage 0 documents reference each other correctly
    if [ $i -lt ${#STAGE0_ORDER[@]}-1 ]; then
      next_doc="${STAGE0_ORDER[$((i+1))]}"
      if grep -q "$next_doc" "$doc"; then
        echo "  ✅ References next document: $next_doc"
      else
        echo "  ⚠️  Does not reference next document: $next_doc"
      fi
    fi
  else
    echo "Step $((i+1)): ❌ CRITICAL - $doc MISSING"
  fi
done

# Verify ai-navigation-matrix.md completeness
if [ -f "docs/reference/ai-navigation-matrix.md" ]; then
  echo "=== Checking AI Navigation Matrix ==="
  
  # Check for all 7 stages
  for stage in {0..6}; do
    if grep -q "Stage $stage" docs/reference/ai-navigation-matrix.md; then
      echo "  ✅ Stage $stage documented"
    else
      echo "  ❌ Stage $stage missing"
    fi
  done
  
  # Check matrix has Required Docs, Outputs, Tools columns
  if grep -q "Required Documents\|Primary Documents\|Key Documents" docs/reference/ai-navigation-matrix.md; then
    echo "  ✅ Required Documents column present"
  else
    echo "  ⚠️  Required Documents column missing/unclear"
  fi
else
  echo "❌ CRITICAL: docs/reference/ai-navigation-matrix.md missing"
fi
```

**Expected Outcome**: AI navigation integrity report with broken Stage 0 sequence or matrix issues.

### 6. Maturity Level Coverage

**Goal**: Ensure all 4 maturity levels are documented with clear guidance.

**Validation Commands**:

```bash
# Check maturity-levels.md completeness
if [ -f "docs/reference/maturity-levels.md" ]; then
  echo "=== Checking Maturity Levels Documentation ==="
  
  LEVELS=("Level 1" "Level 2" "Level 3" "Level 4")
  KEYWORDS=("PoC" "Development" "Pre-Production" "Production")
  
  for i in "${!LEVELS[@]}"; do
    level="${LEVELS[$i]}"
    keyword="${KEYWORDS[$i]}"
    
    if grep -qi "$level.*$keyword\|$keyword.*$level" docs/reference/maturity-levels.md; then
      echo "  ✅ $level ($keyword) documented"
    else
      echo "  ❌ $level ($keyword) missing or unclear"
    fi
  done
  
  # Check for time estimates
  if grep -E "~?[0-9]+\s*(min|minute)" docs/reference/maturity-levels.md | grep -q .; then
    echo "  ✅ Time estimates present"
  else
    echo "  ⚠️  Time estimates missing"
  fi
  
  # Check for quality criteria differences
  if grep -qi "quality.*criteria\|quality.*gate\|testing.*requirement" docs/reference/maturity-levels.md; then
    echo "  ✅ Quality criteria documented"
  else
    echo "  ⚠️  Quality criteria not clearly documented"
  fi
else
  echo "❌ CRITICAL: docs/reference/maturity-levels.md missing"
fi

# Check conditional-stage-rules.md
if [ -f "docs/reference/conditional-stage-rules.md" ]; then
  echo "=== Checking Conditional Stage Rules ==="
  
  # Verify rules exist for each level
  for level in {1..4}; do
    if grep -q "Level $level" docs/reference/conditional-stage-rules.md; then
      echo "  ✅ Level $level rules present"
    else
      echo "  ⚠️  Level $level rules missing"
    fi
  done
else
  echo "⚠️  docs/reference/conditional-stage-rules.md missing (optional but recommended)"
fi
```

**Expected Outcome**: Maturity level coverage report with missing guidance or inconsistencies.

### 7. Architecture Constraint Visibility

**Goal**: Ensure mandatory constraints are clear and discoverable.

**Validation Commands**:

```bash
# Check architecture-guide.md for mandatory constraints
if [ -f "docs/guides/architecture-guide.md" ]; then
  echo "=== Checking Architecture Constraints ==="
  
  CONSTRAINTS=(
    "HTTP-only data access"
    "Service separation"
    "Nginx.*gateway.*mandatory\|API gateway.*mandatory"
    "RabbitMQ.*mandatory"
    "3-part naming"
  )
  
  for constraint in "${CONSTRAINTS[@]}"; do
    if grep -qi "$constraint" docs/guides/architecture-guide.md; then
      echo "  ✅ Constraint documented: $constraint"
    else
      echo "  ⚠️  Constraint unclear: $constraint"
    fi
  done
  
  # Check if constraints are marked as MANDATORY
  MANDATORY_COUNT=$(grep -ci "MANDATORY\|REQUIRED\|MUST" docs/guides/architecture-guide.md)
  echo "  ℹ️  'MANDATORY/REQUIRED/MUST' mentions: $MANDATORY_COUNT"
else
  echo "❌ CRITICAL: docs/guides/architecture-guide.md missing"
fi

# Check service-separation-principles.md
if [ -f "docs/atomic/architecture/service-separation-principles.md" ]; then
  echo "  ✅ Service separation principles documented"
else
  echo "  ⚠️  docs/atomic/architecture/service-separation-principles.md missing"
fi

# Check data-access-architecture.md
if [ -f "docs/atomic/architecture/data-access-architecture.md" ]; then
  echo "  ✅ Data access architecture documented"
  
  # Verify no legacy references (critical for this file)
  if grep -qi "docs/legacy\|deprecated" docs/atomic/architecture/data-access-architecture.md; then
    echo "  ❌ CRITICAL: Contains legacy/deprecated references"
  fi
else
  echo "  ⚠️  docs/atomic/architecture/data-access-architecture.md missing"
fi
```

**Expected Outcome**: Architecture constraint visibility report.

### 8. Naming Convention Clarity

**Goal**: Verify naming conventions (3-part vs 4-part) are clear and unambiguous.

**Validation Commands**:

```bash
# Check naming convention documentation
echo "=== Checking Naming Conventions ==="

# Primary naming docs
if [ -f "docs/atomic/architecture/naming/README.md" ]; then
  echo "✅ Main naming guide exists"
  
  # Check for 3-part default guidance
  if grep -qi "default.*3-part\|3-part.*default" docs/atomic/architecture/naming/README.md; then
    echo "  ✅ 3-part default clearly stated"
  else
    echo "  ⚠️  3-part default not clearly stated"
  fi
  
  # Check for 4-part guidance
  if grep -qi "4-part.*when\|when.*4-part\|4-part.*only" docs/atomic/architecture/naming/README.md; then
    echo "  ✅ 4-part usage guidance present"
  else
    echo "  ⚠️  4-part usage guidance unclear"
  fi
else
  echo "❌ docs/atomic/architecture/naming/README.md missing"
fi

# Check service-naming-checklist.md
if [ -f "docs/checklists/service-naming-checklist.md" ]; then
  echo "✅ Service naming checklist exists"
else
  echo "⚠️  docs/checklists/service-naming-checklist.md missing"
fi

# Check 10 reasons doc
if [ -f "docs/atomic/architecture/naming/naming-4part-reasons.md" ]; then
  echo "✅ 4-part naming reasons documented"
  
  # Verify it actually has ~10 reasons
  REASON_COUNT=$(grep -c "^###\s*[0-9]" docs/atomic/architecture/naming/naming-4part-reasons.md)
  echo "  ℹ️  Number of reasons found: $REASON_COUNT"
  if [ $REASON_COUNT -lt 8 ]; then
    echo "  ⚠️  Expected ~10 reasons, found $REASON_COUNT"
  fi
else
  echo "⚠️  docs/atomic/architecture/naming/naming-4part-reasons.md missing"
fi

# Check template naming guide
if [ -f "docs/guides/template-naming-guide.md" ]; then
  echo "✅ Template naming guide exists"
else
  echo "⚠️  docs/guides/template-naming-guide.md missing"
fi
```

**Expected Outcome**: Naming convention clarity report.

### 9. Template Completeness

**Goal**: Verify all promised service templates exist and are documented.

**Validation Commands**:

```bash
# Check for template services
echo "=== Checking Service Templates ==="

TEMPLATES=(
  "template_business_api"
  "template_business_bot"
  "template_business_worker"
  "template_data_postgres_api"
  "template_data_mongo_api"
)

for template in "${TEMPLATES[@]}"; do
  if [ -d "$template" ]; then
    echo "✅ $template/ directory exists"
    
    # Check for README
    if [ -f "$template/README.md" ]; then
      echo "  ✅ README.md present"
      
      # Check README has key sections
      if grep -qi "usage\|quick start\|getting started" "$template/README.md"; then
        echo "    ✅ Usage instructions present"
      else
        echo "    ⚠️  Usage instructions missing"
      fi
      
      if grep -qi "architecture\|structure" "$template/README.md"; then
        echo "    ✅ Architecture notes present"
      else
        echo "    ⚠️  Architecture notes missing"
      fi
    else
      echo "  ❌ README.md missing"
    fi
    
    # Check for pyproject.toml or package.json
    if [ -f "$template/pyproject.toml" ] || [ -f "$template/package.json" ]; then
      echo "  ✅ Dependency configuration present"
    else
      echo "  ⚠️  Dependency configuration missing"
    fi
  else
    echo "❌ $template/ directory missing"
  fi
done

# Check template documentation
if [ -f "docs/guides/template-naming-guide.md" ]; then
  # Verify guide mentions all templates
  for template in "${TEMPLATES[@]}"; do
    if grep -q "$template" docs/guides/template-naming-guide.md; then
      echo "  ✅ $template documented in guide"
    else
      echo "  ⚠️  $template not mentioned in guide"
    fi
  done
fi
```

**Expected Outcome**: Template completeness report with missing templates or documentation.

### 10. Development Workflow Documentation

**Goal**: Ensure development commands are clear and complete.

**Validation Commands**:

```bash
# Check development-commands.md
if [ -f "docs/guides/development-commands.md" ]; then
  echo "=== Checking Development Commands Documentation ==="
  
  COMMAND_CATEGORIES=(
    "setup\|install\|init"
    "test\|pytest"
    "lint\|ruff\|mypy"
    "format\|black\|isort"
    "security\|bandit"
    "coverage"
    "docker\|compose"
    "migration\|alembic"
  )
  
  for category in "${COMMAND_CATEGORIES[@]}"; do
    if grep -Eqi "$category" docs/guides/development-commands.md; then
      echo "  ✅ Category documented: $category"
    else
      echo "  ⚠️  Category missing/unclear: $category"
    fi
  done
  
  # Check for actual command examples
  CODE_BLOCK_COUNT=$(grep -c '```' docs/guides/development-commands.md)
  echo "  ℹ️  Code blocks found: $((CODE_BLOCK_COUNT / 2))"
  if [ $CODE_BLOCK_COUNT -lt 20 ]; then
    echo "  ⚠️  Few code examples (expected 10+ command blocks)"
  fi
else
  echo "❌ CRITICAL: docs/guides/development-commands.md missing"
fi

# Check agent-toolbox.md (machine-readable commands)
if [ -f "docs/reference/agent-toolbox.md" ]; then
  echo "✅ Agent toolbox exists (machine-readable commands)"
else
  echo "⚠️  docs/reference/agent-toolbox.md missing"
fi
```

**Expected Outcome**: Development workflow documentation completeness report.

### 11-14. Additional Objectives

(Infrastructure, testing, observability, shared components - follow same pattern as above with validation commands for each)

---

## QUICK AUDIT (5 Minutes)

For rapid health checks, run only smoke tests + critical validations:

```bash
#!/bin/bash
# Quick audit script (5 minutes max)

echo "=== QUICK DOCUMENTATION AUDIT ==="
echo "Started: $(date)"

# 1. Smoke Tests
echo -e "\n### SMOKE TESTS ###"

# Smoke 1: File counts
MD_COUNT=$(find docs/ -name "*.md" 2>/dev/null | wc -l)
echo "Markdown files: $MD_COUNT"

# Smoke 2: Link count
LINK_COUNT=$(grep -roh '\[.*\](.*\.md' docs/ 2>/dev/null | wc -l)
echo "Total links: $LINK_COUNT"

# Smoke 3: Legacy references (CRITICAL)
LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" docs/ README.md CLAUDE.md 2>/dev/null | wc -l)
echo "Legacy references: $LEGACY_COUNT"
if [ $LEGACY_COUNT -gt 0 ]; then
  echo "  🚨 CRITICAL: Found $LEGACY_COUNT legacy references"
fi

# Smoke 4: Broken link sample
echo "Sample broken links (first 3):"
grep -rho '\[.*\](.*\.md' docs/ 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | while read -r ref; do
  if [ ! -f "$ref" ] && [ ! -f "docs/$ref" ]; then
    echo "  ❌ $ref"
  fi
done | head -3

# Smoke 5: Stage 0 files
echo -e "\nStage 0 initialization files:"
for doc in "CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md"; do
  if [ -f "$doc" ]; then
    echo "  ✅ $doc"
  else
    echo "  ❌ $doc (CRITICAL)"
  fi
done

# 2. Critical Validations Only
echo -e "\n### CRITICAL VALIDATIONS ###"

# Check architecture guide exists
[ -f "docs/guides/architecture-guide.md" ] && echo "✅ Architecture guide" || echo "❌ Architecture guide (CRITICAL)"

# Check AI workflow exists
[ -f "docs/guides/ai-code-generation-master-workflow.md" ] && echo "✅ AI workflow" || echo "❌ AI workflow (CRITICAL)"

# Check navigation matrix
[ -f "docs/reference/ai-navigation-matrix.md" ] && echo "✅ Navigation matrix" || echo "❌ Navigation matrix (CRITICAL)"

echo -e "\nCompleted: $(date)"
echo -e "\n💡 Run full audit for detailed analysis: bash scripts/audit_docs.sh --full"
```

**Usage**:
```bash
bash scripts/quick_audit.sh
```

---

## FOCUSED AUDITS

### Audit Only Links

```bash
# Link-only audit
bash scripts/audit_docs.sh --links
```

### Audit Only Structure

```bash
# Structure-only audit
bash scripts/audit_docs.sh --structure
```

### Audit Only AI Navigation

```bash
# AI navigation audit
bash scripts/audit_docs.sh --ai-navigation
```

---

## AUTOMATION SCRIPT TEMPLATE

Create `scripts/audit_docs.sh` for reusable auditing:

```bash
#!/bin/bash

# scripts/audit_docs.sh - Comprehensive documentation audit automation
# Usage:
#   ./scripts/audit_docs.sh --full      # Full audit
#   ./scripts/audit_docs.sh --quick     # 5-minute audit
#   ./scripts/audit_docs.sh --links     # Link validation only
#   ./scripts/audit_docs.sh --structure # Structure validation only

set -euo pipefail

# Configuration
DOCS_DIR="docs"
OUTPUT_DIR="audit_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/audit_${TIMESTAMP}.md"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Logging helper
log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "$REPORT_FILE"
}

# Smoke tests function
run_smoke_tests() {
  log "=== SMOKE TESTS ==="
  
  log "Smoke 1: File counts"
  MD_COUNT=$(find "$DOCS_DIR" -name "*.md" 2>/dev/null | wc -l)
  log "  Markdown files: $MD_COUNT"
  
  log "Smoke 2: Link count"
  LINK_COUNT=$(grep -roh '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | wc -l)
  log "  Total links: $LINK_COUNT"
  
  log "Smoke 3: 🚨 Legacy references (CRITICAL)"
  LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | wc -l)
  log "  Legacy references: $LEGACY_COUNT"
  if [ "$LEGACY_COUNT" -gt 0 ]; then
    log "  🚨 CRITICAL: Found $LEGACY_COUNT legacy references"
    grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | head -10 | tee -a "$REPORT_FILE"
  fi
  
  log "Smoke 4: Broken link sample"
  BROKEN_SAMPLE=$(grep -rho '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | while read -r ref; do
    if [ ! -f "$ref" ] && [ ! -f "$DOCS_DIR/$ref" ]; then
      echo "  ❌ $ref"
    fi
  done | head -3)
  log "$BROKEN_SAMPLE"
  
  log "Smoke 5: Stage 0 files"
  for doc in "CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md"; do
    if [ -f "$doc" ]; then
      log "  ✅ $doc"
    else
      log "  ❌ $doc (CRITICAL)"
    fi
  done
}

# Link validation function
validate_links() {
  log "=== LINK VALIDATION ==="
  
  # Extract all markdown links
  grep -rn '\[.*\](.*\.md' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null > /tmp/all_links_$$.txt || true
  TOTAL_LINKS=$(wc -l < /tmp/all_links_$$.txt)
  log "Total links found: $TOTAL_LINKS"
  
  # Validate each unique target
  grep -rho '\[.*\](.*\.md' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | \
    sed 's/.*(\(.*\.md\).*/\1/' | sort -u > /tmp/unique_targets_$$.txt || true
  
  BROKEN=0
  while read -r target; do
    if [ ! -f "$target" ] && [ ! -f "$DOCS_DIR/$target" ]; then
      log "  ❌ Broken: $target"
      ((BROKEN++))
      
      # Show which files reference this broken link
      grep -l "$target" "$DOCS_DIR"/**/*.md README.md CLAUDE.md 2>/dev/null | head -3 | while read -r file; do
        LINE=$(grep -n "$target" "$file" | head -1 | cut -d: -f1)
        log "      Referenced in: $file:$LINE"
      done
    fi
  done < /tmp/unique_targets_$$.txt
  
  log "Broken links: $BROKEN"
  rm -f /tmp/all_links_$$.txt /tmp/unique_targets_$$.txt
}

# Structure validation function
validate_structure() {
  log "=== STRUCTURE VALIDATION ==="
  
  # Check atomic/* structure
  EXPECTED_DIRS=("architecture" "databases" "infrastructure" "integrations" "observability" "services" "testing")
  
  for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$DOCS_DIR/atomic/$dir" ]; then
      README_COUNT=$(find "$DOCS_DIR/atomic/$dir" -name "README.md" | wc -l)
      log "  ✅ $DOCS_DIR/atomic/$dir (READMEs: $README_COUNT)"
    else
      log "  ❌ $DOCS_DIR/atomic/$dir missing"
    fi
  done
}

# AI navigation validation function
validate_ai_navigation() {
  log "=== AI NAVIGATION VALIDATION ==="
  
  # Verify Stage 0 sequence
  STAGE0_DOCS=("CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md")
  
  for i in "${!STAGE0_DOCS[@]}"; do
    doc="${STAGE0_DOCS[$i]}"
    if [ -f "$doc" ]; then
      log "  Step $((i+1)): ✅ $doc"
    else
      log "  Step $((i+1)): ❌ CRITICAL - $doc missing"
    fi
  done
  
  # Check navigation matrix
  if [ -f "docs/reference/ai-navigation-matrix.md" ]; then
    log "  ✅ AI navigation matrix exists"
    
    # Check for all 7 stages
    for stage in {0..6}; do
      if grep -q "Stage $stage" docs/reference/ai-navigation-matrix.md; then
        log "    ✅ Stage $stage documented"
      else
        log "    ❌ Stage $stage missing"
      fi
    done
  else
    log "  ❌ CRITICAL: AI navigation matrix missing"
  fi
}

# Main execution
MODE="${1:---full}"

case "$MODE" in
  --quick)
    log "Starting QUICK AUDIT"
    run_smoke_tests
    ;;
  --links)
    log "Starting LINK VALIDATION"
    validate_links
    ;;
  --structure)
    log "Starting STRUCTURE VALIDATION"
    validate_structure
    ;;
  --ai-navigation)
    log "Starting AI NAVIGATION VALIDATION"
    validate_ai_navigation
    ;;
  --full)
    log "Starting FULL AUDIT"
    run_smoke_tests
    validate_links
    validate_structure
    validate_ai_navigation
    log "=== FULL AUDIT COMPLETE ==="
    log "Report saved to: $REPORT_FILE"
    ;;
  *)
    echo "Usage: $0 [--full|--quick|--links|--structure|--ai-navigation]"
    exit 1
    ;;
esac

log "Audit completed at $(date)"
```

**Make executable**:
```bash
chmod +x scripts/audit_docs.sh
```

---

## CI/CD INTEGRATION

### GitHub Actions Example

```yaml
# .github/workflows/docs-audit.yml
name: Documentation Audit

on:
  push:
    paths:
      - 'docs/**'
      - '*.md'
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Quick Audit
        run: |
          bash scripts/audit_docs.sh --quick
          
      - name: Check for Critical Issues
        run: |
          # Fail if legacy references found
          LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/" docs/ 2>/dev/null | wc -l)
          if [ $LEGACY_COUNT -gt 0 ]; then
            echo "::error::Found $LEGACY_COUNT legacy references"
            exit 1
          fi
          
      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: audit_reports/
```

---

## USAGE EXAMPLES

### Example 1: First-Time Audit

```bash
# Clone repository
cd /path/to/doc4microservices

# Run full audit
bash scripts/audit_docs.sh --full

# Review report
cat audit_reports/audit_*.md | less

# Fix critical issues first
grep "CRITICAL" audit_reports/audit_*.md
```

### Example 2: Pre-Commit Audit

```bash
# Quick check before committing docs
bash scripts/audit_docs.sh --quick

# If issues found, run focused audit
bash scripts/audit_docs.sh --links
```

### Example 3: CI/CD Integration

```bash
# In CI pipeline
bash scripts/audit_docs.sh --quick
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Documentation audit failed"
  exit 1
fi
```

---

## MAINTENANCE SCHEDULE

### Daily (Automated)
- Quick audit (5 min) on every commit touching `docs/` or `*.md`
- Check for broken links only

### Weekly (Automated)
- Full audit with all 14 objectives
- Generate trend report (compare with previous week)

### Monthly (Manual)
- Review accumulated issues
- Prioritize fixes
- Update audit template if needed

### Quarterly (Manual)
- Deep content quality review
- Update validation commands
- Review and update this audit template

---

## SHELL SCRIPTING BEST PRACTICES

When writing validation scripts:

1. **Use `find -print0 | xargs -0`** for file operations (handles spaces)
   ```bash
   find docs/ -name "*.md" -print0 | xargs -0 grep -l "pattern"
   ```

2. **Avoid `while read` loops** when possible (slow for large datasets)
   ```bash
   # Bad: slow
   ls *.md | while read file; do grep pattern "$file"; done
   
   # Good: parallel processing
   grep -r pattern *.md
   ```

3. **Use parallel processing** for independent checks
   ```bash
   find docs/ -name "*.md" -print0 | xargs -0 -P 8 -I {} bash -c 'check_file "$@"' _ {}
   ```

4. **Capture errors properly**
   ```bash
   grep -r pattern docs/ 2>/dev/null || echo "Pattern not found"
   ```

5. **Use temporary files** for complex pipelines
   ```bash
   grep -r pattern docs/ > /tmp/results.txt
   process_results < /tmp/results.txt
   rm /tmp/results.txt
   ```

---

## NOTES

### Why This Template is Critical

This audit template prevents systemic documentation failures by:

1. **Forcing direct execution** (no delegation to unreliable agents)
2. **Requiring exhaustive checking** (no sample-based estimation)
3. **Providing explicit validation commands** (no room for interpretation)
4. **Mandating smoke tests** (catch critical issues in 30 seconds)
5. **Requiring proof of work** (show commands used, spot checks performed)

### Lessons from Previous Failures

The original template allowed an AI agent to miss 64+ critical broken legacy links because:
- Delegation was permitted → Task agent used sample-based checking
- No explicit validation commands → Agent estimated instead of executing
- Smoke tests came too late → Critical issues not caught early
- No spot check requirements → No verification that issues were real
- Health score calculation not enforced → Agent estimated 72/100 (actual: ~0/100)

This V2 template fixes ALL of these failure modes.

### When to Update This Template

Update this template when:
- New documentation categories added (e.g., "deployment-guides/")
- New quality criteria introduced (e.g., "check for AI-readability")
- New tools adopted (e.g., "vale" for prose linting)
- Audit failure modes discovered (add to CONSTRAINTS)
- Framework structure changes (update expected directories)

### Recovery from Audit Failures

If an audit using this template still misses critical issues:

1. **Root cause analysis** (ultrathink):
   - Which objective failed?
   - Was validation command inadequate?
   - Was constraint unclear?

2. **Template fix**:
   - Update validation commands
   - Add explicit constraint
   - Add to anti-patterns section

3. **Verify fix**:
   - Re-run audit with updated template
   - Confirm issue now caught

4. **Document lesson**:
   - Add to "Lessons from Previous Failures" section
   - Update CI/CD checks

---

## END OF TEMPLATE

**Version**: 2.0  
**Last Updated**: 2025-10-11  
**Changelog**:
- v2.0 (2025-10-11): Complete rewrite with mandatory execution protocol, explicit validation commands, smoke tests, verification protocol
- v1.0 (2025-10-10): Original template (proved insufficient - missed 64+ critical issues)


### 11. Infrastructure Integration Documentation

**Goal**: Verify all infrastructure components are documented with examples.

**Validation Commands**:

```bash
# Check infrastructure documentation
echo "=== Checking Infrastructure Documentation ==="

INFRA_COMPONENTS=(
  "postgres"
  "redis"
  "rabbitmq"
  "nginx"
  "docker"
)

for component in "${INFRA_COMPONENTS[@]}"; do
  echo "Checking: $component"
  
  # Check docs/atomic/integrations/ or docs/atomic/infrastructure/
  if [ -d "docs/atomic/integrations/$component" ] || [ -d "docs/atomic/infrastructure/$component" ]; then
    echo "  ✅ Documentation directory exists"
    
    # Check for README
    README_PATH=$(find docs/atomic/integrations/$component docs/atomic/infrastructure/$component -name "README.md" 2>/dev/null | head -1)
    if [ -n "$README_PATH" ]; then
      echo "  ✅ README.md present: $README_PATH"
      
      # Check for code examples
      if grep -q '```' "$README_PATH"; then
        echo "    ✅ Contains code examples"
      else
        echo "    ⚠️  No code examples"
      fi
    else
      echo "  ⚠️  README.md missing"
    fi
  else
    echo "  ⚠️  No documentation directory for $component"
  fi
done
```

**Expected Outcome**: Infrastructure documentation completeness report.

### 12. Testing Documentation

**Goal**: Verify testing patterns, examples, and coverage requirements are documented.

**Validation Commands**:

```bash
# Check testing documentation
echo "=== Checking Testing Documentation ==="

if [ -d "docs/atomic/testing" ]; then
  echo "✅ Testing documentation directory exists"
  
  # Check for key testing topics
  TESTING_TOPICS=(
    "unit.*test\|test.*unit"
    "integration.*test\|test.*integration"
    "pytest"
    "coverage"
    "mock\|fixture"
  )
  
  for topic in "${TESTING_TOPICS[@]}"; do
    if grep -rqi "$topic" docs/atomic/testing/; then
      echo "  ✅ Topic documented: $topic"
    else
      echo "  ⚠️  Topic missing/unclear: $topic"
    fi
  done
  
  # Check for coverage thresholds
  if grep -rE "coverage.*[0-9]+%|[0-9]+%.*coverage" docs/atomic/testing/ docs/guides/development-commands.md 2>/dev/null | grep -q .; then
    echo "  ✅ Coverage thresholds documented"
  else
    echo "  ⚠️  Coverage thresholds not clearly documented"
  fi
else
  echo "⚠️  docs/atomic/testing/ directory missing"
fi
```

**Expected Outcome**: Testing documentation completeness report.

### 13. Observability Documentation

**Goal**: Verify logging, metrics, tracing, and error tracking are documented.

**Validation Commands**:

```bash
# Check observability documentation
echo "=== Checking Observability Documentation ==="

if [ -d "docs/atomic/observability" ]; then
  echo "✅ Observability documentation directory exists"
  
  # Check for pillars of observability
  OBSERVABILITY_PILLARS=(
    "logging\|logs"
    "metrics\|prometheus"
    "tracing\|jaeger\|opentelemetry"
    "error.*tracking\|sentry"
    "elk\|elasticsearch"
  )
  
  for pillar in "${OBSERVABILITY_PILLARS[@]}"; do
    if grep -rqi "$pillar" docs/atomic/observability/; then
      echo "  ✅ Pillar documented: $pillar"
    else
      echo "  ⚠️  Pillar missing/unclear: $pillar"
    fi
  done
  
  # Check for structured logging examples
  if grep -rq "structlog\|json.*log\|structured.*log" docs/atomic/observability/; then
    echo "  ✅ Structured logging documented"
  else
    echo "  ⚠️  Structured logging not documented"
  fi
else
  echo "⚠️  docs/atomic/observability/ directory missing"
fi
```

**Expected Outcome**: Observability documentation completeness report.

### 14. Shared Components Documentation

**Goal**: Verify shared configuration, utilities, and DI patterns are documented.

**Validation Commands**:

```bash
# Check shared components documentation
echo "=== Checking Shared Components Documentation ==="

if [ -f "docs/guides/shared-components.md" ]; then
  echo "✅ Shared components guide exists"
  
  # Check for key shared component topics
  SHARED_TOPICS=(
    "config\|configuration\|settings"
    "dependency.*injection\|DI"
    "logging.*setup"
    "database.*pool\|connection.*pool"
    "middleware"
  )
  
  for topic in "${SHARED_TOPICS[@]}"; do
    if grep -Eqi "$topic" docs/guides/shared-components.md; then
      echo "  ✅ Topic documented: $topic"
    else
      echo "  ⚠️  Topic missing: $topic"
    fi
  done
else
  echo "⚠️  docs/guides/shared-components.md missing"
fi

# Check for src/core/ documentation
if grep -rq "src/core\|core/config.py\|core/logging.py" docs/; then
  echo "  ✅ src/core/ patterns documented"
else
  echo "  ⚠️  src/core/ patterns not documented"
fi
```

**Expected Outcome**: Shared components documentation report.

---

## DELIVERABLES

### 1. Executive Summary (MANDATORY FORMAT - SHOW YOUR WORK)

#### Health Score Calculation (MUST SHOW CALCULATION)

**Formula:**
```
Health Score = 100 - (CRITICAL_count × 3) - (HIGH_count × 1.5) - (MEDIUM_count × 0.5) - (LOW_count × 0.1)
```

**Calculation (SHOW THIS IN YOUR REPORT):**
```
Base:                    100 points
CRITICAL issues (64):    64 × 3  = -192 points
HIGH issues (10):        10 × 1.5 = -15 points
MEDIUM issues (5):       5 × 0.5 = -2.5 points
LOW issues (3):          3 × 0.1 = -0.3 points
FINAL HEALTH SCORE:      max(0, 100 - 209.8) = 0/100
```

#### Validation Commands Used (PROOF OF WORK - MANDATORY)

**Must list ALL commands executed**:

```bash
# Example (replace with actual commands you ran):
grep -rn "docs/legacy" docs/ README.md CLAUDE.md 2>/dev/null | wc -l
find docs/ -name "*.md" -print0 | xargs -0 grep -l "pattern"
for doc in "${STAGE0_DOCS[@]}"; do [ -f "$doc" ] && echo "✅" || echo "❌"; done
```

**Spot checks performed (MANDATORY - verify 3+ random issues):**

Pick 3+ random issues from your findings and verify them manually:

```markdown
#### Spot Check 1: Verify docs/atomic/architecture/data-access-architecture.md:66

**Command Run**:
```bash
sed -n '66p' docs/atomic/architecture/data-access-architecture.md
```

**Output**:
```
- Legacy reference: `docs/legacy/architecture/data-access-rules.md`
```

**Verified**: ✅ Issue is real - line 66 contains broken legacy reference
**Fix Tested**: ✅ sed replacement command works correctly
```

#### Issue Summary Table

| Severity | Count | Weight | Score Impact |
|----------|-------|--------|--------------|
| CRITICAL | 64    | 3.0    | -192         |
| HIGH     | 10    | 1.5    | -15          |
| MEDIUM   | 5     | 0.5    | -2.5         |
| LOW      | 3     | 0.1    | -0.3         |
| **Total**| **82**| -      | **-209.8**   |

**Health Score**: 0/100 (Critical - immediate action required)

#### Top 5 Critical Issues

1. **64 Broken Legacy References** - blocks users/AI agents from finding current docs
2. **Missing Stage 0 Document** - AI initialization fails
3. **Broken AI Navigation Matrix** - Stage 2-4 links point to non-existent files
4. **Missing Service Templates** - 4 out of 5 promised templates don't exist
5. **Architecture Constraints Unclear** - HTTP-only data access not emphasized

---

### 2. Detailed Findings by Objective

For each objective (1-14), provide:

#### Objective N: [Objective Name]

**Status**: ✅ Passed / ⚠️  Issues Found / ❌ Critical Issues

**Issues Found**: [count]

**Detailed Issues**:

##### Issue N.1: [Issue Title]

**File**: `/path/to/file.md:123`  
**Priority**: CRITICAL | HIGH | MEDIUM | LOW  
**Category**: Link Validation | Structure | Content Quality | etc.

**Problem Description**:  
Clear explanation of what's wrong and why it matters.

**Impact**:  
Who is affected (users, AI agents, developers) and how.

**How Found**:
```bash
grep -rn "pattern" docs/file.md
```

**Fix Command**:
```bash
sed -i 's/old/new/g' docs/file.md
# OR
mv docs/old.md docs/new.md && find docs/ -name "*.md" -exec sed -i 's|old.md|new.md|g' {} \;
```

**Verification**:
```bash
grep -n "old" docs/file.md  # Expected: no output
# OR
test -f docs/new.md && echo "✅ File exists" || echo "❌ Still missing"
```

**Related Issues**: [Link to related issues if applicable]

---

### 3. Actionable Recommendations

#### Immediate Actions (Within 24 Hours)

1. **Fix all CRITICAL issues** (64 broken legacy links, missing Stage 0 docs)
   - Priority: P0
   - Estimated effort: 2-3 hours
   - Blocking: Yes (AI agents cannot navigate documentation)

2. **Update AI Navigation Matrix**
   - Priority: P0
   - Estimated effort: 1 hour
   - Blocking: Yes (Stage 1-6 broken)

#### Short-Term Actions (Within 1 Week)

3. **Add missing service templates**
   - Priority: P1
   - Estimated effort: 4-6 hours
   - Blocking: Partially (80% of service types cannot be generated)

4. **Fix HIGH priority issues**
   - Priority: P1
   - Estimated effort: 3-4 hours

#### Long-Term Actions (Within 1 Month)

5. **Address MEDIUM and LOW issues**
   - Priority: P2
   - Estimated effort: 5-8 hours

6. **Implement automated audit in CI/CD**
   - Priority: P2
   - Estimated effort: 2-3 hours

---

### 4. Automation Recommendations

#### Create Audit Script

```bash
# Save as scripts/audit_docs.sh
# (Use AUTOMATION SCRIPT TEMPLATE section below)
```

#### Add to CI/CD

```yaml
# .github/workflows/docs-audit.yml
# (Use CI/CD INTEGRATION section below)
```

#### Schedule Regular Audits

- **Daily**: Quick audit (5 min) on documentation changes
- **Weekly**: Full audit (15 min) with trend analysis
- **Monthly**: Manual review of accumulated issues

---

### 5. Trend Analysis (Optional - For Regular Audits)

Compare current audit with previous audits:

| Metric                  | Previous | Current | Change |
|-------------------------|----------|---------|--------|
| Total Issues            | 95       | 82      | -13 ✅ |
| CRITICAL Issues         | 70       | 64      | -6 ✅  |
| HIGH Issues             | 12       | 10      | -2 ✅  |
| Health Score            | 0/100    | 0/100   | 0      |
| Documentation Files     | 187      | 203     | +16    |
| Total Links             | 1,245    | 1,389   | +144   |
| Broken Link Rate        | 5.1%     | 4.6%    | -0.5% ✅|

**Analysis**: Overall trend is positive - 13 fewer issues despite 16 new documentation files. However, CRITICAL issue count is still too high (target: 0).

---

## OUTPUT FORMAT

### Structure Requirements

1. **Use Markdown** with clear section hierarchy
2. **Code blocks** with syntax highlighting (```bash, ```python, etc.)
3. **File paths** format: `/path/to/file.md:123` (clickable in most IDEs)
4. **Tables** for large datasets (issue lists, file inventories)
5. **Command examples** showing exact fix commands with expected output

### Example Output Structure

```markdown
## Critical Issues (Priority: CRITICAL)

### Issue 1: Broken Legacy Reference

**File**: `docs/atomic/architecture/data-access-architecture.md:66`  
**Problem**: Reference to non-existent `docs/legacy/architecture/data-access-rules.md`  
**Impact**: Blocks users/AI agents trying to find data access rules  
**Category**: Link Validation

**How Found**:
```bash
grep -rn "docs/legacy" docs/atomic/architecture/data-access-architecture.md
```

**Fix Command**:
```bash
sed -i 's|docs/legacy/architecture/data-access-rules.md|docs/atomic/architecture/data-access-architecture.md|g' \
  docs/atomic/architecture/data-access-architecture.md
```

**Verification**:
```bash
grep -n "docs/legacy" docs/atomic/architecture/data-access-architecture.md
# Expected: no output (issue fixed)
```
```

---

## CONSTRAINTS ⚡ MANDATORY

### Execution Constraints

1. **DO NOT delegate this audit to Task agent**
   - You MUST execute all validation commands yourself using Bash tool
   - Delegation leads to incomplete audits (proven failure mode)

2. **DO NOT use sample-based checking**
   - Check ALL files, not 10% with extrapolation
   - Use `find`, `grep -r`, `xargs -P` for exhaustive scans

3. **DO NOT skip smoke tests**
   - Run all 5 smoke tests before full audit
   - If any smoke test shows critical issues, report immediately

4. **DO NOT estimate health score**
   - Calculate using exact formula: `100 - (CRITICAL×3) - (HIGH×1.5) - (MEDIUM×0.5) - (LOW×0.1)`
   - Show calculation in report

5. **DO NOT trust "Related Documents" sections without verification**
   - These are NOT optional metadata
   - Users/AI agents click these links expecting valid targets
   - Broken "Related Documents" = CRITICAL issue

### Reporting Constraints

1. **MUST show validation commands used** (proof of work)
2. **MUST perform 3+ spot checks** to verify issues are real
3. **MUST include fix commands** for each issue (not just descriptions)
4. **MUST include verification commands** showing how to confirm fix worked
5. **MUST report file:line locations** for all issues (not just filenames)

### Quality Constraints

1. **Accuracy > Speed**: Better to take 10 minutes and find all issues than 2 minutes with 50% false negatives
2. **Explicit > Implicit**: Show commands, outputs, calculations
3. **Reproducible**: Any human/AI should be able to run your commands and get same results
4. **Actionable**: Every issue should have clear fix command

---

## VERIFICATION PROTOCOL ⚡ MANDATORY

After completing the audit, perform these self-checks:

### Automated Verification

```bash
# Save your audit report to /tmp/audit_output.md first

# Check 1: Did you run smoke tests?
grep -q "SMOKE TEST" /tmp/audit_output.md
echo "Smoke tests documented: $?"  # Expected: 0 (yes)

# Check 2: Did you show health score calculation?
grep -q "100 - (CRITICAL" /tmp/audit_output.md
echo "Health score formula shown: $?"  # Expected: 0 (yes)

# Check 3: Did you perform spot checks?
grep -c "Spot Check" /tmp/audit_output.md
# Expected: >= 3

# Check 4: Are all issues tagged with severity?
ISSUES=$(grep -c "^### Issue" /tmp/audit_output.md)
SEVERITIES=$(grep -c "Priority: \(CRITICAL\|HIGH\|MEDIUM\|LOW\)" /tmp/audit_output.md)
echo "Issues: $ISSUES, Tagged: $SEVERITIES"  # Should match

# Check 5: Do all issues have fix commands?
FIX_COMMANDS=$(grep -c "**Fix Command**:" /tmp/audit_output.md)
echo "Issues with fixes: $ISSUES/$FIX_COMMANDS"  # Should match
```

### Manual Spot Checks (Pick 3 Random Issues)

For each spot check:

1. **Copy the "How Found" command** → Run it yourself
2. **Verify the issue exists** at reported file:line
3. **Copy the "Fix Command"** → Run it in test environment
4. **Copy the "Verification Command"** → Confirm fix works
5. **Document result** in audit report

**Example Spot Check Documentation**:

```markdown
#### Spot Check 1: Legacy Reference Verification

**Issue**: docs/atomic/architecture/data-access-architecture.md:66 references non-existent legacy file

**Command Run**:
```bash
sed -n '66p' docs/atomic/architecture/data-access-architecture.md
```

**Output**:
```
- Legacy reference: `docs/legacy/architecture/data-access-rules.md`
```

**Verification**: ✅ Issue confirmed - line 66 contains broken legacy reference

**Fix Tested**: ✅ sed replacement works, file updated correctly
```

### Self-Audit Checklist

Before submitting audit report, confirm:

- [ ] All 5 smoke tests executed and documented
- [ ] Health score calculation shown with formula
- [ ] All validation commands listed (proof of work)
- [ ] 3+ spot checks performed and documented
- [ ] Every issue has: file:line, impact, category, how found, fix command, verification
- [ ] No delegation used (all commands run directly by you)
- [ ] Exhaustive checking used (not sample-based)
- [ ] "Related Documents" sections validated (not skipped)

**If ANY checklist item is unchecked → AUDIT IS INCOMPLETE**

---

## QUICK AUDIT (5 Minutes)

For rapid health checks, run only smoke tests + critical validations:

```bash
#!/bin/bash
# Quick audit script (5 minutes max)

echo "=== QUICK DOCUMENTATION AUDIT ==="
echo "Started: $(date)"

# 1. Smoke Tests
echo -e "\n### SMOKE TESTS ###"

# Smoke 1: File counts
MD_COUNT=$(find docs/ -name "*.md" 2>/dev/null | wc -l)
echo "Markdown files: $MD_COUNT"

# Smoke 2: Link count
LINK_COUNT=$(grep -roh '\[.*\](.*\.md' docs/ 2>/dev/null | wc -l)
echo "Total links: $LINK_COUNT"

# Smoke 3: Legacy references (CRITICAL)
LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" docs/ README.md CLAUDE.md 2>/dev/null | wc -l)
echo "Legacy references: $LEGACY_COUNT"
if [ $LEGACY_COUNT -gt 0 ]; then
  echo "  🚨 CRITICAL: Found $LEGACY_COUNT legacy references"
fi

# Smoke 4: Broken link sample
echo "Sample broken links (first 3):"
grep -rho '\[.*\](.*\.md' docs/ 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | while read -r ref; do
  if [ ! -f "$ref" ] && [ ! -f "docs/$ref" ]; then
    echo "  ❌ $ref"
  fi
done | head -3

# Smoke 5: Stage 0 files
echo -e "\nStage 0 initialization files:"
for doc in "CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md"; do
  if [ -f "$doc" ]; then
    echo "  ✅ $doc"
  else
    echo "  ❌ $doc (CRITICAL)"
  fi
done

# 2. Critical Validations Only
echo -e "\n### CRITICAL VALIDATIONS ###"

# Check architecture guide exists
[ -f "docs/guides/architecture-guide.md" ] && echo "✅ Architecture guide" || echo "❌ Architecture guide (CRITICAL)"

# Check AI workflow exists
[ -f "docs/guides/ai-code-generation-master-workflow.md" ] && echo "✅ AI workflow" || echo "❌ AI workflow (CRITICAL)"

# Check navigation matrix
[ -f "docs/reference/ai-navigation-matrix.md" ] && echo "✅ Navigation matrix" || echo "❌ Navigation matrix (CRITICAL)"

echo -e "\nCompleted: $(date)"
echo -e "\n💡 Run full audit for detailed analysis: bash scripts/audit_docs.sh --full"
```

**Usage**:
```bash
bash scripts/quick_audit.sh
```

---

## FOCUSED AUDITS

### Audit Only Links

```bash
# Link-only audit
bash scripts/audit_docs.sh --links
```

### Audit Only Structure

```bash
# Structure-only audit
bash scripts/audit_docs.sh --structure
```

### Audit Only AI Navigation

```bash
# AI navigation audit
bash scripts/audit_docs.sh --ai-navigation
```

---

## AUTOMATION SCRIPT TEMPLATE

Create `scripts/audit_docs.sh` for reusable auditing:

```bash
#!/bin/bash

# scripts/audit_docs.sh - Comprehensive documentation audit automation
# Usage:
#   ./scripts/audit_docs.sh --full      # Full audit
#   ./scripts/audit_docs.sh --quick     # 5-minute audit
#   ./scripts/audit_docs.sh --links     # Link validation only
#   ./scripts/audit_docs.sh --structure # Structure validation only

set -euo pipefail

# Configuration
DOCS_DIR="docs"
OUTPUT_DIR="audit_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/audit_${TIMESTAMP}.md"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Logging helper
log() {
  echo "[$(date +%H:%M:%S)] $*" | tee -a "$REPORT_FILE"
}

# Smoke tests function
run_smoke_tests() {
  log "=== SMOKE TESTS ==="
  
  log "Smoke 1: File counts"
  MD_COUNT=$(find "$DOCS_DIR" -name "*.md" 2>/dev/null | wc -l)
  log "  Markdown files: $MD_COUNT"
  
  log "Smoke 2: Link count"
  LINK_COUNT=$(grep -roh '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | wc -l)
  log "  Total links: $LINK_COUNT"
  
  log "Smoke 3: 🚨 Legacy references (CRITICAL)"
  LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | wc -l)
  log "  Legacy references: $LEGACY_COUNT"
  if [ "$LEGACY_COUNT" -gt 0 ]; then
    log "  🚨 CRITICAL: Found $LEGACY_COUNT legacy references"
    grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | head -10 | tee -a "$REPORT_FILE"
  fi
  
  log "Smoke 4: Broken link sample"
  BROKEN_SAMPLE=$(grep -rho '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | while read -r ref; do
    if [ ! -f "$ref" ] && [ ! -f "$DOCS_DIR/$ref" ]; then
      echo "  ❌ $ref"
    fi
  done | head -3)
  log "$BROKEN_SAMPLE"
  
  log "Smoke 5: Stage 0 files"
  for doc in "CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md"; do
    if [ -f "$doc" ]; then
      log "  ✅ $doc"
    else
      log "  ❌ $doc (CRITICAL)"
    fi
  done
}

# Link validation function
validate_links() {
  log "=== LINK VALIDATION ==="
  
  # Extract all markdown links
  grep -rn '\[.*\](.*\.md' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null > /tmp/all_links_$$.txt || true
  TOTAL_LINKS=$(wc -l < /tmp/all_links_$$.txt)
  log "Total links found: $TOTAL_LINKS"
  
  # Validate each unique target
  grep -rho '\[.*\](.*\.md' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | \
    sed 's/.*(\(.*\.md\).*/\1/' | sort -u > /tmp/unique_targets_$$.txt || true
  
  BROKEN=0
  while read -r target; do
    if [ ! -f "$target" ] && [ ! -f "$DOCS_DIR/$target" ]; then
      log "  ❌ Broken: $target"
      ((BROKEN++))
      
      # Show which files reference this broken link
      grep -l "$target" "$DOCS_DIR"/**/*.md README.md CLAUDE.md 2>/dev/null | head -3 | while read -r file; do
        LINE=$(grep -n "$target" "$file" | head -1 | cut -d: -f1)
        log "      Referenced in: $file:$LINE"
      done
    fi
  done < /tmp/unique_targets_$$.txt
  
  log "Broken links: $BROKEN"
  rm -f /tmp/all_links_$$.txt /tmp/unique_targets_$$.txt
}

# Structure validation function
validate_structure() {
  log "=== STRUCTURE VALIDATION ==="
  
  # Check atomic/* structure
  EXPECTED_DIRS=("architecture" "databases" "infrastructure" "integrations" "observability" "services" "testing")
  
  for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$DOCS_DIR/atomic/$dir" ]; then
      README_COUNT=$(find "$DOCS_DIR/atomic/$dir" -name "README.md" | wc -l)
      log "  ✅ $DOCS_DIR/atomic/$dir (READMEs: $README_COUNT)"
    else
      log "  ❌ $DOCS_DIR/atomic/$dir missing"
    fi
  done
}

# AI navigation validation function
validate_ai_navigation() {
  log "=== AI NAVIGATION VALIDATION ==="
  
  # Verify Stage 0 sequence
  STAGE0_DOCS=("CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md")
  
  for i in "${!STAGE0_DOCS[@]}"; do
    doc="${STAGE0_DOCS[$i]}"
    if [ -f "$doc" ]; then
      log "  Step $((i+1)): ✅ $doc"
    else
      log "  Step $((i+1)): ❌ CRITICAL - $doc missing"
    fi
  done
  
  # Check navigation matrix
  if [ -f "docs/reference/ai-navigation-matrix.md" ]; then
    log "  ✅ AI navigation matrix exists"
    
    # Check for all 7 stages
    for stage in {0..6}; do
      if grep -q "Stage $stage" docs/reference/ai-navigation-matrix.md; then
        log "    ✅ Stage $stage documented"
      else
        log "    ❌ Stage $stage missing"
      fi
    done
  else
    log "  ❌ CRITICAL: AI navigation matrix missing"
  fi
}

# Main execution
MODE="${1:---full}"

case "$MODE" in
  --quick)
    log "Starting QUICK AUDIT"
    run_smoke_tests
    ;;
  --links)
    log "Starting LINK VALIDATION"
    validate_links
    ;;
  --structure)
    log "Starting STRUCTURE VALIDATION"
    validate_structure
    ;;
  --ai-navigation)
    log "Starting AI NAVIGATION VALIDATION"
    validate_ai_navigation
    ;;
  --full)
    log "Starting FULL AUDIT"
    run_smoke_tests
    validate_links
    validate_structure
    validate_ai_navigation
    log "=== FULL AUDIT COMPLETE ==="
    log "Report saved to: $REPORT_FILE"
    ;;
  *)
    echo "Usage: $0 [--full|--quick|--links|--structure|--ai-navigation]"
    exit 1
    ;;
esac

log "Audit completed at $(date)"
```

**Make executable**:
```bash
chmod +x scripts/audit_docs.sh
```

---

## CI/CD INTEGRATION

### GitHub Actions Example

```yaml
# .github/workflows/docs-audit.yml
name: Documentation Audit

on:
  push:
    paths:
      - 'docs/**'
      - '*.md'
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Quick Audit
        run: |
          bash scripts/audit_docs.sh --quick
          
      - name: Check for Critical Issues
        run: |
          # Fail if legacy references found
          LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/" docs/ 2>/dev/null | wc -l)
          if [ $LEGACY_COUNT -gt 0 ]; then
            echo "::error::Found $LEGACY_COUNT legacy references"
            exit 1
          fi
          
      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: audit_reports/
```

---

## USAGE EXAMPLES

### Example 1: First-Time Audit

```bash
# Clone repository
cd /path/to/doc4microservices

# Run full audit
bash scripts/audit_docs.sh --full

# Review report
cat audit_reports/audit_*.md | less

# Fix critical issues first
grep "CRITICAL" audit_reports/audit_*.md
```

### Example 2: Pre-Commit Audit

```bash
# Quick check before committing docs
bash scripts/audit_docs.sh --quick

# If issues found, run focused audit
bash scripts/audit_docs.sh --links
```

### Example 3: CI/CD Integration

```bash
# In CI pipeline
bash scripts/audit_docs.sh --quick
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Documentation audit failed"
  exit 1
fi
```

---

## MAINTENANCE SCHEDULE

### Daily (Automated)
- Quick audit (5 min) on every commit touching `docs/` or `*.md`
- Check for broken links only

### Weekly (Automated)
- Full audit with all 14 objectives
- Generate trend report (compare with previous week)

### Monthly (Manual)
- Review accumulated issues
- Prioritize fixes
- Update audit template if needed

### Quarterly (Manual)
- Deep content quality review
- Update validation commands
- Review and update this audit template

---

## SHELL SCRIPTING BEST PRACTICES

When writing validation scripts:

1. **Use `find -print0 | xargs -0`** for file operations (handles spaces)
   ```bash
   find docs/ -name "*.md" -print0 | xargs -0 grep -l "pattern"
   ```

2. **Avoid `while read` loops** when possible (slow for large datasets)
   ```bash
   # Bad: slow
   ls *.md | while read file; do grep pattern "$file"; done
   
   # Good: parallel processing
   grep -r pattern *.md
   ```

3. **Use parallel processing** for independent checks
   ```bash
   find docs/ -name "*.md" -print0 | xargs -0 -P 8 -I {} bash -c 'check_file "$@"' _ {}
   ```

4. **Capture errors properly**
   ```bash
   grep -r pattern docs/ 2>/dev/null || echo "Pattern not found"
   ```

5. **Use temporary files** for complex pipelines
   ```bash
   grep -r pattern docs/ > /tmp/results.txt
   process_results < /tmp/results.txt
   rm /tmp/results.txt
   ```

---

## NOTES

### Why This Template is Critical

This audit template prevents systemic documentation failures by:

1. **Forcing direct execution** (no delegation to unreliable agents)
2. **Requiring exhaustive checking** (no sample-based estimation)
3. **Providing explicit validation commands** (no room for interpretation)
4. **Mandating smoke tests** (catch critical issues in 30 seconds)
5. **Requiring proof of work** (show commands used, spot checks performed)

### Lessons from Previous Failures

The original template allowed an AI agent to miss 64+ critical broken legacy links because:
- Delegation was permitted → Task agent used sample-based checking
- No explicit validation commands → Agent estimated instead of executing
- Smoke tests came too late → Critical issues not caught early
- No spot check requirements → No verification that issues were real
- Health score calculation not enforced → Agent estimated 72/100 (actual: ~0/100)

This V2 template fixes ALL of these failure modes.

### When to Update This Template

Update this template when:
- New documentation categories added (e.g., "deployment-guides/")
- New quality criteria introduced (e.g., "check for AI-readability")
- New tools adopted (e.g., "vale" for prose linting)
- Audit failure modes discovered (add to CONSTRAINTS)
- Framework structure changes (update expected directories)

### Recovery from Audit Failures

If an audit using this template still misses critical issues:

1. **Root cause analysis** (ultrathink):
   - Which objective failed?
   - Was validation command inadequate?
   - Was constraint unclear?

2. **Template fix**:
   - Update validation commands
   - Add explicit constraint
   - Add to anti-patterns section

3. **Verify fix**:
   - Re-run audit with updated template
   - Confirm issue now caught

4. **Document lesson**:
   - Add to "Lessons from Previous Failures" section
   - Update CI/CD checks

---

## END OF TEMPLATE

**Version**: 2.0  
**Last Updated**: 2025-10-11  
**Changelog**:
- v2.0 (2025-10-11): Complete rewrite with mandatory execution protocol, explicit validation commands, smoke tests, verification protocol
- v1.0 (2025-10-10): Original template (proved insufficient - missed 64+ critical issues)

