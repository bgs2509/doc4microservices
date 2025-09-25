# Service Discovery

Ensure services discover one another reliably in every environment.

## Approaches

- **Static configuration** – environment variables or configuration files mapping service names to URLs (suitable for small deployments).
- **DNS-based discovery** – rely on container orchestrators (Kubernetes services, Docker Compose hostnames).
- **Registry-based discovery** – use Consul, etcd, or service meshes when dynamic scaling and health-based routing are required.

## Guidelines

- Reference services by logical names (for example, `DATA_SERVICE_URL`) rather than hard-coded IP addresses.
- Document discovery requirements per environment (local, staging, production).
- Combine discovery with health checks to avoid routing traffic to unhealthy instances.
- Cache discovery results cautiously and honour TTLs.

## Security

- Authenticate with the service registry using mTLS or API tokens.
- Restrict who can register or deregister services to prevent poisoning the registry.

## Related Documents

- `docs/atomic/integrations/cross-service/health-checks.md`
- `docs/atomic/architecture/service-separation-principles.md`
