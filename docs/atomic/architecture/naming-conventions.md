# Naming Conventions

## Core Principle

**Use underscores for code/data layer, hyphens for network/DNS layer.**

This framework employs a **context-layered naming strategy** where separator choice depends on the technical layer:
- **Layer 1 (Code & Data)**: Underscores required (Python, PostgreSQL, MongoDB, environment variables)
- **Layer 2 (Container Orchestration)**: Context-dependent (underscores in Docker Compose dev, hyphens in Kubernetes prod)
- **Layer 3 (Network & DNS)**: Hyphens required (DNS hostnames, Nginx, REST APIs, SSL certificates)

This approach ensures compatibility across all technologies while maintaining clear conversion rules between development and production environments.

---

## Separator Rules by Context

| Context | Convention | Reason | Examples |
|---------|------------|--------|----------|
| **Python code** | `snake_case` (underscore) | PEP 8 requirement, import system | `pm_house_calc_api.py`, `get_user()` |
| **Database** | `snake_case` (underscore) | SQL standard, PostgreSQL/MongoDB requirement | `user_accounts`, `created_at` |
| **Docker Compose services** | `snake_case` (underscore) | Internal use, matches code layer | `pm_house_calc_api` |
| **Container names (dev)** | `snake_case` (underscore) | Compose v1 compatibility, consistency | `pm_house_calc_api_1` |
| **Kubernetes services** | `kebab-case` (hyphen) | RFC 1035 compliance, DNS requirement | `pm-house-calc-api` |
| **DNS hostnames** | `kebab-case` (hyphen) | RFC 1035/1123 standard | `api-service.example.com` |
| **Nginx server_name** | `kebab-case` (hyphen) | DNS hostname validation | `house-calc.example.com` |
| **Nginx upstreams** | `snake_case` (underscore) | Internal name, matches service names | `upstream pm_house_calc_api` |
| **REST API paths** | `kebab-case` (hyphen) | SEO-friendly, URL standard | `/api/v1/house-calc` |
| **Git branches** | `kebab-case` (hyphen) | Git convention, URL compatibility | `feature/house-calc` |
| **Environment variables** | `UPPER_SNAKE_CASE` (underscore) | POSIX standard, shell requirement | `DATABASE_URL` |

---

## Layer 1: Code and Data (Underscore Required)

These components **require underscores** due to language/platform restrictions:

### Python Code

| Component | Convention | Examples |
|-----------|------------|----------|
| Modules | `snake_case` | `user_repository.py`, `order_dto.py` |
| Packages | `snake_case` | `pm_house_calc_api/`, `shared/` |
| Classes | `PascalCase` | `UserService`, `HouseCalculator` |
| Functions & methods | `snake_case` | `get_user_by_id()`, `calculate_price()` |
| Variables | `snake_case` | `max_retry_attempts`, `user_id` |
| Constants | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `MAX_CONNECTIONS` |
| Private members | `_snake_case` | `_internal_cache`, `_validate()` |

**Rules**:
- Modules and packages must use `snake_case` (hyphens cause `SyntaxError` in imports).
- Classes use `PascalCase`; data classes and Pydantic models follow the same rule.
- Functions, methods, and variables use `snake_case`.
- Constants use `UPPER_SNAKE_CASE` and live at module scope.
- DTOs adopt descriptive suffixes (`...Base`, `...Create`, `...Update`, `...Public`, `...Payload`). Avoid generic names like `DataDTO`.

**PyPI Distribution Names Exception**:
- PyPI package names can use hyphens: `scikit-learn`, `django-rest-framework`
- Import names must use underscores: `import sklearn`, `import rest_framework`
- Prefer underscores in distribution names for consistency: `my_package` over `my-package`

### Databases

| Component | Convention | Examples |
|-----------|------------|----------|
| PostgreSQL tables | `snake_case` | `user_accounts`, `order_items` |
| PostgreSQL columns | `snake_case` | `created_at`, `user_id`, `is_active` |
| PostgreSQL indexes | `snake_case` | `idx_user_email`, `idx_order_created` |
| PostgreSQL constraints | `snake_case` | `fk_order_customer`, `uk_user_email` |
| PostgreSQL schemas | `snake_case` | `public`, `analytics`, `audit_log` |
| MongoDB collections | `snake_case` | `analytics_events`, `user_sessions` |
| MongoDB fields | `snake_case` | `event_type`, `created_at` |
| MongoDB databases | `snake_case` | `user_service_db`, `analytics_db` |

**Rules**:
- PostgreSQL **prohibits hyphens** in unquoted identifiers (interpreted as subtraction operator).
- MongoDB **discourages hyphens** (requires special syntax: `db.getCollection("name-with-hyphen")`).
- Use `snake_case` for all database identifiers to avoid quoting everywhere.
- Migrations use sequential prefixes: `202501010101_initial_schema.py`, `202501020930_add_user_index.py`.

**Quoted Identifier Escape Hatch** (Discouraged):
```sql
-- Avoid this pattern
CREATE TABLE "user-accounts" (...);  -- Works but requires quotes everywhere
SELECT * FROM "user-accounts";       -- Must quote on every reference

-- Prefer this pattern
CREATE TABLE user_accounts (...);    -- No quotes needed
SELECT * FROM user_accounts;         -- Clean and simple
```

### Environment Variables

| Component | Convention | Examples |
|-----------|------------|----------|
| All environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `REDIS_HOST`, `API_KEY` |

**Rule**: POSIX standard requires underscores (hyphens invalid in shell variable names).

### JSON Fields and Query Parameters

| Component | Convention | Examples |
|-----------|------------|----------|
| JSON keys | `snake_case` | `{ "created_at": "2025-01-01", "user_id": 123 }` |
| Query parameters | `snake_case` | `?user_id=123&sort_by=created_at` |
| OpenAPI operation IDs | `snake_case` | `get_user_by_id`, `create_order` |

**Rules**:
- Maintain consistency with Python code layer.
- Never expose internal IDs or enums with hyphens.
- Response payloads use `snake_case` for all keys.

---

## Layer 2: Container Orchestration (Context-Dependent)

### Development (Docker Compose) - Underscore Preferred

| Component | Convention | Examples |
|-----------|------------|----------|
| Service names | `snake_case` | `pm_house_calc_api`, `db_postgres_service` |
| Container names | `snake_case` | `pm_house_calc_api_1`, `redis_cache` |
| Volume names | `snake_case` | `postgres_data`, `redis_cache_data` |
| Network names | `snake_case` | `app_network`, `pm_network` |

**Example `docker-compose.yml`**:
```yaml
services:
  pm_house_calc_api:
    build: ./services/pm/house/calc_api
    container_name: pm_house_calc_api
    networks:
      - app_network
    volumes:
      - api_data:/data

  db_postgres_service:
    image: postgres:16
    container_name: db_postgres_service
    networks:
      - app_network
    volumes:
      - postgres_data:/var/lib/postgresql/data

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
  api_data:
```

**Rationale**:
- Matches Python module names (folder `pm_house_calc_api/` matches service name)
- Compose v1 uses underscores in generated names (`project_service_1`)
- Internal development environment, no DNS constraints

### Production (Kubernetes) - Hyphen Required

| Component | Convention | Examples |
|-----------|------------|----------|
| Service names | `kebab-case` | `pm-house-calc-api`, `db-postgres-service` |
| Deployment names | `kebab-case` | `pm-house-calc-api`, `worker-payment-process` |
| Pod labels | `kebab-case` | `app: pm-house-calc-api` |
| Namespace names | `kebab-case` | `property-management`, `user-management` |
| ConfigMap names | `kebab-case` | `pm-house-config`, `api-env-config` |
| Secret names | `kebab-case` | `db-credentials`, `api-keys` |

**Example Kubernetes manifests**:
```yaml
# Service
apiVersion: v1
kind: Service
metadata:
  name: pm-house-calc-api
  namespace: property-management
spec:
  selector:
    app: pm-house-calc-api
  ports:
    - port: 8000

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pm-house-calc-api
  namespace: property-management
spec:
  selector:
    matchLabels:
      app: pm-house-calc-api
  template:
    metadata:
      labels:
        app: pm-house-calc-api
    spec:
      containers:
        - name: api
          image: pm-house-calc-api:latest
```

**Rationale**:
- Kubernetes requires RFC 1035 DNS labels (lowercase alphanumeric + hyphens only)
- Underscores cause validation errors: `Invalid value: "pm_house_calc_api": a DNS-1035 label`
- Services become DNS entries: `pm-house-calc-api.property-management.svc.cluster.local`

---

## Layer 3: Network and DNS (Hyphen Required)

These components **require hyphens** due to DNS/network standards:

### DNS Hostnames

| Component | Convention | Examples |
|-----------|------------|----------|
| Domain names | `kebab-case` | `api.example.com`, `house-calc.example.com` |
| Subdomains | `kebab-case` | `api-v2.example.com`, `staging-api.example.com` |

**Rule**: RFC 1035/1123 prohibit underscores in hostnames (valid characters: `[a-z0-9-]`).

### Nginx Configuration

| Component | Convention | Examples |
|-----------|------------|----------|
| `server_name` directive | `kebab-case` | `server_name api.example.com;` |
| Upstream block names | `snake_case` | `upstream pm_house_calc_api { ... }` |
| Upstream server hostnames | `kebab-case` | `server pm-house-calc-api:8000;` |

**Example nginx configuration**:
```nginx
# Upstream name uses underscore (internal, matches Docker Compose)
upstream pm_house_calc_api {
    server pm-house-calc-api:8000;  # Server hostname uses hyphen (DNS)
}

# Server block
server {
    listen 80;
    server_name house-calc.example.com;  # Hyphen (DNS hostname)

    location /api/ {
        proxy_pass http://pm_house_calc_api;  # Upstream name (underscore OK)
        proxy_set_header Host $host;
    }
}
```

**Rationale**:
- Upstream names are internal identifiers (underscores allowed)
- Server names and hostnames must be DNS-compliant (hyphens only)
- Backend server addresses follow DNS rules

### REST API Paths

| Component | Convention | Examples |
|-----------|------------|----------|
| URL path segments | `kebab-case` | `/api/v1/house-calc`, `/user-accounts/{id}` |
| URL slugs | `kebab-case` | `/properties/house-123`, `/blog/my-post-title` |

**Example API endpoints**:
```
GET  /api/v1/house-calc/{id}
POST /api/v1/user-accounts
GET  /api/v1/payment-history
PUT  /api/v1/tenant-profiles/{id}
```

**Rationale**:
- SEO-friendly (search engines prefer hyphens over underscores)
- URL standard convention (RFC 3986 allows hyphens, underscores less common)
- Better readability in browser address bar

**Alternative (snake_case) is valid but discouraged**:
```
GET  /api/v1/house_calc/{id}        # Valid but less SEO-friendly
POST /api/v1/user_accounts           # Valid but unconventional
```

### Git Branches

| Component | Convention | Examples |
|-----------|------------|----------|
| Feature branches | `kebab-case` | `feature/house-calc`, `feature/user-auth` |
| Bugfix branches | `kebab-case` | `bugfix/fix-login`, `bugfix/calc-error` |
| Release branches | `kebab-case` | `release/v1.2.0`, `release/v2.0.0-beta` |

**Rationale**: Git convention, URL compatibility, readability.

---

## Conversion Rules

### Development → Production Transformation

When deploying from Docker Compose (underscores) to Kubernetes (hyphens), use automatic conversion:

#### Bash Script
```bash
#!/bin/bash
# convert_service_names.sh

SERVICE_NAME="pm_house_calc_api"
K8S_NAME=$(echo "$SERVICE_NAME" | tr '_' '-')
echo "Docker Compose: $SERVICE_NAME"
echo "Kubernetes: $K8S_NAME"
# Output:
# Docker Compose: pm_house_calc_api
# Kubernetes: pm-house-calc-api
```

#### Python Function
```python
def service_to_k8s(service_name: str) -> str:
    """Convert Docker Compose service name to Kubernetes-compatible name."""
    return service_name.replace('_', '-')

# Usage
compose_name = "pm_house_calc_api"
k8s_name = service_to_k8s(compose_name)
print(f"Compose: {compose_name}")
print(f"K8s: {k8s_name}")
# Output:
# Compose: pm_house_calc_api
# K8s: pm-house-calc-api
```

#### Make Target
```makefile
# Makefile

.PHONY: k8s-deploy
k8s-deploy:
	@for service in services/*; do \
		SERVICE_NAME=$$(basename $$service); \
		K8S_NAME=$$(echo $$SERVICE_NAME | tr '_' '-'); \
		echo "Deploying $$SERVICE_NAME as $$K8S_NAME..."; \
		kubectl apply -f k8s/$$K8S_NAME.yml; \
	done
```

### CI/CD Pipeline Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Convert service names and deploy
        run: |
          for service_dir in services/*/; do
            SERVICE_NAME=$(basename "$service_dir")
            K8S_NAME=$(echo "$SERVICE_NAME" | tr '_' '-')

            echo "Deploying $SERVICE_NAME to Kubernetes as $K8S_NAME"

            # Generate K8s manifest from template
            sed "s/{{SERVICE_NAME}}/$K8S_NAME/g" \
              k8s/service-template.yml > k8s/generated/$K8S_NAME.yml

            # Apply manifest
            kubectl apply -f k8s/generated/$K8S_NAME.yml
          done
```

### Service Name Mapping Reference

| Code Layer | Docker Compose | Kubernetes | DNS |
|------------|----------------|------------|-----|
| `pm_house_calc_api/` | `pm_house_calc_api` | `pm-house-calc-api` | `house-calc.example.com` |
| `fn_payment_process_worker/` | `fn_payment_process_worker` | `fn-payment-process-worker` | `payment.example.com` |
| `um_tenant_auth_api/` | `um_tenant_auth_api` | `um-tenant-auth-api` | `auth.example.com` |
| `db_postgres_service/` | `db_postgres_service` | `db-postgres-service` | `db-postgres.internal` |

**Key Insight**: All representations refer to the SAME service, just different layers with layer-appropriate separators.

---

## Naming Formula for Large Projects

For projects with 100+ microservices, use hierarchical naming:

### 4-Level Formula (Recommended for 50+ Services)

**Pattern**: `{context}_{domain}_{function}_{type}` (code layer)
**Pattern**: `{context}-{domain}-{function}-{type}` (network layer)

| Context | Domain | Function | Type | Code Name | Network Name |
|---------|--------|----------|------|-----------|--------------|
| `pm` | `house` | `calc` | `api` | `pm_house_calc_api` | `pm-house-calc-api` |
| `pm` | `apartment` | `listing` | `api` | `pm_apartment_listing_api` | `pm-apartment-listing-api` |
| `fn` | `payment` | `process` | `worker` | `fn_payment_process_worker` | `fn-payment-process-worker` |
| `um` | `tenant` | `auth` | `api` | `um_tenant_auth_api` | `um-tenant-auth-api` |
| `cm` | `telegram` | `notification` | `bot` | `cm_telegram_notification_bot` | `cm-telegram-notification-bot` |

### Context Abbreviations

| Abbreviation | Full Name | Business Domain |
|--------------|-----------|-----------------|
| `pm` | Property Management | Real estate, housing, rentals |
| `um` | User Management | Authentication, profiles, tenants, landlords |
| `fn` | Financial | Payments, invoicing, commissions, taxes |
| `cm` | Communication | Notifications, emails, SMS, bots |
| `an` | Analytics | Reporting, metrics, user behavior |
| `da` | Data Access | Database services (PostgreSQL, MongoDB) |
| `int` | Integration | Third-party APIs (Stripe, Google, etc.) |
| `sec` | Security | Auth, audit, compliance |
| `ops` | Operations | Monitoring, backup, infrastructure |

### 3-Level Formula (For Simpler Projects)

**Pattern**: `{context}_{function}_{type}` (code layer)
**Pattern**: `{context}-{function}-{type}` (network layer)

Use when domain is obvious from context or for smaller projects (< 50 services):

| Context | Function | Type | Code Name | Network Name |
|---------|----------|------|-----------|--------------|
| `house` | `calc` | `api` | `house_calc_api` | `house-calc-api` |
| `payment` | `process` | `worker` | `payment_process_worker` | `payment-process-worker` |
| `telegram` | `bot` | `bot` | `telegram_bot` | `telegram-bot` |

---

## Character Restrictions by Technology

### Complete Reference Table

| Technology | Underscores | Hyphens | Max Length | Pattern |
|------------|-------------|---------|------------|---------|
| **Kubernetes** | ❌ Prohibited | ✅ Required | 253 chars | `[a-z0-9]([-a-z0-9]*[a-z0-9])?` |
| **DNS hostnames** | ❌ Prohibited | ✅ Required | 253 chars | RFC 1035/1123 |
| **Nginx server_name** | ❌ Prohibited | ✅ Required | - | DNS hostname |
| **Nginx upstream** | ✅ Allowed | ✅ Allowed | - | Any (internal) |
| **Docker Compose services** | ✅ Allowed | ✅ Allowed | ~242 chars | `[a-zA-Z0-9._-]+` |
| **Docker containers** | ✅ Allowed | ✅ Allowed | ~242 chars | `[a-zA-Z0-9][a-zA-Z0-9_.-]*` |
| **Python modules** | ✅ Required | ❌ Prohibited | - | `[a-z_][a-z0-9_]*` |
| **PostgreSQL (unquoted)** | ✅ Required | ❌ Prohibited | 63 bytes | `[a-z_][a-z0-9_$]*` |
| **MongoDB collections** | ✅ Preferred | ⚠️ Discouraged | 120 bytes | Special syntax for hyphens |
| **MongoDB databases** | ✅ Allowed | ❌ Prohibited | 64 bytes | `[a-zA-Z0-9_]+` |
| **Environment variables** | ✅ Required | ❌ Prohibited | - | `[A-Z_][A-Z0-9_]*` |

---

## Files & Folders

| Component | Convention | Examples |
|-----------|------------|----------|
| Directories | `snake_case` | `user_service/`, `api_endpoints/`, `shared/` |
| Python files | `snake_case` | `user_repository.py`, `config.py` |
| Config files | Tool-specific | `pyproject.toml`, `.env`, `Dockerfile` |
| Documentation | `snake_case` or `UPPERCASE` | `README.md`, `api_guide.md` |

**File-folder alignment**: Directory name should match Python package name:
```
services/
  pm_house_calc_api/          # Folder (snake_case)
    src/
      pm_house_calc_api/      # Python package (snake_case)
        __init__.py
        main.py
```

---

## Infrastructure

### Docker Compose

- Service names: `snake_case` (`pm_house_calc_api`)
- Container names: `snake_case` (`pm_house_calc_api_1`)
- Volume names: `snake_case` (`postgres_data`)
- Network names: `snake_case` (`app_network`)

### Kubernetes

- All resource names: `kebab-case` (`pm-house-calc-api`)
- Labels and annotations: `kebab-case` keys (`app: pm-house-calc-api`)
- Namespaces: `kebab-case` (`property-management`)

### Git

- Branch names: `kebab-case` with prefix (`feature/house-calc`, `bugfix/login-fix`)
- Tag names: Semantic versioning (`v1.2.3`, `v2.0.0-beta.1`)

---

## Exceptions

Some tools mandate specific naming formats. These are allowed and documented:

### Mandatory Hyphenated Files
- `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`
- `.gitignore`, `.dockerignore`, `.env.example`
- `.pre-commit-config.yaml`, `.github/workflows/*.yml`
- `pyproject.toml`, `requirements.txt`

### Third-Party Package Names
- PyPI packages: `flask-sqlalchemy`, `django-rest-framework` (distribution names)
- Import as: `import flask_sqlalchemy`, `import rest_framework` (Python modules)

### HTTP Headers
- Standard format: `X-Request-ID`, `Content-Type`, `Authorization`
- Nginx drops underscore headers by default (security feature)

### Protocol-Specific
- DNS SRV records: `_http._tcp.example.com` (underscore prefix for service records)
- Well-known URIs: `/.well-known/acme-challenge/` (RFC 8615)

Any new exception must be documented in the consuming service's README and, if long-lived, added to this list.

---

## Migration Guidance

### Audit Current Names

```bash
# Find hyphenated service names (should convert to underscore for code layer)
rg --pcre2 "\b[a-z]+-[a-z]+" services/ --type py

# Find service directories with hyphens
find services/ -type d -name "*-*"

# Check docker-compose.yml for inconsistent naming
grep "services:" -A 100 docker-compose.yml | grep -E "^\s+\w"
```

### Conversion Strategy

1. **Code Layer (Underscore)**:
   - Rename folders: `api-service/` → `api_service/`
   - Rename Python modules: `api_service.py` (ensure snake_case)
   - Update imports: `from api_service import ...`
   - Update database names: `api_service_db`

2. **Docker Compose (Underscore)**:
   ```yaml
   services:
     api_service:  # Underscore
       container_name: api_service
   ```

3. **Kubernetes (Hyphen)**:
   ```yaml
   metadata:
     name: api-service  # Hyphen (auto-convert from api_service)
   ```

### Backward Compatibility

When renaming public APIs:
```nginx
# Nginx alias for backward compatibility
server {
    # New kebab-case URL (preferred)
    location /api/v1/user-accounts {
        proxy_pass http://api_service;
    }

    # Old snake_case URL (deprecated, redirect)
    location /api/v1/user_accounts {
        return 301 /api/v1/user-accounts$is_args$args;
    }
}
```

### Validation Checklist

- [ ] All Python modules use `snake_case`
- [ ] All database identifiers use `snake_case`
- [ ] Docker Compose service names use `snake_case`
- [ ] Kubernetes manifests use `kebab-case`
- [ ] DNS hostnames use `kebab-case`
- [ ] REST API paths use `kebab-case` (or document snake_case exception)
- [ ] Git branches use `kebab-case`
- [ ] Environment variables use `UPPER_SNAKE_CASE`
- [ ] Conversion automation in CI/CD pipeline
- [ ] Documentation updated with new naming strategy

---

## Related Documents

- [Project Structure Patterns](project-structure-patterns.md) - Folder organization and service layout
- [Linting Standards](../testing/quality-assurance/linting-standards.md) - Automated naming validation
- [Service Separation Principles](service-separation-principles.md) - Service type naming conventions

---

## Summary

**The Golden Rule**: Use the separator appropriate for your technical layer.

| Layer | Separator | Why |
|-------|-----------|-----|
| **Code & Data** | Underscore `_` | Python, SQL, MongoDB require it |
| **Container (Dev)** | Underscore `_` | Matches code layer, Compose v1 compatibility |
| **Container (Prod)** | Hyphen `-` | Kubernetes, DNS require it |
| **Network & DNS** | Hyphen `-` | RFC standards require it |

**Conversion**: Automate `underscore_to_hyphen` transformation at deployment boundary (Docker Compose → Kubernetes).

**Consistency**: Maintain 1:1 mapping across all layers:
- Code: `pm_house_calc_api/`
- Docker Compose: `pm_house_calc_api`
- Kubernetes: `pm-house-calc-api`
- DNS: `house-calc.example.com`

All names refer to the **same logical service**, just using layer-appropriate separators.
