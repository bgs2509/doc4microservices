# 4-Part Service Naming: 10 Serious Reasons (Detailed)

This guide provides comprehensive analysis of when to use 4-part service naming in the doc4microservices framework. It presents 10 objective reasons that justify adding a `{function}` component to the standard 3-part naming pattern.

**PRINCIPLE**: Default to 3-part. Use 4-part ONLY when one of these 10 reasons applies. If NONE apply, use 3-part naming.

---

## Guiding Rules

**BURDEN OF PROOF**: Always start with 3-part naming (`{context}_{domain}_{type}`). The burden of proof is on justifying the 4th component.

**OBJECTIVE TEST**: Can this domain word refer to 3+ different operations in this context? If yes, consider 4-part. If no, use 3-part.

---

## Reason 1: Domain Ambiguity ⭐ PRIMARY REASON

**Criterion**: The domain word can mean **3 or more different operations** in the given context.

**Test**: If you tell a colleague "We have a `fleet` service", and they ask "What does it do with the fleet?" — use 4-part.

### Examples of Ambiguous Domains

| Domain | Possible Operations | Required 4-Part Names |
|--------|-------------------|----------------------|
| `fleet` | tracking, management, maintenance, scheduling, optimization | `logistics_fleet_tracking_api`, `logistics_fleet_management_api` |
| `analytics` | reporting, querying, processing, visualization, aggregation | `analytics_reporting_api`, `analytics_querying_api` |
| `data` | collection, storage, transformation, aggregation, export | `analytics_data_aggregation_worker` |
| `communication` | notification, email, sms, push, webhook, chat | `communication_notification_worker` |
| `warehouse` | inventory, fulfillment, shipping, receiving, storage | `logistics_warehouse_inventory_api` |
| `delivery` | routing, tracking, scheduling, optimization | `logistics_delivery_routing_api` |
| `content` | creation, moderation, publishing, archiving | `media_content_moderation_api` |
| `user` (broad context) | authentication, profile, preferences, activity, analytics | `platform_user_authentication_api` |
| `document` | creation, storage, processing, conversion, signing | `legal_document_signing_api` |
| `event` | creation, tracking, processing, notification, analytics | `platform_event_processing_worker` |
| `monitoring` | collection, alerting, visualization, reporting | `infrastructure_monitoring_alerting_api` |
| `network` | routing, monitoring, configuration, security | `infrastructure_network_monitoring_api` |
| `asset` | tracking, valuation, maintenance, disposal | `finance_asset_valuation_api` |
| `inventory` | tracking, management, optimization, forecasting | `retail_inventory_optimization_api` |
| `customer` | acquisition, retention, support, analytics | `sales_customer_acquisition_api` |

### Counter-examples (Clear Domains - Use 3-Part)
- `lending` → clearly means loan matching/approval
- `payment` → clearly means payment processing
- `telemedicine` → clearly means online consultation
- `house` (in construction context) → clearly means project management

---

## Reason 2: Multiple Services per Domain

**Criterion**: You need **2 or more separate services** within the same `{context}_{domain}`, each handling different functions.

### Example: Logistics Fleet Management

```
logistics_fleet_tracking_api      ← GPS tracking in real-time
logistics_fleet_management_api    ← Driver/vehicle management
logistics_fleet_maintenance_api   ← Maintenance scheduling
logistics_fleet_optimization_api  ← Route optimization
```

**Without 4-part**: Impossible to create multiple services in same domain without name collision.

**Test**: If you need to split domain into multiple independent services → use 4-part.

---

## Reason 3: Cross-Context Name Collision

**Criterion**: The same domain word is used in **different contexts with different meanings**, requiring disambiguation.

### Example: `notification` in Different Contexts

```
# Context: communication (user-facing notifications)
communication_push_notification_worker  ← Push to users

# Context: system (internal system alerts)
system_alert_notification_api           ← Internal alerts for admins

# Context: analytics (metric threshold alerts)
analytics_threshold_notification_api    ← Business metric alerts
```

**Problem without 4-part**: All three would be `{context}_notification_api`, but they serve completely different purposes.

**Test**: If domain is used in 2+ contexts with different semantics → consider 4-part or rename domain.

---

## Reason 4: Organizational Policy

**Criterion**: Your team/organization has an **established policy** requiring explicit functions for certain contexts.

### Example Policy

"All services in `analytics` context must explicitly state their function"

```yaml
# Policy enforced:
analytics_reporting_api          ← explicit function required
analytics_querying_api           ← explicit function required
analytics_aggregation_worker     ← explicit function required
```

**Test**: Check your Context Registry (`docs/atomic/architecture/context-registry.md`) for context-specific policies.

---

## Reason 5: Technical Differentiation

**Criterion**: The domain has **multiple technical implementations** (different technologies/providers) requiring separate services.

### Example: Payment Processing with Multiple Providers

```
# Problem: one domain, multiple providers
finance_payment_api  ← Which provider? Stripe? PayPal? Crypto?

# Solution: explicit provider as function
finance_payment_stripe_api    ← Stripe gateway
finance_payment_paypal_api    ← PayPal gateway
finance_payment_crypto_api    ← Cryptocurrency processing
```

### Example: Data Storage with Different Engines

```
storage_data_postgres_api     ← PostgreSQL wrapper
storage_data_mongo_api        ← MongoDB wrapper
storage_data_s3_api           ← S3 file storage
```

**Test**: If domain needs multiple services for different technologies/providers → use 4-part.

---

## Reason 6: Functional Split During Migration

**Criterion**: Blue-green deployment or migration requires **functional decomposition** of a monolith.

### Example: Monolith to Microservices Migration

```
# Legacy monolith
finance_lending_api              ← old monolithic service

# New microservices (functional split)
finance_lending_matching_api     ← borrower-lender matching
finance_lending_approval_api     ← credit approval workflow
finance_lending_servicing_api    ← loan servicing
```

**Note**: Use 4-part **ONLY** if migration requires functional split. Not for simple v1/v2 versioning (versions belong in API paths, not service names).

**Test**: If migration requires splitting ONE domain into multiple functional areas → use 4-part.

---

## Reason 7: Legacy System Integration

**Criterion**: Integration with existing system where terminology is **already established** and changing it would cause confusion.

### Example: Migrating from ERP System

```
# Old ERP modules (established terminology)
OldERP.FleetTrackingModule     ← legacy name
OldERP.FleetManagementModule   ← legacy name

# New architecture (preserve terminology)
logistics_fleet_tracking_api      ← matches FleetTrackingModule
logistics_fleet_management_api    ← matches FleetManagementModule
```

**Rationale**: Team is familiar with "tracking" vs "management" distinction — don't change terminology unnecessarily.

**Test**: If legacy system has established functional names → preserve them via 4-part.

---

## Reason 8: Regulatory/Compliance Requirements

**Criterion**: Regulations or audits require **explicit functional separation** at the service level.

### Example: Financial Services with Regulatory Separation

```
# Regulation: "Payment processing and payment data storage must be separate systems"

finance_payment_processing_api   ← explicit: processing
finance_payment_storage_api      ← explicit: storage (GDPR/PCI)
```

### Example: Healthcare (HIPAA/GDPR Compliance)

```
# Requirement: "Patient data storage and processing must be separate"

healthcare_patient_storage_api      ← HIPAA-compliant storage
healthcare_patient_processing_api   ← Data processing/analytics
```

**Test**: If regulator requires explicit separation → use 4-part.

---

## Reason 9: Different SLA/Resource Requirements

**Criterion**: Functions within a domain require **radically different SLA** or infrastructure resources, dictating separate services.

### Example: Analytics with Different Performance Profiles

```
analytics_querying_api           ← high load, low latency (ms), horizontal scaling
analytics_aggregation_worker     ← low load, high latency (min/hours), vertical scaling
```

**Characteristics comparison**:
- `querying`: 1000 req/sec, response < 100ms, 10+ replicas
- `aggregation`: 10 jobs/hour, response 10-60 min, 2 large workers

**Test**: If functions need different infrastructure strategies → use 4-part.

---

## Reason 10: Onboarding Clarity

**Criterion**: Large team (10+ developers) where **newcomers regularly struggle** to understand service purpose from 3-part names.

### Example: Platform with 50+ Microservices

```
# Problem: newcomer confusion
communication_api  ← What does it do? Send? Receive? Both?
communication_bot  ← What's the difference?

# Solution: explicit functions for self-documentation
communication_notification_worker   ← clear: sends notifications
communication_telegram_bot          ← clear: Telegram interface
communication_webhook_api           ← clear: receives webhooks
```

**Test**: If new developers can't understand service purpose from 3-part name → use 4-part.

---

## Decision Checklist: 3-Part vs 4-Part

**Before adding `{function}`, verify at least ONE reason applies:**

- [ ] **Reason 1**: Domain implies 3+ operations?
- [ ] **Reason 2**: Need 2+ services in same domain?
- [ ] **Reason 3**: Cross-context name collision?
- [ ] **Reason 4**: Organizational policy requires it?
- [ ] **Reason 5**: Different technologies/providers?
- [ ] **Reason 6**: Functional split during migration?
- [ ] **Reason 7**: Legacy system has established terms?
- [ ] **Reason 8**: Regulatory requirement for separation?
- [ ] **Reason 9**: Radically different SLA/resources?
- [ ] **Reason 10**: Onboarding clarity issue?

**If ALL unchecked** → ✅ Use 3-part (function is implied)

**If AT LEAST ONE checked** → ✅ Use 4-part with explicit `{function}`

---

## Anti-Patterns: DO NOT Use 4-Part For

### ❌ Anti-Pattern 1: Service Has Many Features

**Bad reasoning**: "Service has multiple code features (CRUD, search, export) → need 4-part"

```yaml
# WRONG
construction_house_management_bot  ← redundant
```

**Correct**:
```yaml
# RIGHT
construction_house_bot  ← management implied by context
```

**Rule**: Multiple **code features** ≠ ambiguous domain. Use 3-part.

### ❌ Anti-Pattern 2: Service Has Many Endpoints

**Bad reasoning**: "API has many endpoints (/create, /update, /delete) → need 4-part"

```yaml
# WRONG
finance_lending_operations_api  ← redundant
```

**Correct**:
```yaml
# RIGHT
finance_lending_api  ← CRUD operations implied for API
```

**Rule**: Multiple REST endpoints ≠ ambiguous domain. Use 3-part.

### ❌ Anti-Pattern 3: Name Seems Too Short

**Bad reasoning**: "19 chars seems short → add generic word for length"

```yaml
# WRONG
finance_lending_platform_api  ← adding "platform" for length
```

**Correct**:
```yaml
# RIGHT
finance_lending_api  ← brevity is good
```

**Rule**: Brevity is a virtue, not a problem. Use 3-part.

### ❌ Anti-Pattern 4: Symmetry with Other Services

**Bad reasoning**: "Other service uses 4-part → use 4-part for symmetry"

```yaml
# WRONG (forced symmetry)
finance_lending_processing_api    ← has 4-part cause
finance_payment_processing_api    ← forced to match (bad!)
```

**Correct**:
```yaml
# RIGHT (independent evaluation)
finance_lending_api               ← processing implied
finance_payment_api               ← processing implied
```

**Rule**: Evaluate each service independently. Don't force symmetry.

---

## Expected Distribution

**In a well-designed architecture**:
- **80-90% of services**: 3-part (most domains are specific)
- **10-20% of services**: 4-part (only truly ambiguous domains)

**Warning**: If your project has **> 30% services using 4-part** → domains are probably too generic. Consider refactoring domain decomposition.

---

## Related Documents

- `naming-services.md` — Service naming patterns guide
- `../../guides/SEMANTIC_SHORTENING_GUIDE.md` — Decision tree for 3-part vs 4-part
- `../../checklists/SERVICE_NAMING_CHECKLIST.md` — Quick checklist for naming decisions
- `../context-registry.md` — Context name registry to prevent conflicts