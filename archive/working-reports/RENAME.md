# Naming Convention Compliance Analysis & Rename Action Plan

**Project**: doc4microservices framework
**Analysis Date**: 2025-10-02
**Reference Standard**: [docs/atomic/architecture/naming-conventions.md](docs/atomic/architecture/naming-conventions.md)
**Total Files Analyzed**: 199 files across 68 directories

---

## Executive Summary

### Critical Finding: Template Services Violate Framework's Own Naming Rules

After comprehensive analysis of the entire doc4microservices project against the framework's naming conventions, I've identified **one critical violation**: template service names use **generic 2-part naming** instead of the required **3-part `{context}_{domain}_{type}` pattern**.

**Current Template Service Names (NON-COMPLIANT):**

```
api_service           ❌ Missing context and domain
bot_service           ❌ Missing context and domain
worker_service        ❌ Missing context and domain
db_postgres_service   ❌ Missing context
db_mongo_service      ❌ Missing context
```

**According to naming-conventions.md (line 39):**
> Microservice (default) pattern: `{context}_{domain}_{type}`

**Impact:**
- Framework teaches strict rules but violates them in templates
- Users copying templates will perpetuate non-compliant naming
- Creates credibility gap in documentation
- Affects **38+ files** across templates and documentation

**Good News:**
- ✅ All Python code is 100% compliant (classes, functions, variables)
- ✅ All infrastructure naming uses correct separators
- ✅ The violation is concentrated and fixable with find-and-replace

---

## Complete File Inventory

### Files by Category

```
Total Files:     199
Total Dirs:      68

Documentation:   167 markdown files
Templates:       15 config/code files
Scripts:         2 Python files
Configuration:   15 YAML/Docker/Make files
```

### Key Directories

```
/home/bgs/Henry_Bud_GitHub/doc4microservices/
├── docs/                          # 167 markdown files
│   ├── atomic/                    # 154 atomic documentation files
│   ├── guides/                    # 9 guide files
│   ├── quality/                   # 2 QA template files
│   └── reference/                 # 12 reference files
├── templates/                     # Template files
│   ├── infrastructure/            # Docker, configs (9 files)
│   ├── nginx/                     # Nginx configs (5 files)
│   └── services/                  # Service templates (1 dir)
│       └── api_service/           # ❌ NON-COMPLIANT NAME
├── scripts/                       # 2 Python scripts
└── [root files]                   # Config, README (15 files)
```

---

## Naming Violations by Priority

## P0 - CRITICAL: Template Service Names (Must Fix)

### Violation 1: Generic Service Names Lack Context

**Rule Violated**: Section 2 - Microservice Naming Patterns (line 531)
> Primary Pattern (3-part): `{context}_{domain}_{type}`

**Current Violations:**

| Current Name | Parts | Missing Components | Severity |
|--------------|-------|-------------------|----------|
| `api_service` | 2 | context, domain | CRITICAL |
| `bot_service` | 2 | context, domain | CRITICAL |
| `worker_service` | 2 | context, domain | CRITICAL |
| `db_postgres_service` | 3 | context | CRITICAL |
| `db_mongo_service` | 3 | context | CRITICAL |

**Why This Violates the Framework:**

From naming-conventions.md:
- Line 39: "Microservice (default)" pattern is `{context}_{domain}_{type}`
- Line 534: "This hierarchical formula creates self-documenting service names"
- Line 542: "Function words are often redundant when context+domain already imply the action"

**Current template names fail to:**
1. Identify the business context (finance, healthcare, etc.)
2. Specify the domain within that context (lending, telemedicine, etc.)
3. Self-document their purpose

**Example from framework documentation:**
- ✅ Correct: `finance_lending_api` (context=finance, domain=lending, type=api)
- ❌ Wrong: `api_service` (no context, no domain, type=api)

---

### Affected Files: Complete List (38 occurrences)

#### Category 1: Docker Compose Files (3 files)

**File 1: `templates/infrastructure/docker-compose.yml`**

```yaml
# Line 21: depends_on reference
depends_on:
  api_service:           # ❌ Should be: template_business_api

# Line 40: Service definition
services:
  api_service:           # ❌ Should be: template_business_api

# Line 46: Container name
container_name: ${PROJECT_NAME:-myapp}_api_service  # ❌

# Line 54: Service URL
- POSTGRES_SERVICE_URL=http://db_postgres_service:8000  # ❌

# Lines 77-84: Depends on declarations
depends_on:
  db_postgres_service:   # ❌ Should be: template_data_postgres_api
    condition: service_healthy

# Line 88: Volume
- api_logs:/var/log/app  # ❌ Should be: template_business_api_logs

# Line 97: Bot service definition
bot_service:             # ❌ Should be: template_business_bot

# Line 103: Bot container name
container_name: ${PROJECT_NAME:-myapp}_bot_service  # ❌

# Line 141: Worker service definition
worker_service:          # ❌ Should be: template_business_worker

# Line 147: Worker container name
container_name: ${PROJECT_NAME:-myapp}_worker_service  # ❌

# Line 187: Postgres data service definition
db_postgres_service:     # ❌ Should be: template_data_postgres_api

# Line 193: Postgres data service container
container_name: ${PROJECT_NAME:-myapp}_db_postgres_service  # ❌

# Line 222: Mongo data service definition
db_mongo_service:        # ❌ Should be: template_data_mongo_api

# Line 228: Mongo data service container
container_name: ${PROJECT_NAME:-myapp}_db_mongo_service  # ❌

# Lines 451-459: Volume definitions
api_logs:                # ❌ Should be: template_business_api_logs
bot_logs:                # ❌ Should be: template_business_bot_logs
worker_logs:             # ❌ Should be: template_business_worker_logs
postgres_service_logs:   # ❌ Should be: template_data_postgres_api_logs
mongo_service_logs:      # ❌ Should be: template_data_mongo_api_logs
```

**File 2: `templates/infrastructure/docker-compose.dev.yml`**

```yaml
# Line 12: Service override
api_service:             # ❌ Should be: template_business_api

# Line 21: Volume mount
- ./services/api_service/src:/app/src:ro  # ❌ Path reference

# Line 25: Bot service override
bot_service:             # ❌ Should be: template_business_bot

# Line 33: Bot volume mount
- ./services/bot_service/src:/app/src:ro  # ❌ Path reference

# Line 35: Worker service override
worker_service:          # ❌ Should be: template_business_worker

# Line 43: Worker volume mount
- ./services/worker_service/src:/app/src:ro  # ❌ Path reference
```

**File 3: `templates/infrastructure/docker-compose.prod.yml`**

```yaml
# Similar violations in production configuration
# Lines 12, 36, 53: Service definitions
api_service:             # ❌
bot_service:             # ❌
worker_service:          # ❌
```

#### Category 2: Nginx Configuration (2 files)

**File 4: `templates/nginx/conf.d/upstream.conf`**

```nginx
# Line 6: Upstream block name (internal - uses underscore correctly)
upstream api_service {   # ❌ Should be: template_business_api
    least_conn;
    # Line 8: Server address
    server api_service:8000 max_fails=3 fail_timeout=30s;  # ❌
    keepalive 32;
}

# Line 13: Bot upstream
upstream bot_service {   # ❌ Should be: template_business_bot
    # Line 14: Server address
    server bot_service:8000 max_fails=3 fail_timeout=30s;  # ❌
    keepalive 16;
}

# Line 19: Postgres data service upstream
upstream db_postgres_service {  # ❌ Should be: template_data_postgres_api
    # Line 20: Server address
    server db_postgres_service:8000 max_fails=3 fail_timeout=30s;  # ❌
    keepalive 16;
}

# Line 25: Mongo data service upstream
upstream db_mongo_service {  # ❌ Should be: template_data_mongo_api
    # Line 26: Server address
    server db_mongo_service:8000 max_fails=3 fail_timeout=30s;  # ❌
    keepalive 16;
}
```

**File 5: `templates/nginx/conf.d/api-gateway.conf`**

```nginx
# Line 44: Proxy pass to API service
proxy_pass http://api_service;  # ❌ Should be: template_business_api

# Line 77: Another proxy pass
proxy_pass http://api_service;  # ❌

# Line 103: Bot webhook proxy
proxy_pass http://bot_service/webhook;  # ❌ Should be: template_business_bot
```

#### Category 3: Python Configuration (1 file)

**File 6: `templates/services/api_service/src/core/config.py`**

```python
# Line 82-89: Data Service URLs
POSTGRES_SERVICE_URL: str = Field(
    default="http://db_postgres_service:8000",  # ❌ Should be: template_data_postgres_api
    description="PostgreSQL service URL",
)
MONGO_SERVICE_URL: str = Field(
    default="http://db_mongo_service:8000",  # ❌ Should be: template_data_mongo_api
    description="MongoDB service URL",
)
```

#### Category 4: Makefile (1 file)

**File 7: `templates/infrastructure/Makefile`**

```makefile
# Line 61: Directory creation
@mkdir -p services/{api_service,bot_service,worker_service,db_postgres_service,db_mongo_service}  # ❌

# Line 112: Log viewing example
logs: ## Show logs from all services (or specific: make logs SERVICE=api_service)  # ❌

# Line 119-121: Shell access example
shell: ## Open shell in service container (make shell SERVICE=api_service)  # ❌
@if [ -z "$(SERVICE)" ]; then \
    echo "$(RED)Error: SERVICE not specified. Usage: make shell SERVICE=api_service$(RESET)"; \  # ❌

# Line 151-153: Test service example
test-service: ## Run tests for specific service (make test-service SERVICE=api_service)  # ❌
@if [ -z "$(SERVICE)" ]; then \
    echo "$(RED)Error: SERVICE not specified. Usage: make test-service SERVICE=api_service$(RESET)"; \  # ❌
```

#### Category 5: Directory Structure (1 directory)

**File 8: `templates/services/api_service/` (directory name)**

```
Current: templates/services/api_service/  # ❌
Should be: templates/services/template_business_api/  # ✅
```

#### Category 6: CI/CD Workflows (2 files)

**File 9: `templates/ci-cd/.github/workflows/ci.yml`**

```yaml
# Line 87-89: Service matrix
matrix:
  service:
    - api_service      # ❌ Should be: template_business_api
    - bot_service      # ❌ Should be: template_business_bot
    - worker_service   # ❌ Should be: template_business_worker

# Line 128: Conditional check
if: matrix.service == 'api_service'  # ❌
```

**File 10: `templates/ci-cd/.github/workflows/cd.yml`**

```yaml
# Line 42-44: Service matrix
matrix:
  service:
    - api_service      # ❌
    - bot_service      # ❌
    - worker_service   # ❌
```

#### Category 7: Monitoring Configuration (1 file)

**File 11: `templates/infrastructure/monitoring/prometheus/prometheus.yml`**

```yaml
# Line 35: API service job
- job_name: 'api_service'  # ❌ Should be: 'template_business_api'
  static_configs:
    # Line 37: Target
    - targets: ['api_service:8000']  # ❌

# Line 41: Bot service job
- job_name: 'bot_service'  # ❌ Should be: 'template_business_bot'
  static_configs:
    # Line 43: Target
    - targets: ['bot_service:8000']  # ❌

# Line 47: Worker service job
- job_name: 'worker_service'  # ❌ Should be: 'template_business_worker'
  static_configs:
    # Line 49: Target
    - targets: ['worker_service:8000']  # ❌
```

---

## P1 - HIGH: Documentation Examples (Should Fix)

### Violation 2: Documentation Propagates Non-Compliant Names

**Issue**: 36+ documentation files use template service names in examples, teaching users incorrect patterns.

**Affected Documentation Files:**

#### Core Reference Documents (5 files)

1. **`docs/reference/PROJECT_STRUCTURE.md`**
   - Lines 21, 36, 41: Directory structure examples
   - Lines 108-110: Service descriptions
   - Lines 165-182: Docker Compose example
   - **Impact**: PRIMARY structure reference document

2. **`docs/reference/troubleshooting.md`**
   - Line 176: Connection error example
   - Line 186: Service URL example
   - Line 414: Service configuration example
   - **Impact**: Users copy-paste troubleshooting examples

3. **`docs/reference/MATURITY_LEVELS.md`**
   - Lines 71, 136, 219, 320: Project structure examples
   - **Impact**: Maturity level examples show wrong naming

4. **`docs/reference/FAILURE_SCENARIOS.md`**
   - Line 235: Coverage report example
   - **Impact**: Testing examples use wrong names

5. **`docs/reference/AGENT_CONTEXT_SUMMARY.md`**
   - Likely contains service name references
   - **Impact**: AI agent learning examples

#### Implementation Guides (4 files)

6. **`docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md`**
   - Lines 451-464: File path examples
   - Lines 496-498: Command examples
   - Lines 509-511: Test examples
   - **Impact**: CRITICAL - AI agents learn from this

7. **`docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md`**
   - Lines 132, 159, 177, 181: Service structure
   - Lines 266, 269: Implementation examples
   - **Impact**: Primary implementation reference

8. **`docs/guides/DEVELOPMENT_COMMANDS.md`**
   - Lines 127, 154, 387: Command examples
   - **Impact**: Users copy commands directly

9. **`docs/guides/shared_components.md`**
   - Lines 50, 63, 84: Import examples
   - **Impact**: Shared component imports

#### Atomic Documentation (27+ files)

10. **`docs/atomic/services/fastapi/*.md` (11 files)**
    - Multiple service name references
    - **Impact**: FastAPI service templates

11. **`docs/atomic/infrastructure/api-gateway/*.md` (5 files)**
    - Nginx configuration examples
    - **Impact**: Gateway setup instructions

12. **`docs/atomic/infrastructure/configuration/*.md` (4 files)**
    - Configuration examples with service URLs
    - **Impact**: Environment configuration

13. **`docs/atomic/infrastructure/containerization/*.md` (5 files)**
    - Docker Compose examples
    - **Impact**: Container orchestration examples

14. **`docs/atomic/testing/integration-testing/*.md` (5 files)**
    - Service testing examples
    - **Impact**: Testing setup instructions

#### Status and Analysis Documents (3 files)

15. **`TEMPLATES_STATUS.md`**
    - Lines 68, 72, 76, 80: Template progress tracking
    - **Impact**: Template inventory document

16. **`TEMPLATES_UNIVERSALITY_ANALYSIS.md`**
    - Line 102-103: Upstream analysis
    - Lines 186, 192: Solution examples
    - **Impact**: Template analysis document

17. **`UNIVERSAL_TEMPLATES_LIST.md`**
    - Line 169: API service scaffolding note
    - Line 202: Bot service unused example
    - **Impact**: Universal template list

18. **`templates/README.md`**
    - Lines 37, 61-62, 122-123: Service scaffolding
    - Lines 204-206: Progress tracking
    - **Impact**: Template documentation

---

## P2 - COMPLIANT: Python Code & Infrastructure ✅

### Python Code Analysis: 100% Compliant

**Files Analyzed:**
- `scripts/validate_docs.py`
- `templates/services/api_service/src/core/config.py`
- `templates/services/api_service/src/main.py`

#### Class Names ✅

```python
# All use PascalCase with appropriate suffixes
class Settings(BaseSettings):        # ✅ PascalCase, inherits from BaseSettings
class FastAPI:                       # ✅ PascalCase (library class)
```

**Compliance**: Line 726 - `{Noun}{Suffix}` pattern followed correctly

#### Function Names ✅

```python
# All use snake_case with verb prefixes
def get_settings() -> Settings:              # ✅ get_ prefix
def parse_cors_origins() -> list:            # ✅ parse_ prefix
def is_production() -> bool:                 # ✅ is_ prefix (boolean)
def is_development() -> bool:                # ✅ is_ prefix
def create_app() -> FastAPI:                 # ✅ create_ prefix
async def lifespan() -> AsyncGenerator:      # ✅ snake_case
def slugify(text: str) -> str:               # ✅ snake_case
def collect_anchors(path: Path) -> set:      # ✅ collect_ prefix
def iter_links(path: Path) -> Iterable:      # ✅ iter_ prefix
def validate_link() -> list[str]:            # ✅ validate_ prefix
def main() -> int:                           # ✅ snake_case
```

**Compliance**: Line 779 - `{verb}_{noun}[_qualifier]` pattern followed correctly

#### Variable Names ✅

```python
# All use snake_case
settings = get_settings()                    # ✅ snake_case
logger = logging.getLogger(__name__)         # ✅ snake_case
md_file: Path                                # ✅ snake_case
line_number: int                             # ✅ snake_case
anchor_slug: str                             # ✅ snake_case
markdown_files: list                         # ✅ snake_case (plural)
```

**Compliance**: Line 820 - `{noun}[_qualifier]` pattern followed correctly

#### Python Module Names ✅

```python
validate_docs.py                             # ✅ snake_case
config.py                                    # ✅ snake_case
main.py                                      # ✅ snake_case
```

**Compliance**: Line 223 - Modules use `snake_case`

### Infrastructure Naming: 100% Compliant ✅

#### Docker Compose Naming ✅

```yaml
# Layer 1 (Code & Data): Underscores required
services:
  api_service:                               # ✅ Uses underscore (correct for Docker Compose)
container_name: myapp_api_service            # ✅ Uses underscore
volumes:
  postgres_data:                             # ✅ Uses underscore
  api_logs:                                  # ✅ Uses underscore
networks:
  app_network:                               # ✅ Uses underscore
```

**Compliance**: Line 204 - "Docker Compose services: `snake_case` (underscore)"

#### Nginx Naming ✅

```nginx
# Upstream block names: Internal identifier, uses underscore
upstream api_service {                       # ✅ Uses underscore (internal name)
    server api_service:8000;                 # ✅ Server address matches Docker Compose
}
```

**Compliance**: Line 419 - "Upstream block name (internal identifier): `snake_case` (always)"

#### Environment Variables ✅

```bash
DATABASE_URL=...                             # ✅ UPPER_SNAKE_CASE
REDIS_URL=...                                # ✅ UPPER_SNAKE_CASE
API_PORT=8000                                # ✅ UPPER_SNAKE_CASE
```

**Compliance**: Line 277 - "All environment variables: `UPPER_SNAKE_CASE`"

---

## Proposed Solution: Three Naming Options

### Option A: Substitution Variables (Most Flexible)

```
{{context}}_{{domain}}_api
{{context}}_{{domain}}_bot
{{context}}_{{domain}}_worker
{{context}}_data_postgres_api
{{context}}_data_mongo_api
```

**Pros:**
- AI agents can do direct substitution
- Forces users to think about context/domain
- Most educationally valuable

**Cons:**
- Templates won't run without substitution
- Requires additional tooling/documentation
- May confuse manual users

### Option B: "myapp" Context (Minimal Change)

```
myapp_business_api
myapp_business_bot
myapp_business_worker
myapp_data_postgres_api
myapp_data_mongo_api
```

**Pros:**
- Simple, runs out-of-box
- Uses existing PROJECT_NAME variable pattern
- Easy to search-and-replace

**Cons:**
- "myapp" is generic but not clearly a placeholder
- "business" domain is vague
- May not clearly signal "this is a template"

### Option C: "template" Context (RECOMMENDED)

```
template_business_api
template_business_bot
template_business_worker
template_data_postgres_api
template_data_mongo_api
```

**Pros:**
- ✅ Clearly indicates this is a template
- ✅ Follows 3-part pattern exactly
- ✅ "business" domain covers generic business logic
- ✅ "data_postgres" / "data_mongo" are specific domains
- ✅ Easy to search-and-replace: `template_` → `yourcontext_`
- ✅ Templates run out-of-box for testing

**Cons:**
- None significant

**Rationale for "template" context:**
- Makes it obvious these are placeholder names
- "template" is not a business domain, preventing confusion
- Clear migration path: `template_business_api` → `finance_lending_api`

**Rationale for domain names:**
- `business` = generic business logic (API, bot, worker)
- `data_postgres` = PostgreSQL data access domain
- `data_mongo` = MongoDB data access domain

---

## Detailed Rename Action Plan

### Phase 1: Service Renaming

**Mapping Table:**

| Current Name | New Name | Justification |
|--------------|----------|---------------|
| `api_service` | `template_business_api` | context=template, domain=business, type=api |
| `bot_service` | `template_business_bot` | context=template, domain=business, type=bot |
| `worker_service` | `template_business_worker` | context=template, domain=business, type=worker |
| `db_postgres_service` | `template_data_postgres_api` | context=template, domain=data_postgres, type=api |
| `db_mongo_service` | `template_data_mongo_api` | context=template, domain=data_mongo, type=api |

**Note**: Data services are HTTP APIs providing data access, so `type=api` is correct.

### Phase 2: File Updates (Priority Order)

#### Step 1: Create Backup Branch

```bash
git checkout -b feature/rename-template-services
git branch backup/before-rename-$(date +%Y%m%d)
```

#### Step 2: Rename Service Directory

```bash
cd /home/bgs/Henry_Bud_GitHub/doc4microservices/templates/services
mv api_service template_business_api
```

#### Step 3: Update Docker Compose Files (3 files)

**File: `templates/infrastructure/docker-compose.yml`**

Find-and-replace (case-sensitive):
```
api_service           → template_business_api
bot_service           → template_business_bot
worker_service        → template_business_worker
db_postgres_service   → template_data_postgres_api
db_mongo_service      → template_data_mongo_api
api_logs              → template_business_api_logs
bot_logs              → template_business_bot_logs
worker_logs           → template_business_worker_logs
postgres_service_logs → template_data_postgres_api_logs
mongo_service_logs    → template_data_mongo_api_logs
```

**Repeat for:**
- `templates/infrastructure/docker-compose.dev.yml`
- `templates/infrastructure/docker-compose.prod.yml`

#### Step 4: Update Nginx Configuration (2 files)

**File: `templates/nginx/conf.d/upstream.conf`**

Update upstream blocks:
```nginx
upstream template_business_api {
    least_conn;
    server template_business_api:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream template_business_bot {
    server template_business_bot:8000 max_fails=3 fail_timeout=30s;
    keepalive 16;
}

upstream template_data_postgres_api {
    server template_data_postgres_api:8000 max_fails=3 fail_timeout=30s;
    keepalive 16;
}

upstream template_data_mongo_api {
    server template_data_mongo_api:8000 max_fails=3 fail_timeout=30s;
    keepalive 16;
}
```

**File: `templates/nginx/conf.d/api-gateway.conf`**

Update proxy_pass directives:
```nginx
proxy_pass http://template_business_api;
proxy_pass http://template_business_bot/webhook;
```

#### Step 5: Update Python Configuration (1 file)

**File: `templates/services/template_business_api/src/core/config.py`**

```python
POSTGRES_SERVICE_URL: str = Field(
    default="http://template_data_postgres_api:8000",
    description="PostgreSQL service URL",
)
MONGO_SERVICE_URL: str = Field(
    default="http://template_data_mongo_api:8000",
    description="MongoDB service URL",
)
```

#### Step 6: Update Makefile (1 file)

**File: `templates/infrastructure/Makefile`**

Line 61:
```makefile
@mkdir -p services/{template_business_api,template_business_bot,template_business_worker,template_data_postgres_api,template_data_mongo_api}
```

Lines 112, 119-121, 151-153 (examples):
```makefile
logs: ## Show logs from all services (or specific: make logs SERVICE=template_business_api)

shell: ## Open shell in service container (make shell SERVICE=template_business_api)
@if [ -z "$(SERVICE)" ]; then \
    echo "$(RED)Error: SERVICE not specified. Usage: make shell SERVICE=template_business_api$(RESET)"; \

test-service: ## Run tests for specific service (make test-service SERVICE=template_business_api)
@if [ -z "$(SERVICE)" ]; then \
    echo "$(RED)Error: SERVICE not specified. Usage: make test-service SERVICE=template_business_api$(RESET)"; \
```

#### Step 7: Update CI/CD Workflows (2 files)

**File: `templates/ci-cd/.github/workflows/ci.yml`**

Lines 87-89:
```yaml
matrix:
  service:
    - template_business_api
    - template_business_bot
    - template_business_worker
```

Line 128:
```yaml
if: matrix.service == 'template_business_api'
```

**File: `templates/ci-cd/.github/workflows/cd.yml`**

Lines 42-44:
```yaml
matrix:
  service:
    - template_business_api
    - template_business_bot
    - template_business_worker
```

#### Step 8: Update Monitoring Configuration (1 file)

**File: `templates/infrastructure/monitoring/prometheus/prometheus.yml`**

```yaml
- job_name: 'template_business_api'
  static_configs:
    - targets: ['template_business_api:8000']

- job_name: 'template_business_bot'
  static_configs:
    - targets: ['template_business_bot:8000']

- job_name: 'template_business_worker'
  static_configs:
    - targets: ['template_business_worker:8000']
```

#### Step 9: Update Documentation Files (36+ files)

**Global Find-and-Replace** (in all `.md` files):

```bash
# In documentation files only
find docs/ templates/README.md TEMPLATES*.md UNIVERSAL*.md -name "*.md" -type f -exec sed -i '' \
  -e 's/api_service/template_business_api/g' \
  -e 's/bot_service/template_business_bot/g' \
  -e 's/worker_service/template_business_worker/g' \
  -e 's/db_postgres_service/template_data_postgres_api/g' \
  -e 's/db_mongo_service/template_data_mongo_api/g' \
  {} \;
```

**Manual review required for:**
- Context-specific examples (may need domain adjustment)
- Code blocks with custom context/domain
- Examples showing migration from old to new

**Key files to manually review:**
1. `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md` - AI learning examples
2. `docs/reference/PROJECT_STRUCTURE.md` - Primary structure reference
3. `docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md` - Implementation examples
4. `docs/atomic/architecture/naming-conventions.md` - May need template naming note

### Phase 3: Create Migration Documentation

#### Create New File: `docs/guides/TEMPLATE_NAMING_GUIDE.md`

**Content:**

```markdown
# Template Service Naming Guide

## Why Template Names Use `template_` Context

Framework templates use the `template_` context prefix to clearly indicate these are placeholder names that should be replaced with your actual business context.

## Template Service Names

| Template Name | Purpose | Replace With |
|---------------|---------|--------------|
| `template_business_api` | FastAPI REST API | `{yourcontext}_{yourdomain}_api` |
| `template_business_bot` | Aiogram Telegram bot | `{yourcontext}_{yourdomain}_bot` |
| `template_business_worker` | AsyncIO background worker | `{yourcontext}_{yourdomain}_worker` |
| `template_data_postgres_api` | PostgreSQL data service | `{yourcontext}_data_postgres_api` |
| `template_data_mongo_api` | MongoDB data service | `{yourcontext}_data_mongo_api` |

## Renaming Process

### Step 1: Choose Your Context and Domain

**Examples:**
- P2P Lending Platform: `finance` context, `lending` domain → `finance_lending_api`
- Telemedicine Platform: `healthcare` context, `telemedicine` domain → `healthcare_telemedicine_api`
- Construction Bot: `construction` context, `house` domain → `construction_house_bot`

### Step 2: Global Search-and-Replace

```bash
# Replace template_business_api with your service name
find . -name "*.yml" -o -name "*.yaml" -o -name "*.py" -o -name "*.conf" | \
  xargs sed -i '' 's/template_business_api/finance_lending_api/g'
```

### Step 3: Rename Directories

```bash
mv services/template_business_api services/finance_lending_api
```

### Step 4: Update Import Paths

```python
# Update Python imports if any
from services.template_business_api.config import settings
# becomes:
from services.finance_lending_api.config import settings
```

## Validation

After renaming, verify:
- [ ] All service names follow `{context}_{domain}_{type}` pattern
- [ ] Docker Compose services renamed
- [ ] Nginx upstreams updated
- [ ] Directory names match service names
- [ ] Environment variables reference correct services
- [ ] No remaining `template_` references (grep for them)

## Common Examples

### P2P Lending Platform

```
template_business_api     → finance_lending_api
template_business_worker  → finance_lending_worker
template_data_postgres_api → finance_data_postgres_api
```

### Healthcare Telemedicine

```
template_business_api     → healthcare_telemedicine_api
template_business_bot     → healthcare_appointment_bot
template_data_postgres_api → healthcare_data_postgres_api
```

### E-commerce Marketplace

```
template_business_api     → ecommerce_marketplace_api
template_business_worker  → ecommerce_marketplace_worker
template_data_mongo_api   → ecommerce_data_mongo_api
```

## See Also

- [Naming Conventions](../atomic/architecture/naming-conventions.md)
- [Semantic Shortening Guide](SEMANTIC_SHORTENING_GUIDE.md)
- [Context Registry](../atomic/architecture/context-registry.md)
```

#### Update `CLAUDE.md`

Add note about template naming:

```markdown
## Template Service Naming

Template services use the `template_` context prefix:
- `template_business_api` - Generic business API template
- `template_business_bot` - Generic bot template
- `template_business_worker` - Generic worker template

These are placeholder names. When generating code, replace with actual context/domain:
- P2P Lending: `finance_lending_api`
- Telemedicine: `healthcare_telemedicine_api`
- Construction: `construction_house_bot`

See [Template Naming Guide](docs/guides/TEMPLATE_NAMING_GUIDE.md) for details.
```

### Phase 4: Validation

#### Automated Validation Script

Create `scripts/validate_naming.py`:

```python
#!/usr/bin/env python3
"""Validate service naming conventions."""
import re
import sys
from pathlib import Path

VALID_PATTERN = re.compile(r'^[a-z]+_[a-z]+_(api|bot|worker)$')

def check_service_names():
    """Check docker-compose files for valid service names."""
    errors = []

    compose_files = list(Path('templates/infrastructure').glob('docker-compose*.yml'))

    for file in compose_files:
        content = file.read_text()
        # Find service definitions (simple pattern)
        services = re.findall(r'^  ([a-z_]+):', content, re.MULTILINE)

        for service in services:
            if not VALID_PATTERN.match(service) and service not in ['nginx', 'postgres', 'mongodb', 'redis', 'rabbitmq', 'prometheus', 'grafana', 'jaeger']:
                errors.append(f"{file.name}: Invalid service name '{service}'")

    return errors

if __name__ == '__main__':
    errors = check_service_names()
    if errors:
        print("Naming convention violations found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("All service names are valid.")
    sys.exit(0)
```

#### Manual Validation Checklist

- [ ] All template services follow `{context}_{domain}_{type}` pattern
- [ ] No remaining `api_service`, `bot_service`, `worker_service` references
- [ ] Docker Compose service names updated (all 3 files)
- [ ] Nginx upstream names updated
- [ ] Nginx proxy_pass directives updated
- [ ] Python config file updated
- [ ] Makefile updated
- [ ] CI/CD workflows updated
- [ ] Monitoring configs updated
- [ ] Service directory renamed
- [ ] Documentation examples updated
- [ ] Template naming guide created
- [ ] CLAUDE.md updated with template naming note
- [ ] All volumes renamed
- [ ] All container names updated
- [ ] Run `docker-compose config` to validate YAML syntax
- [ ] Run `scripts/validate_naming.py` (after creating it)
- [ ] Search for lingering violations: `grep -r "api_service\|bot_service\|worker_service" templates/ docs/`

### Phase 5: Testing

#### Test 1: Docker Compose Validation

```bash
cd templates/infrastructure
docker-compose config
# Should output valid configuration with no errors
```

#### Test 2: Nginx Configuration Test

```bash
cd templates/nginx
docker build -t test-nginx .
docker run --rm test-nginx nginx -t
# Should output "configuration file is ok"
```

#### Test 3: Python Configuration Test

```bash
cd templates/services/template_business_api
python -m py_compile src/core/config.py
python -m py_compile src/main.py
# Should compile without errors
```

#### Test 4: Documentation Link Check

```bash
python scripts/validate_docs.py
# Should pass all link validations
```

#### Test 5: Search for Violations

```bash
# Should return NO results for template files
grep -r "api_service\|bot_service\|worker_service" templates/ --exclude-dir=.git
```

---

## Summary Statistics

### Naming Compliance Report

| Category | Total | Compliant | Violations | Rate |
|----------|-------|-----------|------------|------|
| **Service Names** | 5 | 0 | 5 | 0% ❌ |
| **Python Classes** | 1 | 1 | 0 | 100% ✅ |
| **Python Functions** | 11 | 11 | 0 | 100% ✅ |
| **Python Variables** | ~50 | ~50 | 0 | 100% ✅ |
| **Python Modules** | 2 | 2 | 0 | 100% ✅ |
| **Folder Names** | 1 | 0 | 1 | 0% ❌ |
| **Docker Services** | 5 | 5* | 0 | 100%* ✅ |
| **Nginx Upstreams** | 7 | 7* | 0 | 100%* ✅ |
| **Documentation** | 167 | ~130 | ~37 | 78% ⚠️ |
| **OVERALL** | 249 | 206 | 43 | 83% |

*Separator usage is compliant; naming pattern compliance is 0%

### Files Requiring Updates

| Priority | Category | Files | Effort |
|----------|----------|-------|--------|
| **P0** | Template configs | 8 | 2 hours |
| **P0** | CI/CD workflows | 2 | 30 min |
| **P0** | Directory rename | 1 | 5 min |
| **P1** | Documentation | 36 | 2 hours |
| **P1** | New guides | 2 | 1 hour |
| **P2** | Testing/validation | - | 1 hour |
| **TOTAL** | | 49+ | **6-8 hours** |

---

## Risk Assessment

### Critical Risks

1. **Framework Credibility** - HIGH RISK
   - Framework teaches naming rules but violates them
   - Users learn incorrect patterns from templates
   - Documentation inconsistency

2. **User Confusion** - MEDIUM RISK
   - Templates show one pattern, rules require another
   - Migration path unclear without guide
   - May perpetuate wrong naming in user projects

### Low Risks

1. **Technical Implementation** - LOW RISK
   - Mostly find-and-replace operations
   - No complex refactoring needed
   - Can be done incrementally

2. **Backward Compatibility** - LOW RISK
   - These are templates, not published packages
   - Users customize templates anyway
   - No API contracts to maintain

### Mitigation Strategies

1. ✅ Create clear migration guide
2. ✅ Add validation scripts
3. ✅ Document template naming conventions
4. ✅ Show examples of proper conversion
5. ✅ Test all configurations before commit

---

## Recommended Timeline

### Week 1: Critical Fixes (P0)
- Day 1: Create backup, rename directory
- Day 2: Update Docker Compose files (all 3)
- Day 3: Update Nginx configs, Python configs
- Day 4: Update Makefile, CI/CD workflows
- Day 5: Testing and validation

### Week 2: Documentation (P1)
- Day 1-2: Update core documentation (5 files)
- Day 3-4: Update atomic documentation (27 files)
- Day 5: Create template naming guide

### Week 3: Polish & Validation
- Day 1: Final testing
- Day 2: Create validation scripts
- Day 3: Update CLAUDE.md and README
- Day 4: Code review
- Day 5: Merge to main

---

## Conclusion

The doc4microservices framework has **excellent Python code compliance** (100%) but a **critical violation in template service naming** (0% pattern compliance). The violation affects 43+ occurrences across templates and documentation.

**The Fix**:
- Rename 5 template services to follow `template_{domain}_{type}` pattern
- Update 49+ files (mostly find-and-replace)
- Create clear migration documentation
- Add validation tooling

**Estimated Effort**: 6-8 hours total

**Priority**: HIGH - Should fix before promoting framework or next major release to maintain credibility and prevent users from learning incorrect patterns.

**Next Steps**:
1. Review and approve this rename plan
2. Choose naming option (Option C recommended)
3. Create feature branch
4. Execute Phase 1-5 of action plan
5. Test and validate
6. Merge to main

---

## Appendix: Quick Reference

### Find-and-Replace Commands

```bash
# Template files (case-sensitive)
find templates/ -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.py" -o -name "*.conf" -o -name "Makefile" \) -exec sed -i '' \
  -e 's/\bapi_service\b/template_business_api/g' \
  -e 's/\bbot_service\b/template_business_bot/g' \
  -e 's/\bworker_service\b/template_business_worker/g' \
  -e 's/\bdb_postgres_service\b/template_data_postgres_api/g' \
  -e 's/\bdb_mongo_service\b/template_data_mongo_api/g' \
  {} \;

# Documentation files
find docs/ -name "*.md" -type f -exec sed -i '' \
  -e 's/\bapi_service\b/template_business_api/g' \
  -e 's/\bbot_service\b/template_business_bot/g' \
  -e 's/\bworker_service\b/template_business_worker/g' \
  -e 's/\bdb_postgres_service\b/template_data_postgres_api/g' \
  -e 's/\bdb_mongo_service\b/template_data_mongo_api/g' \
  {} \;

# Directory rename
mv templates/services/api_service templates/services/template_business_api
```

### Validation Commands

```bash
# Check for remaining violations
grep -r "\bapi_service\b\|\bbot_service\b\|\bworker_service\b" templates/ docs/

# Validate Docker Compose
docker-compose -f templates/infrastructure/docker-compose.yml config

# Validate Nginx
docker run --rm -v $(pwd)/templates/nginx:/etc/nginx:ro nginx nginx -t

# Validate Python syntax
python -m py_compile templates/services/template_business_api/src/**/*.py

# Check documentation links
python scripts/validate_docs.py
```

---

**Document Version**: 1.0
**Last Updated**: 2025-10-02
**Author**: Claude Code Analysis
**Status**: Ready for Review
