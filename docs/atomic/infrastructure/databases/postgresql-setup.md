# PostgreSQL Setup

Provision PostgreSQL instances with repeatable configuration across environments.

## Configuration Checklist

- Use version 15+ (align with `docs/reference/tech_stack.md`).
- Enforce UTF-8 encoding and `UTC` timezone.
- Configure logical separation (one database per data service) to avoid cross-domain coupling.
- Enable SSL/TLS for production connections and manage certificates via secrets.
- Tune parameters based on workload: `max_connections`, `shared_buffers`, `work_mem`, `maintenance_work_mem`.

## Operational Practices

- Provision read replicas when analytical workloads compete with transactional queries.
- Automate backups (physical + logical) and test restoration regularly.
- Monitor with pg_stat_statements and expose metrics through `postgres_exporter`.
- Maintain infrastructure-as-code definitions (Terraform, Ansible) for repeatability.

## Security

- Use dedicated roles per service with least privileges (separate read/write roles when necessary).
- Rotate credentials and store them in secret managers.
- Enforce network policies or security groups to restrict access to trusted services only.

## Related Documents

- `docs/atomic/services/data-services/postgres-service-setup.md`
- `docs/atomic/infrastructure/databases/migrations.md`
