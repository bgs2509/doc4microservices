# Naming Conventions

This guide provides comprehensive naming conventions for the doc4microservices framework, covering all technical layers from Python code to Kubernetes infrastructure. It establishes consistent, predictable naming patterns that enable AI-first development and seamless transitions between development and production environments.

**Philosophy**: Use separators appropriate to each technical layer (underscores for code/data, hyphens for network/DNS). Default to 3-part service naming (`{context}_{domain}_{type}`), using 4-part only when domain is ambiguous.

**Quick Start**: Use the Quick Reference Table and AI Decision Tree below for immediate lookup. For detailed explanations, see the specialized guides in this directory.

---

## AI Quick Reference

> **NAMING PHILOSOPHY**: **DEFAULT TO 3-PART** — Use `{context}_{domain}_{type}`. Add `{function}` ONLY when domain is ambiguous (burden of proof required).
>
> Use **semantic shortening**: clear context + domain, omit redundant function words. Average length: 20-27 chars (no abbreviations needed).

> ⚠️ **CRITICAL**: Maintain a Context Registry to prevent context name conflicts across your project. Never reuse context names for different business domains.
>
> **Location**: Create `docs/atomic/architecture/context-registry.md` in your project
> **Structure**: List each context with its business domain and example services
> **Example entry**: `finance` → Financial services (lending, payments, crypto)
> **See**: [context-registry.md](../context-registry.md) template for detailed format

### 3-Part vs 4-Part Service Naming Decision

**DEFAULT (80-90% of services)**: Use 3-part `{context}_{domain}_{type}` — function is implied by domain.

**EXCEPTION (10-20% of services)**: Use 4-part ONLY when domain is ambiguous (see 10 Serious Reasons below).

**BURDEN OF PROOF**: Always start with 3-part. Justify adding 4th component.

**OBJECTIVE DECISION RULE**:

Ask: **"Can this domain word refer to 3+ different operations in this context?"**

- **YES** → Use 4-part: `{context}_{domain}_{function}_{type}`
- **NO** → Use 3-part: `{context}_{domain}_{type}`

**USE 4-PART ONLY WHEN domain is ambiguous**:
- `fleet` → Could mean: tracking, management, maintenance, scheduling (4+ operations)
- `analytics` → Could mean: reporting, querying, processing, visualization (4+ operations)
- `communication` → Could mean: email, SMS, push, in-app notifications (4+ channels)

**USE 3-PART WHEN domain is specific**:
- `lending` → Clearly means loan matching/approval (1 primary operation)
- `payment` → Clearly means payment processing (1 primary operation)
- `telemedicine` → Clearly means online consultation (1 primary operation)

**NOTE**: The `{type}` component (api, worker, bot) indicates technical implementation, NOT business function. Don't use 4-part just because a service has multiple code features—use it only when the DOMAIN word itself is ambiguous.

### When to Use 4-Part: The 10 Serious Reasons

**PRINCIPLE**: Default to 3-part. Use 4-part ONLY when one of these reasons applies:

1. **Domain Ambiguity** — Domain implies 3+ operations (`fleet`, `analytics`, `communication`)
2. **Multiple Services per Domain** — Need 2+ services in same `{context}_{domain}`
3. **Cross-Context Collision** — Same domain word in different contexts with different meanings
4. **Organizational Policy** — Team/company requires explicit functions for certain contexts
5. **Technical Differentiation** — Different technologies/providers (e.g., `payment_stripe_api`, `payment_paypal_api`)
6. **Functional Split (Migration)** — Blue-green deployment with functional separation
7. **Legacy Terminology** — Integration with existing system that uses established terms
8. **Regulatory Requirements** — Compliance requires explicit separation of functions
9. **Different SLA/Resources** — Radically different infrastructure requirements
10. **Onboarding Clarity** — New team members regularly confused by 3-part names

**Burden of Proof**: If NONE of these apply → use 3-part.

> **Detailed explanations**: See [naming-4part-reasons.md](naming-4part-reasons.md)

---

| Element Type | Pattern | Example | Separator |
|--------------|---------|---------|-----------

|
| **Microservice (default)** | `{context}_{domain}_{type}` | `finance_lending_api` | `_` |
| **Microservice (ambiguous domain)** | `{context}_{domain}_{function}_{type}` | `logistics_fleet_tracking_api` | `_` |
| **Python Class** | `{Noun}{Suffix}` | `UserService`, `OrderRepository` | None (PascalCase) |
| **Python Function** | `{verb}_{noun}[_qualifier]` | `get_user_by_id`, `create_order` | `_` |
| **Python Variable** | `{noun}[_qualifier]` | `user_id`, `max_attempts` | `_` |
| **Python Parameter** | `{noun}[_qualifier]` | `user_id: int`, `is_active: bool` | `_` |
| **Python Constant** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `MAX_RETRIES` | `_` |
| **Python Module/File** | `{class_name}.py` | `user_service.py`, `order_dto.py` | `_` |
| **Folder/Package** | `{service_name}/` | `finance_lending_api/` | `_` |
| **Documentation (entry points)** | `SCREAMING_SNAKE_CASE` | `README.md`, `CLAUDE.md` | None |
| **Documentation (content)** | `kebab-case` | `naming-conventions.md`, `architecture-guide.md` | `-` |
| **Docker Compose Service** | `{service_name}` | `finance_lending_api` | `_` |
| **Kubernetes Service** | `{service-name}` | `finance-lending-api` | `-` |
| **Database Table** | `{plural_noun}[_{qualifier}]` | `users`, `order_items` | `_` |
| **Database Column** | `{noun}[_qualifier]` | `created_at`, `user_id` | `_` |
| **Env Variable** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `API_KEY` | `_` |
| **REST API Path** | `/api/v{N}/{resource}[/{id}]` | `/api/v1/users/{id}` | `/` (segments), `-` (words) |
| **Git Branch** | `{type}/{description}` | `feature/user-auth` | `-` |

> **✅ Validation**: After naming elements, verify compliance with the validation checklist in [naming-conversion.md](naming-conversion.md).

---

## AI Decision Tree: How to Name Any Element

### Quick Navigation by Element Type

```
SERVICE (microservice/app)     → naming-services.md
PYTHON CLASS                   → naming-python.md (Classes section)
PYTHON FUNCTION                → naming-python.md (Functions section)
PYTHON VARIABLE/PARAMETER      → naming-python.md (Variables section)
FILE/FOLDER                    → naming-python.md (Files & Folders section)
DOCUMENTATION FILES (.md)      → naming-documentation.md
DATABASE (table/column)        → naming-databases.md
INFRASTRUCTURE (K8s/Docker)    → naming-infrastructure.md
```

**Most Common: Naming a Service** → See [naming-services.md](naming-services.md)

---

## Detailed Guides

### Microservices

- **[naming-services.md](naming-services.md)** — Service naming formula (3-part vs 4-part), domain-function mapping, context catalog
- **[naming-4part-reasons.md](naming-4part-reasons.md)** — 10 serious reasons for 4-part naming (detailed analysis with examples)

### Code & Infrastructure

- **[naming-python.md](naming-python.md)** — Python classes, functions, variables, files/folders
- **[naming-infrastructure.md](naming-infrastructure.md)** — Docker Compose, Kubernetes, Nginx, 3-layer separator strategy
- **[naming-databases.md](naming-databases.md)** — PostgreSQL/MongoDB tables, columns, indexes, migrations

### Documentation & Tools

- **[naming-documentation.md](naming-documentation.md)** — Documentation file naming (entry points vs content, kebab-case vs SCREAMING)
- **[naming-conversion.md](naming-conversion.md)** — Dev→Prod transformation (service_to_k8s function, validation checklist)

---

## Common Questions

### Q: When do I use 3-part vs 4-part service naming?

**Default (80-90%)**: Use 3-part `{context}_{domain}_{type}`

Function is implied by the domain:
- `finance_lending_api` — lending implies matching/approval
- `healthcare_telemedicine_api` — telemedicine implies consultation
- `construction_house_bot` — house implies project management

**Exception (10-20%)**: Use 4-part `{context}_{domain}_{function}_{type}`

Only when domain is ambiguous (refers to 3+ different operations):
- `logistics_fleet_tracking_api` — fleet could mean tracking, management, or maintenance
- `analytics_reporting_api` — analytics could mean reporting, querying, or processing
- `communication_notification_worker` — communication could mean email, SMS, or notifications

**Decision Rule**: Ask "Can this domain word refer to 3+ different operations?" If yes → 4-part. If no → 3-part.

See [naming-services.md](naming-services.md) for complete decision tree and examples.

### Q: Which separator for which layer?

**Code/Data Layer** (underscore `_`):
- Python: `finance_lending_api.py`, `get_user_by_id()`
- SQL: `users`, `created_at`
- MongoDB: `user_sessions`
- Environment variables: `DATABASE_URL`

**Container Layer (Development)** (underscore `_`):
- Docker Compose: `finance_lending_api`
- Internal dev environment

**Container Layer (Production)** (hyphen `-`):
- Kubernetes: `finance-lending-api`
- DNS-compliant (RFC 1035)

**Network/DNS Layer** (hyphen `-`):
- DNS hostnames: `api.example.com`
- REST API paths: `/api/v1/lending`
- Git branches: `feature/user-auth`

**Rationale**: Each layer has technical requirements. Python/SQL require underscores, Kubernetes/DNS require hyphens.

See [naming-infrastructure.md](naming-infrastructure.md) for detailed layer breakdown.

### Q: How to convert service names for Kubernetes?

Use the `service_to_k8s()` function to convert Docker Compose names (underscores) to Kubernetes names (hyphens):

```python
def service_to_k8s(service_name: str) -> str:
    """Convert Docker Compose service name to Kubernetes DNS-compliant name.

    Example:
        >>> service_to_k8s("finance_lending_api")
        "finance-lending-api"
    """
    name = service_name.lower().replace('_', '-').strip('-')
    return re.sub(r'-+', '-', name)
```

**Mapping Example**:
- Code: `finance_lending_api/` (folder)
- Docker Compose: `finance_lending_api` (service)
- Kubernetes: `finance-lending-api` (service)
- DNS: `lending-api.finance.example.com` (hostname)

See [naming-conversion.md](naming-conversion.md) for complete function code with validation.

### Q: How to name documentation files?

**Two-tier strategy**:

**Entry Points** (SCREAMING_SNAKE_CASE):
- `README.md` — Project/directory entry point
- `CLAUDE.md` — AI agent entry point
- `LICENSE` — Legal entry point
- `CONTRIBUTING.md` — Contributor entry point (optional)

**Content Files** (kebab-case):
- `naming-conventions.md` — Guide document
- `architecture-guide.md` — Reference document
- `tech-stack.md` — Technical reference
- `agent-verification-checklist.md` — Checklist

**Decision Rule**: Ask "Is this the FIRST file a human/AI reads when discovering this project/section?"
- **YES** → Entry point → `SCREAMING_SNAKE_CASE`
- **NO** → Content → `kebab-case`

**Rationale**:
- Entry points: SCREAMING emphasizes importance, industry convention
- Content: kebab-case is URL-friendly, SEO-optimized, web publishing standard

See [naming-documentation.md](naming-documentation.md) for complete guide with examples.

---

## Summary

**The Golden Rule**: Use the separator appropriate for your technical layer.

| Layer | Separator | Why |
|-------|-----------|-----|
| **Code & Data** | Underscore `_` | Python, SQL, MongoDB require it |
| **Container (Dev)** | Underscore `_` | Matches code layer, internal dev environment |
| **Container (Prod)** | Hyphen `-` | Kubernetes, DNS require it |
| **Network & DNS** | Hyphen `-` | RFC standards require it |

**Conversion**: Automate `underscore_to_hyphen` transformation at deployment boundary (Docker Compose → Kubernetes).

**Consistency**: Maintain 1:1 mapping across all layers:
- Code: `finance_lending_api/`
- Docker Compose: `finance_lending_api`
- Kubernetes: `finance-lending-api`
- DNS: `lending-api.finance.example.com`

All names refer to the **same logical service**, just using layer-appropriate separators.

**Service Naming**:
- **DEFAULT (80-90%)**: `{context}_{domain}_{type}` (3-part) — function implied
- **EXCEPTION (10-20%)**: `{context}_{domain}_{function}_{type}` (4-part) — only when one of 10 reasons applies
- **BURDEN OF PROOF**: Always start with 3-part, justify 4-part addition
- **See**: [naming-services.md](naming-services.md) and [naming-4part-reasons.md](naming-4part-reasons.md)

**Element Naming**: Use appropriate suffixes for classes (Service, Repository, DTO, Handler, Router), verbs for functions (get_, create_, validate_), and descriptive patterns for variables.

**Name Length**: Average 20-27 characters with 3-part formula (no abbreviations needed). 95%+ compatibility with Kubernetes DNS limits (253 chars).

---

## Related Documents

- `../context-registry.md` — Context name registry (prevent conflicts)
- `../../../guides/semantic-shortening-guide.md` — 3-part vs 4-part decision guide
- `../../../checklists/service-naming-checklist.md` — Quick naming decision checklist
- `../../../guides/architecture-guide.md` — Framework architecture overview
