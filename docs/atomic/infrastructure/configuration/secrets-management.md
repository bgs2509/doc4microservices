# Secrets Management

Protect credentials, tokens, and certificates across environments.

## Practices

- Store secrets in dedicated secret managers (Vault, AWS Secrets Manager, Kubernetes Secrets) rather than `.env` files.
- Restrict access using least privilege roles; audit secret usage regularly.
- Rotate secrets on a defined cadence; automate rotation when supported.
- Encrypt secrets at rest and in transit.

## Application Loading

- Inject secrets via environment variables or mounted files at runtime.
- Load them using `Settings` classes and keep them out of logs (mask values when logging configuration).
- Provide fallbacks for local development (e.g., `.env.local` stored outside version control).

## Incident Response

- Document revocation steps (invalidate tokens, rotate keys) in runbooks.
- Detect leaked secrets using scanners (Trufflehog, GitGuardian) and fail CI on findings.

## Related Documents

- `docs/atomic/infrastructure/configuration/configuration-validation.md`
- `docs/atomic/infrastructure/deployment/production-deployment.md`
