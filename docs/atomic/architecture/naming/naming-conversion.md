# Naming Conversion Utilities

This guide provides utilities and patterns for converting service names between development (Docker Compose) and production (Kubernetes) environments. It ensures consistent name transformation across deployment boundaries.

**Key Principle**: Automate underscore-to-hyphen conversion at deployment. Maintain 1:1 mapping between environments.

---

## Conversion Functions

### Python Implementation

```python
import re
from typing import Dict, List

def service_to_k8s(service_name: str) -> str:
    """Convert Docker Compose service name to Kubernetes DNS-compliant name.

    Args:
        service_name: Docker Compose service name with underscores

    Returns:
        Kubernetes-compatible name with hyphens

    Example:
        >>> service_to_k8s("finance_lending_api")
        "finance-lending-api"
    """
    # Convert to lowercase and replace underscores
    name = service_name.lower().replace('_', '-').strip('-')

    # Remove any duplicate hyphens
    name = re.sub(r'-+', '-', name)

    # Ensure DNS compliance (alphanumeric and hyphens only)
    name = re.sub(r'[^a-z0-9-]', '', name)

    # Kubernetes names must not start/end with hyphen
    name = name.strip('-')

    # Enforce max length (253 chars for DNS)
    if len(name) > 253:
        # Truncate and ensure no trailing hyphen
        name = name[:253].rstrip('-')

    return name


def k8s_to_service(k8s_name: str) -> str:
    """Convert Kubernetes name back to Docker Compose format.

    Args:
        k8s_name: Kubernetes service name with hyphens

    Returns:
        Docker Compose service name with underscores

    Example:
        >>> k8s_to_service("finance-lending-api")
        "finance_lending_api"
    """
    return k8s_name.replace('-', '_')


def validate_service_name(name: str, environment: str = "docker") -> bool:
    """Validate service name for target environment.

    Args:
        name: Service name to validate
        environment: Target environment ('docker' or 'k8s')

    Returns:
        True if valid, False otherwise
    """
    if environment == "docker":
        # Docker Compose: letters, numbers, underscores
        pattern = r'^[a-z][a-z0-9_]*$'
    elif environment == "k8s":
        # Kubernetes: DNS-compliant (lowercase, numbers, hyphens)
        pattern = r'^[a-z][a-z0-9-]*[a-z0-9]$'
        if len(name) > 253:
            return False
    else:
        raise ValueError(f"Unknown environment: {environment}")

    return bool(re.match(pattern, name))


def batch_convert_services(services: List[str],
                          target: str = "k8s") -> Dict[str, str]:
    """Convert multiple service names.

    Args:
        services: List of service names
        target: Target format ('k8s' or 'docker')

    Returns:
        Dictionary mapping original names to converted names
    """
    result = {}
    for service in services:
        if target == "k8s":
            result[service] = service_to_k8s(service)
        elif target == "docker":
            result[service] = k8s_to_service(service)
        else:
            raise ValueError(f"Unknown target: {target}")

    return result
```

### Bash Implementation

```bash
#!/bin/bash

# Convert Docker Compose name to Kubernetes
service_to_k8s() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr '_' '-' | sed 's/^-*//' | sed 's/-*$//'
}

# Convert Kubernetes name to Docker Compose
k8s_to_service() {
    echo "$1" | tr '-' '_'
}

# Validate Kubernetes name
validate_k8s_name() {
    local name="$1"
    if [[ "$name" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] && [ ${#name} -le 253 ]; then
        return 0
    else
        return 1
    fi
}

# Example usage
SERVICE="finance_lending_api"
K8S_NAME=$(service_to_k8s "$SERVICE")
echo "Docker Compose: $SERVICE"
echo "Kubernetes: $K8S_NAME"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Convert service names
        run: |
          # Convert all service names for deployment
          export K8S_LENDING_API=$(echo "finance_lending_api" | tr '_' '-')
          export K8S_PAYMENT_WORKER=$(echo "finance_payment_worker" | tr '_' '-')

          echo "Deploying $K8S_LENDING_API to Kubernetes..."

      - name: Update Kubernetes manifests
        run: |
          sed -i "s/{{SERVICE_NAME}}/$K8S_LENDING_API/g" k8s/deployment.yaml
```

### Helm Values Transformation

```yaml
# values.yaml (Docker Compose names)
services:
  finance_lending_api:
    image: finance_lending_api:latest
    replicas: 3

# values-k8s.yaml (transformed)
services:
  finance-lending-api:
    image: finance-lending-api:latest
    replicas: 3
```

Transform with script:

```python
# transform_values.py
import yaml

def transform_helm_values(input_file, output_file):
    with open(input_file) as f:
        values = yaml.safe_load(f)

    # Transform service names
    transformed = {}
    for key, value in values.get('services', {}).items():
        k8s_name = service_to_k8s(key)
        value['name'] = k8s_name
        transformed[k8s_name] = value

    values['services'] = transformed

    with open(output_file, 'w') as f:
        yaml.dump(values, f)
```

---

## Validation Checklist

### Pre-Deployment Validation

```python
# validate_names.py
def validate_deployment_names(compose_file: str, k8s_dir: str):
    """Validate name consistency between Docker Compose and Kubernetes."""
    errors = []

    # Load Docker Compose services
    with open(compose_file) as f:
        compose = yaml.safe_load(f)

    compose_services = set(compose.get('services', {}).keys())

    # Check Kubernetes manifests
    for k8s_file in Path(k8s_dir).glob('*.yaml'):
        with open(k8s_file) as f:
            manifest = yaml.safe_load(f)

        # Extract service name from metadata
        if manifest.get('kind') in ['Service', 'Deployment']:
            k8s_name = manifest['metadata']['name']
            expected_compose = k8s_to_service(k8s_name)

            if expected_compose not in compose_services:
                errors.append(f"K8s service '{k8s_name}' has no matching "
                            f"Docker Compose service '{expected_compose}'")

    return errors
```

---

## Common Mappings

### Service Name Mappings

| Docker Compose | Kubernetes | DNS Entry |
|----------------|------------|-----------|
| `finance_lending_api` | `finance-lending-api` | `finance-lending-api.finance.svc` |
| `healthcare_telemedicine_api` | `healthcare-telemedicine-api` | `healthcare-telemedicine-api.healthcare.svc` |
| `logistics_fleet_tracking_api` | `logistics-fleet-tracking-api` | `logistics-fleet-tracking-api.logistics.svc` |
| `postgres_db` | `postgres-db` | `postgres-db.default.svc` |
| `redis_cache` | `redis-cache` | `redis-cache.default.svc` |

### Environment Variable Mappings

```bash
# Docker Compose
LENDING_API_URL=http://finance_lending_api:8000
PAYMENT_API_URL=http://finance_payment_worker:8000

# Kubernetes
LENDING_API_URL=http://finance-lending-api.finance.svc:80
PAYMENT_API_URL=http://finance-payment-worker.finance.svc:80
```

---

## Troubleshooting

### Common Issues

1. **Name too long for Kubernetes**
   ```python
   def truncate_k8s_name(name: str, max_length: int = 63) -> str:
       """Truncate name for Kubernetes labels (63 char limit)."""
       if len(name) <= max_length:
           return name
       # Keep prefix and suffix, add hash in middle
       import hashlib
       hash_str = hashlib.md5(name.encode()).hexdigest()[:6]
       keep_chars = max_length - 7  # 6 for hash + 1 for hyphen
       prefix_len = keep_chars // 2
       suffix_len = keep_chars - prefix_len
       return f"{name[:prefix_len]}-{hash_str}-{name[-suffix_len:]}"
   ```

2. **Special characters in names**
   ```python
   def sanitize_name(name: str) -> str:
       """Remove special characters for Kubernetes."""
       # Replace common special chars
       name = name.replace('/', '-')
       name = name.replace('.', '-')
       name = name.replace('@', 'at')
       # Remove any remaining special chars
       return re.sub(r'[^a-z0-9-]', '', name.lower())
   ```

---

## Related Documents

- `./README.md` — Main naming conventions hub
- `naming-infrastructure.md` — Infrastructure naming patterns
- `naming-services.md` — Service naming patterns