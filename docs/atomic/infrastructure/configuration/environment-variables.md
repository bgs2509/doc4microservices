# Environment Variables Management

Environment variables provide runtime configuration without rebuilding images.

## Principles

- Define variable names in `Settings` classes and document them in service READMEs.
- Provide `.env.example` files with safe defaults; never commit secrets.
- Names use uppercase snake case (`DATA_SERVICE_URL`, `RABBITMQ_URL`).
- Scope variables per service to avoid implicit coupling.

## Loading Strategy

- Use `pydantic.BaseSettings` or similar to load variables once at startup.
- Support environment prefixes to differentiate services (`API_`, `BOT_`).
- Fail fast when required variables are missing; include clear error messages.

## Environments

- Maintain separate `.env` files for local development vs. production (managed via secret stores).
- In Kubernetes, map environment variables from ConfigMaps (non-sensitive) and Secrets (sensitive).

## Related Documents

- `docs/atomic/infrastructure/configuration/settings-patterns.md`
- `docs/atomic/infrastructure/deployment/development-environment.md`
