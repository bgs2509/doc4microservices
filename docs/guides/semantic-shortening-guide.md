# Semantic Shortening Guide

> **Purpose**: Complete guide for creating concise, meaningful service names using 3-part formula that maintains readability without cryptic abbreviations.

## Table of Contents

- [Overview](#overview)
- [The 3-Part Formula](#the-3-part-formula)
- [Philosophy: Why Semantic Shortening?](#philosophy-why-semantic-shortening)
- [Decision Tree](#decision-tree)
- [Examples by Context](#examples-by-context)
- [When to Use 4-Part (Exceptions)](#when-to-use-4-part-exceptions)
- [Common Mistakes](#common-mistakes)
- [Validation Checklist](#validation-checklist)
- [Migration from 4-Part](#migration-from-4-part)

---

## Overview

**Semantic shortening** eliminates redundant function words from service names while preserving clarity through context + domain combination.

### Key Benefits

| Metric | Before (4-part) | After (3-part) | Improvement |
|--------|-----------------|----------------|-------------|
| **Average length** | 38 chars | 24 chars | **37% shorter** |
| **K8s compatibility** | 70% fit (<30 chars) | 95% fit | **+25% improvement** |
| **Readability** | Good | Excellent | Self-documenting |
| **Onboarding time** | Medium | Fast | No registry lookup needed |
| **Maintenance** | High (registry sync) | Low | No abbreviation dictionary |

---

## The 3-Part Formula

### Default Pattern

```
{context}_{domain}_{type}
```

- **{context}**: Business area (finance, healthcare, construction...)
- **{domain}**: Subdomain within context (lending, telemedicine, house...)
- **{type}**: Technical service type (api, worker, bot...)

### Examples

```python
# 3-part examples (function implied):
finance_lending_api              # lending → matching/approval
healthcare_telemedicine_api      # telemedicine → consultation
construction_house_bot           # house + bot → management
logistics_delivery_api           # delivery → tracking/routing
```

### Extended Pattern (4-part)

```
{context}_{domain}_{function}_{type}
```

Use **only** when domain alone is ambiguous:

```python
# 4-part examples (function NOT implied):
logistics_fleet_tracking_api        # fleet = tracking? management? maintenance?
analytics_reporting_api             # analytics = reporting? querying? processing?
communication_notification_worker   # communication = notifications? email? SMS?
```

---

## Philosophy: Why Semantic Shortening?

### The Problem with 4-Part Names

**Over-specification** leads to verbose names:

```python
# 4-part formula (redundant):
finance_lending_matching_api                # "matching" redundant (lending = matching)
finance_payment_processing_worker           # "processing" redundant (worker = processing)
healthcare_telemedicine_consultation_api    # "consultation" redundant (telemedicine = consultation)

# Character counts:
# - finance_lending_matching_api: 28 chars
# - finance_payment_processing_worker: 33 chars
# - healthcare_telemedicine_consultation_api: 42 chars
```

### The Solution: Implied Functions

**Context + domain combination** already communicates function:

```python
# 3-part formula (semantic):
finance_lending_api           # 19 chars (-9 chars, -32%)
finance_payment_worker        # 22 chars (-11 chars, -33%)
healthcare_telemedicine_api   # 27 chars (-15 chars, -36%)
```

**Why this works:**
- `lending` in finance context → P2P matching is the only function
- `payment` + `worker` type → processing is obvious
- `telemedicine` in healthcare → consultation is the service

---

## Decision Tree

### Step 1: Identify Context & Domain

```
Example:
- Context: finance
- Domain: lending
- Type: api
```

### Step 2: Test for Implicit Function

**Question**: Does "{context}_{domain}_{type}" clearly communicate what the service does?

```
Test name: finance_lending_api

Ask team: "What does finance_lending_api do?"
Expected answer: "P2P lending matching/approval platform"

If 90%+ of team gives correct answer → Use 3-part ✅
If answers vary widely → Use 4-part with explicit function ❌
```

### Step 3: Check for Ambiguity

**Question**: Could this domain have multiple functions?

```python
# Example: logistics_fleet_api

Possible interpretations:
1. Fleet tracking (GPS monitoring)
2. Fleet management (vehicles, drivers)
3. Fleet maintenance (repairs, inspections)

Result: AMBIGUOUS → Use 4-part
Correct name: logistics_fleet_tracking_api
```

### Decision Algorithm (Code)

```python
def choose_service_name_pattern(context: str, domain: str, type: str) -> str:
    """
    Determine whether to use 3-part or 4-part service name.

    Returns:
        "3-part" if domain implies function
        "4-part" if explicit function needed
    """
    # Step 1: Check if domain has single obvious function
    implied_functions = get_implied_functions(context, domain)

    if len(implied_functions) == 1:
        return "3-part"  # Domain clearly implies ONE function

    # Step 2: Check if type clarifies function
    if type == "worker" and "processing" in implied_functions:
        return "3-part"  # worker type implies processing

    # Step 3: Check if combination is unambiguous
    if is_combination_clear(context, domain, type):
        return "3-part"

    # Default: use explicit function
    return "4-part"


# Example usage:
choose_service_name_pattern("finance", "lending", "api")
# Returns: "3-part" → finance_lending_api

choose_service_name_pattern("logistics", "fleet", "api")
# Returns: "4-part" → logistics_fleet_{function}_api
```

---

## Examples by Context

### Finance Context (95% use 3-part)

| Domain | Implied Function | 3-Part Name | Why 3-Part? |
|--------|------------------|-------------|-------------|
| `lending` | matching, approval | `finance_lending_api` | Lending always means P2P matching |
| `payment` | processing | `finance_payment_api` | Payment systems process transactions |
| `crypto` | portfolio mgmt | `finance_crypto_api` | Crypto services manage portfolios |
| `billing` | invoicing, cycles | `finance_billing_api` | Billing generates invoices |
| `trading` | algo trading | `finance_trading_api` | Trading executes orders |

**Exception (4-part needed)**:
```python
finance_crypto_trading_api      # Crypto could be trading or portfolio management
finance_payment_validation_api  # Payment could be processing or validation
```

---

### Healthcare Context (80% use 3-part)

| Domain | Implied Function | 3-Part Name | Why 3-Part? |
|--------|------------------|-------------|-------------|
| `telemedicine` | consultation | `healthcare_telemedicine_api` | Telemedicine means online consultation |
| `appointment` | booking | `healthcare_appointment_api` | Appointments are booked/scheduled |
| `pharmacy` | medication mgmt | `healthcare_pharmacy_api` | Pharmacy manages medications |
| `mental_health` | therapy | `healthcare_mental_health_api` | Mental health provides therapy |

**Exception (4-part needed)**:
```python
healthcare_appointment_reminder_worker  # Appointments could be booking or reminders
healthcare_pharmacy_inventory_api       # Pharmacy could be inventory or prescriptions
```

---

### Construction Context (90% use 3-part)

| Domain | Implied Function | 3-Part Name | Why 3-Part? |
|--------|------------------|-------------|-------------|
| `house` | project mgmt | `construction_house_bot` | House projects need management |
| `material` | calc, inventory | `construction_material_api` | Materials are calculated/tracked |
| `renovation` | planning | `construction_renovation_api` | Renovations are planned/tracked |
| `commercial` | project mgmt | `construction_commercial_api` | Commercial projects managed |

---

### Logistics Context (50% use 4-part)

⚠️ **Logistics requires explicit functions** — domains are highly ambiguous.

| Domain | Multiple Functions | 4-Part Name (Required) | Why 4-Part? |
|--------|-------------------|------------------------|-------------|
| `fleet` | tracking, management, maintenance | `logistics_fleet_tracking_api` | Fleet has 3+ functions |
| `delivery` | routing, tracking | `logistics_delivery_tracking_api` | Delivery could route or track |
| `warehouse` | inventory, fulfillment | `logistics_warehouse_inventory_api` | Warehouse has multiple ops |

**Rare 3-part cases**:
```python
logistics_shipping_api   # Shipping is clearly booking/scheduling shipments
```

---

### Analytics Context (60% use 4-part)

| Domain | Multiple Functions | Name | Pattern |
|--------|-------------------|------|---------|
| `reporting` | generation | `analytics_reporting_api` | 3-part (specific) |
| `data` | aggregation, transformation | `analytics_data_aggregation_worker` | 4-part (ambiguous) |
| `dashboard` | visualization | `analytics_dashboard_api` | 3-part (specific) |
| `metrics` | collection, calculation | `analytics_metrics_collection_worker` | 4-part (ambiguous) |

---

## When to Use 4-Part (Exceptions)

### Rule 1: Domain Has Multiple Common Functions

```python
# ❌ BAD (ambiguous):
logistics_fleet_api

# ✅ GOOD (explicit):
logistics_fleet_tracking_api      # vs management, maintenance
logistics_fleet_management_api    # vs tracking, maintenance
```

### Rule 2: Context is Generic

```python
# ❌ BAD (too generic):
communication_email_api

# ✅ GOOD (specific function):
communication_email_notification_worker   # vs campaign, validation
communication_email_campaign_api          # vs notification, validation
```

### Rule 3: Type Doesn't Clarify Function

```python
# ✅ OK (type clarifies):
finance_payment_worker    # worker → processing implied

# ❌ BAD (type doesn't clarify):
finance_payment_api       # API could be processing, validation, history

# ✅ GOOD (explicit):
finance_payment_processing_api
finance_payment_validation_api
```

---

## Common Mistakes

### Mistake #1: Over-Shortening (Under-Specification)

❌ **WRONG**:
```python
logistics_fleet_api         # Ambiguous - what does it do?
analytics_data_api          # Too generic
communication_bot           # Which communication channel?
```

✅ **CORRECT**:
```python
logistics_fleet_tracking_api        # Explicit function
analytics_data_aggregation_worker   # Specific operation
communication_telegram_bot          # Specific channel
```

### Mistake #2: Over-Specification (Redundancy)

❌ **WRONG**:
```python
finance_lending_matching_api                # "matching" redundant
finance_payment_processing_worker           # "processing" redundant
healthcare_telemedicine_consultation_api    # "consultation" redundant
```

✅ **CORRECT**:
```python
finance_lending_api           # matching implied
finance_payment_worker        # processing implied
healthcare_telemedicine_api   # consultation implied
```

### Mistake #3: Inconsistent Patterns Within Context

❌ **WRONG**:
```python
# Mixing 3-part and 4-part without reason:
finance_lending_api                    # 3-part
finance_crypto_portfolio_api           # 4-part (unnecessary)
finance_billing_invoicing_generation_api  # 4-part (over-specified)
```

✅ **CORRECT**:
```python
# Consistent 3-part (all have clear functions):
finance_lending_api     # matching implied
finance_crypto_api      # portfolio implied
finance_billing_api     # invoicing implied
```

### Mistake #4: Using Abbreviations Instead of Semantic Shortening

❌ **WRONG**:
```python
fin_lend_api           # Cryptic abbreviations
health_telem_api       # Hard to read
constr_house_bot       # Onboarding nightmare
```

✅ **CORRECT**:
```python
finance_lending_api              # Full words, semantic shortening
healthcare_telemedicine_api      # Clear and professional
construction_house_bot           # Self-documenting
```

---

## Validation Checklist

### Before Naming a New Service

- [ ] **Step 1**: Identified context, domain, and type clearly
- [ ] **Step 2**: Asked 3+ team members: "What does `{context}_{domain}_{type}` do?"
- [ ] **Step 3**: 90%+ of answers were consistent → use 3-part
- [ ] **Step 4**: If answers varied → add explicit function (4-part)
- [ ] **Step 5**: Checked name length < 30 chars (95% compatibility)
- [ ] **Step 6**: Verified no ambiguity with existing services in same context
- [ ] **Step 7**: Tested in Kubernetes DNS format (`name.replace('_', '-')`)

### Quality Gates

**Must pass ALL checks:**

1. **Clarity Test**: Can a new developer understand service purpose from name alone?
2. **Uniqueness Test**: No other service in same context has similar name?
3. **Length Test**: Name ≤ 30 chars (Kubernetes compatibility)?
4. **Consistency Test**: Follows same pattern as other services in context?
5. **No Abbreviations Test**: All words are full words (no `fin`, `telem`, `mgmt`)?

---

## Migration from 4-Part

### When to Migrate

**Migrate when:**
- ✅ Service name > 30 chars
- ✅ Function word is clearly redundant
- ✅ Team consensus that 3-part is clear
- ✅ Service is under active development (low risk)

**DON'T migrate when:**
- ❌ Service is in production with external integrations
- ❌ Function word adds meaningful clarity
- ❌ Team is uncertain about 3-part clarity
- ❌ Migration requires >1 hour of work

### Migration Steps

#### Step 1: Identify Candidates

```bash
# Find all services with >30 char names:
find services/ -type d -name "*_*_*_*" | \
  awk -F'/' '{print length($NF), $NF}' | \
  awk '$1 > 30' | \
  sort -rn

# Example output:
# 42 healthcare_telemedicine_consultation_api
# 38 finance_payment_processing_worker
# 36 construction_material_calculation_api
```

#### Step 2: Apply Decision Tree

```python
# For each candidate:
def should_migrate(service_name: str) -> bool:
    context, domain, function, type_ = service_name.split('_')

    # Test if function is redundant:
    if is_function_implied(context, domain, type_):
        return True

    # Test if domain is ambiguous without function:
    if is_domain_ambiguous(context, domain):
        return False

    return True

# Examples:
should_migrate("healthcare_telemedicine_consultation_api")  # True
should_migrate("logistics_fleet_tracking_api")              # False (ambiguous)
```

#### Step 3: Refactor Service

```python
# Old structure:
services/
  finance_payment_processing_worker/
    src/
      finance_payment_processing_worker/
        __init__.py
        main.py

# New structure (refactored):
services/
  finance_payment_worker/
    src/
      finance_payment_worker/
        __init__.py
        main.py
```

**Refactoring checklist:**
- [ ] Rename service folder
- [ ] Rename Python package
- [ ] Update `pyproject.toml` / `setup.py`
- [ ] Update Docker Compose service name
- [ ] Update Kubernetes manifests
- [ ] Update CI/CD pipelines
- [ ] Update documentation references
- [ ] Update inter-service communication configs

#### Step 4: Automated Refactoring Script

```bash
#!/bin/bash
# migrate_service.sh

OLD_NAME="$1"  # e.g., finance_payment_processing_worker
NEW_NAME="$2"  # e.g., finance_payment_worker

# Validate inputs
if [ -z "$OLD_NAME" ] || [ -z "$NEW_NAME" ]; then
    echo "Usage: ./migrate_service.sh <old_name> <new_name>"
    exit 1
fi

# 1. Rename service directory
mv "services/$OLD_NAME" "services/$NEW_NAME"

# 2. Rename Python package
mv "services/$NEW_NAME/src/$OLD_NAME" "services/$NEW_NAME/src/$NEW_NAME"

# 3. Update imports across entire project
find services/ -type f -name "*.py" -exec sed -i \
    "s/from $OLD_NAME/from $NEW_NAME/g" {} +
find services/ -type f -name "*.py" -exec sed -i \
    "s/import $OLD_NAME/import $NEW_NAME/g" {} +

# 4. Update Docker Compose
sed -i "s/$OLD_NAME/$NEW_NAME/g" docker-compose.yml

# 5. Update Kubernetes manifests
find kubernetes/ -type f -name "*.yaml" -exec sed -i \
    "s/${OLD_NAME//_/-}/${NEW_NAME//_/-}/g" {} +

# 6. Update pyproject.toml
sed -i "s/name = \"$OLD_NAME\"/name = \"$NEW_NAME\"/g" \
    "services/$NEW_NAME/pyproject.toml"

echo "✅ Migration complete: $OLD_NAME → $NEW_NAME"
echo "⚠️  Manual steps required:"
echo "  1. Review all changes with git diff"
echo "  2. Update CI/CD pipeline configs"
echo "  3. Update documentation"
echo "  4. Test locally with docker-compose up"
```

#### Step 5: Rollback Plan

```bash
#!/bin/bash
# rollback_migration.sh

# If migration fails, rollback using git:
git checkout services/$OLD_NAME
git checkout docker-compose.yml
git checkout kubernetes/

# Restore original service
mv "services/$NEW_NAME" "services/$OLD_NAME"
mv "services/$OLD_NAME/src/$NEW_NAME" "services/$OLD_NAME/src/$OLD_NAME"

echo "✅ Rollback complete"
```

---

## Summary

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│          SEMANTIC SHORTENING QUICK REFERENCE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DEFAULT: {context}_{domain}_{type}  (3-part)               │
│                                                             │
│  ✅ Use 3-part when:                                        │
│     • Domain clearly implies ONE function                   │
│     • Team understands service from name alone              │
│     • Type clarifies function (worker → processing)         │
│                                                             │
│  ❌ Use 4-part when:                                        │
│     • Domain has MULTIPLE possible functions                │
│     • Context is generic/ambiguous                          │
│     • Explicit function adds critical clarity               │
│                                                             │
│  📏 Target: 20-27 chars (95% K8s compatible)                │
│                                                             │
│  🚫 NEVER use cryptic abbreviations (fin, telem, mgmt)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- **[Naming Conventions](../atomic/architecture/naming/README.md)** — Complete naming standards
- **[Service Catalog](../../README.md#project-structure)** — Current service inventory
- **[Architecture Guide](architecture-guide.md)** — Service design principles
- **Migration Steps** — See Section 5 above for step-by-step migration from 4-part

---

**Last Updated**: 2025-01-02
**Maintainer**: System Architect
**Status**: Active
**Version**: 1.0
