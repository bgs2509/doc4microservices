# Naming Conventions

## AI Quick Reference

> **LENGTH OPTIMIZATION**: For services with names >30 chars, use [Abbreviations Registry](../../reference/ABBREVIATIONS_REGISTRY.md) to shorten while preserving meaning.

| Element Type | Pattern | Example | Separator |
|--------------|---------|---------|-----------|
| **Service** | `{context}_{domain}_{function}_{type}` | `finance_lending_matching_api` | `_` |
| **Service (Abbreviated)** | `{ctx}_{dom}_{func}_{type}` | `fin_lend_match_api` | `_` |
| **Python Class** | `{Noun}{Suffix}` | `UserService`, `OrderRepository` | - |
| **Python Function** | `{verb}_{noun}[_qualifier]` | `get_user_by_id`, `create_order` | `_` |
| **Python Variable** | `{noun}[_qualifier]` | `user_id`, `max_attempts` | `_` |
| **Python Parameter** | `{noun}[_qualifier]` | `user_id: int`, `is_active: bool` | `_` |
| **Python Constant** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `MAX_RETRIES` | `_` |
| **Python Module/File** | `{class_name}.py` | `user_service.py`, `order_dto.py` | `_` |
| **Folder/Package** | `{service_name}/` | `finance_lending_api/` | `_` |
| **Docker Compose Service** | `{service_name}` | `finance_lending_api` | `_` |
| **Kubernetes Service** | `{service-name}` | `finance-lending-api` | `-` |
| **Database Table** | `{plural_noun}` | `users`, `order_items` | `_` |
| **Database Column** | `{noun}[_qualifier]` | `created_at`, `user_id` | `_` |
| **Env Variable** | `{NOUN}_{QUALIFIER}` | `DATABASE_URL`, `API_KEY` | `_` |
| **REST API Path** | `/{noun}[/{id}]` | `/api/v1/users/{id}` | `-` |
| **Git Branch** | `{type}/{description}` | `feature/user-auth` | `-` |

---

## AI Decision Tree: How to Name Any Element

### Step 1: Identify Element Type

```
Is it a SERVICE?          → Step 2 (Service Formula)
Is it a PYTHON CLASS?     → Step 3 (Class Rules)
Is it a PYTHON FUNCTION?  → Step 4 (Function Rules)
Is it a PYTHON VARIABLE?  → Step 5 (Variable Rules)
Is it a FILE/FOLDER?      → Step 6 (File Rules)
Is it a DATABASE object?  → Step 7 (Database Rules)
Is it INFRASTRUCTURE?     → Step 8 (Infrastructure Rules)
```

### Step 2: Service Formula

**Pattern**: `{context}_{domain}_{function}_{type}`

- **Context**: Business area (finance, healthcare, construction...)
- **Domain**: Subdomain (lending, telemedicine, house...)
- **Function**: Action (matching, tracking, management...)
- **Type**: Tech type (api, worker, bot, gateway...)

**Example**: `finance_lending_matching_api`

### Step 3: Python Class Rules

**Pattern**: `{Noun}{Suffix}`

Choose suffix by purpose:
- Business logic → `Service` (UserService, PaymentService)
- Data access → `Repository` (UserRepository, OrderRepository)
- Data transfer → `DTO` (UserCreateDTO, OrderUpdateDTO)
- Request handling → `Handler` (MessageHandler, WebhookHandler)
- API routing → `Router` (UserRouter, PaymentRouter)
- Domain model → No suffix (User, Order, Payment)

### Step 4: Python Function Rules

**Pattern**: `{verb}_{noun}[_qualifier]`

Common verbs:
- `get_`, `find_`, `fetch_` (retrieval)
- `create_`, `add_` (creation)
- `update_`, `modify_` (modification)
- `delete_`, `remove_` (deletion)
- `validate_`, `check_` (validation)
- `calculate_`, `compute_` (computation)
- `send_`, `notify_` (communication)

**Example**: `get_user_by_id`, `calculate_order_total`

### Step 5: Python Variable/Parameter Rules

**Pattern**: `{noun}[_qualifier]`

Examples:
- `user_id` (ID reference)
- `order_total` (computed value)
- `is_active` (boolean flag)
- `created_at` (timestamp)
- `max_retry_count` (configuration)

### Step 6: File/Folder Rules

- **File**: Match class/module name in snake_case
  - Class `UserService` → file `user_service.py`
- **Folder**: Match service/package name
  - Service `finance_lending_api` → folder `finance_lending_api/`

### Step 7: Database Rules

- **Table**: plural noun in snake_case (`users`, `order_items`)
- **Column**: noun with qualifier (`user_id`, `created_at`)
- **Index**: `idx_{table}_{column}` (`idx_users_email`)
- **Constraint**: `{type}_{table}_{column}` (`fk_orders_user_id`)

### Step 8: Infrastructure Rules

- **Docker Compose**: snake_case with underscores
- **Kubernetes**: kebab-case with hyphens
- **DNS**: kebab-case with hyphens

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
| **Container names (dev)** | `snake_case` (underscore) | Compose v1 compatibility, consistency | `finance_lending_api_1` |
| **Kubernetes services** | `kebab-case` (hyphen) | RFC 1035 compliance, DNS requirement | `finance-lending-api` |
| **DNS hostnames** | `kebab-case` (hyphen) | RFC 1035/1123 standard | `api-service.example.com` |
| **Nginx server_name** | `kebab-case` (hyphen) | DNS hostname validation | `lending.example.com` |
| **Nginx upstreams** | `snake_case` (underscore) | Internal name, matches service names | `upstream finance_lending_api` |
| **REST API paths** | `kebab-case` (hyphen) | SEO-friendly, URL standard | `/api/v1/lending-platform` |
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
- DTOs adopt descriptive suffixes (`...Base`, `...Create`, `...Update`, `...Public`, `...Payload`). Avoid generic names like `DataDTO`.

**PyPI Distribution Names Exception**:
- PyPI package names can use hyphens: `scikit-learn`, `django-rest-framework`
- Import names must use underscores: `import sklearn`, `import rest_framework`
- Prefer underscores in distribution names for consistency: `my_package` over `my-package`

#### Databases

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
- Maintain consistency with Python code layer.
- Never expose internal IDs or enums with hyphens.
- Response payloads use `snake_case` for all keys.

---

### Layer 2: Container Orchestration (Context-Dependent)

#### Development (Docker Compose) - Underscore Preferred

| Component | Convention | Examples |
|-----------|------------|----------|
| Service names | `snake_case` | `finance_lending_api`, `db_postgres_service` |
| Container names | `snake_case` | `finance_lending_api_1`, `redis_cache` |
| Volume names | `snake_case` | `postgres_data`, `redis_cache_data` |
| Network names | `snake_case` | `app_network`, `finance_network` |

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
- Compose v1 uses underscores in generated names (`project_service_1`)
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
| Upstream block names | `snake_case` | `upstream finance_lending_api { ... }` |
| Upstream server hostnames | `kebab-case` | `server finance-lending-api:8000;` |

**Example nginx configuration**:
```nginx
# Upstream name uses underscore (internal, matches Docker Compose)
upstream finance_lending_api {
    server finance-lending-api:8000;  # Server hostname uses hyphen (DNS)
}

# Server block
server {
    listen 80;
    server_name lending.example.com;  # Hyphen (DNS hostname)

    location /api/ {
        proxy_pass http://finance_lending_api;  # Upstream name (underscore OK)
        proxy_set_header Host $host;
    }
}
```

**Rationale**:
- Upstream names are internal identifiers (underscores allowed)
- Server names and hostnames must be DNS-compliant (hyphens only)
- Backend server addresses follow DNS rules

#### REST API Paths

| Component | Convention | Examples |
|-----------|------------|----------|
| URL path segments | `kebab-case` | `/api/v1/lending-platform`, `/user-accounts/{id}` |
| URL slugs | `kebab-case` | `/properties/house-123`, `/blog/my-post-title` |

**Example API endpoints**:
```
GET  /api/v1/lending-platform/{id}
POST /api/v1/user-accounts
GET  /api/v1/payment-history
PUT  /api/v1/tenant-profiles/{id}
```

**Rationale**:
- SEO-friendly (search engines prefer hyphens over underscores)
- URL standard convention (RFC 3986 allows hyphens, underscores less common)
- Better readability in browser address bar

#### Git Branches

| Component | Convention | Examples |
|-----------|------------|----------|
| Feature branches | `kebab-case` | `feature/lending-api`, `feature/user-auth` |
| Bugfix branches | `kebab-case` | `bugfix/fix-login`, `bugfix/calc-error` |
| Release branches | `kebab-case` | `release/v1.2.0`, `release/v2.0.0-beta` |

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
| **Environment variables** | ✅ Required | ❌ Prohibited | - | `[A-Z_][A-Z0-9_]*` |

---

## Section 2: Semantic Naming Patterns

### Service Naming Formula

**Pattern**: `{context}_{domain}_{function}_{type}`

This hierarchical formula creates self-documenting service names:
- **{context}**: Business area (finance, healthcare, construction...)
- **{domain}**: Subdomain within context (lending, telemedicine, house...)
- **{function}**: What the service does (matching, tracking, management...)
- **{type}**: Technical service type (api, worker, bot...)

**Examples**:
- `finance_lending_matching_api` - Finance domain, lending subdomain, matching function, API type
- `healthcare_telemedicine_consultation_api` - Healthcare, telemedicine, consultation, API
- `construction_house_management_bot` - Construction, house, management, Telegram bot

---

### Extended Context Catalog

| Context (Full) | Business Domain | Example Services |
|---------------|-----------------|------------------|
| `finance` | Financial services | `finance_lending_api`, `finance_crypto_portfolio_api` |
| `healthcare` | Medical & health | `healthcare_telemedicine_api`, `healthcare_appointment_api` |
| `construction` | Building & construction | `construction_house_management_bot`, `construction_material_calc_api` |
| `education` | Learning & training | `education_lms_api`, `education_courses_api` |
| `logistics` | Transport & delivery | `logistics_fleet_management_api`, `logistics_delivery_tracking_api` |
| `ecommerce` | Online commerce | `ecommerce_marketplace_api`, `ecommerce_dropshipping_api` |
| `corporate` | Enterprise tools | `corporate_crm_api`, `corporate_hr_recruitment_api` |
| `property_management` | Real estate | `property_management_house_calc_api`, `property_management_tenant_api` |
| `communication` | Messaging & notifications | `communication_notification_worker`, `communication_telegram_bot` |
| `analytics` | Data & reporting | `analytics_reporting_api`, `analytics_dashboard_api` |
| `user_management` | Auth & profiles | `user_management_auth_api`, `user_management_profile_api` |
| `integration` | Third-party APIs | `integration_stripe_api`, `integration_google_api` |
| `environment` | Ecology & monitoring | `environment_emission_tracking_api`, `environment_recycling_api` |

**Naming Strategy**:
- ✅ Use FULL WORDS (not abbreviations) for clarity
- ✅ New projects: always start with full context names
- ⚠️ Abbreviations (fn, ht, log) allowed only if documented in project README

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

### Function Naming Patterns

| Function | Use When | Examples |
|----------|----------|----------|
| `management` | Service handles full process | `construction_house_management_bot`, `corporate_fleet_management_api` |
| `matching` | Service finds pairs/matches | `finance_lending_matching_api`, `logistics_carpool_matching_api` |
| `tracking` | Service monitors/tracks | `logistics_delivery_tracking_api`, `environment_emission_tracking_api` |
| `notification` | Service sends alerts | `communication_email_notification_worker`, `user_management_notification_api` |
| `calculation` | Service computes | `construction_material_calculation_api`, `finance_pricing_calculation_api` |
| `consultation` | Service provides advice | `healthcare_telemedicine_consultation_api` |
| `booking` | Service handles reservations | `healthcare_appointment_booking_api`, `logistics_parking_booking_api` |
| `processing` | Service processes data | `finance_payment_processing_worker` |
| `reporting` | Service generates reports | `analytics_financial_reporting_api` |

---

### Service Type Catalog

| Type | Description | Technology | Example |
|------|-------------|------------|---------|
| `api` | REST API service | FastAPI, Flask | `finance_lending_matching_api` |
| `worker` | Background job processor | Celery, RQ | `finance_payment_processing_worker` |
| `bot` | Chat bot interface | Aiogram, Telegram Bot API | `construction_house_management_bot` |
| `gateway` | API Gateway / proxy | Kong, Nginx | `ecommerce_api_gateway` |
| `stream` | Stream processor | Kafka Streams, Flink | `logistics_tracking_stream_processor` |
| `scheduler` | Task scheduler | APScheduler, Celery Beat | `finance_reporting_scheduler` |
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
| Boolean flag | `is_{adjective}` or `has_{noun}` | `is_active`, `has_permission` |
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

### Files & Folders

| Element | Pattern | Example |
|---------|---------|---------|
| Python module | `{class_name}.py` in snake_case | `user_service.py`, `order_repository.py` |
| Package folder | `{package_name}/` in snake_case | `user_management/`, `finance_api/` |
| Service folder | `{service_name}/` | `finance_lending_api/` |
| Test file | `test_{module_name}.py` | `test_user_service.py` |
| Config file | Tool-specific | `pyproject.toml`, `.env`, `Dockerfile` |

**File-folder alignment**: Directory name should match Python package name:
```
services/
  finance_lending_api/          # Folder (snake_case)
    src/
      finance_lending_api/      # Python package (snake_case)
        __init__.py
        main.py
```

---

### Database Elements

| Element | Pattern | Example |
|---------|---------|---------|
| Table | `{plural_noun}` | `users`, `orders`, `order_items` |
| Column | `{noun}[_qualifier]` | `user_id`, `email`, `created_at` |
| Index | `idx_{table}_{column}` | `idx_users_email`, `idx_orders_created_at` |
| Foreign key constraint | `fk_{table}_{ref_table}` | `fk_orders_users`, `fk_order_items_orders` |
| Unique constraint | `uk_{table}_{column}` | `uk_users_email` |
| Primary key | `pk_{table}` | `pk_users` |

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
# Python conversion
def service_to_k8s(service_name: str) -> str:
    """Convert Docker Compose service name to Kubernetes-compatible name."""
    return service_name.replace('_', '-')

# Examples
compose_name = "finance_lending_api"
k8s_name = service_to_k8s(compose_name)  # "finance-lending-api"
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
- [ ] Service names follow `{context}_{domain}_{function}_{type}` pattern
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

### Multi-Function Services

When a service performs multiple unrelated functions, choose strategy:

#### Strategy A: Generic Function Name (Recommended for Start)

Use broad terms when service handles entire workflow:

| Generic Term | Use When | Example |
|--------------|----------|---------|
| `management` | Full process control | `construction_house_management_bot` |
| `assistant` | Helper/support tool | `finance_personal_assistant_api` |
| `platform` | Complete solution | `education_webinar_platform_api` |
| `hub` | Central aggregator | `corporate_communication_hub_api` |

**Example**: Telegram bot doing calculations + uploads + cost tracking:
```
construction_house_management_bot  ✅
```

#### Strategy B: Split into Microservices

When functions are truly independent (different teams, scaling, deployment):

```
construction_house_calculation_api      # Team A
construction_house_documentation_api    # Team B
construction_house_cost_tracking_api    # Team C
```

**Decision Rule**:
- Start with Strategy A (single service)
- Split (Strategy B) when:
  - Service exceeds 5000 lines of code
  - Different teams need ownership
  - Independent scaling required

---

### HTTP Headers

- Standard format: `X-Request-ID`, `Content-Type`, `Authorization`
- Nginx drops underscore headers by default (security feature)

### Context Code Conflicts Warning

⚠️ **CRITICAL**: Never reuse context names for different meanings across your project.

**❌ BAD Examples (Conflicting Codes)**:
```python
# DON'T DO THIS!
property_management_house_calc_api     # pm = Property Management
project_management_task_tracker_api    # pm = Project Management  ⚠️ CONFLICT!

logistics_delivery_api                 # log = Logistics
observability_log_aggregator_api       # log = Logging  ⚠️ CONFLICT!
```

**✅ GOOD Examples (Unique Contexts)**:
```python
# Use distinct full words
property_management_house_calc_api     # Property Management
project_management_task_tracker_api    # Project Management (different context)

logistics_delivery_api                 # Logistics
observability_logging_aggregator_api   # Observability logging
```

**Best Practice**: Maintain a **Context Registry** document listing all used context names.

---

## Section 6: Name Length Optimization with Abbreviations

### Problem Statement

Long service names can become unwieldy, especially in production environments:

**Examples of excessive length:**
```
property_management_house_calculation_api       (45 chars)
healthcare_telemedicine_consultation_api        (42 chars)
construction_house_documentation_worker         (40 chars)
communication_email_notification_worker         (39 chars)
```

**Issues:**
- Hard to read in logs and monitoring dashboards
- Exceed DNS label length recommendations
- Difficult to type in CLI commands
- Cluttered Kubernetes resource names

### Solution: Standardized Abbreviations

**Target**: Limit each part to **5-6 characters** maximum.

**Formula**:
```
{context}_{domain}_{function}_{type}  →  {ctx}_{dom}_{func}_{type}
```

**Abbreviated examples:**
```
propman_house_calc_api                          (22 chars) ✅ -23 chars
health_telem_conslt_api                         (23 chars) ✅ -21 chars
constr_house_doc_worker                         (23 chars) ✅ -17 chars
comm_email_notif_worker                         (23 chars) ✅ -16 chars
```

### Abbreviation Registry

**📖 Complete catalog**: See **[Abbreviations Registry](../../reference/ABBREVIATIONS_REGISTRY.md)** for:
- Full abbreviation dictionary (context, domain, function)
- Usage rules and consistency guidelines
- Conflict resolution strategies
- Transformation examples
- How to propose new abbreviations

### Quick Abbreviation Reference

**Most common abbreviations:**

| Category | Full | Short | Length |
|----------|------|-------|--------|
| **Context** | finance | `fin` | 3 |
| | healthcare | `health` | 6 |
| | construction | `constr` | 6 |
| | education | `edu` | 3 |
| | logistics | `logist` | 6 |
| | ecommerce | `ecom` | 4 |
| **Domain** | lending | `lend` | 4 |
| | payment | `pay` | 3 |
| | telemedicine | `telem` | 5 |
| | appointment | `appt` | 4 |
| **Function** | management | `mgmt` | 4 |
| | matching | `match` | 5 |
| | notification | `notif` | 5 |
| | calculation | `calc` | 4 |
| | tracking | `track` | 5 |

### When to Abbreviate

**Abbreviate when:**
- ✅ Full service name exceeds **30 characters**
- ✅ Deploying to Kubernetes (production)
- ✅ Service name appears in DNS (external URLs)
- ✅ Team consensus prefers shorter names

**Keep full names when:**
- ❌ Total length < 30 characters (unnecessary optimization)
- ❌ Development/local environment only
- ❌ Code clarity is critical (onboarding new developers)
- ❌ Domain-specific terms don't have standard abbreviations

### Usage Example

**Development environment** (full names for clarity):
```yaml
# docker-compose.yml
services:
  finance_lending_matching_api:
    build: ./services/finance/lending_api
    container_name: finance_lending_matching_api
```

**Production environment** (abbreviated for efficiency):
```yaml
# kubernetes/deployment.yml
apiVersion: v1
kind: Service
metadata:
  name: fin-lend-match-api
  namespace: finance
```

### Transformation Rules

**Automatic conversion** at deployment:
```python
def abbreviate_service_name(full_name: str, registry: dict) -> str:
    """Convert full service name to abbreviated form using registry."""
    parts = full_name.split('_')
    abbreviated = [registry.get(part, part) for part in parts]
    return '_'.join(abbreviated)

# Example
full = "finance_lending_matching_api"
short = abbreviate_service_name(full, ABBREVIATION_REGISTRY)
# Result: "fin_lend_match_api"

# For Kubernetes (hyphen separator)
k8s_name = short.replace('_', '-')
# Result: "fin-lend-match-api"
```

### Validation Checklist

- [ ] Service name > 30 chars → consider abbreviation
- [ ] Check [Abbreviations Registry](../../reference/ABBREVIATIONS_REGISTRY.md) for approved abbreviations
- [ ] Never invent ad-hoc abbreviations (must be documented)
- [ ] Ensure consistency: same abbreviation for same word everywhere
- [ ] Update registry if proposing new abbreviation
- [ ] Test readability with team before committing

### Common Pitfalls

❌ **DON'T**:
```python
# Inconsistent abbreviations
fin_lending_match_api      # "lending" not abbreviated
fin_lnd_match_api          # Wrong abbreviation (use "lend")
finance_lend_match_api     # "finance" not abbreviated

# Ambiguous abbreviations
pm_house_mgmt_api          # "pm" = property or project management?
log_track_api              # "log" = logistics or logging?
```

✅ **DO**:
```python
# Consistent registry-based abbreviations
fin_lend_match_api         # All parts abbreviated correctly
propman_house_calc_api     # Unambiguous "propman" for property_management
logist_deliv_track_api     # Clear "logist" for logistics
```

### Best Practices

1. **Registry First**: Always check the registry before naming
2. **Team Consensus**: Propose abbreviations in PR reviews
3. **Document Everything**: Update registry when adding new abbreviations
4. **Be Consistent**: One word → one abbreviation across entire project
5. **Prioritize Clarity**: If abbreviation is confusing, keep full name

### References

- **[Abbreviations Registry](../../reference/ABBREVIATIONS_REGISTRY.md)** — Complete abbreviation catalog
- **[Service Catalog](../../../README.md#services)** — Current service inventory
- **[Deployment Guide](../../guides/deployment.md)** — Name transformation in CI/CD

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
- Code: `finance_lending_api/`
- Docker Compose: `finance_lending_api`
- Kubernetes: `finance-lending-api`
- DNS: `lending-api.finance.example.com`

All names refer to the **same logical service**, just using layer-appropriate separators.

**Service Naming**: Follow `{context}_{domain}_{function}_{type}` pattern using full words for clarity.

**Element Naming**: Use appropriate suffixes for classes (Service, Repository, DTO, Handler, Router), verbs for functions (get_, create_, validate_), and descriptive patterns for variables.
