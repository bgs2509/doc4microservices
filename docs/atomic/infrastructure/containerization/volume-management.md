# Container Volume Management

Persist stateful data with volumes while keeping stateless services disposable.

## Principles

- Use named Docker volumes or Kubernetes PersistentVolumeClaims for databases, queues, and caches.
- Keep volumes per service to avoid cross-service coupling and simplify backups.
- Store configuration templates in images; mount only secrets or environment-specific files.
- Avoid bind mounts in production to prevent drift and permission issues.

## Backups

- Schedule regular backups for persistent volumes (database dumps, snapshot tools).
- Test restoration procedures in staging environments.

## Security

- Restrict volume access to the owning container; drop root privileges to avoid overexposure.
- Encrypt volumes when storing sensitive data (cloud-managed disks, LUKS).

## Related Documents

- `docs/atomic/infrastructure/deployment/production-deployment.md`
- `docs/atomic/services/data-services/postgres-service-setup.md`
