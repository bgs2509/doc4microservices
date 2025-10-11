# Documentation Audit Prompt Template

## Purpose
This prompt helps AI agents conduct comprehensive documentation audits to identify and fix structural, consistency, and content issues.

---

## Full Audit Prompt

```
Conduct a comprehensive documentation audit of this project:

## OBJECTIVES

1. **Understand Project Purpose**
   - Read README.md, CLAUDE.md, and docs/INDEX.md
   - Identify main project goals and target users
   - Understand architecture and technology stack

2. **Link Validation**
   - Check ALL markdown files for broken internal links
   - Verify relative paths resolve correctly
   - Check anchor links (#section-name) point to valid sections
   - Validate cross-references between documents
   - Report all 404 or invalid references with locations

3. **File Completeness**
   - Find all file references in documentation
   - Verify each referenced file exists
   - Check for missing templates, configs, or resources
   - Identify orphaned documents not referenced anywhere

4. **Structural Consistency**
   - Verify directory structure matches PROJECT_STRUCTURE.md
   - Ensure all documents listed in INDEX.md exist
   - Validate LINKS_REFERENCE.md has correct paths
   - Check navigation consistency across guides

5. **Content Quality**
   - Find contradictions between documents
   - Identify outdated information or version mismatches
   - Detect duplicated content across files
   - Check naming convention consistency

6. **Code & Configuration**
   - Validate .env.example files
   - Check docker-compose configurations
   - Verify requirements.txt or pyproject.toml
   - Test sample code blocks where applicable
   - Run shellcheck on all bash examples
   - Validate Python code examples with pylint/flake8
   - If a required tool is unavailable, record the skipped check and suggest a manual alternative.

7. **Language & Readability**
   - Check spelling with aspell/hunspell
   - Verify English-only content (no other languages)
   - Calculate readability scores (Flesch-Kincaid, SMOG)
   - Measure documentation complexity metrics
   - Check technical terminology consistency

8. **Version Consistency**
   - Extract all technology versions mentioned
   - Cross-reference with tech_stack.md
   - Identify version conflicts or mismatches
   - Check dependency compatibility matrix
   - Verify Docker image tags alignment

9. **AI Navigation & Workflow Validation** (NEW - Critical for AI-first framework)
   - Verify Stage 0 initialization sequence (CLAUDE.md → agent-context-summary.md → workflow → maturity-levels.md)
   - Validate Navigation Matrix accuracy (all referenced documents exist)
   - Check workflow coherence (entry/exit criteria alignment)
   - Detect circular dependencies in reading order
   - Ensure maturity levels integrated into workflow stages
   - Update the Stage 0 sequence to match the current repository structure before flagging inconsistencies.

10. **Submodule Path Validation** (NEW - Framework-as-submodule model)
   - Ensure documentation works in standalone and submodule modes
   - Detect hardcoded absolute paths that break in submodule
   - Verify examples show both path variants where relevant
   - Check CLAUDE.md guidance mentions both usage modes

11. **Maturity Levels Consistency** (NEW - Core framework concept)
   - Verify features correctly marked per maturity level (✅/❌)
   - Ensure conditional stage rules align with maturity-levels.md
   - Check upgrade paths documented
   - Validate time estimates consistency (5/10/15/30 min)
   - Verify coverage thresholds per level (60%/75%/80%/85%)

12. **Architectural Constraints Consistency** (NEW - Mandatory patterns)
   - Verify HTTP-only data access mentioned consistently
   - Check service separation principles in examples
   - Ensure API Gateway mandatory for production (Level 3+)
   - Validate RabbitMQ mandatory for async communication
   - Check DEFAULT TO 3-PART naming guidance consistency

13. **Atomic Documentation Coverage** (NEW - Implementation patterns)
   - Verify all atomic docs referenced in Navigation Matrix exist
   - Check atomic docs cover all patterns mentioned in workflow
   - Find orphaned atomic docs (not referenced anywhere)
   - Validate atomic docs completeness per service type

14. **Agent Toolbox Command Validation** (NEW - Executable commands)
   - Verify all commands in agent-toolbox.md are executable
   - Check tool versions align with tech_stack.md
   - Ensure development-commands.md consistent with agent-toolbox.md
   - Test sample commands for syntax correctness

## DELIVERABLES

Create a detailed report with:

### 1. Executive Summary
- Project purpose (1-2 paragraphs)
- Health score (0-100)
- Total issues found with severity breakdown
- Top 3 critical issues

### 2. Issue Categories

#### Link & Reference Issues
- Broken internal links
- Invalid anchor references
- Missing referenced files

#### Content Quality Issues
- Spelling errors with corrections
- Duplicate content locations
- Contradictory information

#### Code Quality Issues
- Shellcheck violations in bash examples
- Python syntax errors in examples
- Invalid JSON/YAML snippets

#### Language & Readability Issues
- Non-English content found
- Complex sentences (>30 words)
- Low readability scores (<30)
- Passive voice overuse

#### Version Consistency Issues
- Conflicting version numbers
- Mismatched dependencies
- Outdated technology references

#### AI Navigation & Workflow Issues (NEW)
- Broken Stage 0 initialization sequence
- Missing documents in Navigation Matrix
- Entry/exit criteria misalignment between stages
- Circular reading dependencies detected
- Maturity levels not integrated into workflow

#### Submodule Compatibility Issues (NEW)
- Hardcoded absolute paths found
- Documentation missing submodule usage guidance
- Examples don't show both standalone/.framework/ paths

#### Maturity Levels Issues (NEW)
- Features incorrectly marked for maturity levels
- Conditional rules misaligned with maturity-levels.md
- Time estimates inconsistent across documents
- Coverage thresholds not matching level requirements

#### Architectural Constraints Issues (NEW)
- Code examples showing direct database access in business services
- Service separation violated in examples
- API Gateway not mandatory for Level 3+ examples
- RabbitMQ missing from async patterns
- 4-part naming used without justification

#### Atomic Documentation Issues (NEW)
- Referenced atomic docs missing
- Orphaned atomic docs found
- Coverage gaps for service types
- Navigation Matrix references broken

#### Toolbox Command Issues (NEW)
- Non-executable commands in agent-toolbox.md
- Tool versions mismatched with tech_stack.md
- Command inconsistency between toolbox and development-commands.md

For each issue, provide:
- **Priority**: CRITICAL / HIGH / MEDIUM / LOW
- **Location**: File path and line numbers
- **Description**: What's broken and why it matters
- **Impact**: How it affects users/AI agents
- **Fix**: Exact commands or changes needed
- **Verification**: How to test the fix

### 3. TODO List

Organize fixes into phases:
- **Phase 1: Quick Fixes** (< 1 hour) - Critical broken links, typos
- **Phase 2: Content Updates** (1-4 hours) - Missing docs, inconsistencies
- **Phase 3: Structural** (> 4 hours) - Architecture changes, major rewrites

For each task:
- Estimated time
- Priority level
- Dependencies (what must be done first)
- Validation command

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

## OUTPUT FORMAT

- Use markdown with clear sections
- Include code blocks with syntax highlighting
- Add file paths as: `/path/to/file.md:123`
- Use tables for large datasets
- Include command examples for fixes

## CONSTRAINTS

- Focus on actionable issues (things that cause errors or confusion)
- Prioritize issues affecting AI agents and developers
- Provide specific fixes, not general suggestions
- Include verification steps for every fix
- Keep recommendations practical and scoped
```

---

## Quick Audit Prompt (Faster, Less Detailed)

```
Quick documentation health check:

1. Find all broken markdown links (internal only)
2. List missing referenced files
3. Check for contradictions in key docs:
   - README.md
   - CLAUDE.md
   - docs/guides/architecture-guide.md
   - docs/INDEX.md

Provide:
- Count of issues by severity
- Top 5 critical issues with file:line locations
- Quick fix commands for each

Time limit: 10 minutes
```

---

## Focused Audit Prompts

### Links Only
```
Check all markdown links in /docs directory:
- Find broken internal links (relative paths)
- Verify anchor links point to valid sections
- Report all issues with file:line format
- Provide sed/awk commands to fix
```

### Structure Only
```
Verify documentation structure:
- Compare docs/INDEX.md with actual files
- Check docs/LINKS_REFERENCE.md paths
- Find orphaned documents
- Validate directory hierarchy
```

### Content Consistency
```
Find content inconsistencies:
- Compare architecture principles across guides
- Check technology versions in all docs
- Find duplicated content
- Identify contradictory instructions
```

### Template Completeness
```
Audit template services:
- List all referenced template files
- Verify which templates exist
- Check completion status
- Validate template examples in docs
```

### Spell Check
```
Run spell checking across all documentation:
- Use aspell/hunspell with technical dictionary
- Identify misspelled words with file:line locations
- Exclude code blocks and file paths
- Generate correction suggestions
- Check proper nouns consistency
```

### Code Examples Validation
```
Validate all code examples in documentation:
- Extract bash scripts and run shellcheck
- Validate Python examples with pylint
- Check JSON/YAML syntax validity
- Verify Docker commands correctness
- Report syntax errors with locations
```

### Readability Analysis
```
Analyze documentation readability:
- Calculate Flesch-Kincaid score per document
- Measure SMOG index for technical docs
- Identify overly complex sentences (>30 words)
- Find passive voice overuse
- Suggest simplifications for score <30
```

### Language Validation
```
Ensure English-only documentation:
- Detect non-English characters (except code)
- Find non-ASCII text outside code blocks
- Identify localized strings or comments
- Check for mixed language sections
- Validate UTF-8 encoding consistency
```

### Version Consistency Check
```
Audit technology versions across docs:
- Extract all version numbers (Python 3.11, Node 18, etc.)
- Compare with canonical tech_stack.md
- Find conflicting version requirements
- Check Docker base image versions
- Validate package.json/requirements.txt versions
```

### AI Navigation Validation (NEW)
```
Validate AI agent navigation and workflow:
- Check Stage 0 initialization: CLAUDE.md → agent-context-summary.md → workflow → maturity-levels.md
- Validate Navigation Matrix: all docs in "Documents to Read" exist
- Check entry/exit criteria alignment between stages
- Detect circular dependencies (A→B→C→A)
- Verify maturity levels mentioned in Stage 1, 3, 5 docs
- Ensure conditional stage rules reference maturity-levels.md

Report:
- Broken navigation paths with file:line
- Missing documents blocking workflow stages
- Circular dependency chains
- Maturity level integration gaps
```

### Submodule Path Audit (NEW)
```
Ensure framework works as standalone and submodule:
- Find absolute project paths (/home/user/project)
- Check for root-absolute paths (/docs/)
- Verify CLAUDE.md mentions both usage modes
- Validate relative path consistency
- Check examples show both docs/ and .framework/docs/ where relevant

Report:
- Hardcoded paths with locations
- Missing submodule guidance
- Incompatible path references
```

### Maturity Levels Audit (NEW)
```
Verify maturity levels consistency:
- Extract Feature Comparison Matrix from maturity-levels.md
- Cross-reference with conditional-stage-rules.md
- Check workflow docs mention maturity levels (prompt-validation, planning, verification)
- Validate time estimates (L1=5min, L2=10min, L3=15min, L4=30min)
- Verify coverage thresholds (60%/75%/80%/85%) in verification docs

Report:
- Feature misalignment per level
- Time estimate conflicts
- Coverage threshold inconsistencies
- Missing maturity level guidance in workflow
```

### Architectural Constraints Audit (NEW)
```
Validate mandatory architectural patterns:
- Check code examples for HTTP-only data access (no direct DB in business services)
- Verify service separation in examples (FastAPI/Aiogram/Worker separate)
- Ensure Nginx mandatory for Level 3+ examples
- Check RabbitMQ used for async communication
- Validate DEFAULT TO 3-PART naming (template_{context}_{domain}_{type})

Report:
- Anti-patterns in code examples (direct DB access, etc.)
- Missing architectural constraints in guides
- Naming convention violations
- Infrastructure gaps per maturity level
```

### Atomic Documentation Coverage (NEW)
```
Verify atomic documentation completeness:
- Extract all atomic doc references from workflow, navigation matrix, planning template
- Verify each referenced atomic doc exists
- Find orphaned atomic docs (exist but never referenced)
- Check coverage per service type (FastAPI, Aiogram, Workers, Data Services)

Report:
- Missing atomic docs (referenced but don't exist)
- Orphaned atomic docs (exist but not referenced)
- Coverage gaps by service type
- Broken atomic doc references in Navigation Matrix
```

### Toolbox Command Audit (NEW)
```
Validate agent toolbox commands:
- Extract all commands from agent-toolbox.md
- Check tool availability and versions vs tech_stack.md
- Compare commands between agent-toolbox.md and development-commands.md
- Test non-destructive commands for syntax (uv --version, ruff --version)

Report:
- Tools used but not documented in tech_stack.md
- Command syntax discrepancies
- Version mismatches
- Non-executable command patterns
```

---

## Automation Script Template

Use the following reference when preparing `scripts/audit_docs.sh`. Adapt it to the current repository tooling and treat it as optional guidance rather than an instruction to run during manual audits.

```bash
#!/bin/bash
# Documentation Audit Script
# Usage: ./scripts/audit_docs.sh [--quick|--full|--links|--structure]

set -e

MODE="${1:---full}"
DOCS_DIR="docs"
PARALLEL_JOBS=$(nproc 2>/dev/null || echo 4)  # Auto-detect CPU cores

echo "=== Documentation Audit ==="
echo "Mode: $MODE"
echo "Docs Directory: $DOCS_DIR"
echo "Parallel Jobs: $PARALLEL_JOBS"
echo ""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Process markdown files in parallel using xargs
# Usage: process_md_files <function_name>
# Example: process_md_files check_link_in_file
process_md_files() {
    local func="$1"
    export -f "$func"  # Export function for subshells

    find "$DOCS_DIR" -name "*.md" -print0 | \
        xargs -0 -P "$PARALLEL_JOBS" -I {} bash -c "$func \"\$@\"" _ {}
}

# Check links in a single markdown file
# Usage: check_link_in_file <file_path>
check_link_in_file() {
    local file="$1"

    grep -Hn '\[.*\](.*\.md' "$file" 2>/dev/null | \
    while IFS=: read -r filepath line link; do
        # Extract path from link
        local path
        path=$(echo "$link" | sed 's/.*(\\(.*\\.md\\).*/\\1/')

        # Check if file exists (try relative and absolute paths)
        if [ ! -f "$path" ] && [ ! -f "$DOCS_DIR/$path" ] && [ ! -f "$(dirname "$file")/$path" ]; then
            echo "BROKEN: $file:$line -> $path"
        fi
    done
}

# Check spelling in a single markdown file
# Usage: check_spelling_in_file <file_path>
check_spelling_in_file() {
    local file="$1"

    # Check if aspell is available
    if ! command -v aspell &> /dev/null; then
        return 0
    fi

    # Extract text outside code blocks and check spelling
    sed '/^```/,/^```/d' "$file" | \
    aspell list --lang=en --mode=markdown --personal=/dev/null 2>/dev/null | \
    sort | uniq | while read -r word; do
        # Find first occurrence with line number
        local line_info
        line_info=$(grep -n "$word" "$file" 2>/dev/null | head -1)
        if [ -n "$line_info" ]; then
            echo "SPELLING: $file:${line_info%%:*} - '$word'"
        fi
    done
}

# Check code examples in a single markdown file
# Usage: check_code_in_file <file_path>
check_code_in_file() {
    local file="$1"
    local temp_bash="/tmp/check_bash_$$.sh"
    local temp_python="/tmp/check_python_$$.py"

    # Extract and check bash code blocks
    if command -v shellcheck &> /dev/null; then
        awk '/^```bash/,/^```/' "$file" | sed '1d;$d' > "$temp_bash"
        if [ -s "$temp_bash" ]; then
            shellcheck "$temp_bash" 2>&1 | while read -r issue; do
                echo "SHELLCHECK: $file - $issue"
            done
        fi
        rm -f "$temp_bash"
    fi

    # Extract and check Python code blocks
    if command -v python3 &> /dev/null; then
        awk '/^```python/,/^```/' "$file" | sed '1d;$d' > "$temp_python"
        if [ -s "$temp_python" ]; then
            python3 -m py_compile "$temp_python" 2>&1 | while read -r issue; do
                echo "PYTHON: $file - $issue"
            done
        fi
        rm -f "$temp_python"
    fi
}

# Check readability metrics for a single markdown file
# Usage: check_readability_in_file <file_path>
check_readability_in_file() {
    local file="$1"

    # Count average words per sentence (excluding code blocks)
    local avg_words
    avg_words=$(sed '/^```/,/^```/d' "$file" | \
               sed 's/\. /.\n/g' | \
               awk 'NF>0 {words+=NF; sentences++} END {if(sentences>0) printf "%.1f", words/sentences; else print "0"}')

    # Count long sentences (>30 words)
    local long_sentences
    long_sentences=$(sed '/^```/,/^```/d' "$file" | \
                    sed 's/\. /.\n/g' | \
                    awk 'NF>30 {count++} END {print count+0}')

    echo "READABILITY: $file - Avg words/sentence: $avg_words, Long sentences: $long_sentences"
}

# Check for non-English content in a single markdown file
# Usage: check_language_in_file <file_path>
check_language_in_file() {
    local file="$1"

    # Check for non-ASCII characters outside code blocks
    sed '/^```/,/^```/d' "$file" | \
    grep -n '[^ -~]' 2>/dev/null | while IFS=: read -r line content; do
        echo "NON-ASCII: $file:$line - ${content:0:80}"
    done

    # Check for common non-English patterns (Cyrillic, CJK, etc.)
    sed '/^```/,/^```/d' "$file" | \
    grep -nE '[а-яА-Я]|[一-龯]|[ぁ-ゔ]|[ァ-ヴー]|[가-힣]' 2>/dev/null | while IFS=: read -r line content; do
        echo "NON-ENGLISH: $file:$line - ${content:0:80}"
    done
}

# Check AI navigation patterns in a single markdown file
# Usage: check_ai_navigation_in_file <file_path>
check_ai_navigation_in_file() {
    local file="$1"

    # Check for Stage 0 documents in workflow docs
    if echo "$file" | grep -q "workflow\|CLAUDE.md"; then
        # Verify Stage 0 sequence references
        for doc in "CLAUDE.md" "agent-context-summary.md" "ai-code-generation-master-workflow.md" "maturity-levels.md"; do
            if grep -q "$doc" "$file" 2>/dev/null; then
                local referenced_path=$(grep -o "[^(]*${doc}" "$file" | head -1)
                if [ -n "$referenced_path" ] && [ ! -f "$referenced_path" ]; then
                    echo "AI_NAV: $file references $doc at non-existent path: $referenced_path"
                fi
            fi
        done
    fi

    # Check for Navigation Matrix references
    if echo "$file" | grep -q "navigation-matrix\|implementation-plan"; then
        grep -oE 'docs/[^`)\s]*\.md' "$file" 2>/dev/null | while read -r ref; do
            if [ ! -f "$ref" ]; then
                echo "AI_NAV: $file references missing doc: $ref"
            fi
        done
    fi
}

# Check for hardcoded absolute paths that break in submodule mode
# Usage: check_submodule_paths_in_file <file_path>
check_submodule_paths_in_file() {
    local file="$1"

    # Skip code blocks for path checking
    sed '/^```/,/^```/d' "$file" | grep -nE '/home/|/Users/|^/docs/' 2>/dev/null | while IFS=: read -r line content; do
        echo "SUBMODULE: $file:$line - Absolute path: ${content:0:100}"
    done
}

# Check maturity level consistency in workflow documents
# Usage: check_maturity_levels_in_file <file_path>
check_maturity_levels_in_file() {
    local file="$1"

    # Check if workflow/planning docs mention maturity levels
    if echo "$file" | grep -qE "prompt-validation|implementation-plan|verification-checklist"; then
        if ! grep -qi "maturity level\|Level [1-4]\|PoC\|Development\|Pre-Production\|Production" "$file"; then
            echo "MATURITY: $file - Missing maturity level guidance"
        fi
    fi

    # Check for coverage thresholds in verification docs
    if echo "$file" | grep -q "verification"; then
        if ! grep -qE "60%|75%|80%|85%" "$file"; then
            echo "MATURITY: $file - Missing level-specific coverage thresholds"
        fi
    fi
}

# Check architectural constraints in code examples
# Usage: check_architecture_patterns_in_file <file_path>
check_architecture_patterns_in_file() {
    local file="$1"
    local temp_code="/tmp/arch_check_$$.py"

    # Extract Python code blocks
    awk '/^```python/,/^```/' "$file" | sed '1d;$d' > "$temp_code"

    if [ -s "$temp_code" ]; then
        # Check for direct DB access in business service examples
        if echo "$file" | grep -qE "business|use-case"; then
            if grep -qE "from sqlalchemy import|session\.execute|session\.commit|db\.query" "$temp_code"; then
                echo "ARCHITECTURE: $file - Direct database access in business service example (violates HTTP-only)"
            fi
        fi

        # Check for HTTP client usage in business services
        if echo "$file" | grep -q "use-case"; then
            if ! grep -qE "HTTPClient|http_client|\.get\(|\.post\(" "$temp_code"; then
                echo "ARCHITECTURE: $file - Use case example doesn't show HTTP client pattern"
            fi
        fi
    fi

    rm -f "$temp_code"
}

# Export all helper functions for use in subshells
export -f check_link_in_file
export -f check_spelling_in_file
export -f check_code_in_file
export -f check_readability_in_file
export -f check_language_in_file
export -f check_ai_navigation_in_file
export -f check_submodule_paths_in_file
export -f check_maturity_levels_in_file
export -f check_architecture_patterns_in_file
export DOCS_DIR

# ============================================================================
# MAIN AUDIT FUNCTIONS
# ============================================================================

# Function: Check Markdown Links (optimized with parallel processing)
check_links() {
    echo "Checking markdown links (parallel processing)..."
    process_md_files check_link_in_file
}

# Function: Check File References
check_files() {
    echo "Checking referenced files..."
    grep -rh '`[^`]*\.md`' "$DOCS_DIR" | \
    sed 's/.*`\([^`]*\.md\)`.*/\1/' | sort | uniq | \
    while read -r file; do
        if [ ! -f "$file" ] && [ ! -f "$DOCS_DIR/$file" ]; then
            echo "MISSING: $file"
        fi
    done
}

# Function: Check Structure
check_structure() {
    echo "Checking structure consistency..."

    # Compare INDEX.md with actual files
    echo "Files in INDEX.md vs actual:"
    diff <(grep -o '[^(]*\.md' "$DOCS_DIR/INDEX.md" | sort) \
         <(find "$DOCS_DIR" -name "*.md" | sed "s|$DOCS_DIR/||" | sort)
}

# Function: Find Duplicates
check_duplicates() {
    echo "Checking for duplicate content..."

    # Find files with similar names
    find "$DOCS_DIR" -name "*.md" -exec basename {} \; | sort | uniq -d

    # Check for duplicate headings across files
    grep -rh '^# ' "$DOCS_DIR" | sort | uniq -d
}

# Function: Spell Check (optimized with parallel processing)
check_spelling() {
    echo "Checking spelling (parallel processing)..."

    # Check if aspell is installed
    if ! command -v aspell &> /dev/null; then
        echo "WARNING: aspell not installed. Install with: apt-get install aspell aspell-en"
        return 1
    fi

    process_md_files check_spelling_in_file
}

# Function: Validate Code Examples (optimized with parallel processing)
check_code_examples() {
    echo "Validating code examples (parallel processing)..."

    # Check if required tools are installed
    if ! command -v shellcheck &> /dev/null; then
        echo "WARNING: shellcheck not installed. Install with: apt-get install shellcheck"
    fi

    process_md_files check_code_in_file
}

# Function: Check Readability (optimized with parallel processing)
check_readability() {
    echo "Analyzing readability (parallel processing)..."
    process_md_files check_readability_in_file
}

# Function: Check Language (English only - optimized with parallel processing)
check_language() {
    echo "Checking for non-English content (parallel processing)..."
    process_md_files check_language_in_file
}

# Function: Check Version Consistency (optimized with parallel grep)
check_versions() {
    echo "Checking version consistency (optimized)..."

    # Extract all version patterns using parallel grep
    VERSIONS_FILE="/tmp/versions_found_$$.txt"
    > "$VERSIONS_FILE"

    # Use grep -rhoE for recursive, parallel processing
    # Python versions
    grep -rhoE 'Python[ ]?[0-9]+\.[0-9]+(\.[0-9]+)?' "$DOCS_DIR" --include="*.md" >> "$VERSIONS_FILE" 2>/dev/null || true
    # Node versions
    grep -rhoE 'Node(\.js)?[ ]?v?[0-9]+(\.[0-9]+)*' "$DOCS_DIR" --include="*.md" >> "$VERSIONS_FILE" 2>/dev/null || true
    # Docker images with tags
    grep -rhoE '[a-z]+:[0-9]+\.[0-9]+(\.[0-9]+)?(-[a-z]+)?' "$DOCS_DIR" --include="*.md" >> "$VERSIONS_FILE" 2>/dev/null || true
    # Generic version patterns
    grep -rhoE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' "$DOCS_DIR" --include="*.md" >> "$VERSIONS_FILE" 2>/dev/null || true

    # Show version conflicts
    if [ -s "$VERSIONS_FILE" ]; then
        sort "$VERSIONS_FILE" | uniq -c | sort -rn | while read -r count version; do
            if [ "$count" -gt 1 ]; then
                echo "VERSION: '$version' appears $count times - check for consistency"
            fi
        done
    fi

    # Cleanup
    rm -f "$VERSIONS_FILE"
}

# Function: Check AI Navigation & Workflow (NEW)
check_ai_navigation() {
    echo "Checking AI navigation and workflow (NEW)..."

    # Check Stage 0 initialization sequence
    echo "Verifying Stage 0 sequence..."
    for doc in CLAUDE.md \
               docs/reference/agent-context-summary.md \
               docs/guides/ai-code-generation-master-workflow.md \
               docs/reference/maturity-levels.md; do
        [ ! -f "$doc" ] && echo "CRITICAL: Missing Stage 0 document: $doc"
    done

    # Check Navigation Matrix references
    if [ -f "docs/reference/ai-navigation-matrix.md" ]; then
        echo "Validating Navigation Matrix references..."
        grep -oE 'docs/[^`)\s]*\.md' docs/reference/ai-navigation-matrix.md | sort -u | while read -r ref; do
            [ ! -f "$ref" ] && echo "AI_NAV: Navigation Matrix references missing: $ref"
        done
    fi

    # Parallel check for navigation issues in all docs
    process_md_files check_ai_navigation_in_file
}

# Function: Check Submodule Path Compatibility (NEW)
check_submodule_paths() {
    echo "Checking submodule path compatibility (NEW)..."

    # Check for absolute paths
    echo "Finding hardcoded absolute paths..."
    grep -rn '/home/\|/Users/' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | \
        grep -v '.git' | head -20

    # Parallel check for path issues
    process_md_files check_submodule_paths_in_file

    # Check CLAUDE.md mentions both modes
    if [ -f "CLAUDE.md" ]; then
        if ! grep -q "submodule\|\.framework/" CLAUDE.md; then
            echo "SUBMODULE: CLAUDE.md missing submodule usage guidance"
        fi
    fi
}

# Function: Check Maturity Levels Consistency (NEW)
check_maturity_levels() {
    echo "Checking maturity levels consistency (NEW)..."

    # Check maturity level integration in workflow
    for doc in docs/guides/prompt-validation-guide.md \
               docs/guides/implementation-plan-template.md \
               docs/quality/agent-verification-checklist.md; do
        if [ -f "$doc" ]; then
            if ! grep -qi "maturity level\|Level [1-4]" "$doc"; then
                echo "MATURITY: $doc missing maturity level guidance"
            fi
        fi
    done

    # Check coverage thresholds
    if [ -f "docs/quality/agent-verification-checklist.md" ]; then
        if ! grep -qE "60%|75%|80%|85%" docs/quality/agent-verification-checklist.md; then
            echo "MATURITY: agent-verification-checklist.md missing level-specific thresholds"
        fi
    fi

    # Parallel check for maturity level consistency
    process_md_files check_maturity_levels_in_file
}

# Function: Check Architectural Constraints (NEW)
check_architecture_patterns() {
    echo "Checking architectural constraints (NEW)..."

    # Check for HTTP-only data access mentions
    echo "Validating HTTP-only data access principle..."
    http_mentions=$(grep -rc "HTTP-only\|http_client\|HTTPClient" "$DOCS_DIR" --include="*.md" | grep -v ":0" | wc -l)
    echo "HTTP-only pattern mentioned in $http_mentions documents"

    # Check for 3-part naming guidance
    echo "Validating naming conventions..."
    if ! grep -rq "DEFAULT TO 3-PART\|default to 3-part" "$DOCS_DIR"; then
        echo "ARCHITECTURE: Missing 'DEFAULT TO 3-PART' naming guidance"
    fi

    # Parallel check for architecture violations in code examples
    process_md_files check_architecture_patterns_in_file
}

# Function: Check Atomic Documentation Coverage (NEW)
check_atomic_coverage() {
    echo "Checking atomic documentation coverage (NEW)..."

    # Extract atomic doc references
    echo "Finding referenced atomic docs..."
    ATOMIC_REFS="/tmp/atomic_refs_$$.txt"
    grep -rhoE 'docs/atomic/[^`)\s]*\.md' docs/guides/ docs/reference/ 2>/dev/null | \
        sort -u > "$ATOMIC_REFS"

    # Check if referenced docs exist
    if [ -s "$ATOMIC_REFS" ]; then
        while read -r ref; do
            [ ! -f "$ref" ] && echo "ATOMIC: Referenced but missing: $ref"
        done < "$ATOMIC_REFS"
    fi

    # Find orphaned atomic docs
    echo "Finding orphaned atomic docs..."
    if [ -d "docs/atomic" ]; then
        comm -23 \
            <(find docs/atomic -name "*.md" | sort) \
            <(cat "$ATOMIC_REFS") | head -10 | while read -r orphan; do
                echo "ATOMIC: Orphaned (not referenced): $orphan"
            done
    fi

    rm -f "$ATOMIC_REFS"
}

# Function: Check Toolbox Command Validity (NEW)
check_toolbox_commands() {
    echo "Checking agent toolbox commands (NEW)..."

    # Check if toolbox exists
    if [ ! -f "docs/reference/agent-toolbox.md" ]; then
        echo "TOOLBOX: agent-toolbox.md not found"
        return 1
    fi

    # Extract commands from toolbox
    echo "Extracting commands from agent-toolbox.md..."
    TOOLBOX_CMDS="/tmp/toolbox_cmds_$$.txt"
    grep -oE 'uv run [a-z]+|docker-compose [a-z]+|pytest|ruff|mypy|bandit' \
        docs/reference/agent-toolbox.md | sort -u > "$TOOLBOX_CMDS"

    # Check for tool availability
    for tool in uv ruff mypy pytest bandit docker-compose; do
        if grep -q "$tool" "$TOOLBOX_CMDS"; then
            if ! grep -q "$tool" docs/reference/tech_stack.md 2>/dev/null; then
                echo "TOOLBOX: Tool '$tool' used but not documented in tech_stack.md"
            fi
        fi
    done

    rm -f "$TOOLBOX_CMDS"
}

# Main execution
case "$MODE" in
    --quick)
        check_links
        check_spelling
        check_ai_navigation
        ;;
    --links)
        check_links
        ;;
    --structure)
        check_structure
        ;;
    --spelling)
        check_spelling
        ;;
    --code)
        check_code_examples
        ;;
    --readability)
        check_readability
        ;;
    --language)
        check_language
        ;;
    --versions)
        check_versions
        ;;
    --ai-navigation)
        check_ai_navigation
        ;;
    --submodule)
        check_submodule_paths
        ;;
    --maturity)
        check_maturity_levels
        ;;
    --architecture)
        check_architecture_patterns
        ;;
    --atomic)
        check_atomic_coverage
        ;;
    --toolbox)
        check_toolbox_commands
        ;;
    --ai-full)
        echo "=== AI-Specific Audits ==="
        check_ai_navigation
        check_submodule_paths
        check_maturity_levels
        check_architecture_patterns
        check_atomic_coverage
        check_toolbox_commands
        ;;
    --full)
        echo "=== Standard Audits ==="
        check_links
        check_files
        check_structure
        check_duplicates
        check_spelling
        check_code_examples
        check_readability
        check_language
        check_versions
        echo ""
        echo "=== AI-Specific Audits (NEW) ==="
        check_ai_navigation
        check_submodule_paths
        check_maturity_levels
        check_architecture_patterns
        check_atomic_coverage
        check_toolbox_commands
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo ""
        echo "Usage: $0 [MODE]"
        echo ""
        echo "Standard Modes:"
        echo "  --quick         Quick check (links, spelling, AI navigation)"
        echo "  --full          Full audit (all standard + AI checks)"
        echo "  --links         Markdown link validation"
        echo "  --structure     Directory structure validation"
        echo "  --spelling      Spell checking"
        echo "  --code          Code example validation"
        echo "  --readability   Readability analysis"
        echo "  --language      English-only validation"
        echo "  --versions      Version consistency check"
        echo ""
        echo "AI-Specific Modes (NEW):"
        echo "  --ai-full       Run all AI-specific audits"
        echo "  --ai-navigation AI workflow navigation validation"
        echo "  --submodule     Submodule path compatibility"
        echo "  --maturity      Maturity levels consistency"
        echo "  --architecture  Architectural constraints validation"
        echo "  --atomic        Atomic documentation coverage"
        echo "  --toolbox       Agent toolbox command validation"
        exit 1
        ;;
esac

echo ""
echo "=== Audit Complete ==="
```

---

## CI/CD Integration

### GitHub Actions Workflow

`.github/workflows/docs-validation.yml`:

```yaml
name: Documentation Validation

on:
  push:
    paths:
      - 'docs/**/*.md'
      - '*.md'
  pull_request:
    paths:
      - 'docs/**/*.md'
      - '*.md'

jobs:
  validate-docs:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Check markdown links
        run: |
          echo "Checking all markdown links..."
          find docs -name "*.md" -exec grep -Hn '\[.*\](.*\.md' {} \; | \
          while IFS=: read -r file line link; do
            path=$(echo "$link" | sed 's/.*(\(.*\.md\).*/\1/')
            if [ ! -f "$path" ] && [ ! -f "docs/$path" ]; then
              echo "::error file=$file,line=$line::Broken link: $path"
              exit 1
            fi
          done

      - name: Check structure
        run: |
          echo "Validating INDEX.md against actual structure..."
          if ! diff <(grep -o '[^(]*\.md' docs/INDEX.md | sort) \
                    <(find docs -name "*.md" | sed 's|docs/||' | sort); then
            echo "::error::INDEX.md doesn't match actual file structure"
            exit 1
          fi

      - name: Markdown lint
        uses: DavidAnson/markdownlint-cli2-action@v11
        with:
          globs: 'docs/**/*.md'

      - name: Install validation tools
        run: |
          sudo apt-get update
          sudo apt-get install -y aspell aspell-en shellcheck
          pip install textstat

      - name: Check spelling
        run: ./scripts/audit_docs.sh --spelling

      - name: Validate code examples
        run: ./scripts/audit_docs.sh --code

      - name: Check language consistency
        run: ./scripts/audit_docs.sh --language

      - name: Check version consistency (optimized)
        run: |
          echo "Checking version consistency (using grep -r for speed)..."
          # Extract Python versions
          python_versions=$(grep -rhoE 'Python[ ]?[0-9]+\.[0-9]+' docs --include="*.md" 2>/dev/null | sort -u | wc -l)
          if [ "$python_versions" -gt 1 ]; then
            echo "::warning::Multiple Python versions found. Check consistency."
            grep -rhoE 'Python[ ]?[0-9]+\.[0-9]+' docs --include="*.md" | sort | uniq -c
          fi
          # Extract Node versions
          node_versions=$(grep -rhoE 'Node(\.js)?[ ]?v?[0-9]+' docs --include="*.md" 2>/dev/null | sort -u | wc -l)
          if [ "$node_versions" -gt 1 ]; then
            echo "::warning::Multiple Node versions found. Check consistency."
            grep -rhoE 'Node(\.js)?[ ]?v?[0-9]+' docs --include="*.md" | sort | uniq -c
          fi
```

---

## Pre-commit Hook

`.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to validate documentation

echo "Running documentation validation..."

# Temporary file to track errors across subshells
ERROR_FLAG="/tmp/precommit_errors_$$"
rm -f "$ERROR_FLAG"

# Check for broken links in staged markdown files
git diff --cached --name-only | grep '\.md$' | while read file; do
    echo "Checking $file..."

    # Extract links
    grep -n '\[.*\](.*\.md' "$file" | while IFS=: read -r line link; do
        path=$(echo "$link" | sed 's/.*(\(.*\.md\).*/\1/')

        if [ ! -f "$path" ] && [ ! -f "docs/$path" ]; then
            echo "ERROR: Broken link in $file:$line -> $path"
            echo "1" > "$ERROR_FLAG"
        fi
    done
done

# Check if errors were found
if [ -f "$ERROR_FLAG" ]; then
    rm -f "$ERROR_FLAG"
    echo "Documentation validation failed. Commit aborted."
    exit 1
fi

echo "Documentation validation passed."
```

---

## Usage Examples

### Run Full Audit
```bash
# Using AI agent
claude-code "Run comprehensive documentation audit using the template in .claude/prompts/documentation_audit.md"

# Using script
./scripts/audit_docs.sh --full > audit_results.txt
```

### Quick Link Check
```bash
# Using AI agent
claude-code "Quick audit: check only markdown links"

# Using script
./scripts/audit_docs.sh --links
```

### Spell Check
```bash
# Install dependencies first
sudo apt-get install aspell aspell-en

# Run spell check
./scripts/audit_docs.sh --spelling

# Add custom dictionary for technical terms
echo "kubernetes\ndocker\nfastapi\naiogram" > ~/.aspell.en.pws
```

### Code Examples Validation
```bash
# Install shellcheck for bash validation
sudo apt-get install shellcheck

# Validate all code examples
./scripts/audit_docs.sh --code

# Check specific file's code blocks
shellcheck <(awk '/^```bash/,/^```/' docs/guides/quickstart.md | sed '1d;$d')
```

### Readability Analysis
```bash
# Check documentation readability
./scripts/audit_docs.sh --readability

# Install advanced readability tools
pip install textstat
python -c "import textstat; print(textstat.flesch_reading_ease(open('README.md').read()))"
```

### Language Validation (English-only)
```bash
# Check for non-English content
./scripts/audit_docs.sh --language

# Find all non-ASCII characters
find docs -name "*.md" -exec grep -Hn '[^ -~]' {} \; | grep -v '^```'
```

### Version Consistency
```bash
# Check technology versions
./scripts/audit_docs.sh --versions

# Compare with tech_stack.md
diff <(grep -oE 'Python [0-9.]+' docs/reference/tech_stack.md) \
     <(grep -rhoE 'Python [0-9.]+' docs | sort -u)
```

### Before Release
```bash
# Full validation pipeline with all new checks
./scripts/audit_docs.sh --full
pytest docs/tests/
markdownlint docs/**/*.md

# Generate comprehensive report
./scripts/audit_docs.sh --full > AUDIT_REPORT_$(date +%Y%m%d).md
```

### Continuous Monitoring
```bash
# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "Running documentation quality checks..."
./scripts/audit_docs.sh --quick
if [ $? -ne 0 ]; then
    echo "Documentation issues found. Run './scripts/audit_docs.sh --full' for details."
    exit 1
fi
EOF
chmod +x .git/hooks/pre-push
```

### AI Navigation Validation (NEW)
```bash
# Check AI workflow navigation
./scripts/audit_docs.sh --ai-navigation

# Verify Stage 0 sequence manually
for doc in CLAUDE.md \
           docs/reference/agent-context-summary.md \
           docs/guides/ai-code-generation-master-workflow.md \
           docs/reference/maturity-levels.md; do
  [ -f "$doc" ] && echo "✅ $doc" || echo "❌ MISSING: $doc"
done

# Check Navigation Matrix references
if [ -f "docs/reference/ai-navigation-matrix.md" ]; then
  grep -oE 'docs/[^`)\s]*\.md' docs/reference/ai-navigation-matrix.md | \
    while read ref; do
      [ -f "$ref" ] && echo "✅ $ref" || echo "❌ MISSING: $ref"
    done
fi
```

### Submodule Path Validation (NEW)
```bash
# Check for hardcoded absolute paths
./scripts/audit_docs.sh --submodule

# Find all absolute paths manually
grep -rn '/home/\|/Users/' docs/ README.md CLAUDE.md | grep -v '.git'

# Check CLAUDE.md mentions both modes
grep -i "submodule\|\.framework/" CLAUDE.md
```

### Maturity Levels Consistency (NEW)
```bash
# Check maturity level integration
./scripts/audit_docs.sh --maturity

# Verify maturity levels in workflow docs
for doc in docs/guides/prompt-validation-guide.md \
           docs/guides/implementation-plan-template.md \
           docs/quality/agent-verification-checklist.md; do
  echo "=== $doc ==="
  grep -i "maturity level\|Level [1-4]\|PoC\|Development\|Production" "$doc" || \
    echo "⚠️ No maturity level guidance found"
done

# Check coverage thresholds
grep -E "60%|75%|80%|85%" docs/quality/agent-verification-checklist.md
```

### Architectural Constraints Validation (NEW)
```bash
# Check architectural patterns in documentation
./scripts/audit_docs.sh --architecture

# Check for HTTP-only data access mentions
grep -rc "HTTP-only\|http_client\|HTTPClient" docs/ --include="*.md" | grep -v ":0"

# Check for 3-part naming guidance
grep -rn "DEFAULT TO 3-PART\|default to 3-part" docs/

# Find direct DB access anti-patterns in examples
grep -rn "from sqlalchemy import\|session.execute" docs/ --include="*.md" | \
  grep -v "data_service"
```

### Atomic Documentation Coverage (NEW)
```bash
# Check atomic doc coverage
./scripts/audit_docs.sh --atomic

# List all referenced atomic docs
grep -rhoE 'docs/atomic/[^`)\s]*\.md' docs/guides/ docs/reference/ | sort -u

# Find orphaned atomic docs
comm -23 \
  <(find docs/atomic -name "*.md" | sort) \
  <(grep -rhoE 'docs/atomic/[^`)\s]*\.md' docs/guides/ docs/reference/ | sort -u)

# Check coverage by service type
for type in fastapi aiogram asyncio-workers data-services; do
  echo "=== $type ==="
  find docs/atomic/services/$type -name "*.md" 2>/dev/null | wc -l
done
```

### Toolbox Command Validation (NEW)
```bash
# Check toolbox commands
./scripts/audit_docs.sh --toolbox

# Extract and verify commands
grep -oE 'uv run [a-z]+|ruff|mypy|pytest' docs/reference/agent-toolbox.md | sort -u

# Check tools documented in tech_stack.md
for tool in uv ruff mypy pytest bandit docker-compose; do
  grep -q "$tool" docs/reference/tech_stack.md && \
    echo "✅ $tool" || echo "⚠️ $tool not in tech_stack.md"
done

# Compare toolbox vs development-commands
diff -u \
  <(grep -oE 'uv run [a-z]+' docs/reference/agent-toolbox.md | sort -u) \
  <(grep -oE 'uv run [a-z]+' docs/guides/development-commands.md | sort -u)
```

### Run All AI-Specific Audits (NEW)
```bash
# Run all AI-specific checks at once
./scripts/audit_docs.sh --ai-full

# Generate AI-specific audit report
./scripts/audit_docs.sh --ai-full > AI_AUDIT_REPORT_$(date +%Y%m%d).md

# CI/CD: Run AI audits in pipeline
./scripts/audit_docs.sh --ai-full
if [ $? -ne 0 ]; then
  echo "::error::AI-specific documentation issues found"
  exit 1
fi
```

---

## Maintenance Schedule

### Standard Checks
- **Weekly**: Automated link checking in CI
- **Bi-weekly**: Spell checking and code validation
- **Monthly**: Full audit with AI agent
- **Quarterly**: Technology version consistency check
- **Yearly**: Comprehensive structure review

### AI-Specific Checks (NEW)
- **Daily (CI/CD)**: AI navigation validation on every PR
- **Weekly**: Maturity levels and architectural constraints audit
- **Bi-weekly**: Atomic documentation coverage check
- **Monthly**: Toolbox command validation and submodule path audit
- **Before major releases**: Full AI audit (`--ai-full`)

---

## What's New in This Version

This updated audit template adds **7 critical categories** specifically designed for AI-first microservices framework:

### 🎯 **High Priority Additions**

1. **AI Navigation & Workflow Validation** (Objective 9)
   - Ensures AI agents can navigate 7-stage workflow
   - Validates Stage 0 initialization sequence
   - Checks Navigation Matrix completeness
   - Detects circular dependencies

2. **Maturity Levels Consistency** (Objective 11)
   - Verifies 4 maturity levels (PoC → Production)
   - Validates conditional stage rules
   - Checks coverage thresholds (60%/75%/80%/85%)

3. **Architectural Constraints Consistency** (Objective 12)
   - Validates HTTP-only data access in examples
   - Checks service separation principles
   - Ensures DEFAULT TO 3-PART naming
   - Verifies mandatory infrastructure per level

4. **Atomic Documentation Coverage** (Objective 13)
   - Validates all atomic doc references
   - Finds orphaned documentation
   - Checks coverage per service type

### 🛠️ **Medium Priority Additions**

5. **Submodule Path Validation** (Objective 10)
   - Ensures framework works as standalone AND submodule
   - Detects hardcoded absolute paths
   - Validates relative path consistency

6. **Toolbox Command Validation** (Objective 14)
   - Verifies executable commands
   - Checks tool version alignment
   - Validates command consistency

### 📊 **New Features**

- **6 new focused audit prompts** for targeted checks
- **6 new shell functions** with parallel processing
- **New audit modes**: `--ai-full`, `--ai-navigation`, `--submodule`, `--maturity`, `--architecture`, `--atomic`, `--toolbox`
- **Enhanced CI/CD examples** for AI-specific validations
- **10+ new usage examples** with practical commands

### 🚀 **Performance Improvements**

- All new functions use parallel processing where applicable
- Optimized grep patterns for large documentation trees
- Efficient temporary file handling

---

## Shell Scripting Best Practices

### Pattern Comparison: find | while vs find | xargs

#### ❌ Anti-pattern: `find | while read`

```bash
# SLOW: Creates subshell per iteration, no parallelism
find "$DOCS_DIR" -name "*.md" | while read -r file; do
    process_file "$file"
done
```

**Problems:**
- Sequential execution (one file at a time)
- Subshell created for each iteration
- Variables set inside loop not visible outside
- Breaks with filenames containing spaces/newlines
- ~10x slower on large projects (>100 files)

#### ✅ Best practice: `find -print0 | xargs -0 -P`

```bash
# FAST: Parallel processing, no subshells
find "$DOCS_DIR" -name "*.md" -print0 | \
    xargs -0 -P 4 -I {} bash -c 'process_file "$@"' _ {}
```

**Advantages:**
- Parallel execution (4 processes simultaneously)
- Handles special characters correctly (-print0/-0)
- 4-8x faster on multi-core systems
- Better resource utilization

### Pattern Comparison: Multiple grep loops vs grep -r

#### ❌ Anti-pattern: Loop with grep per file

```bash
# SLOW: Multiple process spawns
find "$DOCS_DIR" -name "*.md" | while read -r file; do
    grep -oE 'pattern' "$file" >> output.txt
done
```

#### ✅ Best practice: Single recursive grep

```bash
# FAST: Single process, internal optimization
grep -rhoE 'pattern' "$DOCS_DIR" --include="*.md" >> output.txt
```

**Advantages:**
- Single process invocation
- Internal parallelization (ripgrep/modern grep)
- Optimized directory traversal
- 5-10x faster than loop

### Performance Optimization Guidelines

1. **Determine CPU cores available:**
   ```bash
   PARALLEL_JOBS=$(nproc)  # Linux
   PARALLEL_JOBS=$(sysctl -n hw.ncpu)  # macOS
   ```

2. **Adjust parallelism based on task type:**
   - CPU-bound tasks (shellcheck, parsing): `PARALLEL_JOBS=$(nproc)`
   - I/O-bound tasks (file reading): `PARALLEL_JOBS=$(($(nproc) * 2))`
   - Network tasks: Higher parallelism (8-16)

3. **Use appropriate tools:**
   - File search: `find` with `-print0`
   - Content search: `grep -r` or `ripgrep`
   - Parallel execution: `xargs -P` or GNU `parallel`
   - Text processing: `awk`, `sed` (avoid loops)

### Common Mistakes to Avoid

| Mistake | Problem | Solution |
|---------|---------|----------|
| `for file in $(find ...)` | Word splitting, no quotes | Use `find -print0 \| xargs -0` |
| `cat file \| grep pattern` | Useless use of cat (UUOC) | `grep pattern file` |
| `grep pattern \| wc -l` | Inefficient | `grep -c pattern` |
| Nested loops for file operations | O(n²) complexity | Use associative arrays or single pass |
| `$(command)` in loops | Multiple subprocess spawns | Move outside loop or use xargs |

### Benchmarking Example

Test with 100 markdown files (avg 50KB each):

```bash
# Method 1: find | while read (sequential)
time find docs -name "*.md" | while read -r f; do
    grep -c "TODO" "$f" > /dev/null
done
# Result: ~2.5 seconds

# Method 2: find | xargs (parallel, 4 cores)
time find docs -name "*.md" -print0 | \
    xargs -0 -P 4 grep -c "TODO" > /dev/null
# Result: ~0.6 seconds (4x faster)

# Method 3: grep -r (optimized)
time grep -rc "TODO" docs --include="*.md" > /dev/null
# Result: ~0.3 seconds (8x faster)
```

### Memory Considerations

- **xargs**: Processes files in batches (default: as many as fit in ARG_MAX)
- **find -exec**: One fork per file (slower but lower memory)
- **grep -r**: Loads directory tree into memory (fast but higher memory)

**Rule of thumb:**
- < 1000 files: Use any method
- 1000-10000 files: Prefer `xargs -P` or `grep -r`
- > 10000 files: Use `xargs -P` with batching or GNU parallel

### Debugging Parallel Scripts

1. **Test with single file first:**
   ```bash
   echo "docs/README.md" | xargs -I {} bash -c 'your_function "$@"' _ {}
   ```

2. **Add verbose output:**
   ```bash
   find docs -name "*.md" -print0 | \
       xargs -0 -P 4 -t -I {} bash -c 'echo "Processing {}"; your_function "{}"'
   ```

3. **Use `-P 1` to disable parallelism for debugging:**
   ```bash
   find docs -name "*.md" -print0 | \
       xargs -0 -P 1 -I {} bash -c 'set -x; your_function "$@"' _ {}
   ```

### CI/CD Specific Optimizations

In GitHub Actions or similar CI environments:

```bash
# Detect available cores (CI often has 2-4 cores)
CORES=$(nproc 2>/dev/null || echo 2)

# Use parallelism but don't overwhelm shared runners
PARALLEL_JOBS=$((CORES > 4 ? 4 : CORES))

# Add timeouts to prevent hung jobs
timeout 300 find docs -name "*.md" -print0 | \
    xargs -0 -P "$PARALLEL_JOBS" your_check_function
```

---

## Notes

### General Maintenance
- Keep this prompt template updated as project evolves
- Add new audit categories as needed
- Integrate with CI/CD for automated checks
- Use for onboarding new team members
- Include in documentation review process
- Apply shell scripting best practices for performance
- Benchmark critical operations when optimizing

### AI-Specific Considerations (NEW)
- **AI navigation audits are critical** - broken Stage 0 sequence blocks all AI generation
- **Maturity levels drive conditional generation** - inconsistencies cause incorrect code generation
- **Architectural constraints must be consistent** - AI learns from examples, bad examples = bad code
- **Atomic docs are building blocks** - missing atomic docs break implementation phases
- **Submodule compatibility is mandatory** - framework must work in both modes

### Recommended Audit Frequency by Priority

**Critical (blocks AI generation)**:
- AI Navigation Validation → Daily in CI/CD
- Stage 0 document validation → On every doc change
- Navigation Matrix validation → On every workflow doc change

**High (affects code quality)**:
- Architectural Constraints → Weekly
- Maturity Levels Consistency → Weekly
- Atomic Documentation Coverage → Bi-weekly

**Medium (affects usability)**:
- Submodule Path Validation → Monthly
- Toolbox Command Validation → Monthly

**Standard (general quality)**:
- Links, spelling, readability → As per original schedule

### Integration with Development Workflow

1. **Pre-commit**: Run `--quick` (includes AI navigation)
2. **Pre-push**: Run `--ai-navigation` + `--links`
3. **CI/CD Pipeline**: Run `--ai-full` on workflow doc changes
4. **Before Release**: Run `--full` (includes all standard + AI checks)
5. **Monthly Review**: Generate full audit report for documentation health tracking
