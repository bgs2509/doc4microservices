#!/bin/bash

# Documentation Validation Script
# Purpose: Comprehensive validation of documentation quality and integrity
# Usage: ./validate_docs.sh [--links|--versions|--todos|--full]

set -uo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_ISSUES=0
CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0
LOW_ISSUES=0

# Configuration
DOCS_DIR="docs"
PARALLEL_JOBS="${PARALLEL_JOBS:-4}"
MODE="${1:---full}"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

increment_counter() {
    local severity="$1"
    ((TOTAL_ISSUES++))
    case "$severity" in
        CRITICAL) ((CRITICAL_ISSUES++)) ;;
        HIGH) ((HIGH_ISSUES++)) ;;
        MEDIUM) ((MEDIUM_ISSUES++)) ;;
        LOW) ((LOW_ISSUES++)) ;;
    esac
}

# Function to check markdown links
check_markdown_links() {
    log_info "Checking markdown links..."
    local broken_links=0

    # Export functions for subshell usage
    export -f log_error
    export -f increment_counter
    export RED NC DOCS_DIR

    find "$DOCS_DIR" -name "*.md" -print0 | \
        xargs -0 -P "$PARALLEL_JOBS" -I {} bash -c '
            file="$1"
            grep -Hn "\[.*\](.*\.md" "$file" 2>/dev/null | while IFS=: read -r filepath line_num line_content; do
                # Extract the link path
                link=$(echo "$line_content" | sed -n "s/.*](\([^)]*\.md[^)]*\)).*/\1/p")
                if [ -n "$link" ]; then
                    # Remove anchor if present
                    link_path="${link%%#*}"

                    # Check if file exists
                    if [[ "$link_path" == http* ]]; then
                        # Skip external links
                        continue
                    elif [[ "$link_path" == /* ]]; then
                        # Absolute path
                        test_path="${link_path#/}"
                    else
                        # Relative path
                        dir=$(dirname "$filepath")
                        test_path="$dir/$link_path"
                    fi

                    # Normalize path
                    test_path=$(realpath -m "$test_path" 2>/dev/null || echo "$test_path")

                    if [ ! -f "$test_path" ]; then
                        echo "BROKEN_LINK:$filepath:$line_num:$link_path"
                    fi
                fi
            done
        ' _ {} | while IFS=: read -r type file line link; do
            if [ "$type" = "BROKEN_LINK" ]; then
                log_error "Broken link in $file:$line -> $link"
                increment_counter "CRITICAL"
                ((broken_links++))
            fi
        done

    if [ $broken_links -eq 0 ]; then
        log_success "All markdown links are valid"
    fi
}

# Function to check Python version consistency
check_python_versions() {
    log_info "Checking Python version consistency..."
    local inconsistent=0

    # Define expected Python version
    EXPECTED_VERSION="3.12"

    # Check for different Python versions
    versions=$(grep -rh "Python [0-9]\.[0-9]" "$DOCS_DIR" --include="*.md" | \
               sed -n 's/.*Python \([0-9]\.[0-9][0-9]*\).*/\1/p' | \
               sort -u)

    if [ $(echo "$versions" | wc -l) -gt 1 ]; then
        log_warning "Multiple Python versions found: $(echo $versions | tr '\n' ', ')"
        increment_counter "HIGH"
        ((inconsistent++))

        # Show files with non-standard versions
        for version in $versions; do
            if [ "$version" != "$EXPECTED_VERSION" ]; then
                log_warning "Files with Python $version (should be $EXPECTED_VERSION):"
                grep -rl "Python $version" "$DOCS_DIR" --include="*.md" | head -5
            fi
        done
    fi

    if [ $inconsistent -eq 0 ]; then
        log_success "Python versions are consistent ($EXPECTED_VERSION)"
    fi
}

# Function to check for TODO sections
check_todo_sections() {
    log_info "Checking for TODO documentation sections..."
    local todo_count=0

    # Find TODO markers in documentation
    todo_files=$(grep -rl "TODO" "$DOCS_DIR" --include="*.md" 2>/dev/null || true)

    if [ -n "$todo_files" ]; then
        todo_count=$(echo "$todo_files" | wc -l)
        log_warning "Found $todo_count files with TODO sections:"
        echo "$todo_files" | head -10

        # Count by directory for better insight
        echo -e "\n${YELLOW}TODO distribution by directory:${NC}"
        echo "$todo_files" | xargs -I {} dirname {} | sort | uniq -c | sort -rn | head -10

        increment_counter "MEDIUM"
    fi

    if [ $todo_count -eq 0 ]; then
        log_success "No TODO sections found"
    fi
}

# Function to check file existence from INDEX.md
check_index_references() {
    log_info "Checking INDEX.md file references..."
    local missing_files=0

    if [ ! -f "$DOCS_DIR/INDEX.md" ]; then
        log_warning "INDEX.md not found"
        return
    fi

    # Extract all .md references from INDEX.md
    grep -o '[^(]*\.md' "$DOCS_DIR/INDEX.md" | while read -r ref; do
        if [[ "$ref" == http* ]]; then
            continue  # Skip URLs
        fi

        # Check if file exists
        if [[ "$ref" == /* ]]; then
            test_path="${ref#/}"
        else
            test_path="$DOCS_DIR/$ref"
        fi

        if [ ! -f "$test_path" ]; then
            log_error "Missing file referenced in INDEX.md: $ref"
            increment_counter "HIGH"
            ((missing_files++))
        fi
    done || true

    if [ $missing_files -eq 0 ]; then
        log_success "All INDEX.md references are valid"
    fi
}

# Function to check duplicate headings
check_duplicate_headings() {
    log_info "Checking for duplicate headings..."

    # Find all headings and count duplicates
    headings=$(find "$DOCS_DIR" -name "*.md" -exec grep -h "^#\+" {} \; | \
               sort | uniq -c | sort -rn | awk '$1 > 5 {print}')

    if [ -n "$headings" ]; then
        log_warning "Found frequently duplicated headings (>5 occurrences):"
        echo "$headings" | head -10
        increment_counter "LOW"
    else
        log_success "No problematic heading duplications found"
    fi
}

# Function to validate template services
check_template_services() {
    log_info "Checking template services..."
    local templates_dir="templates/services"
    local missing_readme=0

    if [ ! -d "$templates_dir" ]; then
        log_warning "Templates directory not found: $templates_dir"
        increment_counter "HIGH"
        return
    fi

    # Expected templates
    expected_templates=(
        "template_business_api"
        "template_business_bot"
        "template_business_worker"
        "template_data_postgres_api"
        "template_data_mongo_api"
    )

    for template in "${expected_templates[@]}"; do
        if [ ! -d "$templates_dir/$template" ]; then
            log_error "Missing template: $template"
            increment_counter "HIGH"
        elif [ ! -f "$templates_dir/$template/README.md" ]; then
            log_warning "Missing README.md in $template"
            increment_counter "MEDIUM"
            ((missing_readme++))
        fi
    done

    if [ $missing_readme -eq 0 ]; then
        log_success "All template services have documentation"
    fi
}

# Function to check for common documentation issues
check_common_issues() {
    log_info "Checking for common documentation issues..."

    # Check for very long lines (>200 characters)
    long_lines=$(find "$DOCS_DIR" -name "*.md" -exec grep -l '.\{200,\}' {} \; | wc -l)
    if [ $long_lines -gt 0 ]; then
        log_warning "Found $long_lines files with very long lines (>200 chars)"
        increment_counter "LOW"
    fi

    # Check for missing newline at end of file
    missing_newline=$(find "$DOCS_DIR" -name "*.md" -exec sh -c '[ -z "$(tail -c 1 <"$1")" ]' _ {} \; -print | wc -l)
    if [ $missing_newline -gt 0 ]; then
        log_warning "Found $missing_newline files without newline at end"
        increment_counter "LOW"
    fi

    # Check for tabs vs spaces inconsistency
    tabs_files=$(find "$DOCS_DIR" -name "*.md" -exec grep -l $'\t' {} \; | wc -l)
    if [ $tabs_files -gt 0 ]; then
        log_warning "Found $tabs_files files using tabs (should use spaces)"
        increment_counter "LOW"
    fi
}

# Generate summary report
generate_report() {
    echo
    echo "========================================"
    echo "    Documentation Validation Report"
    echo "========================================"
    echo
    echo -e "${BLUE}Total Issues Found:${NC} $TOTAL_ISSUES"
    echo -e "${RED}  - CRITICAL:${NC} $CRITICAL_ISSUES"
    echo -e "${YELLOW}  - HIGH:${NC} $HIGH_ISSUES"
    echo -e "${YELLOW}  - MEDIUM:${NC} $MEDIUM_ISSUES"
    echo -e "${GREEN}  - LOW:${NC} $LOW_ISSUES"
    echo

    # Calculate health score
    HEALTH_SCORE=$((100 - CRITICAL_ISSUES*10 - HIGH_ISSUES*5 - MEDIUM_ISSUES*2 - LOW_ISSUES))
    if [ $HEALTH_SCORE -lt 0 ]; then
        HEALTH_SCORE=0
    fi

    echo -e "${BLUE}Documentation Health Score:${NC} ${HEALTH_SCORE}/100"

    if [ $CRITICAL_ISSUES -gt 0 ]; then
        echo -e "\n${RED}⚠️  Critical issues found! Fix immediately.${NC}"
        exit 1
    elif [ $HIGH_ISSUES -gt 0 ]; then
        echo -e "\n${YELLOW}⚠️  High priority issues found. Please address soon.${NC}"
        exit 1
    elif [ $TOTAL_ISSUES -eq 0 ]; then
        echo -e "\n${GREEN}✅ All validation checks passed!${NC}"
    else
        echo -e "\n${GREEN}✅ No critical issues. Minor improvements suggested.${NC}"
    fi
}

# Main execution
main() {
    echo "Starting documentation validation..."
    echo "Mode: $MODE"
    echo "Documentation directory: $DOCS_DIR"
    echo

    case "$MODE" in
        --links)
            check_markdown_links
            check_index_references
            ;;
        --versions)
            check_python_versions
            ;;
        --todos)
            check_todo_sections
            ;;
        --structure)
            check_template_services
            check_duplicate_headings
            check_common_issues
            ;;
        --quick)
            check_markdown_links
            check_python_versions
            ;;
        --full|*)
            check_markdown_links
            check_python_versions
            check_todo_sections
            check_index_references
            check_duplicate_headings
            check_template_services
            check_common_issues
            ;;
    esac

    generate_report
}

# Run main function
main "$@"