# Abbreviations Registry

> **Purpose**: Canonical registry of approved abbreviations for service naming to limit name length while preserving semantic meaning.

## Overview

This registry provides **standardized abbreviations** for the 4-part service naming formula:

```
{context}_{domain}_{function}_{type}
```

**Target**: Maximum **5-6 characters per part** (excluding `type` which uses standard suffixes).

**Principle**: Abbreviations must be:
1. **Unique** within their category (no conflicts)
2. **Recognizable** (industry-standard or intuitive)
3. **Consistent** (one word → one abbreviation across entire project)
4. **Documented** (all abbreviations listed here before use)

---

## Quick Reference Table

| Category | Full Name | Abbreviation | Length | Priority |
|----------|-----------|--------------|--------|----------|
| **Context** | finance | `fin` | 3 | High |
| **Context** | healthcare | `health` | 6 | High |
| **Context** | construction | `constr` | 6 | Medium |
| **Context** | education | `edu` | 3 | High |
| **Context** | logistics | `logist` | 6 | High |
| **Context** | ecommerce | `ecom` | 4 | Medium |
| **Context** | property_management | `propman` | 7 | Low |
| **Domain** | lending | `lend` | 4 | High |
| **Domain** | telemedicine | `telem` | 5 | Medium |
| **Domain** | appointment | `appt` | 4 | High |
| **Domain** | payment | `pay` | 3 | High |
| **Function** | management | `mgmt` | 4 | High |
| **Function** | matching | `match` | 5 | High |
| **Function** | notification | `notif` | 5 | High |
| **Function** | calculation | `calc` | 4 | High |

---

## Part 1: Context Abbreviations

**Category**: Business area / domain context

| Full Name | Abbreviation | Length | Example Service |
|-----------|--------------|--------|-----------------|
| `finance` | `fin` | 3 | `fin_lend_match_api` |
| `healthcare` | `health` | 6 | `health_telem_conslt_api` |
| `construction` | `constr` | 6 | `constr_house_mgmt_bot` |
| `education` | `edu` | 3 | `edu_lms_course_api` |
| `logistics` | `logist` | 6 | `logist_fleet_track_api` |
| `ecommerce` | `ecom` | 4 | `ecom_market_order_api` |
| `corporate` | `corp` | 4 | `corp_crm_lead_api` |
| `property_management` | `propman` | 7 | `propman_house_calc_api` |
| `communication` | `comm` | 4 | `comm_email_notif_worker` |
| `analytics` | `analyt` | 6 | `analyt_report_gen_api` |
| `user_management` | `usermgmt` | 8 | `usermgmt_auth_verify_api` |
| `integration` | `integr` | 6 | `integr_stripe_pay_api` |
| `environment` | `enviro` | 6 | `enviro_emission_track_api` |

### Context Conflict Warning

⚠️ **Avoid these ambiguous abbreviations:**

| ❌ Avoid | Reason | ✅ Use Instead |
|---------|--------|----------------|
| `pm` | property_management vs project_management | `propman` / `projman` |
| `log` | logistics vs logging | `logist` / `observ` (observability context) |
| `prop` | property vs proposition | `propman` / specify domain |

---

## Part 2: Domain Abbreviations

**Category**: Subdomain within business context

| Full Name | Abbreviation | Length | Context | Example |
|-----------|--------------|--------|---------|---------|
| `lending` | `lend` | 4 | finance | `fin_lend_match_api` |
| `crypto` | `crypto` | 6 | finance | `fin_crypto_trade_api` |
| `payment` | `pay` | 3 | finance | `fin_pay_proc_worker` |
| `billing` | `bill` | 4 | finance | `fin_bill_cycle_api` |
| `trading` | `trade` | 5 | finance | `fin_trade_algo_api` |
| `telemedicine` | `telem` | 5 | healthcare | `health_telem_conslt_api` |
| `appointment` | `appt` | 4 | healthcare | `health_appt_book_api` |
| `mental_health` | `mental` | 6 | healthcare | `health_mental_therapy_api` |
| `pharmacy` | `pharm` | 5 | healthcare | `health_pharm_stock_api` |
| `house` | `house` | 5 | construction | `constr_house_mgmt_bot` |
| `commercial` | `commer` | 6 | construction | `constr_commer_proj_api` |
| `renovation` | `renov` | 5 | construction | `constr_renov_plan_api` |
| `material` | `mater` | 5 | construction | `constr_mater_calc_api` |
| `lms` | `lms` | 3 | education | `edu_lms_course_api` |
| `courses` | `course` | 6 | education | `edu_course_enroll_api` |
| `webinar` | `webin` | 5 | education | `edu_webin_stream_api` |
| `assessment` | `assess` | 6 | education | `edu_assess_grade_api` |
| `fleet` | `fleet` | 5 | logistics | `logist_fleet_track_api` |
| `delivery` | `deliv` | 5 | logistics | `logist_deliv_route_api` |
| `warehouse` | `whouse` | 6 | logistics | `logist_whouse_stock_api` |
| `marketplace` | `market` | 6 | ecommerce | `ecom_market_order_api` |
| `dropshipping` | `dropsh` | 6 | ecommerce | `ecom_dropsh_fulfil_api` |

---

## Part 3: Function Abbreviations

**Category**: What the service does (action/purpose)

| Full Name | Abbreviation | Length | Example Service |
|-----------|--------------|--------|-----------------|
| `management` | `mgmt` | 4 | `constr_house_mgmt_bot` |
| `matching` | `match` | 5 | `fin_lend_match_api` |
| `tracking` | `track` | 5 | `logist_deliv_track_api` |
| `notification` | `notif` | 5 | `comm_email_notif_worker` |
| `calculation` | `calc` | 4 | `propman_house_calc_api` |
| `consultation` | `conslt` | 6 | `health_telem_conslt_api` |
| `booking` | `book` | 4 | `health_appt_book_api` |
| `processing` | `proc` | 4 | `fin_pay_proc_worker` |
| `reporting` | `report` | 6 | `analyt_report_gen_api` |
| `verification` | `verify` | 6 | `usermgmt_auth_verify_api` |
| `aggregation` | `aggr` | 4 | `analyt_data_aggr_worker` |
| `generation` | `gen` | 3 | `analyt_report_gen_api` |
| `synchronization` | `sync` | 4 | `integr_crm_sync_worker` |
| `routing` | `route` | 5 | `logist_deliv_route_api` |
| `fulfillment` | `fulfil` | 6 | `ecom_dropsh_fulfil_api` |
| `enrollment` | `enroll` | 6 | `edu_course_enroll_api` |
| `grading` | `grade` | 5 | `edu_assess_grade_api` |

---

## Part 4: Type Suffixes (No Abbreviation Needed)

**Category**: Technical service type

| Type | Length | Description | Keep As-Is |
|------|--------|-------------|------------|
| `api` | 3 | REST API service | ✅ Yes |
| `worker` | 6 | Background job processor | ✅ Yes |
| `bot` | 3 | Chat bot (Telegram, etc.) | ✅ Yes |
| `gateway` | 7 | API Gateway / proxy | ⚠️ Consider `gw` (2) |
| `stream` | 6 | Stream processor | ✅ Yes |
| `scheduler` | 9 | Task scheduler | ⚠️ Consider `sched` (5) |
| `cli` | 3 | Command-line tool | ✅ Yes |
| `webhook` | 7 | Webhook receiver | ⚠️ Consider `hook` (4) |

**Optional abbreviations** (use when total name length exceeds 30 chars):
- `gateway` → `gw`
- `scheduler` → `sched`
- `webhook` → `hook`

---

## Usage Rules

### Rule 1: When to Abbreviate

**Abbreviate when:**
- Full name exceeds **30 characters**
- Service name used in DNS (Kubernetes, production environments)
- Code readability suffers from extreme length

**Keep full names when:**
- Total length < 30 characters
- Development/local environment only
- Clarity is critical (new developers, documentation)

### Rule 2: Consistency Enforcement

**All team members MUST:**
1. Check this registry before creating new service names
2. Propose new abbreviations via PR (update this document)
3. Never invent ad-hoc abbreviations
4. Use exact abbreviations from this table (no variations)

### Rule 3: Adding New Abbreviations

**Process:**
1. Propose abbreviation in PR description
2. Check for conflicts with existing abbreviations
3. Ensure length ≤ 6 characters
4. Update this registry in same PR
5. Get approval from tech lead / architect

**Template for proposals:**
```markdown
## New Abbreviation Proposal

- **Full Name**: `project_management`
- **Proposed Abbreviation**: `projman`
- **Length**: 7 characters
- **Category**: Context
- **Conflicts**: None (checked against registry)
- **Example Service**: `projman_task_track_api`
```

---

## Transformation Examples

### Before (Full Names)

```
finance_lending_matching_api                    (28 chars)
healthcare_telemedicine_consultation_api        (44 chars)
construction_house_management_bot               (33 chars)
property_management_house_calculation_api       (45 chars)
logistics_fleet_management_tracking_api         (43 chars)
communication_email_notification_worker         (39 chars)
```

### After (Abbreviated)

```
fin_lend_match_api                              (18 chars) ✅ -10
health_telem_conslt_api                         (23 chars) ✅ -21
constr_house_mgmt_bot                           (21 chars) ✅ -12
propman_house_calc_api                          (22 chars) ✅ -23
logist_fleet_mgmt_track_api                     (27 chars) ✅ -16
comm_email_notif_worker                         (23 chars) ✅ -16
```

**Average reduction**: ~16 characters per service name

---

## Conflict Resolution

### Known Conflicts

| Abbreviation | Meaning 1 | Meaning 2 | Resolution |
|--------------|-----------|-----------|------------|
| `log` | logistics | logging | Use `logist` / `observ` |
| `pm` | property_management | project_management | Use `propman` / `projman` |
| `comm` | communication | commercial | Use `comm` / `commer` |
| `prop` | property | proposition | Use `propman` / specify |

### Conflict Detection Strategy

**Before accepting new abbreviation:**
1. Search this document for proposed abbreviation
2. Check if it exists in different category
3. Verify semantic uniqueness across all contexts
4. Run grep across codebase: `grep -r "proposed_abbr" services/`

---

## Special Cases

### Multi-Word Domains/Functions

When domain/function contains multiple words, prioritize first word + key syllable:

| Full Name | Strategy | Abbreviation |
|-----------|----------|--------------|
| `mental_health` | First word only | `mental` |
| `fleet_management` | First word only | `fleet` |
| `user_authentication` | First + key syllable | `userauth` |
| `payment_processing` | First word only | `pay` (function = `proc`) |

### Industry Standard Abbreviations

**Always prefer industry standards:**

| Industry Term | Standard Abbr | Length | Use |
|---------------|---------------|--------|-----|
| Learning Management System | `lms` | 3 | ✅ |
| Customer Relationship Management | `crm` | 3 | ✅ |
| Human Resources | `hr` | 2 | ✅ |
| Application Programming Interface | `api` | 3 | ✅ |
| Point of Sale | `pos` | 3 | ✅ |

---

## Maintenance

**Registry Owner**: Tech Lead / System Architect

**Review Frequency**: Quarterly (every 3 months)

**Update Triggers**:
- New business context introduced
- Conflict discovered in production
- Team feedback on readability issues
- Migration to new deployment environment (Kubernetes, etc.)

**Version History**:
- **v1.0** (2025-01-02): Initial registry with core abbreviations
- *(future versions logged here)*

---

## References

- **[Naming Conventions](../atomic/architecture/naming-conventions.md)** — Full naming rules and context
- **[Service Catalog](../../README.md#services)** — Complete service inventory
- **[Architecture Guide](../ARCHITECTURE.md)** — Service design principles
- **[Agent Context Summary](./AGENT_CONTEXT_SUMMARY.md)** — AI agent quick reference

---

**Last Updated**: 2025-01-02
**Maintainer**: System Architect
**Status**: Active
