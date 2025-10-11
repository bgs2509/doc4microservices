#!/bin/bash
# Documentation Audit Script
# Usage: ./scripts/audit_docs.sh [--quick|--full|--links|--structure|--spelling|--code|--readability|--language|--versions]

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
        # Extract path from link (improved regex to avoid table pipe separators)
        local path
        path=$(echo "$link" | sed -n 's/.*(\([^)]*\.md\)).*/\1/p')

        # Skip if path extraction failed
        [ -z "$path" ] && continue

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
