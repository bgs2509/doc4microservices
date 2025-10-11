# Context Registry

> **Purpose**: Maintain a single source of truth for all context names used across the microservices framework to prevent naming conflicts and ambiguity.

---

## Active Contexts

| Context | Full Name | Description | Domain Examples | Services Using It | Owner/Team |
|---------|-----------|-------------|-----------------|-------------------|------------|
| `finance` | Financial Services | Financial operations, transactions, payments | `lending`, `crypto`, `payment`, `billing`, `trading` | `finance_lending_api`, `finance_crypto_api`, `finance_payment_worker` | @finance-team |
| `healthcare` | Healthcare & Medical | Medical services, appointments, patient care | `telemedicine`, `appointment`, `pharmacy`, `mental_health` | `healthcare_telemedicine_api`, `healthcare_appointment_api` | @health-team |
| `construction` | Construction & Building | Construction project management | `house`, `commercial`, `renovation`, `material` | `construction_house_bot`, `construction_material_api` | @construction-team |
| `logistics` | Logistics & Delivery | Transport, delivery, fleet management | `fleet`, `delivery`, `warehouse` | `logistics_fleet_tracking_api`, `logistics_delivery_tracking_api` | @logistics-team |
| `ecommerce` | E-Commerce & Retail | Online commerce, marketplaces | `marketplace`, `dropship`, `cart` | `ecommerce_marketplace_api`, `ecommerce_cart_api` | @commerce-team |
| `corporate` | Enterprise Tools | Internal business tools | `crm`, `hr`, `payroll` | `corporate_crm_api`, `corporate_hr_api` | @corporate-team |
| `education` | Education & Learning | Learning platforms, courses | `lms`, `courses`, `webinar`, `assessment` | `education_lms_api`, `education_courses_api` | @education-team |
| `user_management` | User Management | Authentication, profiles, permissions | `auth`, `profile`, `permission` | `user_auth_api`, `user_profile_api` | @platform-team |
| `integration` | Third-Party Integrations | External API integrations | `stripe`, `google`, `twilio` | `integration_stripe_api`, `integration_google_api` | @platform-team |
| `analytics` | Analytics & Reporting | Data analytics, business intelligence | `reporting`, `dashboard`, `data` | `analytics_reporting_api`, `analytics_dashboard_api` | @data-team |
| `communication` | Communication Services | Messaging, notifications | `notification`, `telegram`, `email`, `sms` | `communication_notification_worker`, `communication_telegram_bot` | @platform-team |
| `property_management` | Real Estate Management | Property rental, tenant management | `house`, `tenant`, `lease` | `property_house_api`, `property_tenant_api` | @property-team |
| `environment` | Environmental Services | Ecology, sustainability | `emission`, `recycling`, `carbon` | `environment_emission_api`, `environment_recycling_api` | @environment-team |

---

## Reserved Contexts (Planned)

| Context | Planned Use | Target Release | Status |
|---------|-------------|----------------|--------|
| `compliance` | Regulatory compliance, auditing | Q3 2025 | Planned |
| `security` | Security services, threat detection | Q2 2025 | In Progress |
| `gaming` | Gaming platform services | Q4 2025 | Planned |

---

## Deprecated Contexts (DO NOT USE)

| Context | Reason | Replaced By | Deprecated Date |
|---------|--------|-------------|-----------------|
| ~~`log`~~ | Ambiguous (Logistics vs Logging) | Use `logistics` or `observability` | 2025-01-15 |
| ~~`property`~~ | Ambiguous (Real Estate vs Object Property) | Use `property_management` | 2025-02-01 |
| ~~`project`~~ | Too generic | Use specific context (`construction`, `enterprise`, etc.) | 2025-02-10 |

---

## Naming Rules

### ✅ DO:
- Use **specific, descriptive** context names
- Choose context names that represent a **business domain** or **functional area**
- Keep contexts **mutually exclusive** (no overlapping meanings)
- Use **snake_case** for multi-word contexts (e.g., `user_management`, not `usermanagement`)

### ❌ DON'T:
- Reuse the same context name for different meanings across projects
- Use abbreviations unless universally understood (e.g., `hr` for Human Resources is OK)
- Use generic names like `data`, `service`, `system`, `app`
- Mix language contexts (stick to English)

---

## Adding a New Context

1. **Check for conflicts**: Ensure the name doesn't exist in Active or Deprecated sections
2. **Verify specificity**: Context should represent a clear business domain
3. **Update this registry**: Add row to "Active Contexts" table
4. **Notify teams**: Announce new context in team channels
5. **Update documentation**: Add to relevant guides (Architecture, Naming Conventions)

---

## Context Conflict Resolution

If you discover a potential conflict:

1. **Document the issue**:
   ```markdown
   ## Conflict Report
   - **Context**: `logistics`
   - **Conflict**: Used for both "Logistics Services" and "Logging System"
   - **Impact**: 5 services affected
   - **Proposed Resolution**: Rename logging context to `observability`
   ```

2. **Discuss with stakeholders**
3. **Create migration plan** (if renaming existing context)
4. **Update registry** (move old name to Deprecated, add new name to Active)
5. **Execute migration** (rename services, update documentation)

---

## Examples of Good Context Selection

### ✅ GOOD:
- `finance` → Clear business domain
- `healthcare` → Specific industry
- `user_management` → Specific function
- `integration` → Clear technical purpose

### ❌ BAD:
- `data` → Too generic (data for what?)
- `api` → Too technical (everything has APIs)
- `system` → Meaningless
- `app` → Vague

---

## Validation Checklist

Before adding a context, verify:

- [ ] Context name is unique (not in Active or Deprecated tables)
- [ ] Context name describes a business domain or clear functional area
- [ ] Context name is specific enough (not generic like `data`, `service`)
- [ ] Context name won't conflict with similar contexts (e.g., `log` vs `logistics`)
- [ ] Multi-word contexts use `snake_case`
- [ ] Context name is in English
- [ ] No abbreviations unless universally understood
- [ ] Owner/team assigned

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-02 | Initial context registry created | System |
| 2025-10-02 | Added 13 active contexts from existing services | System |

---

## Related Documents

- `docs/atomic/architecture/naming/README.md` — Comprehensive naming patterns for services
- `docs/atomic/architecture/service-separation-principles.md` — Service boundary definitions
- `docs/atomic/architecture/improved-hybrid-overview.md` — Overall architecture approach
- `docs/guides/template-naming-guide.md` — Template service renaming instructions

---

**Maintained by**: Platform Team (@platform-team)
**Last Updated**: 2025-10-02
**Review Frequency**: Quarterly
