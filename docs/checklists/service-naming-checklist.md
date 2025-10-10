# Service Naming Decision Checklist

**Purpose**: Machine-readable checklist for AI agents and developers to decide between 3-part and 4-part service naming.

**Related**: [Naming Conventions](../atomic/architecture/naming-conventions.md) | [Semantic Shortening Guide](../guides/semantic-shortening-guide.md)

---

## Step 1: Start with 3-Part (Default)

**Formula**: `{context}_{domain}_{type}`

**Examples**:
- `finance_lending_api` (P2P lending platform)
- `healthcare_telemedicine_api` (Online consultation service)
- `construction_house_bot` (House project management bot)

**Expected distribution**: 80-90% of services should use 3-part naming.

---

## Step 2: Check 10 Reasons for 4-Part

**IMPORTANT**: Use 4-part ONLY if **at least ONE** reason applies.

### Checklist

- [ ] **Reason 1: Domain Ambiguity** — Domain word implies 3+ operations?
  - Examples: `fleet`, `analytics`, `communication`, `warehouse`, `delivery`
  - Test: "Can this domain mean tracking OR management OR maintenance OR...?"

- [ ] **Reason 2: Multiple Services per Domain** — Need 2+ services in same `{context}_{domain}`?
  - Example: `logistics_fleet_tracking_api` AND `logistics_fleet_management_api`
  - Test: "Do I need to split this domain into separate microservices?"

- [ ] **Reason 3: Cross-Context Collision** — Same domain word in different contexts?
  - Example: `communication_notification_worker` vs `system_notification_api`
  - Test: "Is this domain used in 2+ contexts with different meanings?"

- [ ] **Reason 4: Organizational Policy** — Team requires explicit functions?
  - Check: Context Registry (`docs/atomic/architecture/context-registry.md`)
  - Test: "Does our policy require explicit functions for this context?"

- [ ] **Reason 5: Technical Differentiation** — Different technologies/providers?
  - Example: `finance_payment_stripe_api` vs `finance_payment_paypal_api`
  - Test: "Do I need separate services for different providers/technologies?"

- [ ] **Reason 6: Functional Split (Migration)** — Blue-green with functional split?
  - Example: Monolith → `finance_lending_matching_api` + `finance_lending_approval_api`
  - Test: "Am I decomposing a monolith into functional areas?"

- [ ] **Reason 7: Legacy Terminology** — Existing system has established terms?
  - Example: `OldERP.FleetTrackingModule` → `logistics_fleet_tracking_api`
  - Test: "Should I preserve legacy naming to avoid team confusion?"

- [ ] **Reason 8: Regulatory Requirements** — Compliance requires separation?
  - Example: `finance_payment_processing_api` vs `finance_payment_storage_api` (PCI)
  - Test: "Does regulator require explicit functional separation?"

- [ ] **Reason 9: Different SLA/Resources** — Radically different infrastructure?
  - Example: `analytics_querying_api` (ms latency) vs `analytics_aggregation_worker` (hour latency)
  - Test: "Do functions need completely different scaling strategies?"

- [ ] **Reason 10: Onboarding Clarity** — New team members confused?
  - Example: Large platform (50+ services) where 3-part names are unclear
  - Test: "Would new developers struggle to understand this service from 3-part name?"

---

## Step 3: Make Decision

### If ALL unchecked → Use 3-part ✅

**Pattern**: `{context}_{domain}_{type}`

**Rationale**: Function is implied by context + domain.

**Examples**:
```
finance_lending_api          ← lending = matching/approval (clear)
healthcare_telemedicine_api  ← telemedicine = consultation (clear)
construction_house_bot       ← house = project management (clear)
finance_payment_worker       ← payment = processing (clear)
```

---

### If AT LEAST ONE checked → Use 4-part ✅

**Pattern**: `{context}_{domain}_{function}_{type}`

**Rationale**: Domain is ambiguous, explicit function required.

**Examples**:
```
logistics_fleet_tracking_api         ← fleet ambiguous (Reason 1)
analytics_reporting_api              ← analytics ambiguous (Reason 1)
communication_notification_worker    ← communication ambiguous (Reason 1)
finance_payment_stripe_api           ← multiple providers (Reason 5)
healthcare_patient_storage_api       ← regulatory separation (Reason 8)
```

---

## Anti-Patterns to Avoid

### ❌ DO NOT use 4-part for:

1. **Multiple code features** — Service has CRUD + search + export
   - ❌ BAD: `construction_house_management_bot`
   - ✅ GOOD: `construction_house_bot` (management implied)

2. **Multiple endpoints** — API has /create, /update, /delete routes
   - ❌ BAD: `finance_lending_operations_api`
   - ✅ GOOD: `finance_lending_api` (CRUD implied)

3. **Name seems short** — Adding words for length
   - ❌ BAD: `finance_lending_platform_api`
   - ✅ GOOD: `finance_lending_api` (brevity is good)

4. **Symmetry with others** — Matching other services' patterns
   - ❌ BAD: Forcing all services to 4-part for consistency
   - ✅ GOOD: Evaluate each service independently

---

## Quick Examples by Context

### Finance (mostly 3-part)
```
✅ finance_lending_api          # lending = matching/approval (clear)
✅ finance_payment_api          # payment = processing (clear)
✅ finance_crypto_api           # crypto = portfolio mgmt (clear)
✅ finance_billing_api          # billing = invoicing (clear)
```

### Healthcare (mostly 3-part)
```
✅ healthcare_telemedicine_api  # telemedicine = consultation (clear)
✅ healthcare_appointment_api   # appointment = booking (clear)
✅ healthcare_pharmacy_api      # pharmacy = medication mgmt (clear)
```

### Logistics (often 4-part)
```
✅ logistics_fleet_tracking_api      # fleet ambiguous → need function
✅ logistics_delivery_routing_api    # delivery ambiguous → need function
✅ logistics_warehouse_inventory_api # warehouse ambiguous → need function
```

### Analytics (often 4-part)
```
✅ analytics_reporting_api           # analytics ambiguous → need function
✅ analytics_querying_api            # analytics ambiguous → need function
✅ analytics_aggregation_worker      # analytics ambiguous → need function
```

### Communication (often 4-part)
```
✅ communication_notification_worker # communication ambiguous → need function
✅ communication_email_api           # communication ambiguous → need function
✅ communication_webhook_api         # communication ambiguous → need function
```

---

## For AI Agents

### Automated Decision Process

```python
def decide_naming_pattern(context: str, domain: str, type_: str) -> str:
    """
    Automated 3-part vs 4-part decision for AI agents.

    Returns:
        "3-PART" or "4-PART_REQUIRED"
    """
    # Check Reason 1: Domain Ambiguity
    ambiguous_domains = [
        'fleet', 'analytics', 'data', 'communication', 'warehouse',
        'delivery', 'content', 'user', 'document', 'event',
        'monitoring', 'network', 'asset', 'inventory', 'customer'
    ]

    if domain in ambiguous_domains:
        return "4-PART_REQUIRED"

    # For other reasons (2-10), human judgment or explicit input needed
    # Default to 3-part
    return "3-PART"

# Usage
result = decide_naming_pattern("finance", "lending", "api")
# Returns: "3-PART" → use finance_lending_api

result = decide_naming_pattern("logistics", "fleet", "api")
# Returns: "4-PART_REQUIRED" → use logistics_fleet_{function}_api
```

### AI Prompt Template

When AI needs to name a service:

```
Context: {context}
Domain: {domain}
Type: {type}

Step 1: Check domain ambiguity
- Is domain in ambiguous list? [YES/NO]
- Can domain mean 3+ operations? [YES/NO]

Step 2: Check other reasons (2-10)
- [List any applicable reasons]

Step 3: Decision
- If domain ambiguous OR any reason applies → 4-PART
- Otherwise → 3-PART

Result: {chosen_pattern}
Rationale: {explanation}
```

---

## Validation

After naming, verify:

- [ ] **Pattern correct** — 3-part or 4-part as decided
- [ ] **Separator correct** — Underscores in code/data layer
- [ ] **No abbreviations** — Full words (e.g., `finance`, not `fin`)
- [ ] **Function justified** — If 4-part, cite specific reason (1-10)
- [ ] **Documented** — Add to Context Registry if new context

---

## Expected Statistics

**Healthy project distribution**:
- **80-90% services**: 3-part (clear domains)
- **10-20% services**: 4-part (ambiguous domains)

**Warning**: If your project has **> 30% 4-part services** → domains may be too generic. Consider refactoring domain decomposition.

---

## References

- **Complete guide**: [Naming Conventions](../atomic/architecture/naming/README.md)
- **10 Reasons detailed**: [10 Serious Reasons for 4-Part Naming](../atomic/architecture/naming/naming-4part-reasons.md)
- **Decision tree**: [Semantic Shortening Guide](../guides/semantic-shortening-guide.md)
- **Context tracking**: [Context Registry](../atomic/architecture/context-registry.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-03
**Maintained By**: Framework Core Team
