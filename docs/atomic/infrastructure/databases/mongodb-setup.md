# MongoDB Setup

Prepare MongoDB clusters for document-centric data services.

## Configuration Checklist

- Use MongoDB 6.0+ with replica sets to support transactions when required.
- Enable authentication (`SCRAM-SHA-256`) and enforce TLS for production traffic.
- Configure WiredTiger cache size to ~50% of RAM, adjusting for workload.
- Create separate databases per bounded context to avoid collection leakage.
- Define indexes ahead of time and manage them via migrations/startup scripts.

## Operational Practices

- Enable periodic backups (mongodump or continuous backup services) and test restores.
- Monitor cluster health (replica lag, cache usage, slow queries) via MongoDB Exporter or Atlas metrics.
- Adjust connection limits to match driver pool sizes.

## Security

- Restrict network access with firewalls or security groups.
- Rotate credentials using secret managers; avoid embedding passwords in configs.
- Enable auditing if regulatory requirements apply.

## Related Documents

- `docs/atomic/services/data-services/mongo-service-setup.md`
- `docs/atomic/infrastructure/databases/performance-optimization.md`
