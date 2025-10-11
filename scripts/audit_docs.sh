#!/bin/bash

# scripts/audit_docs.sh - Comprehensive documentation audit automation
# Usage:
#   ./scripts/audit_docs.sh --full      # Full audit
#   ./scripts/audit_docs.sh --quick     # 5-minute audit
#   ./scripts/audit_docs.sh --links     # Link validation only
#   ./scripts/audit_docs.sh --structure # Structure validation only

set -euo pipefail

# Enable globstar for ** pattern
shopt -s globstar 2>/dev/null || true

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
  LINK_COUNT=$(grep -roh '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | wc -l || echo "0")
  log "  Total links: $LINK_COUNT"
  
  log "Smoke 3: 🚨 Legacy references (CRITICAL)"
  LEGACY_COUNT=$(grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | wc -l || echo "0")
  log "  Legacy references: $LEGACY_COUNT"
  if [ "$LEGACY_COUNT" -gt 0 ]; then
    log "  🚨 CRITICAL: Found $LEGACY_COUNT legacy references"
    grep -rn "docs/legacy\|/legacy/\|deprecated\|old-" "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | head -10 | tee -a "$REPORT_FILE" || true
  fi
  
  log "Smoke 4: Broken link sample (first 3)"
  # Use find instead of ** glob
  BROKEN_COUNT=0
  grep -rho '\[.*\](.*\.md' "$DOCS_DIR" 2>/dev/null | sed 's/.*(\(.*\.md\).*/\1/' | sort -u | head -10 | while read -r ref; do
    if [ ! -f "$ref" ] && [ ! -f "$DOCS_DIR/$ref" ]; then
      if [ $BROKEN_COUNT -lt 3 ]; then
        log "    ❌ $ref"
        BROKEN_COUNT=$((BROKEN_COUNT + 1))
      fi
    fi
  done || true
  
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
  TOTAL_LINKS=$(wc -l < /tmp/all_links_$$.txt || echo "0")
  log "Total links found: $TOTAL_LINKS"
  
  # Validate each unique target
  grep -rho '\[.*\](.*\.md' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | \
    sed 's/.*(\(.*\.md\).*/\1/' | sort -u > /tmp/unique_targets_$$.txt || true
  
  BROKEN=0
  while IFS= read -r target; do
    if [ ! -f "$target" ] && [ ! -f "$DOCS_DIR/$target" ]; then
      log "  ❌ Broken: $target"
      BROKEN=$((BROKEN + 1))
      
      # Show which files reference this broken link (use find instead of **)
      find "$DOCS_DIR" -name "*.md" -exec grep -l "$target" {} \; 2>/dev/null | head -3 | while IFS= read -r file; do
        LINE=$(grep -n "$target" "$file" 2>/dev/null | head -1 | cut -d: -f1 || echo "?")
        log "      Referenced in: $file:$LINE"
      done || true
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
      README_COUNT=$(find "$DOCS_DIR/atomic/$dir" -name "README.md" 2>/dev/null | wc -l || echo "0")
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
      if grep -q "Stage $stage" docs/reference/ai-navigation-matrix.md 2>/dev/null; then
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
    log "Audit completed at $(date)"
    log ""
    log "💡 Run full audit for detailed analysis: bash scripts/audit_docs.sh --full"
    ;;
  --links)
    log "Starting LINK VALIDATION"
    validate_links
    log "Audit completed at $(date)"
    ;;
  --structure)
    log "Starting STRUCTURE VALIDATION"
    validate_structure
    log "Audit completed at $(date)"
    ;;
  --ai-navigation)
    log "Starting AI NAVIGATION VALIDATION"
    validate_ai_navigation
    log "Audit completed at $(date)"
    ;;
  --full)
    log "Starting FULL AUDIT"
    run_smoke_tests
    log ""
    validate_links
    log ""
    validate_structure
    log ""
    validate_ai_navigation
    log ""
    log "=== FULL AUDIT COMPLETE ==="
    log "Report saved to: $REPORT_FILE"
    ;;
  *)
    echo "Usage: $0 [--full|--quick|--links|--structure|--ai-navigation]"
    exit 1
    ;;
esac
