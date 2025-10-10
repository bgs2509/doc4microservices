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
   - docs/guides/ARCHITECTURE_GUIDE.md
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

---

## Automation Script Template

Create this as `scripts/audit_docs.sh`:

```bash
#!/bin/bash
# Documentation Audit Script
# Usage: ./scripts/audit_docs.sh [--quick|--full|--links|--structure]

set -e

MODE="${1:---full}"
DOCS_DIR="docs"
REPORT_FILE="DOCUMENTATION_AUDIT_REPORT.md"
PARALLEL_JOBS=4  # Adjust based on CPU cores

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

# Export all helper functions for use in subshells
export -f check_link_in_file
export -f check_spelling_in_file
export -f check_code_in_file
export -f check_readability_in_file
export -f check_language_in_file
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

# Main execution
case "$MODE" in
    --quick)
        check_links
        check_spelling
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
    --full)
        check_links
        check_files
        check_structure
        check_duplicates
        check_spelling
        check_code_examples
        check_readability
        check_language
        check_versions
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [--quick|--full|--links|--structure|--spelling|--code|--readability|--language|--versions]"
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

      - name: Check spelling (optimized)
        run: |
          echo "Running spell check (parallel)..."
          # Define helper function for per-file checking
          check_spelling() {
            local file="$1"
            misspelled=$(sed '/^```/,/^```/d' "$file" | aspell list --lang=en --mode=markdown 2>/dev/null)
            if [ -n "$misspelled" ]; then
              echo "::warning file=$file::Potential misspellings: $misspelled"
            fi
          }
          export -f check_spelling

          # Use xargs for parallel processing
          find docs -name "*.md" -print0 | \
            xargs -0 -P 4 -I {} bash -c 'check_spelling "$@"' _ {}

      - name: Validate code examples (optimized)
        run: |
          echo "Validating bash code examples (parallel)..."
          # Define helper function
          check_code() {
            local file="$1"
            local temp="/tmp/check_$$_${RANDOM}.sh"
            awk '/^```bash/,/^```/' "$file" | sed '1d;$d' > "$temp"
            if [ -s "$temp" ]; then
              if ! shellcheck "$temp" 2>&1; then
                echo "::warning file=$file::Bash code issues found"
              fi
            fi
            rm -f "$temp"
          }
          export -f check_code

          # Use xargs for parallel processing
          find docs -name "*.md" -print0 | \
            xargs -0 -P 4 -I {} bash -c 'check_code "$@"' _ {}

      - name: Check language consistency (optimized)
        run: |
          echo "Checking for non-English content (parallel)..."
          # Define helper function
          check_language() {
            local file="$1"
            non_ascii=$(sed '/^```/,/^```/d' "$file" | grep -n '[^ -~]' 2>/dev/null || true)
            if [ -n "$non_ascii" ]; then
              echo "::warning file=$file::Non-ASCII characters found: ${non_ascii:0:100}"
            fi
          }
          export -f check_language

          # Use xargs for parallel processing
          find docs -name "*.md" -print0 | \
            xargs -0 -P 4 -I {} bash -c 'check_language "$@"' _ {}

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

# Check for broken links in staged markdown files
git diff --cached --name-only | grep '\.md$' | while read file; do
    echo "Checking $file..."

    # Extract links
    grep -n '\[.*\](.*\.md' "$file" | while IFS=: read -r line link; do
        path=$(echo "$link" | sed 's/.*(\(.*\.md\).*/\1/')

        if [ ! -f "$path" ] && [ ! -f "docs/$path" ]; then
            echo "ERROR: Broken link in $file:$line -> $path"
            exit 1
        fi
    done
done

if [ $? -ne 0 ]; then
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

---

## Maintenance Schedule

- **Weekly**: Automated link checking in CI
- **Monthly**: Full audit with AI agent
- **Quarterly**: Technology version consistency check
- **Yearly**: Comprehensive structure review

---

## Notes

- Keep this prompt template updated as project evolves
- Add new audit categories as needed
- Integrate with CI/CD for automated checks
- Use for onboarding new team members
- Include in documentation review process
