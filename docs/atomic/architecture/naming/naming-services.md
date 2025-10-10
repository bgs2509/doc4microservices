# Service Naming Patterns

This guide covers microservice naming patterns in the doc4microservices framework. It establishes the primary 3-part naming formula (`{context}_{domain}_{type}`) as the default, with 4-part naming reserved for ambiguous domains.

**Key Principle**: DEFAULT TO 3-PART naming. Function is implied by the domain in most cases. Use 4-part only when the domain word can refer to 3+ different operations.

---

## Guiding Rules

1. **DEFAULT TO 3-PART** naming (`{context}_{domain}_{type}`)
2. **Use 4-part ONLY when domain is ambiguous** (burden of proof required)
3. **Semantic shortening**: Clear context + domain, omit redundant function words
4. **Average length**: 20-27 characters (no abbreviations needed)
5. **Context uniqueness**: Never reuse context names for different business domains

---

## Service Naming Formula

### Primary Pattern (3-part)

`{context}_{domain}_{type}`

This hierarchical formula creates self-documenting service names where function is implied:
- **{context}**: Business area (finance, healthcare, construction...)
- **{domain}**: Subdomain within context (lending, telemedicine, house...)
- **{type}**: Technical service type (api, worker, bot...)

**Philosophy**: Function words are often redundant when context+domain already imply the action:
- `lending` domain → matching/approval implied
- `payment` domain → processing implied
- `telemedicine` domain → consultation implied
- `worker` type → background processing implied

**Examples (3-part)**:
- `finance_lending_api` — Lending platform (19 chars, matching implied)
- `healthcare_telemedicine_api` — Telemedicine service (27 chars, consultation implied)
- `construction_house_bot` — House management bot (22 chars, management implied)

### Extended Pattern (4-part)

`{context}_{domain}_{function}_{type}`

Use when domain has multiple possible functions (ambiguous):

**Examples (4-part)**:
- `logistics_fleet_tracking_api` — Fleet needs clarification (vs management, maintenance)
- `analytics_reporting_api` — Analytics needs clarification (vs querying, processing)
- `communication_notification_worker` — Communication needs clarification (vs email, SMS)

---

## When to Use 3-Part vs 4-Part

**TL;DR**: Ask "Can this domain word refer to 3+ different operations?" If yes, use 4-part. If no, use 3-part.

**Common Patterns**:

| Domain Example | Clear (3-part) | Ambiguous (4-part) |
|----------------|----------------|---------------------|
| `lending` | ✅ `finance_lending_api` | - |
| `payment` | ✅ `finance_payment_worker` | - |
| `telemedicine` | ✅ `healthcare_telemedicine_api` | - |
| `fleet` | - | ❌ `logistics_fleet_tracking_api` (vs management, maintenance, scheduling) |
| `analytics` | - | ❌ `analytics_reporting_api` (vs querying, processing, visualization) |
| `communication` | - | ❌ `communication_notification_worker` (vs email, SMS, push) |

**Important**: Don't confuse "multiple code features" with "ambiguous domain"
- ✅ `construction_house_bot` (3-part) — Multiple features (calc, upload, track) serving ONE domain (house projects)
- ❌ DON'T use 4-part just because service has many features

---

## Domain-Function Mapping (Implied Functions)

### Finance Context (mostly 3-part)

| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `lending` | matching, approval | `finance_lending_api` | 19 |
| `payment` | processing | `finance_payment_api` | 19 |
| `crypto` | portfolio management | `finance_crypto_api` | 18 |
| `billing` | invoicing, cycles | `finance_billing_api` | 19 |
| `trading` | algorithmic trading | `finance_trading_api` | 19 |

### Healthcare Context (mostly 3-part)

| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `telemedicine` | consultation | `healthcare_telemedicine_api` | 27 |
| `appointment` | booking | `healthcare_appointment_api` | 26 |
| `pharmacy` | medication management | `healthcare_pharmacy_api` | 23 |
| `mental_health` | therapy, counseling | `healthcare_mental_health_api` | 28 |

### Construction Context (mostly 3-part)

| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `house` | project management | `construction_house_bot` | 22 |
| `material` | calculation, inventory | `construction_material_api` | 25 |
| `renovation` | planning | `construction_renovation_api` | 27 |
| `commercial` | project management | `construction_commercial_api` | 27 |

### Logistics Context (needs 4-part often)

| Domain | Multiple Functions | 4-Part Name (explicit) | Chars |
|--------|--------------------|------------------------|-------|
| `fleet` | tracking OR management OR maintenance | `logistics_fleet_tracking_api` | 28 |
| `delivery` | routing OR tracking | `logistics_delivery_tracking_api` | 31 |
| `warehouse` | inventory OR fulfillment | `logistics_warehouse_inventory_api` | 34 |

### Analytics Context (needs 4-part often)

| Domain | Multiple Functions | 4-Part Name (explicit) | Chars |
|--------|--------------------|------------------------|-------|
| `reporting` | generation (not querying) | `analytics_reporting_api` | 23 |
| `data` | aggregation OR transformation | `analytics_data_aggregation_worker` | 34 |
| `dashboard` | visualization (clear) | `analytics_dashboard_api` | 23 |

---

## Extended Context Catalog

| Context (Full) | Business Domain | Example Services (3-part) |
|---------------|-----------------|---------------------------|
| `finance` | Financial services | `finance_lending_api`, `finance_crypto_api` |
| `healthcare` | Medical & health | `healthcare_telemedicine_api`, `healthcare_appointment_api` |
| `construction` | Building & construction | `construction_house_bot`, `construction_material_api` |
| `education` | Learning & training | `education_lms_api`, `education_courses_api` |
| `logistics` | Transport & delivery | `logistics_fleet_tracking_api`, `logistics_delivery_tracking_api` |
| `ecommerce` | Online commerce | `ecommerce_marketplace_api`, `ecommerce_dropship_api` |
| `corporate` | Enterprise tools | `corporate_crm_api`, `corporate_hr_api` |
| `property_management` | Real estate | `property_house_api`, `property_tenant_api` |
| `communication` | Messaging & notifications | `communication_notification_worker`, `communication_telegram_bot` |
| `analytics` | Data & reporting | `analytics_reporting_api`, `analytics_dashboard_api` |
| `user_management` | Auth & profiles | `user_auth_api`, `user_profile_api` |
| `integration` | Third-party APIs | `integration_stripe_api`, `integration_google_api` |
| `environment` | Ecology & monitoring | `environment_emission_api`, `environment_recycling_api` |

**Naming Strategy**:
- ✅ Use **3-part formula** by default (context + domain + type)
- ✅ Add explicit function (4-part) only when domain is ambiguous
- ✅ Average name length: 20-27 characters (no abbreviations needed)

---

## Domain Examples per Context

### Finance Context
- `lending` - P2P loans, microloans
- `crypto` - Cryptocurrency portfolio, trading
- `payments` - Payment processing
- `billing` - Subscription billing
- `trading` - Algorithmic trading

### Healthcare Context
- `telemedicine` - Online consultations
- `appointment` - Doctor booking
- `mental_health` - Psychological support
- `pharmacy` - Medication management

### Construction Context
- `house` - Residential building
- `commercial` - Commercial projects
- `renovation` - Remodeling projects
- `material` - Materials management

### Education Context
- `lms` - Learning management
- `courses` - Online courses
- `webinar` - Webinar platform
- `assessment` - Testing & grading

---

## Function Naming Patterns (4-Part Only)

Use explicit function words **only** when domain is ambiguous. Most services use 3-part (function implied).

| Function | Use When (Domain Ambiguous) | 4-Part Example |
|----------|----------------------------|----------------|
| `tracking` | Fleet/delivery could be tracking OR routing OR management | `logistics_fleet_tracking_api`, `logistics_delivery_tracking_api` |
| `notification` | Communication could be notification OR email OR SMS | `communication_notification_worker` |
| `reporting` | Analytics could be reporting OR querying OR processing | `analytics_reporting_api` |
| `aggregation` | Data could be aggregation OR transformation OR storage | `analytics_data_aggregation_worker` |
| `inventory` | Warehouse could be inventory OR fulfillment OR shipping | `logistics_warehouse_inventory_api` |

**Note**: For clear domains, use 3-part:
- `finance_lending_api` (matching implied)
- `healthcare_telemedicine_api` (consultation implied)
- `construction_house_bot` (management implied)
- `finance_payment_worker` (processing implied)

---

## Service Type Catalog

| Type | Description | Technology | Example (3-part) |
|------|-------------|------------|------------------|
| `api` | REST API service | FastAPI, Flask | `finance_lending_api` |
| `worker` | Background job processor | Celery, RQ | `finance_payment_worker` |
| `bot` | Chat bot interface | Aiogram, Telegram Bot API | `construction_house_bot` |
| `gateway` | API Gateway / proxy | Kong, Nginx | `ecommerce_gateway` |
| `stream` | Stream processor | Kafka Streams, Flink | `logistics_tracking_stream` |
| `scheduler` | Task scheduler | APScheduler, Celery Beat | `analytics_scheduler` |
| `cli` | Command-line tool | Click, Typer | `database_migration_cli` |
| `webhook` | Webhook receiver | FastAPI | `integration_stripe_webhook` |

---

## Related Documents

- `naming-4part-reasons.md` — 10 serious reasons for 4-part naming
- `../context-registry.md` — Context name registry (prevent conflicts)
- `../../../guides/SEMANTIC_SHORTENING_GUIDE.md` — Complete shortening guide
- `../../../checklists/SERVICE_NAMING_CHECKLIST.md` — Quick naming decision checklist