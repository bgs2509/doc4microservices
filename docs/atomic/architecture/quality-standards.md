# Quality Standards

Quality is enforced through automated gates and manual reviews. This document summarises non-negotiable expectations for services built on the platform.

## Principles

- **Shift left** – write tests alongside implementation and run them locally before raising a merge request.
- **Automation first** – linting, type checking, security scans, and tests run automatically in CI.
- **Observable outcomes** – every release must provide health checks, metrics, and structured logs.
- **Documentation parity** – update relevant guides whenever behaviour changes.

## Mandatory Checks

| Category | Tooling | Requirement |
|----------|---------|-------------|
| Linting | `ruff` (python), `markdownlint` (docs) | Zero lint errors. |
| Typing | `mypy` or `pyright` | No type regressions; strict mode for new modules. |
| Security | `bandit`, dependency scanners | No high/critical findings without mitigation. |
| Tests | `pytest` (unit/integration/e2e) | 100% coverage for new/changed code; critical paths always covered. |
| Docs | Link checker, spell checker (optional) | No broken links; follow `docs/STYLE_GUIDE.md`. |

## Test Expectations

- **Unit tests** validate domain logic and application services with mocked ports.
- **Integration tests** run against real dependencies via Testcontainers (PostgreSQL, MongoDB, Redis, RabbitMQ).
- **Service tests** cover HTTP and messaging interfaces end-to-end.
- **E2E tests** ensure critical user journeys remain functional.
- Mock external HTTP calls using `respx` or similar libraries to keep tests deterministic.

## Release Checklist

1. CI pipeline green with all mandatory jobs.
2. Manual review performed by at least one domain expert.
3. OpenAPI schema updated (FastAPI services) and published.
4. Changelog or release notes summarise functional impact.
5. Observability dashboards updated when metrics or logs change.

## Incident Prevention

- Use feature flags for risky changes and provide rollback instructions.
- Monitor release metrics (error rate, latency, saturation) for at least one hour after deployment.
- Capture post-release validation steps in the team runbook.

## Documentation Requirements

- Reflect service changes in `docs/atomic/services/*` and `docs/INDEX.md`.
- Archive superseded rules in `docs/legacy/` and note the replacement file.
- Keep README files concise but accurate: include run/test/build commands and links to relevant atomic documents.

## Related Documents

- `docs/atomic/testing/*`
- `docs/atomic/observability/*`
- `docs/atomic/architecture/service-separation-principles.md`
