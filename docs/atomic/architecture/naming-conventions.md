# Naming Conventions

## AI Quick Reference

> **NAMING PHILOSOPHY**: Use **semantic shortening** — clear context + domain, omit redundant function words. Average length: 20-27 chars (no abbreviations needed).

> ⚠️ **CRITICAL**: Maintain a Context Registry to prevent context name conflicts across your project. Never reuse context names for different business domains.
>
> **Location**: Create `docs/atomic/architecture/context-registry.md` in your project
> **Structure**: List each context with its business domain and example services
> **Example entry**: `finance` → Financial services (lending, payments, crypto)
> **See**: [context-registry.md](context-registry.md) template for detailed format

### 3-Part vs 4-Part Service Naming Decision

**DEFAULT**: Use 3-part `{context}_{domain}_{type}` — function is implied by domain.

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

| Element Type | Pattern | Example | Separator |
|--------------|---------|---------|-----------|
| **Microservice (default)** | `{context}_{domain}_{type}` | `finance_lending_api` | `_` |
| **Microservice (ambiguous domain)** | `{context}_{domain}_{function}_{type}` | `logistics_fleet_tracking_api` | `_` |
| **Python Class** | `{Noun}{Suffix}` | `UserService`, `OrderRepository` | None (PascalCase) |
| **Python Function** | `{verb}_{noun}[_qualifier]` | `get_user_by_id`, `create_order` | `_` |
| **Python Variable** | `{noun}[_qualifier]` | `user_id`, `max_attempts` | `_` |
| **Python Parameter** | `{noun}[_qualifier]` | `user_id: int`, `is_active: bool` | `_` |
| **Python Constant** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `MAX_RETRIES` | `_` |
| **Python Module/File** | `{class_name}.py` | `user_service.py`, `order_dto.py` | `_` |
| **Folder/Package** | `{service_name}/` | `finance_lending_api/` | `_` |
| **Docker Compose Service** | `{service_name}` | `finance_lending_api` | `_` |
| **Kubernetes Service** | `{service-name}` | `finance-lending-api` | `-` |
| **Database Table** | `{plural_noun}[_{qualifier}]` | `users`, `order_items` | `_` |
| **Database Column** | `{noun}[_qualifier]` | `created_at`, `user_id` | `_` |
| **Env Variable** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `API_KEY` | `_` |
| **REST API Path** | `/api/v{N}/{resource}[/{id}]` | `/api/v1/users/{id}` | `/` (segments), `-` (words) |
| **Git Branch** | `{type}/{description}` | `feature/user-auth` | `-` |

> **✅ Validation**: After naming elements, verify compliance with the [Validation Checklist](#validation-checklist) (Section 4).

---

## AI Decision Tree: How to Name Any Element

### Quick Navigation by Element Type

```
SERVICE (microservice/app)     → Section 2: Microservice Naming Patterns (line 485+)
PYTHON CLASS                   → Section 3: Python Classes (line 683+)
PYTHON FUNCTION                → Section 3: Python Functions (line 741+)
PYTHON VARIABLE/PARAMETER      → Section 3: Variables & Parameters (line 782+)
FILE/FOLDER                    → Section 3: Files & Folders (line 864+)
DATABASE (table/column)        → Section 3: Database Elements (line 906+)
INFRASTRUCTURE (K8s/Docker)    → Section 1: Technical Rules (line 168+)
```

**Most Common: Naming a Service**

### Step 2: Service Formula (Quick Reference)

**Default Pattern (3-part)**: `{context}_{domain}_{type}`

- **Context**: Business area (finance, healthcare, construction...)
- **Domain**: Subdomain (lending, telemedicine, house...)
- **Type**: Tech type (api, worker, bot, gateway...)

**Examples (3-part)**:
- `finance_lending_api` — Lending platform (matching/approval implied)
- `healthcare_telemedicine_api` — Telemedicine service (consultation implied)
- `construction_house_bot` — House management (management implied)

**Extended Pattern (4-part)**: `{context}_{domain}_{function}_{type}`

Use 4-part only when function is NOT implied by domain:

**Examples (4-part needed)**:
- `logistics_fleet_tracking_api` — Fleet could mean tracking, management, or maintenance
- `analytics_reporting_api` — Analytics could mean reporting, querying, or processing
- `communication_notification_worker` — Communication could mean email, SMS, or notifications

**Decision Rule**:
- If domain clearly implies ONE function → use 3-part
- If domain has MULTIPLE possible functions → use 4-part with explicit function

### Step 3: Python Class Rules (Quick Reference)

**Pattern**: `{Noun}{Suffix}` in PascalCase

| Purpose | Suffix | Example |
|---------|--------|---------|
| Business logic | `Service` | `UserService`, `PaymentService` |
| Data access | `Repository` | `UserRepository`, `OrderRepository` |
| Data transfer | `DTO` | `UserCreateDTO`, `OrderUpdateDTO` |
| Request handling | `Handler` | `MessageHandler`, `WebhookHandler` |
| API routing | `Router` | `UserRouter`, `PaymentRouter` |
| Domain model | No suffix | `User`, `Order`, `Payment` |

**Note**: DTOs use action-based pattern: `{Noun}{Action}DTO` (not `{Noun}DTO{Action}`)

→ **Full details**: Section 3: Python Classes (line 683+)

### Step 4: Python Function Rules (Quick Reference)

**Pattern**: `{verb}_{noun}[_qualifier]` in snake_case

| Verb Category | Verbs | Example |
|--------------|-------|---------|
| Retrieval | `get_`, `find_`, `fetch_` | `get_user_by_id`, `find_orders_by_status` |
| Creation | `create_`, `add_` | `create_order`, `add_user` |
| Modification | `update_`, `modify_` | `update_user`, `modify_order_status` |
| Deletion | `delete_`, `remove_` | `delete_user`, `remove_order` |
| Validation | `validate_`, `check_`, `verify_` | `validate_email`, `check_password_strength` |
| Calculation | `calculate_`, `compute_` | `calculate_total_price`, `compute_discount` |
| Communication | `send_`, `notify_`, `publish_` | `send_email_to_user`, `notify_admin` |

→ **Full details**: Section 3: Python Functions (line 741+)

### Step 5: Python Variable/Parameter Rules (Quick Reference)

**Pattern**: `{noun}[_qualifier]` in snake_case

| Type | Pattern | Example |
|------|---------|---------|
| ID reference | `{noun}_id` | `user_id`, `order_id` |
| Boolean flag | `is_{adj}`, `has_{noun}`, `can_{verb}` | `is_active`, `has_permission`, `can_edit` |
| Timestamp | `{action}_at` | `created_at`, `updated_at`, `deleted_at` |
| Count | `{noun}_count` or `num_{noun}` | `retry_count`, `num_attempts` |
| Limits | `max_{noun}`, `min_{noun}` | `max_retries`, `min_password_length` |

→ **Full details**: Section 3: Variables & Parameters (line 782+)

### Step 6: File/Folder Rules (Quick Reference)

| Element | Pattern | Example |
|---------|---------|---------|
| Python module | `{class_name}.py` (snake_case) | `user_service.py`, `order_repository.py` |
| Package folder | `{package_name}/` (snake_case) | `finance_lending_api/` |
| Test file | `test_{module_name}.py` | `test_user_service.py` |

→ **Full details**: Section 3: Files & Folders (line 864+)

### Step 7: Database Rules (Quick Reference)

| Element | Pattern | Example |
|---------|---------|---------|
| Table | `{plural_noun}` (snake_case) | `users`, `order_items` |
| Column | `{noun}[_qualifier]` | `user_id`, `created_at`, `is_active` |
| Index | `idx_{table}_{column}` | `idx_users_email` |
| Foreign key | `fk_{table}_{ref_table}` | `fk_orders_users` |

→ **Full details**: Section 3: Database Elements (line 906+)

### Step 8: Infrastructure Rules (Quick Reference)

| Layer | Separator | Example |
|-------|-----------|---------|
| **Docker Compose** (dev) | Underscore `_` | `finance_lending_api` |
| **Kubernetes** (prod) | Hyphen `-` | `finance-lending-api` |
| **DNS hostnames** | Hyphen `-` | `api.example.com` |
| **Environment variables** | Underscore `_` | `DATABASE_URL` |

→ **Full details**: Section 1: Technical Rules (line 168+)

---

## Section 1: Technical Rules

### Core Principle

**Use underscores for code/data layer, hyphens for network/DNS layer.**

This framework employs a **context-layered naming strategy** where separator choice depends on the technical layer:
- **Layer 1 (Code & Data)**: Underscores required (Python, PostgreSQL, MongoDB, environment variables)
- **Layer 2 (Container Orchestration)**: Context-dependent (underscores in Docker Compose dev, hyphens in Kubernetes prod)
- **Layer 3 (Network & DNS)**: Hyphens required (DNS hostnames, Nginx, REST APIs, SSL certificates)

This approach ensures compatibility across all technologies while maintaining clear conversion rules between development and production environments.

---

### Separator Rules by Context

| Context | Convention | Reason | Examples |
|---------|------------|--------|----------|
| **Python code** | `snake_case` (underscore) | PEP 8 requirement, import system | `finance_lending_api.py`, `get_user()` |
| **Database** | `snake_case` (underscore) | SQL standard, PostgreSQL/MongoDB requirement | `user_accounts`, `created_at` |
| **Docker Compose services** | `snake_case` (underscore) | Internal use, matches code layer | `finance_lending_api` |
| **Container names (dev)** | `snake_case` (underscore) | Internal dev naming, consistency | `finance_lending_api_1` |
| **Kubernetes services** | `kebab-case` (hyphen) | RFC 1035 compliance, DNS requirement | `finance-lending-api` |
| **DNS hostnames** | `kebab-case` (hyphen) | RFC 1035/1123 standard | `api-service.example.com` |
| **Nginx server_name** | `kebab-case` (hyphen) | DNS hostname validation | `lending.example.com` |
| **Nginx upstreams** | `snake_case` (underscore) | Internal name, matches service names | `upstream finance_lending_api` |
| **REST API paths** | `kebab-case` (hyphen) | SEO-friendly, URL standard | `/api/v1/lending` |
| **Git branches** | `kebab-case` (hyphen) | Git convention, URL compatibility | `feature/lending-api` |
| **Environment variables** | `UPPER_SNAKE_CASE` (underscore) | POSIX standard, shell requirement | `DATABASE_URL` |

---

### Layer 1: Code and Data (Underscore Required)

These components **require underscores** due to language/platform restrictions:

#### Python Code

| Component | Convention | Examples |
|-----------|------------|----------|
| Modules | `snake_case` | `user_repository.py`, `order_dto.py` |
| Packages | `snake_case` | `finance_lending_api/`, `shared/` |
| Classes | `PascalCase` | `UserService`, `LendingCalculator` |
| Functions & methods | `snake_case` | `get_user_by_id()`, `calculate_price()` |
| Variables | `snake_case` | `max_retry_attempts`, `user_id` |
| Constants | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `MAX_CONNECTIONS` |
| Private members | `_snake_case` | `_internal_cache`, `_validate()` |

**Rules**:
- Modules and packages must use `snake_case` (hyphens cause `SyntaxError` in imports).
- Classes use `PascalCase`; data classes and Pydantic models follow the same rule.
- Functions, methods, and variables use `snake_case`.
- Constants use `UPPER_SNAKE_CASE` and live at module scope.
- DTOs use action suffix pattern: `{Noun}{Action}DTO` (e.g., `UserCreateDTO`, `OrderUpdateDTO`, `PaymentPublicDTO`). Never use `{Noun}DTO{Action}` (not `UserDTOCreate`). Avoid generic names like `DataDTO`.

**PyPI Distribution Names Exception**:
- PyPI package names can use hyphens: `scikit-learn`, `django-rest-framework`
- Import names must use underscores: `import sklearn`, `import rest_framework`
- Prefer underscores in distribution names for consistency: `my_package` over `my-package`

#### Databases

| Component | Convention | Pattern | Examples |
|-----------|------------|---------|----------|
| PostgreSQL tables | `snake_case` | `{plural_noun}[_{qualifier}]` | `users`, `orders`, `order_items` *(item is qualifier)* |
| PostgreSQL columns | `snake_case` | `{noun}[_{qualifier}]` | `created_at`, `user_id`, `is_active` |
| PostgreSQL indexes | `snake_case` | `idx_{table}_{column}` | `idx_users_email`, `idx_orders_created` |
| PostgreSQL constraints | `snake_case` | `{type}_{table}_{column}` | `fk_orders_users`, `uk_users_email` |
| PostgreSQL schemas | `snake_case` | `{noun}[_{qualifier}]` | `public`, `analytics`, `audit_log` |
| MongoDB collections | `snake_case` | `{plural_noun}[_{qualifier}]` | `events`, `sessions`, `analytics_events` *(analytics is qualifier)* |
| MongoDB fields | `snake_case` | `{noun}[_{qualifier}]` | `event_type`, `created_at` |
| MongoDB databases | `snake_case` | `{service}_db` or `{noun}_db` | `user_service_db`, `analytics_db` |

**Qualifier Usage Rule**: Add qualifier when:
1. **Disambiguation needed**: `analytics_events` (distinguish from other event types), `user_sessions` (distinguish from other session types)
2. **Subcategory**: `order_items` (items belonging to orders), `audit_log` (log type)
3. **No qualifier needed**: `users`, `orders`, `payments` (unambiguous primary entities)

**Rules**:
- PostgreSQL **prohibits hyphens** in unquoted identifiers (interpreted as subtraction operator).
- MongoDB **discourages hyphens** (requires special syntax: `db.getCollection("name-with-hyphen")`).
- Use `snake_case` for all database identifiers to avoid quoting everywhere.
- **Database migrations**: Use Alembic auto-generated format (recommended):
  - **Pattern**: `{revision_hash}_{description}.py`
  - **Example**: `a1b2c3d4e5f6_add_user_table.py`, `b2c3d4e5f6g7_create_index_users_email.py`
  - **Alembic generates**: revision hash automatically (ensures ordering)
  - **Description**: Use `snake_case`, start with verb (add, create, remove, alter)
  - **Alternative (manual only)**: `YYYYMMDDHHmmss_{description}.py` (UTC) — only if not using Alembic

#### Environment Variables

| Component | Convention | Examples |
|-----------|------------|----------|
| All environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `REDIS_HOST`, `API_KEY` |

**Rule**: POSIX standard requires underscores (hyphens invalid in shell variable names).

#### JSON Fields and Query Parameters

| Component | Convention | Examples |
|-----------|------------|----------|
| JSON keys | `snake_case` | `{ "created_at": "2025-01-01", "user_id": 123 }` |
| Query parameters | `snake_case` | `?user_id=123&sort_by=created_at` |
| OpenAPI operation IDs | `snake_case` | `get_user_by_id`, `create_order` |

**Rules**:
- **Use `snake_case`** for consistency with Python code layer (no case conversion needed in FastAPI/Pydantic models)
- **Rationale**:
  - Direct mapping to Python attributes (no camelCase ↔ snake_case conversion)
  - Consistent with database column names
  - Reduces cognitive load for backend developers
- **Note**: Some REST APIs use camelCase (JavaScript convention). Choose one convention and document it in your API style guide.
- Never expose internal IDs or enums with hyphens.
- Response payloads use `snake_case` for all keys.

---

### Layer 2: Container Orchestration (Context-Dependent)

#### Development (Docker Compose) - Underscore Preferred

| Component | Convention | Examples |
|-----------|------------|----------|
| Service names (in YAML) | `snake_case` | `finance_lending_api`, `db_postgres_service` |
| Container names (auto-generated by Docker) | `{project}_{service}_{replica}` | `myproject_finance_lending_api_1` |
| Container names (explicit via `container_name`) | `snake_case` | `finance_lending_api`, `redis_cache` |
| Volume names | `snake_case` | `postgres_data`, `redis_cache_data` |
| Network names | `snake_case` | `app_network`, `finance_network` |

**Note**: Docker Compose auto-generates container names as `{project}_{service}_{replica}` (e.g., `myproject_finance_lending_api_1`). Use explicit `container_name` in YAML to override this behavior.

**Example `docker-compose.yml`**:
```yaml
services:
  finance_lending_api:
    build: ./services/finance/lending_api
    container_name: finance_lending_api
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
- Matches Python module names (folder `finance_lending_api/` matches service name)
- Docker Compose generates container names with underscores (`project_service_1`)
- Internal development environment, no DNS constraints

#### Production (Kubernetes) - Hyphen Required

| Component | Convention | Examples |
|-----------|------------|----------|
| Service names | `kebab-case` | `finance-lending-api`, `db-postgres-service` |
| Deployment names | `kebab-case` | `finance-lending-api`, `worker-payment-process` |
| Pod labels | `kebab-case` | `app: finance-lending-api` |
| Namespace names | `kebab-case` | `finance`, `user-management` |
| ConfigMap names | `kebab-case` | `finance-lending-config`, `api-env-config` |
| Secret names | `kebab-case` | `db-credentials`, `api-keys` |

**Example Kubernetes manifests**:
```yaml
# Service
apiVersion: v1
kind: Service
metadata:
  name: finance-lending-api
  namespace: finance
spec:
  selector:
    app: finance-lending-api
  ports:
    - port: 8000

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finance-lending-api
  namespace: finance
spec:
  selector:
    matchLabels:
      app: finance-lending-api
  template:
    metadata:
      labels:
        app: finance-lending-api
    spec:
      containers:
        - name: api
          image: finance-lending-api:latest
```

**Rationale**:
- Kubernetes requires RFC 1035 DNS labels (lowercase alphanumeric + hyphens only)
- Underscores cause validation errors: `Invalid value: "finance_lending_api": a DNS-1035 label`
- Services become DNS entries: `finance-lending-api.finance.svc.cluster.local`

---

### Layer 3: Network and DNS (Hyphen Required)

These components **require hyphens** due to DNS/network standards:

#### DNS Hostnames

| Component | Convention | Examples |
|-----------|------------|----------|
| Domain names | `kebab-case` | `api.example.com`, `lending.example.com` |
| Subdomains | `kebab-case` | `api-v2.example.com`, `staging-api.example.com` |

**Rule**: RFC 1035/1123 prohibit underscores in hostnames (valid characters: `[a-z0-9-]`).

#### Nginx Configuration

| Component | Convention | Examples |
|-----------|------------|----------|
| `server_name` directive | `kebab-case` | `server_name api.example.com;` |
| Upstream block name (internal identifier) | `snake_case` (always) | `upstream finance_lending_api { ... }` |
| Upstream server address (dev/Docker Compose) | `snake_case` | `server finance_lending_api:8000;` |
| Upstream server address (prod/Kubernetes) | `kebab-case` | `server finance-lending-api:8000;` |

**Example nginx configuration**:
```nginx
# DEVELOPMENT (Docker Compose)
# Upstream name uses underscore (internal identifier)
upstream finance_lending_api {
    server finance_lending_api:8000;  # Compose service name (underscore)
}

# PRODUCTION (Kubernetes)
# Upstream name still uses underscore (internal identifier)
upstream finance_lending_api {
    server finance-lending-api:8000;  # K8s DNS name (hyphen required)
}

# Server block (same for both environments)
server {
    listen 80;
    server_name lending.example.com;  # DNS hostname (hyphen)

    location /api/ {
        proxy_pass http://finance_lending_api;  # Upstream name (underscore)
        proxy_set_header Host $host;
    }
}
```

**Rationale**:
- **Upstream block name**: Internal Nginx identifier, always use `snake_case` (same in dev and prod)
- **Upstream server address**: Backend service address, environment-specific:
  - **Dev (Docker Compose)**: `finance_lending_api` (underscore) — matches Docker Compose service name
  - **Prod (Kubernetes)**: `finance-lending-api` (hyphen) — must be DNS-compliant
- **server_name directive**: External DNS hostname, always `kebab-case` (RFC 1035 requirement)

#### REST API Paths

| Component | Convention | Examples |
|-----------|------------|----------|
| URL path segments | `kebab-case` | `/api/v1/lending`, `/api/v1/users/{id}` |
| URL slugs | `kebab-case` | `/properties/house-123`, `/blog/my-post-title` |

**Path-to-Service Mapping Rule**:
- REST path uses the **domain** part of service name (context omitted for brevity)
- Service `{context}_{domain}_{type}` → Path `/api/v1/{domain}`
- Convert underscores to hyphens for multi-word domains

**Example API endpoints**:
```
GET  /api/v1/lending/{id}         # matches finance_lending_api (domain: lending)
POST /api/v1/users                 # matches user_auth_api (domain: auth → users)
GET  /api/v1/payments              # matches finance_payment_api (domain: payment)
PUT  /api/v1/appointments/{id}     # matches healthcare_appointment_api (domain: appointment)
```

**Optional**: Include context in path if multiple contexts share the same domain:
```
GET  /api/v1/finance/lending      # explicit context when needed
GET  /api/v1/property/lending     # different context, same domain word
```

**Rationale**:
- SEO-friendly (search engines prefer hyphens over underscores)
- URL standard convention (RFC 3986 allows hyphens, underscores less common)
- Better readability in browser address bar
- Shorter paths when context is implied by API subdomain/gateway

#### Git Branches

> **Note**: Optional reference. Adapt to your team's git workflow.

**Core Pattern**: `{type}/{description}` in `kebab-case`

| Branch Type | Examples |
|-------------|----------|
| Feature | `feature/lending-api`, `feature/user-auth` |
| Bugfix | `bugfix/fix-login`, `bugfix/calc-error` |
| Hotfix | `hotfix/security-patch`, `hotfix/critical-bug` |
| Release | `release/v1.2.0`, `release/v2.0.0-beta` |

**Extended types** (if using conventional commits):
- `refactor/`, `chore/`, `docs/`, `test/`, `perf/`

**Rationale**: Git convention, URL compatibility, readability.

---

### Character Restrictions by Technology

| Technology | Underscores | Hyphens | Max Length | Pattern |
|------------|-------------|---------|------------|---------|
| **Kubernetes** | ❌ Prohibited | ✅ Required | 253 chars | `[a-z0-9]([-a-z0-9]*[a-z0-9])?` |
| **DNS hostnames** | ❌ Prohibited | ✅ Required | 253 chars | RFC 1035/1123 |
| **Python modules** | ✅ Required | ❌ Prohibited | - | `[a-z_][a-z0-9_]*` |
| **PostgreSQL (unquoted)** | ✅ Required | ❌ Prohibited | 63 bytes | `[a-z_][a-z0-9_$]*` |
| **MongoDB databases** | ✅ Allowed | ❌ Prohibited | 64 bytes | `[a-zA-Z0-9_]+` |
| **MongoDB collections** | ✅ Allowed | ❌ Prohibited | - | `[a-zA-Z0-9_]+` |
| **Environment variables** | ✅ Required | ❌ Prohibited | - | `[A-Z_][A-Z0-9_]*` |
| **RabbitMQ queues** | ✅ Allowed | ✅ Allowed | 255 chars | `[a-zA-Z0-9_.-]+` |
| **RabbitMQ exchanges** | ✅ Allowed | ✅ Allowed | 255 chars | `[a-zA-Z0-9_.-]+` |
| **Redis keys** | ✅ Allowed | ✅ Allowed | No limit *(512MB value size)* | Any binary-safe string |
| **Nginx server_name** | ❌ Prohibited | ✅ Required | 253 chars | DNS hostname (RFC 1035) |
| **Nginx upstream** | ✅ Allowed | ✅ Allowed | - | `[a-zA-Z0-9_-]+` |
| **Git branches** | ✅ Allowed | ✅ Recommended | - | `[a-zA-Z0-9_/-]+` |

---

## Section 2: Microservice Naming Patterns

### Service Naming Formula

**Primary Pattern (3-part)**: `{context}_{domain}_{type}`

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

**Extended Pattern (4-part)**: `{context}_{domain}_{function}_{type}`

Use when domain has multiple possible functions (ambiguous):

**Examples (4-part)**:
- `logistics_fleet_tracking_api` — Fleet needs clarification (vs management, maintenance)
- `analytics_reporting_api` — Analytics needs clarification (vs querying, processing)
- `communication_notification_worker` — Communication needs clarification (vs email, SMS)

---

### When to Use 3-Part vs 4-Part

> **See Quick Reference at top of document** for the objective decision rule (line 14).

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

### Domain-Function Mapping (Implied Functions)

**Finance Context** (mostly 3-part):
| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `lending` | matching, approval | `finance_lending_api` | 19 |
| `payment` | processing | `finance_payment_api` | 19 |
| `crypto` | portfolio management | `finance_crypto_api` | 18 |
| `billing` | invoicing, cycles | `finance_billing_api` | 19 |
| `trading` | algorithmic trading | `finance_trading_api` | 19 |

**Healthcare Context** (mostly 3-part):
| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `telemedicine` | consultation | `healthcare_telemedicine_api` | 27 |
| `appointment` | booking | `healthcare_appointment_api` | 26 |
| `pharmacy` | medication management | `healthcare_pharmacy_api` | 23 |
| `mental_health` | therapy, counseling | `healthcare_mental_health_api` | 28 |

**Construction Context** (mostly 3-part):
| Domain | Implied Function | 3-Part Name | Chars |
|--------|------------------|-------------|-------|
| `house` | project management | `construction_house_bot` | 22 |
| `material` | calculation, inventory | `construction_material_api` | 25 |
| `renovation` | planning | `construction_renovation_api` | 27 |
| `commercial` | project management | `construction_commercial_api` | 27 |

**Logistics Context** (needs 4-part often):
| Domain | Multiple Functions | 4-Part Name (explicit) | Chars |
|--------|--------------------|------------------------|-------|
| `fleet` | tracking OR management OR maintenance | `logistics_fleet_tracking_api` | 28 |
| `delivery` | routing OR tracking | `logistics_delivery_tracking_api` | 31 |
| `warehouse` | inventory OR fulfillment | `logistics_warehouse_inventory_api` | 34 |

**Analytics Context** (needs 4-part often):
| Domain | Multiple Functions | 4-Part Name (explicit) | Chars |
|--------|--------------------|------------------------|-------|
| `reporting` | generation (not querying) | `analytics_reporting_api` | 23 |
| `data` | aggregation OR transformation | `analytics_data_aggregation_worker` | 34 |
| `dashboard` | visualization (clear) | `analytics_dashboard_api` | 23 |

---

### Extended Context Catalog

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
- ✅ For complete guide, see [Semantic Shortening Guide](../../guides/SEMANTIC_SHORTENING_GUIDE.md)

---

### Domain Examples per Context

#### Finance Context
- `lending` - P2P loans, microloans
- `crypto` - Cryptocurrency portfolio, trading
- `payments` - Payment processing
- `billing` - Subscription billing
- `trading` - Algorithmic trading

#### Healthcare Context
- `telemedicine` - Online consultations
- `appointment` - Doctor booking
- `mental_health` - Psychological support
- `pharmacy` - Medication management

#### Construction Context
- `house` - Residential building
- `commercial` - Commercial projects
- `renovation` - Remodeling projects
- `material` - Materials management

#### Education Context
- `lms` - Learning management
- `courses` - Online courses
- `webinar` - Webinar platform
- `assessment` - Testing & grading

---

### Function Naming Patterns (4-Part Only)

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

### Service Type Catalog

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

## Section 3: Element-Specific Naming Rules

### Python Classes

| Class Type | Suffix | Pattern | Example |
|------------|--------|---------|---------|
| Service (business logic) | `Service` | `{Noun}Service` | `UserService`, `PaymentService` |
| Repository (data access) | `Repository` | `{Noun}Repository` | `UserRepository`, `OrderRepository` |
| DTO (data transfer) | `DTO` | `{Noun}{Action}DTO` | `UserCreateDTO`, `OrderUpdateDTO` |
| Handler (request handler) | `Handler` | `{Noun}Handler` | `MessageHandler`, `WebhookHandler` |
| Router (API router) | `Router` | `{Noun}Router` | `UserRouter`, `PaymentRouter` |
| Model (domain model) | - | `{Noun}` | `User`, `Order`, `Payment` |
| Exception | `Error` or `Exception` | `{Noun}Error` | `ValidationError`, `NotFoundError` |
| Factory | `Factory` | `{Noun}Factory` | `UserFactory`, `OrderFactory` |
| Middleware | `Middleware` | `{Noun}Middleware` | `AuthMiddleware`, `LoggingMiddleware` |

**Examples**:
```python
# Services
class UserService:
    pass

class PaymentProcessingService:
    pass

# Repositories
class UserRepository:
    pass

class OrderRepository:
    pass

# DTOs
class UserCreateDTO:
    pass

class OrderUpdateDTO:
    pass

# Handlers
class MessageHandler:
    pass

class WebhookHandler:
    pass

# Routers
class UserRouter:
    pass

# Models
class User:
    pass

class Order:
    pass
```

---

### Python Functions

| Function Type | Verb | Pattern | Example |
|--------------|------|---------|---------|
| Retrieval | `get_`, `find_`, `fetch_` | `{verb}_{noun}[_by_{field}]` | `get_user_by_id`, `find_orders_by_status` |
| Creation | `create_`, `add_`, `insert_` | `{verb}_{noun}` | `create_order`, `add_user` |
| Update | `update_`, `modify_`, `change_` | `{verb}_{noun}` | `update_user`, `modify_order_status` |
| Deletion | `delete_`, `remove_` | `{verb}_{noun}` | `delete_user`, `remove_order` |
| Validation | `validate_`, `check_`, `verify_` | `{verb}_{noun}` | `validate_email`, `check_password_strength` |
| Calculation | `calculate_`, `compute_` | `{verb}_{noun}` | `calculate_total_price`, `compute_discount` |
| Communication | `send_`, `notify_`, `publish_` | `{verb}_{noun}[_to_{target}]` | `send_email_to_user`, `notify_admin` |
| Processing | `process_`, `handle_` | `{verb}_{noun}` | `process_payment`, `handle_webhook` |

**Examples**:
```python
# Retrieval
def get_user_by_id(user_id: int) -> User:
    pass

def find_orders_by_status(status: str) -> List[Order]:
    pass

# Creation
def create_order(order_data: OrderCreateDTO) -> Order:
    pass

# Validation
def validate_email(email: str) -> bool:
    pass

# Calculation
def calculate_total_price(items: List[OrderItem]) -> Decimal:
    pass

# Communication
def send_email_to_user(user_id: int, subject: str, body: str) -> None:
    pass
```

---

### Python Variables & Parameters

| Variable Type | Pattern | Example |
|--------------|---------|---------|
| ID reference | `{noun}_id` | `user_id`, `order_id` |
| Boolean flag | `is_{adj}`, `has_{noun}`, `can_{verb}`, `should_{verb}`, `will_{verb}` | `is_active`, `has_permission`, `can_edit`, `should_retry` |
| Timestamp | `{action}_at` | `created_at`, `updated_at`, `deleted_at` |
| Count/Quantity | `{noun}_count` or `num_{noun}` | `retry_count`, `num_attempts` |
| Maximum value | `max_{noun}` | `max_retries`, `max_file_size` |
| Minimum value | `min_{noun}` | `min_password_length` |
| List/Collection | `{noun}s` or `{noun}_list` | `users`, `order_items`, `user_list` |
| Configuration | `{feature}_{setting}` | `database_url`, `api_timeout` |

**Examples**:
```python
# ID references
user_id: int = 123
order_id: UUID = uuid4()

# Boolean flags
is_active: bool = True
has_permission: bool = False

# Timestamps
created_at: datetime = datetime.now()
updated_at: datetime = datetime.now()

# Counts
retry_count: int = 0
num_attempts: int = 3

# Limits
max_retries: int = 5
min_password_length: int = 8

# Collections
users: List[User] = []
order_items: List[OrderItem] = []

# Configuration
database_url: str = "postgresql://..."
api_timeout: int = 30
```

---

### Python Private Members

> **Note**: Standard Python convention, included for completeness.

| Pattern | Use Case | Example |
|---------|----------|---------|
| `_single_leading` | Internal/protected (convention) | `_cache`, `_helper_func()` |
| `__double_leading` | Name mangling (avoid subclass conflicts) | `__private_key` |
| `_trailing_` | Avoid keyword conflicts | `class_`, `type_`, `id_` |
| `__dunder__` | Magic methods (reserved by Python) | `__init__`, `__str__` |

**Rule**: Use `_single_leading` for internal helpers. Avoid `__double` unless needed for name mangling. Never use `__dunder__` for custom names.

---

### Files & Folders

| Element | Pattern | Example |
|---------|---------|---------|
| Python module | `{class_name}.py` in snake_case | `user_service.py`, `order_repository.py` |
| Package folder | `{package_name}/` in snake_case | `user_management/`, `finance_api/` |
| Service folder | `{service_name}/` | `finance_lending_api/` |
| Test file | `test_{module_name}.py` | `test_user_service.py` |
| Config file | Tool-specific | `pyproject.toml`, `.env`, `Dockerfile` |

**File-folder alignment**: Directory name should match Python package name.

**Two common structures**:

```
# Option A: Flat structure (simple services, not distributed as package)
services/
  finance_lending_api/          # Project root = Python package
    __init__.py
    main.py
    domain/
      user_service.py
```

```
# Option B: src layout (distributable packages, testing isolation)
services/
  finance_lending_api/          # Project root (contains pyproject.toml, tests/)
    src/
      finance_lending_api/      # Installable Python package
        __init__.py
        main.py
    tests/
      test_main.py
    pyproject.toml
```

**Use Option A** (flat) for:
- Internal microservices (deployed as Docker containers, not PyPI packages)
- Simple project structure (most cases)

**Use Option B** (src layout) for:
- PyPI packages (libraries distributed via pip)
- Projects with complex test isolation needs (prevents accidental imports of non-installed code)
- Reusable components shared across multiple microservices

---

### Database Elements

| Element | Pattern | Example |
|---------|---------|---------|
| Table | `{plural_noun}` | `users`, `orders`, `order_items` |
| Column | `{noun}[_qualifier]` | `user_id`, `email`, `created_at` |
| Index | `idx_{table}_{column}` | `idx_users_email`, `idx_orders_created_at` |
| Foreign key constraint | `fk_{table}_{ref_table}` | `fk_orders_users`, `fk_order_items_orders` |
| Unique constraint | `uk_{table}_{column}` | `uk_users_email` |
| Primary key | `pk_{table}` (optional, usually auto-generated by DB) | `pk_users` |

**Examples**:
```sql
-- Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_users_email ON users(email);

-- Foreign key
ALTER TABLE orders
ADD CONSTRAINT fk_orders_users
FOREIGN KEY (user_id) REFERENCES users(user_id);

-- Unique constraint
ALTER TABLE users
ADD CONSTRAINT uk_users_email
UNIQUE (email);
```

---

## Section 4: Conversion & Validation

### Development → Production Transformation

**Formula**: `service_name.replace('_', '-')`

When deploying from Docker Compose (underscores) to Kubernetes (hyphens), use automatic conversion:

**Examples**:
```python
import re

def service_to_k8s(service_name: str) -> str:
    """Convert Docker Compose service name to Kubernetes DNS-compliant name.

    Args:
        service_name: Docker Compose service name (e.g., "finance_lending_api")

    Returns:
        Kubernetes-compatible DNS name (e.g., "finance-lending-api")

    Raises:
        ValueError: If conversion results in invalid Kubernetes DNS name

    Examples:
        >>> service_to_k8s("finance_lending_api")
        "finance-lending-api"

        >>> service_to_k8s("Finance_API")
        "finance-api"

        >>> service_to_k8s("_internal_api")
        ValueError: Invalid K8s DNS name: leading/trailing hyphens not allowed
    """
    # 1. Convert to lowercase (K8s requires lowercase)
    name = service_name.lower()

    # 2. Replace underscores with hyphens
    name = name.replace('_', '-')

    # 3. Remove leading/trailing hyphens (invalid in DNS)
    name = name.strip('-')

    # 4. Collapse multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)

    # 5. Validate RFC 1035 DNS label format
    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
        raise ValueError(
            f"Invalid K8s DNS name: '{name}' "
            f"(from '{service_name}'). Must match: [a-z0-9]([-a-z0-9]*[a-z0-9])?"
        )

    # 6. Validate length (max 253 chars for K8s Service name)
    if len(name) > 253:
        raise ValueError(
            f"K8s DNS name too long: {len(name)} chars (max 253). "
            f"Name: '{name}'"
        )

    return name


# Examples
compose_name = "finance_lending_api"
k8s_name = service_to_k8s(compose_name)  # "finance-lending-api"

# Edge cases handled:
service_to_k8s("Finance_API")         # "finance-api" (lowercase)
service_to_k8s("finance__double_api") # "finance-double-api" (collapse hyphens)
# service_to_k8s("_internal_api")     # ValueError: leading hyphen
# service_to_k8s("api_")              # ValueError: trailing hyphen
```

**Service Name Mapping**:
- Code: `finance_lending_api/`
- Docker Compose: `finance_lending_api`
- Kubernetes: `finance-lending-api`
- DNS: `lending-api.finance.example.com`

All names refer to the **same logical service**, just using layer-appropriate separators.

---

### Validation Checklist

- [ ] All Python modules use `snake_case`
- [ ] All database identifiers use `snake_case`
- [ ] Docker Compose service names use `snake_case`
- [ ] Kubernetes manifests use `kebab-case`
- [ ] DNS hostnames use `kebab-case`
- [ ] REST API paths use `kebab-case`
- [ ] Git branches use `kebab-case`
- [ ] Environment variables use `UPPER_SNAKE_CASE`
- [ ] Service names follow 3-part `{context}_{domain}_{type}` (or 4-part when domain ambiguous)
- [ ] Class names have appropriate suffixes (Service, Repository, DTO, Handler, Router)
- [ ] Function names start with appropriate verbs (get_, create_, update_, validate_)
- [ ] No hyphens in Python code
- [ ] No underscores in Kubernetes/DNS names

---

### Common Mistakes to Avoid

❌ **BAD Examples**:
```python
# Hyphens in Python (SyntaxError)
from finance-lending-api import UserService  # ERROR!

# Underscores in Kubernetes
name: finance_lending_api  # Validation error

# Generic class names without suffix
class Data:  # What kind of data?
    pass

# Unclear function names
def process():  # Process what?
    pass

# Mixed separators
service_name = "finance-lending_api"  # Inconsistent
```

✅ **GOOD Examples**:
```python
# Underscores in Python
from finance_lending_api import UserService  # Correct

# Hyphens in Kubernetes
name: finance-lending-api  # Valid

# Descriptive class names with suffix
class UserService:  # Clear business logic service
    pass

# Clear function names
def process_payment(payment_id: int) -> bool:
    pass

# Consistent separators
service_name = "finance_lending_api"  # Consistent underscores
k8s_name = "finance-lending-api"      # Consistent hyphens
```

---

## Section 5: Exceptions & Edge Cases

### Mandatory Tool-Specific Files

Some tools mandate specific naming formats. These are allowed and documented:

- `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`
- `.gitignore`, `.dockerignore`, `.env.example`
- `.pre-commit-config.yaml`, `.github/workflows/*.yml`
- `pyproject.toml`, `requirements.txt`

### Third-Party Package Names

- PyPI packages: `flask-sqlalchemy`, `django-rest-framework` (distribution names)
- Import as: `import flask_sqlalchemy`, `import rest_framework` (Python modules)

### Multi-Feature Services vs Multi-Function Services

⚠️ **CRITICAL DISTINCTION FOR AI**:

**Multi-Feature Service** (ALLOWED - use 3-part naming):
- Single business domain with multiple code features implementing ONE workflow
- Example: `construction_house_bot` (3-part)
  - Features: material calculations, photo uploads, cost tracking
  - Domain: `house` (residential construction projects)
  - Workflow: End-to-end house project management
  - Naming: 3-part because "house project management" is ONE business domain

**Multi-Function Service** (ANTI-PATTERN - split into separate services):
- Multiple unrelated business domains in one service
- Example: ❌ DON'T create `construction_everything_api` that handles:
  - House projects (separate domain)
  - Commercial projects (separate domain)
  - Employee payroll (separate domain)

**Decision Rule**:

```
Ask: "Do these features serve ONE business domain or MULTIPLE domains?"

ONE domain → Use 3-part naming, keep together
MULTIPLE domains → Split into separate services
```

**When to Split a Service**:
1. **Different business domains** (not just different features)
2. **Different teams** need ownership
3. **Independent scaling** required
4. **Service exceeds 5000 lines** of code

**Example - When to Use Generic Terms**:

If you have a legitimate multi-feature service (ONE domain, multiple features), you may use:

| Generic Term | Use When | Example |
|--------------|----------|---------|
| `management` | Full process control for one domain | `construction_house_api` (not `construction_house_management_api`) |
| `platform` | Complete solution for one domain | `education_lms_api` (not `education_platform_api`) |

**Prefer specific domain terms** over generic ones. Use generic terms only when no specific domain word exists.

---

### HTTP Headers

> **Note**: HTTP headers use a different convention (not part of core naming strategy). Included only for Nginx configuration awareness when proxying custom headers.

- **Standard format**: `Title-Case-With-Hyphens` (e.g., `X-Request-ID`, `Content-Type`)
- **Nginx behavior**: Drops underscore headers by default (security feature)
- **Custom headers**: Always use hyphens (RFC 7230 standard)

### Name Length & Kubernetes Limits

**Kubernetes Service Name Limit**: 253 characters (RFC 1035 DNS label standard)

**Framework Compliance**: Our naming patterns are well within limits
- 3-part pattern: 20-27 chars (typical)
- 4-part pattern: 30-35 chars (typical)
- Longest realistic name: ~60 chars (still 193 chars under limit)

**Example of longest realistic name**:
```
enterprise_resource_planning_inventory_management_api  # 52 chars ✓
```

**Conclusion**: Length limits are not a practical concern. Focus on clarity over brevity.

**Version Numbers in Service Names**:
- ❌ **Avoid**: `finance_lending_api_v2` (versions belong in API paths, not service names)
- ✅ **Use**: `/api/v2/lending` (version in URL path)
- **Rationale**: Service name should be stable; API version can evolve independently

**Exception for Blue-Green Deployments**:
- When running v1 and v2 simultaneously during deployment:
  - **Kubernetes labels**: Use `version: v1` and `version: v2` labels (not in service name)
  - **Service names**: Keep stable (`finance-lending-api`)
  - **Deployment names**: Can include version suffix for clarity (`finance-lending-api-v2-deployment`)
  - **Traffic routing**: Use Ingress/Service Mesh to route by API version header/path

### Migration Guide: Old Naming → New Naming

**Scenario**: You have existing services with non-compliant names and want to adopt this convention.

**Approach**:

1. **Create Context Registry First** ([context-registry.md](context-registry.md))
   - Document all existing service contexts
   - Identify conflicts before renaming

2. **Plan Migration**:
   ```python
   # Old naming (before)
   lending_platform_api        # No context, unclear domain
   user_api                    # Too generic
   payment-service             # Hyphen in code layer

   # New naming (after)
   finance_lending_api         # Clear context + domain + type
   user_auth_api               # Specific domain
   finance_payment_api         # Underscore in code layer
   ```

3. **Gradual Migration Strategy**:
   - **Phase 1**: New services use new convention
   - **Phase 2**: Rename services during major version bumps
   - **Phase 3**: Update all references (imports, configs, DNS)

4. **Conversion Script** (for Docker Compose → Kubernetes):
   ```python
   # Use the service_to_k8s function from Section 4
   # Example: finance_lending_api → finance-lending-api
   k8s_name = service_to_k8s("finance_lending_api")
   ```

5. **Update Checklist**:
   - [ ] Python imports (`from old_name import` → `from new_name import`)
   - [ ] Docker Compose service names
   - [ ] Kubernetes manifests (hyphen variant)
   - [ ] Environment variable references
   - [ ] Documentation
   - [ ] CI/CD pipelines
   - [ ] DNS entries (hyphen variant)

**Tip**: Use git grep and IDE refactoring tools to find all references to old service names.

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

**Service Naming**: Follow `{context}_{domain}_{type}` pattern (3-part) by default. Add explicit function (4-part) only when domain is ambiguous. See [Semantic Shortening Guide](../../guides/SEMANTIC_SHORTENING_GUIDE.md) for decision tree.

**Element Naming**: Use appropriate suffixes for classes (Service, Repository, DTO, Handler, Router), verbs for functions (get_, create_, validate_), and descriptive patterns for variables.

**Name Length**: Average 20-27 characters with 3-part formula (no abbreviations needed). 95%+ compatibility with Kubernetes DNS limits.
