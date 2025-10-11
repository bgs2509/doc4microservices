# Scripts Directory

This directory contains automation scripts for documentation validation and maintenance.

## Active Scripts

### audit_docs.sh
**Purpose**: Comprehensive documentation audit with 15 objectives

**Usage**:
```bash
./scripts/audit_docs.sh --full      # Full audit (all 15 objectives)
./scripts/audit_docs.sh --quick     # Quick audit (5 min, smoke tests only)
./scripts/audit_docs.sh --links     # Link validation only
./scripts/audit_docs.sh --structure # Structure validation only
```

**Features**:
- 15 objectives including link validation, structure, content quality, AI navigation, obsolete files
- Smoke tests (30 seconds) to catch critical issues
- Exhaustive link checking (not sample-based)
- Reports saved to `audit_reports/`

**Created**: 2025-10-11  
**Status**: ✅ Active (replaces validate_docs.sh)

---

### check_links.sh
**Purpose**: Wrapper script for Python link validator

**Usage**:
```bash
./scripts/check_links.sh
```

Calls `validate_docs.py` for link validation.

---

### validate_docs.py
**Purpose**: Python-based document link validator

**Usage**:
```bash
python3 scripts/validate_docs.py
```

---

### validate_atomic_docs.py
**Purpose**: Validates atomic documentation structure and completeness

**Usage**:
```bash
python3 scripts/validate_atomic_docs.py
```

---

### validate_naming.py
**Purpose**: Validates service naming conventions (3-part vs 4-part)

**Usage**:
```bash
python3 scripts/validate_naming.py
```

---

## Deprecated Scripts

### validate_docs.sh.deprecated
**Previously**: Basic bash-based documentation audit  
**Replaced by**: `audit_docs.sh` (comprehensive audit)  
**Deprecated**: 2025-10-11  
**Reason**: 
- Limited functionality (basic link checks only)
- No smoke tests
- No exhaustive validation
- Replaced by more comprehensive audit_docs.sh with 15 objectives

**Migration**:
- Old: `./scripts/validate_docs.sh --quick`
- New: `./scripts/audit_docs.sh --quick`

**Old**: `./scripts/validate_docs.sh --links`  
**New**: `./scripts/audit_docs.sh --links`

---

## Development

To add a new audit objective:
1. Edit `prompts/documentation_audit_v2.md`
2. Add objective to list (e.g., Objective 16)
3. Add validation commands in "OBJECTIVES (Detailed)" section
4. Update `audit_docs.sh` if bash implementation needed

---

## CI/CD Integration

See `prompts/documentation_audit_v2.md` for GitHub Actions examples.

