# Agent Toolbox

> **Purpose**: Provide a machine-friendly catalog of commands and scripts referenced throughout the framework. Every entry points back to the canonical source in `docs/guides/DEVELOPMENT_COMMANDS.md` or related references.

## Usage Guidelines

1. Treat this file as a lookup table when selecting commands inside the workflow.
2. Do not invent new commands—always reuse the canonical form from `docs/guides/DEVELOPMENT_COMMANDS.md`.
3. Verify prerequisites (environment variables, running containers) before executing a command.
4. When adding new tools, update `docs/INDEX.md` and cross-reference the source documentation.

## Environment & Setup

| Tool / Command | Parameters | Preconditions | Expected Output | When to Use | References |
|----------------|------------|---------------|-----------------|-------------|------------|
| `uv sync --dev` | none | Python >=3.12, `pyproject.toml` present | Dependencies installed with dev extras | Prepare local environment | `docs/guides/DEVELOPMENT_COMMANDS.md#package-management-uv` |
| `cp .env.example .env` | none | `.env.example` available | Local `.env` file created | Initialize environment variables | `docs/guides/DEVELOPMENT_COMMANDS.md#configuration-and-validation` |

## Docker & Services

| Tool / Command | Parameters | Preconditions | Expected Output | When to Use | References |
|----------------|------------|---------------|-----------------|-------------|------------|
| `docker-compose up -d` | optional service list | Docker daemon running | Services started in background | Start full stack for development | `docs/guides/DEVELOPMENT_COMMANDS.md#docker-compose-operations` |
| `docker-compose logs -f <service>` | `<service>` | Service already running | Streaming logs for service | Investigate service behaviour | `docs/guides/DEVELOPMENT_COMMANDS.md#docker-compose-operations` |
| `docker-compose exec <service> bash` | `<service>` | Container running | Shell inside service container | Run service-level diagnostics | `docs/guides/DEVELOPMENT_COMMANDS.md#docker-compose-operations` |
| `docker-compose --profile monitoring up -d` | none | Monitoring profile defined | Observability stack running | Enable monitoring suite | `docs/guides/DEVELOPMENT_COMMANDS.md#observability-operations` |

## Diagnostics & Health Checks

| Tool / Command | Parameters | Preconditions | Expected Output | When to Use | References |
|----------------|------------|---------------|-----------------|-------------|------------|
| `curl http://localhost:8000/health` | none | API service exposed | HTTP 200 with health payload | Confirm business API availability | `docs/guides/DEVELOPMENT_COMMANDS.md#configuration-and-validation` |
| `docker-compose exec postgres pg_isready -U postgres` | none | Postgres container running | Readiness confirmation | Check PostgreSQL health | `docs/guides/DEVELOPMENT_COMMANDS.md#data-service-operations` |
| `docker-compose exec rabbitmq rabbitmqctl list_queues` | none | RabbitMQ running | Queue listing | Inspect broker state | `docs/guides/DEVELOPMENT_COMMANDS.md#observability-operations` |
| `docker stats` | none | Containers running | Live resource metrics | Monitor performance issues | `docs/guides/DEVELOPMENT_COMMANDS.md#troubleshooting-commands` |

## Quality & Testing

| Tool / Command | Parameters | Preconditions | Expected Output | When to Use | References |
|----------------|------------|---------------|-----------------|-------------|------------|
| `uv run ruff check .` | `--fix` (optional) | Dependencies installed | Lint report, optional fixes applied | Enforce style before commit | `docs/guides/DEVELOPMENT_COMMANDS.md#code-quality-commands` |
| `uv run ruff format . --check` | none | Dependencies installed | Formatting check status | Verify formatting without changes | `docs/guides/DEVELOPMENT_COMMANDS.md#code-quality-commands` |
| `uv run mypy .` | none | Dependencies installed | Type-check report | Ensure static typing compliance | `docs/guides/DEVELOPMENT_COMMANDS.md#code-quality-commands` |
| `uv run bandit -r .` | none | Dependencies installed | Security scan report | Detect common security issues | `docs/guides/DEVELOPMENT_COMMANDS.md#code-quality-commands` |
| `uv run pytest --cov=app --cov-report=html --cov-report=xml` | optional `-k`, `-n` | Test suite available | Test results + coverage artefacts | Run tests with coverage before delivery | `docs/guides/DEVELOPMENT_COMMANDS.md#testing-commands` |

## Release & Recovery

| Tool / Command | Parameters | Preconditions | Expected Output | When to Use | References |
|----------------|------------|---------------|-----------------|-------------|------------|
| `docker-compose down && docker-compose up -d` | none | Stack running | Services restarted | Emergency restart of all services | `docs/guides/DEVELOPMENT_COMMANDS.md#emergency-procedures` |
| `docker-compose down -v` | none | Awareness of data loss | Services stopped, volumes removed | Full reset with volume cleanup | `docs/guides/DEVELOPMENT_COMMANDS.md#emergency-procedures` |
| `docker-compose exec postgres pg_dump -U postgres microservices_db > backup.sql` | destination path | Postgres running | SQL dump file | Create database backup | `docs/guides/DEVELOPMENT_COMMANDS.md#emergency-procedures` |

## Troubleshooting Notes

- For detailed remediation steps, always consult `docs/reference/troubleshooting.md`.
- Observability dashboards (Grafana, Jaeger, Kibana, Prometheus) are documented in `docs/guides/DEVELOPMENT_COMMANDS.md#observability-operations`.

## Maintenance

- Align updates with `docs/guides/DEVELOPMENT_COMMANDS.md` whenever commands change.
- Follow formatting rules from `docs/STYLE_GUIDE.md`.
- Update `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md` after modifying this toolbox.
