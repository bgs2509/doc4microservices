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

## DELIVERABLES

Create a detailed report with:

### 1. Executive Summary
- Project purpose (1-2 paragraphs)
- Health score (0-100)
- Total issues found with severity breakdown
- Top 3 critical issues

### 2. Issue Categories

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

echo "=== Documentation Audit ==="
echo "Mode: $MODE"
echo "Docs Directory: $DOCS_DIR"
echo ""

# Function: Check Markdown Links
check_links() {
    echo "Checking markdown links..."
    find "$DOCS_DIR" -name "*.md" -exec grep -Hn '\[.*\](.*\.md' {} \; | \
    while IFS=: read -r file line link; do
        # Extract path from link
        path=$(echo "$link" | sed 's/.*(\(.*\.md\).*/\1/')

        # Check if file exists
        if [ ! -f "$path" ] && [ ! -f "$DOCS_DIR/$path" ]; then
            echo "BROKEN: $file:$line -> $path"
        fi
    done
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

# Main execution
case "$MODE" in
    --quick)
        check_links
        ;;
    --links)
        check_links
        ;;
    --structure)
        check_structure
        ;;
    --full)
        check_links
        check_files
        check_structure
        check_duplicates
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [--quick|--full|--links|--structure]"
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

### Before Release
```bash
# Full validation pipeline
./scripts/audit_docs.sh --full
pytest docs/tests/
markdownlint docs/**/*.md
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
