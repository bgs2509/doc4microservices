# Production Deployment

Deliver releases safely with predictable pipelines and rollback options.

## Strategy

- Deploy services independently to honour the Improved Hybrid separation (business, data, workers).
- Use blue/green or rolling strategies to minimise downtime.
- Apply database migrations before deploying new service versions.
- Gate production deploys with automated checks (CI status, manual approval when required).

## Automation

- Use Infrastructure as Code (Terraform, Helm) to provision infrastructure.
- Parameterise deployments with environment-specific values stored in secret managers.
- Record deployment metadata (build SHA, version, timestamp) for observability.

## Rollback

- Keep previous container images tagged and ready for immediate rollback.
- Automate rollback scripts that reapply the last known good configuration.
- Document manual steps for database rollbacks when automatic reversal is not feasible.

## Post-Deployment Verification

- Run smoke tests and health checks after rollout.
- Monitor latency, error rate, and saturation for at least one release window.
- Capture incidents and lessons learned in retrospectives.

## Related Documents

- `docs/atomic/infrastructure/deployment/monitoring-setup.md`
- `docs/atomic/architecture/quality-standards.md`
