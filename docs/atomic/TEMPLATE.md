# {Topic Title}

> **INSTRUCTION**: Replace `{Topic Title}` with the specific topic you are documenting (e.g., "Redis Connection Management", "FastAPI Basic Setup", "Service Separation Principles").

{Brief introduction: 1-3 paragraphs describing what this pattern/concept is and why it matters}

> **INSTRUCTION**: Provide context. Answer: What is this? Why does it exist? When should developers use it?
>
> **Example**: "This guide covers the minimum scaffolding required to spin up a FastAPI business service that conforms to the Improved Hybrid Approach."

---

## {Category-Specific Sections}

> **INSTRUCTION**: Choose appropriate sections based on your document category. See "Category-Specific Section Guide" below for detailed examples per category.

### Quick Section Selector

**For Architecture documents**, use:
- Guiding Rules / Principles
- Responsibility Matrix (if applicable)
- When to Use
- Anti-Patterns to Avoid

**For Service Setup documents** (services/fastapi, services/aiogram, services/asyncio-workers, services/data-services), use:
- Prerequisites
- Project Structure / Project Skeleton
- Dependencies
- Entry Point (with code example)
- Checklist

**For Integration documents** (integrations/redis, integrations/rabbitmq, integrations/http-communication, integrations/cross-service), use:
- Client Construction / Configuration (with code example)
- Best Practices / Guidelines
- Observability (if applicable)
- Testing (if applicable)
- Failure Scenarios (if applicable)

**For Infrastructure documents** (infrastructure/containerization, infrastructure/deployment, infrastructure/api-gateway, infrastructure/databases, infrastructure/configuration), use:
- Structure
- Best Practices
- Configuration Examples (if applicable)

**For Testing documents** (testing/unit-testing, testing/integration-testing, testing/service-testing, testing/end-to-end-testing, testing/quality-assurance), use:
- Setup / Configuration
- Test Patterns / Examples (with code)
- Assertions / Expectations

**For Observability documents** (observability/logging, observability/metrics, observability/tracing, observability/error-tracking, observability/elk-stack), use:
- Configuration
- Implementation Examples
- Best Practices
- Integration with Service Types (if applicable)

**For Database documents** (databases/postgresql, databases/postgresql-advanced), use:
- Setup / Configuration
- Connection Management
- Best Practices
- Performance Considerations

**For Security documents**, use:
- Configuration
- Implementation Examples
- Best Practices
- Threat Mitigation

**For Real-time documents**, use:
- Setup / Configuration
- Implementation Examples
- Connection Management
- Best Practices

**For File Storage documents**, use:
- Configuration
- Upload/Download Patterns
- Best Practices

**For External Integrations documents**, use:
- Authentication / Configuration
- API Client Setup
- Best Practices
- Error Handling

---

## Code Examples (if applicable)

> **INSTRUCTION**: Include practical code examples that demonstrate the concept. Use the CORRECT/INCORRECT pattern to show both best practices and anti-patterns.

```python
# CORRECT: Brief description of correct approach
async def good_example():
    """Docstring explaining what this does and why it's correct."""
    return await some_async_operation()

# INCORRECT: Brief description of incorrect approach (anti-pattern)
def bad_example():
    return sync_operation()  # Why this is wrong: blocks event loop
```

> **TIP**: Code examples should be:
> - Runnable (or nearly runnable with minimal context)
> - Follow naming conventions (snake_case, underscore separators)
> - Include type hints (Python 3.12+ style)
> - Have clear docstrings
> - Show both positive and negative examples when relevant

---

## Related Documents

> **INSTRUCTION**: Link to related atomic documents that provide additional context or related patterns. Always include at least 2-3 related documents. Use relative paths starting with `docs/atomic/`.

- `docs/atomic/{category}/{related-file}.md` — Brief description of what this related doc covers
- `docs/atomic/{category}/{another-related-file}.md` — Brief description of what this related doc covers
- Legacy reference: `docs/legacy/{old-file}.mdc` — (if applicable, when migrating from old documentation)

> **TIP**:
> - Architecture docs → link to service setup docs that implement the principles
> - Service docs → link to integration docs for dependencies (Redis, RabbitMQ, etc.)
> - Integration docs → link to testing docs for testing patterns
> - Testing docs → link to service docs being tested

---

## Category-Specific Section Guide

> **FOR REFERENCE ONLY**: This section provides detailed examples of middle sections commonly used in each category. **Remove this entire section** when creating a real document.

### Architecture Documents

**Purpose**: Define principles, boundaries, and patterns for system-wide concerns.

**Common sections:**

#### ## Guiding Rules / Principles
List 3-7 key principles that govern this architectural decision.

**Example**:
```markdown
## Guiding Rules

1. **Business logic stays in business services.** These services expose HTTP APIs, bot handlers, or background jobs.
2. **Data services own persistence.** Data services wrap PostgreSQL or MongoDB and expose domain-aware HTTP endpoints.
3. **Event loop ownership is explicit.** Each process manages exactly one event loop.
```

#### ## Responsibility Matrix (if applicable)
Show what each service type is responsible for.

**Example**:
```markdown
## Responsibility Matrix

| Concern | Business Service | Data Service | Platform |
|---------|-----------------|--------------|----------|
| Domain logic | ✅ | 🚫 | 🚫 |
| Schema migrations | 🚫 | ✅ | 🚫 |
```

#### ## When to Use
Describe scenarios where this pattern/principle applies.

#### ## Anti-Patterns to Avoid
List common mistakes and why they're problematic.

#### ## Enforcement (if applicable)
How to ensure compliance (CI checks, code reviews, etc.)

**Example files**: `improved-hybrid-overview.md`, `service-separation-principles.md`, `event-loop-management.md`

---

### Service Setup Documents (FastAPI, Aiogram, AsyncIO Workers, Data Services)

**Purpose**: Provide step-by-step setup instructions for bootstrapping a new service.

**Common sections:**

#### ## Prerequisites
List required tools, versions, and prior knowledge.

**Example**:
```markdown
## Prerequisites

- Python 3.12+ with `uv` or `pip` for dependency management
- `src/` layout prepared according to `docs/atomic/architecture/project-structure-patterns.md`
- Shared configuration defined in `src/core/config.py` (Pydantic `BaseSettings`)
```

#### ## Project Structure / Project Skeleton
Show the directory layout with explanations.

**Example**:
```markdown
## Initial Project Structure

\`\`\`
src/
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── health_router.py
├── core/
│   ├── config.py
│   └── logging.py
└── main.py
\`\`\`
```

#### ## Dependencies
Show pyproject.toml or requirements with versions.

**Example**:
```markdown
## Dependencies

\`\`\`toml
[project]
name = "my_fastapi_service"
requires-python = ">=3.12"

[project.dependencies]
fastapi = "^0.111"
uvicorn = "^0.30"
\`\`\`
```

#### ## Entry Point (with code example)
Show the main.py or equivalent with full code.

#### ## Checklist
Provide verification steps to confirm setup is correct.

**Example**:
```markdown
## Startup Checklist

- [ ] Project structure matches the reference layout
- [ ] Logging configured once in `create_app()`
- [ ] `/api/v1/health` endpoint returns static status
- [ ] Uvicorn entry point uses application factory
```

**Example files**: `fastapi/basic-setup.md`, `aiogram/basic-setup.md`, `asyncio-workers/basic-setup.md`

---

### Integration Documents (Redis, RabbitMQ, HTTP, Cross-Service)

**Purpose**: Show how to integrate with external systems or services.

**Common sections:**

#### ## Client Construction / Configuration
Show how to create and configure the client.

**Example**:
```markdown
## Client Construction

\`\`\`python
from redis.asyncio import Redis

def build_redis(url: str) -> Redis:
    return Redis.from_url(
        url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=100,
    )
\`\`\`

- Instantiate the client inside FastAPI lifespan or Aiogram startup
- Store the client in application state (`app.state.redis`)
```

#### ## Best Practices / Guidelines
List 3-7 important guidelines for using this integration.

#### ## Observability (if applicable)
How to add logging, metrics, tracing for this integration.

**Example**:
```markdown
## Observability

- Log connection lifecycle events (`redis_connected`, `redis_disconnected`) with request IDs
- Emit metrics for command durations and error counts
```

#### ## Testing (if applicable)
How to test code that uses this integration.

#### ## Failure Scenarios (if applicable)
Common failure modes and how to handle them.

**Example files**: `redis/connection-management.md`, `rabbitmq/message-publishing.md`, `http-communication/http-client-patterns.md`

---

### Infrastructure Documents (Docker, Kubernetes, Nginx, Configuration, Deployment)

**Purpose**: Explain infrastructure setup, configuration, and deployment patterns.

**Common sections:**

#### ## Structure
Describe the organization of infrastructure configuration files.

**Example**:
```markdown
## Structure

- Define services for each microservice, data store, and supporting dependency
- Use `.env` files for secrets-free configuration
- Configure networks to isolate internal communication (`backend`) from external exposure (`public`)
```

#### ## Best Practices
List 3-7 recommendations for configuring this infrastructure component.

**Example**:
```markdown
## Best Practices

- Set `depends_on` with health checks or wait scripts to avoid race conditions
- Persist stateful data via named volumes; keep them separate per service
- Mirror production environment variables to reduce drift
```

#### ## Configuration Examples (if applicable)
Show example configuration files (docker-compose.yml, Dockerfile, nginx.conf, etc.)

**Example files**: `containerization/docker-compose-setup.md`, `api-gateway/nginx-setup.md`, `deployment/production-deployment.md`

---

### Testing Documents (Unit, Integration, Service, E2E, QA)

**Purpose**: Document testing strategies, patterns, and tools.

**Common sections:**

#### ## Setup / Configuration
How to configure the testing framework.

**Example**:
```markdown
## Configuration

\`\`\`ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts =
    --verbose
    --cov=src
\`\`\`
```

#### ## Test Patterns / Examples
Show common test patterns with code.

**Example**:
```markdown
## Test Patterns

\`\`\`python
import pytest

@pytest.mark.asyncio
async def test_user_creation():
    user = await create_user({"email": "test@example.com"})
    assert user.email == "test@example.com"
\`\`\`
```

#### ## Assertions / Expectations
What to verify in tests.

**Example files**: `unit-testing/pytest-setup.md`, `integration-testing/testcontainers-setup.md`, `service-testing/fastapi-testing-patterns.md`

---

### Observability Documents (Logging, Metrics, Tracing, Error Tracking, ELK)

**Purpose**: Document observability implementation patterns.

**Common sections:**

#### ## Configuration
How to set up the observability tool/pattern.

**Example**:
```markdown
## Configuration

\`\`\`python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)
\`\`\`
```

#### ## Implementation Examples
Show how to use the observability pattern in code.

**Example**:
```markdown
## Log Format

\`\`\`json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "event": "user_created",
  "request_id": "req-123",
  "user_id": "user-456"
}
\`\`\`
```

#### ## Best Practices
Guidelines for effective observability.

**Example**:
```markdown
## Best Practices

- Include request_id in all logs
- Use consistent event names
- Never log sensitive data (passwords, tokens)
```

#### ## Integration with Service Types (if applicable)
How to use this observability pattern in FastAPI, Aiogram, Workers.

**Example files**: `logging/structured-logging.md`, `metrics/prometheus-setup.md`, `tracing/opentelemetry-setup.md`

---

### Database Documents (PostgreSQL, MongoDB)

**Purpose**: Document database setup, connection management, and best practices.

**Common sections:**

#### ## Setup / Configuration
Installation and initial configuration.

#### ## Connection Management
How to create and manage database connections.

#### ## Best Practices
Database-specific recommendations (indexing, transactions, etc.)

#### ## Performance Considerations
Query optimization, connection pooling, etc.

**Example files**: `postgresql/basic-setup.md`, `postgresql-advanced/query-optimization.md`

---

### Security Documents

**Purpose**: Document security patterns and implementations.

**Common sections:**

#### ## Configuration
Security tool/pattern setup.

#### ## Implementation Examples
Code showing security best practices.

#### ## Best Practices
Security guidelines.

#### ## Threat Mitigation
How this pattern mitigates specific threats.

---

### Real-time Documents (WebSocket, SSE, etc.)

**Purpose**: Document real-time communication patterns.

**Common sections:**

#### ## Setup / Configuration
How to set up real-time communication.

#### ## Implementation Examples
WebSocket/SSE code examples.

#### ## Connection Management
Lifecycle, reconnection, heartbeats.

#### ## Best Practices
Guidelines for reliable real-time communication.

---

### File Storage Documents

**Purpose**: Document file upload/download patterns.

**Common sections:**

#### ## Configuration
Storage backend setup (S3, local, etc.)

#### ## Upload/Download Patterns
Code examples for file operations.

#### ## Best Practices
File handling guidelines (validation, size limits, security).

---

### External Integrations Documents

**Purpose**: Document integration with third-party APIs.

**Common sections:**

#### ## Authentication / Configuration
API keys, OAuth setup.

#### ## API Client Setup
Creating HTTP client for the external service.

#### ## Best Practices
Rate limiting, retries, error handling.

#### ## Error Handling
Common API errors and how to handle them.

---

## Validation Checklist

> **INSTRUCTION**: Before publishing, verify your document meets these requirements. Remove this section in final document.

- [ ] H1 title is clear and specific (no placeholders like `{Topic Title}`)
- [ ] Introduction explains "what" and "why" (1-3 paragraphs minimum)
- [ ] At least one category-specific section included
- [ ] Code examples follow CORRECT/INCORRECT pattern (if applicable)
- [ ] Code examples use Python 3.12+ syntax with type hints
- [ ] "Related Documents" section with at least 2-3 links
- [ ] No TODO placeholders remaining
- [ ] No sensitive data (passwords, tokens, real IPs, emails)
- [ ] Follows naming conventions (snake_case for Python, kebab-case for Kubernetes)
- [ ] Links use relative paths (`docs/atomic/...` format)
- [ ] All code examples are properly formatted and indented
- [ ] No grammar/spelling errors in English text
- [ ] Removed "Category-Specific Section Guide" section (it's reference only)
- [ ] Removed "Validation Checklist" section (it's reference only)

---

## Meta Information

**Document Type:** Universal Template for Atomic Documentation
**Applies To:** All `docs/atomic/` documentation across all categories
**Version:** 1.0
**Last Updated:** 2025-01-15
**Maintainer:** Documentation Team

---

## Quick Reference Card

| Your Category | Required Sections | Example File |
|---------------|-------------------|--------------|
| **architecture/** | Rules, Matrix, When to Use, Anti-Patterns | `service-separation-principles.md` |
| **services/*** | Prerequisites, Structure, Dependencies, Entry Point, Checklist | `fastapi/basic-setup.md` |
| **integrations/*** | Configuration, Best Practices, Observability, Testing | `redis/connection-management.md` |
| **infrastructure/*** | Structure, Best Practices, Config Examples | `containerization/docker-compose-setup.md` |
| **testing/*** | Setup, Patterns, Code Examples | `integration-testing/testcontainers-setup.md` |
| **observability/*** | Configuration, Examples, Best Practices | `logging/structured-logging.md` |
| **databases/*** | Setup, Connection Management, Best Practices | `postgresql/basic-setup.md` |
| **security/** | Configuration, Examples, Threat Mitigation | — |
| **real-time/** | Setup, Examples, Connection Management | — |
| **file-storage/** | Configuration, Upload/Download, Best Practices | — |
| **external-integrations/** | Auth, Client Setup, Error Handling | — |
