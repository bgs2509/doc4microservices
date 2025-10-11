# Template Service Naming Guide

**Status**: ✅ Active Reference
**Last Updated**: 2025-10-02
**Related**: [Naming Conventions](../atomic/architecture/naming/README.md) | [Semantic Shortening Guide](semantic-shortening-guide.md)

---

## Why Template Names Use `template_` Context

Framework templates use the `template_` context prefix to clearly indicate these are **placeholder names** that should be replaced with your actual business context and domain when generating a real application.

**Design Philosophy**:
- `template_` makes it obvious these are not production service names
- Follows the mandatory `{context}_{domain}_{type}` naming pattern (line 39, naming-conventions.md)
- Provides clear migration path for AI agents and developers
- Prevents confusion about whether templates are real business services

---

## Template Service Names

| Template Name | Purpose | Components | Replace With |
|---------------|---------|------------|--------------|
| `template_business_api` | FastAPI REST API for business logic | context=template, domain=business, type=api | `{yourcontext}_{yourdomain}_api` |
| `template_business_bot` | Aiogram Telegram bot for business logic | context=template, domain=business, type=bot | `{yourcontext}_{yourdomain}_bot` |
| `template_business_worker` | AsyncIO background worker | context=template, domain=business, type=worker | `{yourcontext}_{yourdomain}_worker` |
| `template_data_postgres_api` | PostgreSQL HTTP data access service | context=template, domain=data_postgres, type=api | `{yourcontext}_data_postgres_api` |
| `template_data_mongo_api` | MongoDB HTTP data access service | context=template, domain=data_mongo, type=api | `{yourcontext}_data_mongo_api` |

**Note**: Data services typically keep the `data_` prefix in the domain since they're infrastructure services providing HTTP-only data access per the framework's architecture.

---

## Understanding the Naming Pattern

### The 3-Part Formula

```
{context}_{domain}_{type}
   ↓        ↓       ↓
template_business_api
```

- **context**: Business area (finance, healthcare, logistics, etc.)
- **domain**: Subdomain within context (lending, telemedicine, fleet, etc.)
- **type**: Technical service type (api, worker, bot, gateway, etc.)

### Why "template" and "business"?

**`template` (context)**:
- Clearly signals "this is a placeholder"
- Not a real business domain
- Easy to search-and-replace

**`business` (domain)**:
- Generic placeholder for "your business logic"
- Distinguishes from infrastructure services (`data_postgres`, `data_mongo`)
- Covers API, bot, and worker services that implement business rules

---

## Renaming Process

### Step 1: Choose Your Context and Domain

Identify your business context and specific domain:

**Examples**:
- **P2P Lending**: context=`finance`, domain=`lending` → `finance_lending_api`
- **Telemedicine**: context=`healthcare`, domain=`telemedicine` → `healthcare_telemedicine_api`
- **Construction Management**: context=`construction`, domain=`house` → `construction_house_bot`
- **Fleet Tracking**: context=`logistics`, domain=`fleet_tracking` → `logistics_fleet_tracking_api`

**Decision Guide**:
- **DEFAULT (80-90%)**: Use 3-part naming when domain clearly implies function
- **EXCEPTION (10-20%)**: Use 4-part `{context}_{domain}_{function}_{type}` ONLY when domain is ambiguous
- **BURDEN OF PROOF**: Always start with 3-part, justify 4-part with one of 10 reasons
- See [Service Naming Checklist](../checklists/service-naming-checklist.md) for quick decision
- See [10 Serious Reasons for 4-Part Naming](../atomic/architecture/naming/naming-4part-reasons.md) for complete list of 10 reasons
- See [Semantic Shortening Guide](semantic-shortening-guide.md) for detailed decision tree

### Step 2: Global Search-and-Replace

**Method A: Using find and sed (Bash)**

```bash
# Replace template_business_api with your actual service name
cd your-project-root

find . -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.py" -o -name "*.conf" -o -name "*.md" \) \
  -not -path "./.git/*" \
  -exec sed -i 's/template_business_api/finance_lending_api/g' {} \;

# Repeat for other services:
# template_business_bot → finance_lending_bot
# template_business_worker → finance_lending_worker
# template_data_postgres_api → finance_data_postgres_api
# template_data_mongo_api → finance_data_mongo_api
```

**Method B: Using IDE Global Replace**

1. Open your IDE's "Find and Replace" dialog (usually Ctrl+Shift+H)
2. Enable "Regular Expression" mode
3. Search for: `\btemplate_business_api\b`
4. Replace with: `finance_lending_api`
5. Review matches before replacing
6. Repeat for each template service name

### Step 3: Rename Directories

```bash
# Rename service directories
mv services/template_business_api services/finance_lending_api
mv services/template_business_bot services/finance_lending_bot
mv services/template_business_worker services/finance_lending_worker

# Data services usually stay in separate directories or may not exist yet
# mv services/template_data_postgres_api services/finance_data_postgres_api (if it exists)
```

### Step 4: Update Build Contexts

After renaming directories, verify Docker Compose build contexts:

```yaml
# docker-compose.yml
services:
  finance_lending_api:
    build:
      context: ./services/finance_lending_api  # ✅ Updated path
      dockerfile: Dockerfile
```

### Step 5: Update Import Paths (Python)

If you have any cross-service imports (rare in microservices), update them:

```python
# Before
from services.template_business_api.config import settings

# After
from services.finance_lending_api.config import settings
```

**Note**: Following the framework's HTTP-only data access architecture, you should NOT have direct imports between business services and data services.

---

## Validation Checklist

After renaming, verify all changes:

### Service Names
- [ ] All service names follow `{context}_{domain}_{type}` pattern
- [ ] No remaining `template_` prefixes (except in documentation examples)
- [ ] Docker Compose service names updated
- [ ] Kubernetes manifests updated (if using Kubernetes)
- [ ] Nginx upstream names updated
- [ ] Directory names match service names

### Configuration Files
- [ ] Environment variables reference correct service names
- [ ] Docker Compose service references updated (depends_on, etc.)
- [ ] Nginx proxy_pass directives updated
- [ ] Volume names updated (logs, data, etc.)
- [ ] CI/CD workflow service matrices updated

### Code & Imports
- [ ] No Python imports reference old service names
- [ ] Configuration defaults updated (service URLs)
- [ ] README and documentation updated
- [ ] Comments and docstrings reference correct names

### Testing
- [ ] Run `docker-compose config` to validate YAML syntax
- [ ] Test service startup: `docker-compose up -d`
- [ ] Verify service-to-service communication
- [ ] Check logs for connection errors

---

## Common Renaming Examples

### Example 1: P2P Lending Platform

**Original templates**:
```
template_business_api
template_business_worker
template_data_postgres_api
```

**Renamed for finance domain**:
```
finance_lending_api         # P2P loan matching/approval API
finance_lending_worker      # Background loan processing worker
finance_data_postgres_api   # PostgreSQL data access service
```

**Files to update**:
- `docker-compose.yml`: service definitions, depends_on, URLs
- `nginx/conf.d/upstream.conf`: upstream blocks
- `nginx/conf.d/api-gateway.conf`: proxy_pass directives
- Directory rename: `services/template_business_api/` → `services/finance_lending_api/`

### Example 2: Healthcare Telemedicine

**Original templates**:
```
template_business_api
template_business_bot
template_data_postgres_api
```

**Renamed for healthcare domain**:
```
healthcare_telemedicine_api      # Telemedicine consultation API
healthcare_appointment_bot       # Telegram bot for booking (different domain!)
healthcare_data_postgres_api     # PostgreSQL data access service
```

**Note**: The bot has a different domain (`appointment` vs `telemedicine`) because it serves appointment booking, not consultations. This is correct - services within the same context can have different domains.

### Example 3: E-commerce Marketplace

**Original templates**:
```
template_business_api
template_business_worker
template_data_mongo_api
```

**Renamed for ecommerce domain**:
```
ecommerce_marketplace_api      # Marketplace listings API
ecommerce_order_worker         # Order processing worker (different domain!)
ecommerce_data_mongo_api       # MongoDB data access service
```

**Note**: Worker has `order` domain instead of `marketplace` because it specifically processes orders, not general marketplace operations.

### Example 4: Logistics Fleet Tracking (4-Part Naming)

**Original template**:
```
template_business_api
```

**Renamed with 4-part pattern** (domain `fleet` is ambiguous):
```
logistics_fleet_tracking_api   # 4-part: function "tracking" clarifies intent
```

**Why 4-part?**: "fleet" alone could mean tracking, management, maintenance, or scheduling. Adding "tracking" clarifies the specific function.

---

## Anti-Patterns to Avoid

### ❌ DON'T: Keep template_ prefix in production

```yaml
# BAD - Still using template prefix
services:
  template_business_api:  # ❌ Looks like you forgot to rename
```

### ❌ DON'T: Mix old and new names

```yaml
# BAD - Inconsistent naming
services:
  finance_lending_api:
    environment:
      - POSTGRES_SERVICE_URL=http://template_data_postgres_api:8000  # ❌ Still template
```

### ❌ DON'T: Use generic names

```yaml
# BAD - Too generic, missing context
services:
  api_service:           # ❌ What context? What domain?
  business_api:          # ❌ Missing context
  my_api:                # ❌ Not descriptive
```

### ❌ DON'T: Abbreviate context or domain

```yaml
# BAD - Unnecessary abbreviations
services:
  fin_lend_api:          # ❌ Use full words: finance_lending_api
  hc_telemed_api:        # ❌ Use full words: healthcare_telemedicine_api
```

### ❌ DON'T: Add version numbers to service names

```yaml
# BAD - Version in service name
services:
  finance_lending_api_v2:  # ❌ Versions belong in API paths, not service names
```

**Correct approach**: Keep service name stable, version in API path:
- Service: `finance_lending_api`
- API path: `/api/v2/loans`

---

## Migration from Old Naming Patterns

### If you have existing services with non-compliant names:

**Before** (generic 2-part names):
```
lending_api          # Missing context
payment_service      # Missing context, wrong suffix
user_management      # Missing type
```

**After** (compliant 3-part names):
```
finance_lending_api         # Added context
finance_payment_api         # Added context, fixed suffix
user_auth_api              # Added type (context=user, domain=auth)
```

**Migration strategy**:
1. Create [Context Registry](../atomic/architecture/context-registry.md) first
2. Map old names to new `{context}_{domain}_{type}` pattern
3. Plan service-by-service migration (avoid renaming all at once)
4. Update one service, test, then proceed to next
5. Maintain backward compatibility during transition (DNS aliases, etc.)

---

## Troubleshooting

### Problem: Service won't start after renaming

**Symptoms**:
```
Error: Cannot connect to host template_business_api
Connection refused: template_data_postgres_api:8000
```

**Solutions**:
1. Check Docker Compose service definitions match new names
2. Verify environment variables reference new service names
3. Check Nginx upstream server addresses
4. Ensure all depends_on references are updated
5. Clear old containers: `docker-compose down && docker-compose up -d`

### Problem: Import errors in Python code

**Symptoms**:
```python
ModuleNotFoundError: No module named 'services.template_business_api'
```

**Solutions**:
1. Update all Python import statements
2. Check if using absolute vs relative imports
3. Verify PYTHONPATH includes renamed directories
4. Rebuild Docker images: `docker-compose build --no-cache`

### Problem: Nginx 502 Bad Gateway

**Symptoms**: Nginx returns 502 when accessing API

**Solutions**:
1. Check Nginx upstream blocks use new service names
2. Verify proxy_pass directives reference correct upstream names
3. Ensure backend services are running: `docker-compose ps`
4. Check Nginx logs: `docker-compose logs nginx`
5. Restart Nginx: `docker-compose restart nginx`

---

## Quick Reference Commands

### Verify no template_ references remain

```bash
# Search for remaining template_ prefixes
grep -r "template_" --include="*.yml" --include="*.py" --include="*.conf" \
  --exclude-dir=".git" --exclude="template-naming-guide.md"
```

### Validate Docker Compose syntax

```bash
docker-compose -f docker-compose.yml config
```

### Test renamed services

```bash
# Start services
docker-compose up -d

# Check health
docker-compose ps

# View logs
docker-compose logs -f finance_lending_api

# Test API endpoint
curl http://localhost/api/v1/health
```

### Rollback if needed

```bash
# If using git
git diff                    # Review changes
git checkout .              # Discard all changes
git clean -fd               # Remove new files

# Or restore from backup branch
git checkout backup/before-rename-20251002
```

---

## See Also

- **[Naming Conventions](../atomic/architecture/naming/README.md)** - Complete naming rules reference
- **[Semantic Shortening Guide](semantic-shortening-guide.md)** - Decision tree for 3-part vs 4-part naming
- **[Context Registry](../atomic/architecture/context-registry.md)** - Prevent context name conflicts
- **[Project Structure](../reference/project-structure.md)** - Canonical repository layout
- **[Architecture Guide](architecture-guide.md)** - HTTP-only data access patterns

---

## Examples in the Wild

**Real-world service naming examples** (following the framework):

```yaml
# Finance domain
finance_lending_api          # P2P loan matching
finance_crypto_api           # Cryptocurrency portfolio
finance_payment_worker       # Payment processing
finance_data_postgres_api    # PostgreSQL data access

# Healthcare domain
healthcare_telemedicine_api      # Online consultations
healthcare_appointment_api       # Doctor booking
healthcare_pharmacy_bot          # Telegram medication bot
healthcare_data_postgres_api     # PostgreSQL data access

# Logistics domain
logistics_fleet_tracking_api         # 4-part (domain ambiguous)
logistics_delivery_routing_worker    # 4-part (domain ambiguous)
logistics_data_mongo_api             # MongoDB data access

# E-commerce domain
ecommerce_marketplace_api    # Product listings
ecommerce_checkout_api       # Payment checkout
ecommerce_order_worker       # Order fulfillment
ecommerce_data_postgres_api  # PostgreSQL data access
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Maintained By**: Framework Core Team
