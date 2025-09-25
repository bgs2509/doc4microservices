# CI/CD Patterns

Automate build, test, and deployment workflows with consistent pipelines.

## Pipeline Stages

1. **Lint & format** – ruff, mypy, markdownlint.
2. **Unit tests** – FastAPI, Aiogram, workers.
3. **Integration tests** – Testcontainers (databases, Redis, RabbitMQ).
4. **Security scans** – dependency audit, container image scan.
5. **Package & publish** – build container images, push to registry.
6. **Deploy** – trigger environment-specific deploy jobs (staging, production).

## Best Practices

- Fail fast on linting/type issues to shorten feedback loops.
- Cache dependencies between jobs to reduce pipeline time.
- Sign container images and verify signatures before deployment.
- Use trunk-based development with feature branches gated by pull-request checks.
- Store pipeline definitions in the repository (GitHub Actions, GitLab CI, Argo Workflows).

## Observability

- Export pipeline metrics (duration, success rate) to CI dashboards.
- Notify teams via chat/alerts on failures with actionable context.

## Related Documents

- `docs/atomic/infrastructure/deployment/production-deployment.md`
- `docs/atomic/architecture/quality-standards.md`
