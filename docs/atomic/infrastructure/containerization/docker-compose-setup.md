# Docker Compose Setup

Compose orchestrates local development environments. Keep configuration deterministic and aligned with production topology.

## Structure

- Define services for each microservice, data store, and supporting dependency (Redis, RabbitMQ, PostgreSQL).
- Use `.env` files for secrets-free configuration (ports, credentials, feature toggles).
- Mount source code only for services that require live reload; production builds should copy code during image build.
- Configure networks to isolate internal communication (`backend`) from external exposure (`public`).

## Best Practices

- Set `depends_on` with health checks or wait scripts to avoid race conditions.
- Persist stateful data (PostgreSQL, RabbitMQ) via named volumes; keep them separate per service.
- Mirror production environment variables to reduce drift.
- Keep Compose files under version control and document startup commands in the project README.

## Related Documents

- `docs/atomic/infrastructure/containerization/volume-management.md`
- `docs/atomic/infrastructure/deployment/development-environment.md`
