# Infrastructure Naming Conventions

This guide covers naming patterns for Docker Compose, Kubernetes, Nginx, and other infrastructure components in the doc4microservices framework. It implements a 3-layer separator strategy for smooth development-to-production transitions.

**Key Principle**: Use underscores for development (Docker Compose), hyphens for production (Kubernetes/DNS). Automate conversion at deployment boundary.

---

## 3-Layer Separator Strategy

Different infrastructure layers have different technical requirements for separators:

| Layer | Separator | Reason | Example |
|-------|-----------|--------|---------|
| **Code & Data** | Underscore `_` | Python/SQL requirement | `finance_lending_api` |
| **Container (Dev)** | Underscore `_` | Docker Compose, internal | `finance_lending_api` |
| **Container (Prod)** | Hyphen `-` | Kubernetes DNS requirement | `finance-lending-api` |
| **Network & DNS** | Hyphen `-` | RFC 1035 compliance | `lending-api.finance.svc` |

### Layer Transitions

```
Development              Production
-----------              ----------
finance_lending_api  →   finance-lending-api
(Docker Compose)         (Kubernetes)
```

---

## Docker Compose

### Service Naming

Docker Compose services use **underscores** matching the code layer:

```yaml
# docker-compose.yml
services:
  finance_lending_api:
    build: ./services/finance_lending_api
    container_name: finance_lending_api
    hostname: finance_lending_api
    networks:
      - finance_network

  finance_payment_worker:
    build: ./services/finance_payment_worker
    container_name: finance_payment_worker
    depends_on:
      - finance_lending_api
```

### Network Naming

```yaml
networks:
  finance_network:
    name: finance_network
    driver: bridge

  healthcare_network:
    name: healthcare_network
    driver: bridge
```

### Volume Naming

```yaml
volumes:
  postgres_data:
    name: postgres_data

  redis_data:
    name: redis_data

  rabbitmq_data:
    name: rabbitmq_data
```

### Complete Example

```yaml
version: '3.8'

services:
  # Business services
  finance_lending_api:
    build: ./services/finance_lending_api
    container_name: finance_lending_api
    environment:
      DATABASE_URL: postgresql://user:pass@postgres_db:5432/lending
      REDIS_URL: redis://redis_cache:6379
    depends_on:
      - postgres_db
      - redis_cache
    networks:
      - finance_network

  # Infrastructure services
  postgres_db:
    image: postgres:16
    container_name: postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - finance_network

  redis_cache:
    image: redis:7-alpine
    container_name: redis_cache
    volumes:
      - redis_data:/data
    networks:
      - finance_network

networks:
  finance_network:
    name: finance_network

volumes:
  postgres_data:
  redis_data:
```

---

## Kubernetes

### Service and Deployment Naming

Kubernetes resources use **hyphens** (DNS requirement):

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finance-lending-api
  namespace: finance
  labels:
    app: finance-lending-api
    context: finance
    domain: lending
    type: api
spec:
  selector:
    matchLabels:
      app: finance-lending-api
  template:
    metadata:
      labels:
        app: finance-lending-api
```

### Service Definition

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: finance-lending-api
  namespace: finance
spec:
  selector:
    app: finance-lending-api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
```

### ConfigMap and Secret Naming

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: finance-lending-config
  namespace: finance

# Secret
apiVersion: v1
kind: Secret
metadata:
  name: finance-lending-secret
  namespace: finance
```

### Namespace Organization

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: finance
---
apiVersion: v1
kind: Namespace
metadata:
  name: healthcare
---
apiVersion: v1
kind: Namespace
metadata:
  name: logistics
```

### Label Conventions

```yaml
metadata:
  labels:
    app: finance-lending-api           # Application name
    version: v1.0.0                    # Version
    context: finance                   # Business context
    domain: lending                    # Business domain
    type: api                         # Service type
    environment: production           # Environment
    managed-by: helm                  # Management tool
```

---

## Nginx Configuration

### Upstream Naming

```nginx
# nginx.conf
upstream finance_lending_api {
    server finance_lending_api:8000;
}

upstream healthcare_telemedicine_api {
    server healthcare_telemedicine_api:8000;
}
```

### Server Block Naming

```nginx
server {
    server_name lending-api.finance.example.com;

    location / {
        proxy_pass http://finance_lending_api;
        proxy_set_header X-Service-Name "finance-lending-api";
    }
}
```

### Log File Naming

```nginx
access_log /var/log/nginx/finance-lending-api-access.log;
error_log /var/log/nginx/finance-lending-api-error.log;
```

---

## DNS Naming

### Internal Service Discovery

```
# Kubernetes internal DNS
finance-lending-api.finance.svc.cluster.local
healthcare-telemedicine-api.healthcare.svc.cluster.local

# Docker Compose internal DNS
finance_lending_api
healthcare_telemedicine_api
```

### External Domain Mapping

```
# Production domains
lending-api.finance.example.com      → finance-lending-api
telemedicine-api.healthcare.example.com → healthcare-telemedicine-api

# Staging domains
lending-api.staging.finance.example.com
telemedicine-api.staging.healthcare.example.com
```

---

## Environment Variables

### Naming Pattern

Environment variables use SCREAMING_SNAKE_CASE:

```bash
# Database connections
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Service URLs (internal)
LENDING_API_URL=http://finance_lending_api:8000
PAYMENT_API_URL=http://finance_payment_api:8000

# Service URLs (Kubernetes)
LENDING_API_URL=http://finance-lending-api.finance.svc:80
PAYMENT_API_URL=http://finance-payment-api.finance.svc:80

# Configuration
MAX_CONNECTIONS=100
REQUEST_TIMEOUT=30
ENABLE_DEBUG=false
```

---

## CI/CD Pipeline Naming

### GitHub Actions

```yaml
# .github/workflows/finance-lending-api.yml
name: Finance Lending API CI/CD

jobs:
  test-finance-lending-api:
    name: Test Finance Lending API

  build-finance-lending-api:
    name: Build Finance Lending API

  deploy-finance-lending-api:
    name: Deploy Finance Lending API
```

### Docker Image Tags

```bash
# Pattern: {registry}/{namespace}/{service}:{tag}
myregistry.com/finance/lending-api:latest
myregistry.com/finance/lending-api:v1.0.0
myregistry.com/finance/lending-api:main-abc123
```

---

## Terraform Resource Naming

```hcl
# Terraform resources use underscores
resource "aws_ecs_service" "finance_lending_api" {
  name = "finance-lending-api"  # AWS requires hyphens
  # ...
}

resource "aws_rds_instance" "postgres_lending" {
  identifier = "finance-lending-postgres"
  # ...
}
```

---

## Checklist

- [ ] Docker Compose uses underscores (matches code layer)
- [ ] Kubernetes uses hyphens (DNS compliance)
- [ ] Nginx upstreams use underscores (internal)
- [ ] DNS names use hyphens (RFC compliance)
- [ ] Environment variables use SCREAMING_SNAKE_CASE
- [ ] Labels follow Kubernetes conventions
- [ ] Image tags include namespace and version
- [ ] Terraform resources use appropriate separators

---

## Related Documents

- `./README.md` — Main naming conventions hub
- `naming-conversion.md` — Dev→Prod conversion utilities
- `naming-services.md` — Service naming patterns