# Configuration Validation

Validate configuration at startup to prevent runtime surprises.

## Techniques

- Use Pydantic validation to ensure required values are present and typed.
- Perform cross-field checks (e.g., if feature flag enabled, ensure supporting URLs are provided).
- Validate external connectivity (Redis ping, database connection) inside lifespan startup.

## Failure Handling

- Fail fast when configuration is invalid; emit clear error messages in logs and exit with non-zero status.
- Provide remediation hints (`export API_DATA_SERVICE_URL=...`).

## Testing

- Add unit tests for settings validators and edge cases.
- Run smoke tests in CI that load settings from `.env.example` to ensure defaults remain valid.

## Related Documents

- `docs/atomic/infrastructure/configuration/settings-patterns.md`
- `docs/atomic/infrastructure/deployment/ci-cd-patterns.md`
