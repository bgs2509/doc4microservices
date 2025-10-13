#!/bin/bash

# scripts/quick_audit.sh - Ultra-fast documentation validation (~30 seconds)
# Purpose: Quick smoke test before commits or during development
# For comprehensive audit, use: bash scripts/audit_docs.sh --full

set -euo pipefail

# Configuration
DOCS_DIR="docs"
EXIT_CODE=0

echo "=== Quick Documentation Audit ==="
echo "Started: $(date +%H:%M:%S)"
echo ""

# ✅ Critical Files Check (Stage 0 initialization)
echo "1️⃣  Critical Files (Stage 0):"
CRITICAL_FILES=("CLAUDE.md" "docs/reference/agent-context-summary.md" "docs/guides/ai-code-generation-master-workflow.md" "docs/reference/maturity-levels.md")
MISSING=0

for file in "${CRITICAL_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (MISSING - CRITICAL!)"
    MISSING=$((MISSING + 1))
    EXIT_CODE=1
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "  ✅ All critical files present"
else
  echo "  ⚠️  $MISSING critical files missing!"
fi
echo ""

# ✅ Documentation Stats
echo "2️⃣  Documentation Stats:"
MD_COUNT=$(find "$DOCS_DIR" -name "*.md" 2>/dev/null | wc -l || echo "0")
echo "  📄 Markdown files: $MD_COUNT"

ATOMIC_COUNT=$(find "$DOCS_DIR/atomic" -name "*.md" 2>/dev/null | wc -l || echo "0")
echo "  ⚛️  Atomic docs: $ATOMIC_COUNT"
echo ""

# ✅ Quick Link Check (sample only for speed)
echo "3️⃣  Link Validation (sample):"
BROKEN=0
CHECKED=0

# Extract unique markdown link targets (limit to first 20 for speed)
grep -rho '\[.*\](.*\.md[^)]*)' "$DOCS_DIR" README.md CLAUDE.md 2>/dev/null | \
  sed -E 's/.*\(([^)]+\.md).*/\1/' | \
  sed 's/#.*//' | \
  sort -u | \
  head -20 | while read -r target; do

  CHECKED=$((CHECKED + 1))

  # Try as-is and with docs/ prefix
  if [ ! -f "$target" ] && [ ! -f "$DOCS_DIR/$target" ]; then
    echo "  ❌ Broken: $target"
    BROKEN=$((BROKEN + 1))
    EXIT_CODE=1
  fi
done

if [ $BROKEN -eq 0 ]; then
  echo "  ✅ Sample check passed (checked ~20 links)"
else
  echo "  ⚠️  Found $BROKEN broken links in sample"
  echo "  💡 Run 'bash scripts/audit_docs.sh --links' for full validation"
fi
echo ""

# ✅ Structure Check
echo "4️⃣  Core Structure:"
EXPECTED_DIRS=("atomic/architecture" "atomic/services" "atomic/testing" "guides" "reference" "checklists" "quality")
MISSING_DIRS=0

for dir in "${EXPECTED_DIRS[@]}"; do
  if [ -d "$DOCS_DIR/$dir" ]; then
    FILE_COUNT=$(find "$DOCS_DIR/$dir" -name "*.md" 2>/dev/null | wc -l || echo "0")
    echo "  ✅ $dir ($FILE_COUNT docs)"
  else
    echo "  ❌ $dir (MISSING)"
    MISSING_DIRS=$((MISSING_DIRS + 1))
    EXIT_CODE=1
  fi
done

if [ $MISSING_DIRS -eq 0 ]; then
  echo "  ✅ Core structure intact"
else
  echo "  ⚠️  $MISSING_DIRS directories missing"
fi
echo ""

# ✅ Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Quick audit PASSED"
  echo "   All critical checks passed"
else
  echo "⚠️  Quick audit FOUND ISSUES"
  echo "   Review the warnings above"
  echo ""
  echo "💡 Next steps:"
  echo "   1. Fix critical issues"
  echo "   2. Run full audit: bash scripts/audit_docs.sh --full"
  echo "   3. Check specific areas: --links, --structure, --ai-navigation"
fi

echo ""
echo "Completed: $(date +%H:%M:%S)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $EXIT_CODE
