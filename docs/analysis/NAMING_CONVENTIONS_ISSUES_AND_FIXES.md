# Naming Conventions Deep Analysis: AI Confusion Points & Fixes

**Analysis Date**: 2025-10-02
**Document**: `docs/atomic/architecture/naming-conventions.md` (1020 lines)
**Purpose**: Identify and fix conflicts, misleading patterns, and AI confusion points

---

## Executive Summary

**Total Issues Found**: 35
- **CRITICAL (Blocks AI)**: 7
- **HIGH (Causes Errors)**: 8
- **MEDIUM (Suboptimal Results)**: 12
- **LOW (Minor Confusion)**: 8

**Estimated Time to Fix**: 2-3 hours for critical + high priority

---

## CRITICAL ISSUES (Must Fix Immediately)

### 1. **Terminology Conflict: "Service" Means 4+ Different Things** ⚠️ BLOCKER

**Lines**: 9-11, 149, 277-279, 614

**Problem**: The word "Service" is used for:
1. **Microservice/Application**: `finance_lending_api` (line 9)
2. **Python class suffix**: `UserService` (line 614)
3. **Docker Compose service**: `finance_lending_api` (line 149)
4. **Kubernetes Service resource**: `finance-lending-api` (line 277)

**AI Confusion**: When asked "create a service for user auth", AI cannot determine which type.

**Current State**:
```markdown
| **Service** | `{context}_{domain}_{type}` | `finance_lending_api` | `_` |
```

**Fix**:
```markdown
| **Microservice/Application** | `{context}_{domain}_{type}` | `finance_lending_api` | `_` |
```

**Impact**: CRITICAL - affects all service naming decisions

---

### 2. **Separator Column Ambiguity: "-" Means Both "Hyphen" and "None"** ⚠️ BLOCKER

**Line**: 11

**Problem**:
```markdown
| **Python Class** | `{Noun}{Suffix}` | `UserService`, `OrderRepository` | - |
```

The `-` in separator column is ambiguous:
- Does it mean "use hyphens" (e.g., `User-Service`)? ❌ Wrong interpretation
- Does it mean "no separator/N/A" (PascalCase)? ✅ Correct but unclear

**AI Confusion**: AI might generate `User-Service` class names.

**Fix**:
```markdown
| **Python Class** | `{Noun}{Suffix}` | `UserService`, `OrderRepository` | None (PascalCase) |
```

**Impact**: CRITICAL - could generate invalid Python class names

---

###  3. **3-Part vs 4-Part Decision Contradiction** ⚠️ CRITICAL

**Lines**: 65-66 vs 929-940

**Contradiction**:

**Rule 1** (line 66):
```
If domain has MULTIPLE possible functions → use 4-part with explicit function
```

**Rule 2** (lines 929-940 - Multi-Function Services):
```
construction_house_bot ✅ (management implied by bot handling full workflow)
```
But bot does: calculations + uploads + cost tracking (3 functions!)

**AI Confusion**: Which rule to follow?

**Fix**: Add clarification:
```markdown
## When to Use 3-Part vs 4-Part

### 3-Part: Domain Implies ONE Primary Function
- `finance_lending_api` → lending implies matching/approval
- `construction_house_bot` → bot implies comprehensive house management workflow

### 4-Part: Domain Has MULTIPLE POSSIBLE Functions (Ambiguous)
- `logistics_fleet_tracking_api` → fleet could mean tracking OR management OR maintenance
- `analytics_reporting_api` → analytics could mean reporting OR querying OR processing

### Decision Rule:
1. Does domain + type imply ONE clear primary function? → 3-part
2. Could domain mean multiple unrelated functions? → 4-part with explicit function
```

**Impact**: CRITICAL - core naming decision logic

---

### 4. **Database Table Pattern Incomplete**

**Line**: 20

**Problem**:
```markdown
| **Database Table** | `{plural_noun}` | `users`, `order_items` | `_` |
```

Pattern says `{plural_noun}` but example `order_items` is `{plural_noun}_{plural_noun}`.

**Fix**:
```markdown
| **Database Table** | `{plural_noun}[_{qualifier}]` | `users`, `order_items` | `_` |
```

---

### 5. **REST API Pattern Doesn't Match Example**

**Line**: 23

**Problem**:
```markdown
| **REST API Path** | `/{noun}[/{id}]` | `/api/v1/users/{id}` | `-` |
```

Pattern missing `/api/v1/` prefix. Separator column shows `-` but paths use `/`.

**Fix**:
```markdown
| **REST API Path** | `/api/v{N}/{resource}[/{id}]` | `/api/v1/users/{id}` | `/` (segments), `-` (words) |
```

---

### 6. **DTO Suffix Placement Confusion**

**Lines**: 182 vs 616

**Problem**:

Line 182:
```
DTOs adopt descriptive suffixes (...Create, ...Update)
```
The `...Create` notation implies suffix AFTER DTO.

Line 616:
```
{Noun}{Action}DTO → UserCreateDTO
```
Shows action BEFORE DTO.

**Fix** (line 182):
```markdown
DTOs use action-based middle components: `{Noun}CreateDTO`, `{Noun}UpdateDTO`, `{Noun}PublicDTO`
(not `UserDTOCreate`)
```

---

### 7. **Nginx Upstream Example Mismatch**

**Lines**: 151-154 vs 350-354

**Problem**:

Table says (line 152):
```
Nginx upstreams: snake_case | matches Docker Compose service names
```

Example shows (line 352-353):
```nginx
upstream finance_lending_api {
    server finance-lending-api:8000;  # K8s DNS (hyphens)
}
```

Example shows **production** (K8s) but table describes **development** (Compose).

**Fix**: Add both examples:
```nginx
# Development (Docker Compose)
upstream finance_lending_api {
    server finance_lending_api:8000;  # Matches Compose service name (underscore)
}

# Production (Kubernetes)
upstream finance_lending_api {
    server finance-lending-api:8000;  # K8s DNS name (hyphen required)
}
```

---

## HIGH PRIORITY ISSUES

### 8. **Docker Compose v1 Deprecated** ⚠️ OUTDATED

**Lines**: 150, 272

**Problem**:
```
Compose v1 compatibility, consistency
```

Docker Compose v1 reached EOL June 2023. Framework should use v2.

**Fix**: Remove v1 references:
```diff
- Container names (dev) | `snake_case` | Compose v1 compatibility | ...
+ Container names (dev) | `snake_case` | Internal dev naming | ...
```

---

### 9. **Function Pattern Too Vague**

**Line**: 82

**Problem**:
```
Pattern: `{verb}_{noun}[_qualifier]`
```

But examples show:
- `get_user_by_id` → `{verb}_{noun}_by_{field}`
- `send_email_to_user` → `{verb}_{noun}_to_{target}`

**Fix**:
```markdown
| Pattern | Example |
|---------|---------|
| `{verb}_{noun}` | `create_order`, `delete_user` |
| `{verb}_{noun}_by_{field}` | `get_user_by_id`, `find_order_by_status` |
| `{verb}_{noun}_to_{target}` | `send_email_to_user`, `export_data_to_csv` |
| `{verb}_{noun}_from_{source}` | `fetch_data_from_api`, `import_users_from_csv` |
```

---

### 10. **Boolean Variable Pattern Incomplete**

**Line**: 714

**Problem**:
```
Boolean flag | `is_{adjective}`, `has_{noun}`
```

Missing common Python patterns:
- `can_{verb}` → `can_edit`, `can_delete`
- `should_{verb}` → `should_retry`
- `will_{verb}` → `will_expire`

**Fix**:
```markdown
| Boolean flag | `is_{adj}`, `has_{noun}`, `can_{verb}`, `should_{verb}`, `will_{verb}` | `is_active`, `can_edit`, `should_retry` |
```

---

### 11. **Git Branch Types Incomplete**

**Lines**: 396-400

**Problem**: Only lists 3 types:
- `feature/`, `bugfix/`, `release/`

Missing:
- `hotfix/`, `chore/`, `docs/`, `refactor/`, `test/`, `perf/`

**Fix**: Add complete list or reference Git flow standard.

---

### 12. **Character Restrictions Table Incomplete**

**Lines**: 407-414

**Problem**: Missing technologies framework uses:
- ❌ **RabbitMQ** queue/exchange names
- ❌ **Redis** keys
- ❌ **Nginx** server_name
- ❌ **Git** branches

**Fix**: Add rows:
```markdown
| **RabbitMQ queues** | ✅ Allowed | ✅ Allowed | 255 chars | `[a-zA-Z0-9_.-]+` |
| **Redis keys** | ✅ Allowed | ✅ Allowed | 512 MB | Any binary string |
| **Nginx server_name** | ❌ Prohibited | ✅ Required | 253 chars | RFC 1035 DNS |
| **Git branches** | ✅ Allowed | ✅ Allowed (recommended) | - | `[a-z0-9-/_]+` |
```

---

### 13. **Service-to-K8s Conversion Missing Validation**

**Lines**: 823-831

**Problem**:
```python
def service_to_k8s(service_name: str) -> str:
    return service_name.replace('_', '-')
```

Missing edge cases:
- Names starting/ending with `_`
- Double underscores
- Uppercase letters
- DNS validation

**Fix**:
```python
import re

def service_to_k8s(service_name: str) -> str:
    """Convert service name to Kubernetes DNS-compliant name.

    Examples:
        finance_lending_api → finance-lending-api ✅
        Finance_API → finance-api ✅
        _internal_api → ValueError ❌
    """
    name = service_name.lower().replace('_', '-').strip('-')
    name = re.sub(r'-+', '-', name)  # Collapse multiple hyphens

    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
        raise ValueError(f"Invalid K8s DNS name: {name}")
    if len(name) > 253:
        raise ValueError(f"Name exceeds 253 chars: {len(name)}")

    return name
```

---

### 14. **Migration File Naming Incomplete**

**Line**: 206

**Problem**:
```
Migrations: 202501010101_initial_schema.py
```

Missing:
- Timestamp format spec (YYYYMMDDHHmm vs YYYYMMDDHHmmss)
- Timezone (UTC?)
- Tool reference (Alembic?)

**Fix**:
```markdown
Migrations follow Alembic naming convention:
- Auto-generated: `{revision_hash}_{description}.py` (e.g., `a1b2c3d4_add_user_table.py`)
- Manual timestamp (discouraged): `YYYYMMDDHHmmss_{description}.py` in UTC timezone
```

---

### 15. **MongoDB Collection Pattern Not Explicit**

**Line**: 198

**Problem**:
```
MongoDB collections | `snake_case` | `analytics_events`, `user_sessions`
```

Shows examples without stating pattern.

**Fix**:
```markdown
| MongoDB collections | `{plural_noun}[_{qualifier}]` | `analytics_events`, `user_sessions` | `_` |
```

---

## MEDIUM PRIORITY ISSUES

### 16. **Redundant Content Across Sections**

**Problem**: Same rules explained 3 times:

- **Python Class**: Quick Ref (line 11) + Decision Tree (68-79) + Section 3 (611-664)
- **Service Naming**: Quick Ref (9-10) + Decision Tree (42-66) + Section 2 (418-605)

**Impact**: Increases doc size, risk of inconsistency.

**Fix**: Add cross-references:
```markdown
## AI Quick Reference

| Element Type | Pattern | See Details |
|--------------|---------|-------------|
| **Microservice** | `{context}_{domain}_{type}` | → Section 2 |
| **Python Class** | `{Noun}{Suffix}` | → Section 3.1 |
```

---

### 17. **File-Folder Alignment Example Confusing**

**Lines**: 765-773

**Problem**:
```
services/
  finance_lending_api/
    src/
      finance_lending_api/  # TWO nested folders!
```

Why two `finance_lending_api/` folders? Is `src/` mandatory?

**Fix**: Clarify or reference Project Structure guide:
```markdown
# Option A: Flat (simple projects)
services/finance_lending_api/
  __init__.py
  main.py

# Option B: src layout (distributable packages)
services/finance_lending_api/  # Project root
  src/finance_lending_api/     # Installable package
    __init__.py
```

---

### 18. **Context Registry Without Implementation**

**Line**: 990

**Problem**:
```
Best Practice: Maintain a Context Registry document
```

But no guidance on format, location, or template.

**Fix**: Provide template location:
```markdown
**Best Practice**: Maintain a Context Registry at `docs/atomic/architecture/context-registry.md`:

| Context | Description | Services | Owner |
|---------|-------------|----------|-------|
| `finance` | Financial services | finance_lending_api, finance_crypto_api | @finance-team |
```

---

### 19. **Broken Reference Check Needed**

**Lines**: 540, 1015

**Problem**:
```
See [Semantic Shortening Guide](../../guides/SEMANTIC_SHORTENING_GUIDE.md)
```

Git history shows abbreviations registry removed. Verify guide still exists.

**Fix**: Check file existence and update/remove reference.

---

### 20. **Primary Key Constraint Rarely Used**

**Line**: 786

**Problem**:
```
| Primary key | `pk_{table}` | `pk_users` |
```

In practice, ORMs auto-generate PK constraint names. Explicit naming is rare.

**Fix**: Add note:
```markdown
| Primary key | `pk_{table}` (optional, usually auto-generated) | `pk_users` |
```

---

### 21. **HTTP Headers Out of Place**

**Lines**: 961-964

**Problem**: Section "Exceptions & Edge Cases" includes HTTP headers, but this isn't a naming convention exception.

**Fix**: Move to separate document or remove.

---

### 22. **Private Member Examples Missing**

**Line**: 175

**Problem**: Pattern shown but no expanded examples.

**Fix**: Add to Section 3:
```markdown
### Python Private Members

| Pattern | Use Case | Example |
|---------|----------|---------|
| `_single_leading` | Internal, not imported by `*` | `_cache`, `_validate()` |
| `__double_leading` | Name mangling for subclasses | `__private_id` |
| `_trailing_` | Avoid keyword conflicts | `class_`, `type_` |
```

---

### 23. **Section Title Misleading**

**Line**: 418

**Problem**:
```
## Section 2: Semantic Naming Patterns
```

Section is 95% about SERVICE naming, not general patterns.

**Fix**:
```diff
- ## Section 2: Semantic Naming Patterns
+ ## Section 2: Microservice Naming Patterns
```

---

### 24. **Validation Checklist Buried**

**Lines**: 843-857

**Problem**: Critical checklist in middle of doc.

**Fix**: Move to end or add prominent link from Quick Reference.

---

### 25. **REST API Path Separator Confusion**

**Line**: 23

**Problem**: Separator column shows `-` but REST paths use `/` as primary separator.

**Fix**: Clarify:
```markdown
| **REST API Path** | ... | `/` (segments), `-` (words within segments) |
```

---

## LOW PRIORITY ISSUES

### 26-35. **Additional Minor Issues**

26. **PyPI package naming exception** - exists but could be clearer
27. **Multi-word domain examples** - need more examples
28. **Cache key naming** - not covered
29. **Queue naming patterns** - mentioned but no pattern
30. **Environment file naming** - `.env.example` vs `.env.dev`
31. **Test file prefixes** - `test_` vs `_test.py` inconsistency risk
32. **Constants in classes** - class-level constants pattern missing
33. **Property naming** - Python `@property` not covered
34. **Async function naming** - `async def` same as sync?
35. **Type alias naming** - `UserID = int` pattern missing

---

## RECOMMENDED FIX PRIORITY

### Phase 1: Immediate (Today)
1. Fix "Service" terminology (Issue #1)
2. Fix separator column ambiguity (Issue #2)
3. Clarify 3-part vs 4-part decision (Issue #3)
4. Fix database table pattern (Issue #4)
5. Fix REST API pattern (Issue #5)

### Phase 2: This Week
6. Fix DTO suffix placement (Issue #6)
7. Add Nginx dev/prod examples (Issue #7)
8. Remove Docker Compose v1 refs (Issue #8)
9. Expand function patterns (Issue #9)
10. Complete boolean patterns (Issue #10)
11. Add missing character restrictions (Issue #12)
12. Fix service-to-k8s conversion (Issue #13)

### Phase 3: Next Sprint
- Add cross-references to reduce redundancy (Issue #16)
- Create context registry template (Issue #18)
- Reorganize validation checklist (Issue #24)
- Add private member examples (Issue #22)
- Remaining low-priority items

---

## VALIDATION TESTS TO ADD

After fixes, add these validation checks:

```python
# scripts/validate_naming_conventions.py

def test_all_examples_match_patterns():
    """Verify every example in doc matches its stated pattern."""
    assert "finance_lending_api" matches "{context}_{domain}_{type}"
    assert "UserService" matches "{Noun}{Suffix}"
    # ... 50+ tests

def test_separator_consistency():
    """Ensure separator column matches examples."""
    for row in quick_reference_table:
        if row.separator == "_":
            assert "_" in row.example
        if row.separator == "None (PascalCase)":
            assert "_" not in row.example and "-" not in row.example
```

---

**END OF ANALYSIS**
