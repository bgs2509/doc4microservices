#!/usr/bin/env python3
"""
Validate service naming conventions.

Checks that all service names in template files follow the
{context}_{domain}_{type} pattern as specified in:
docs/atomic/architecture/naming-conventions.md

Usage:
    python scripts/validate_naming.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Valid service name pattern: {context}_{domain}_{type}
# Examples: template_business_api, finance_lending_api, healthcare_telemedicine_api
VALID_SERVICE_PATTERN = re.compile(r'^[a-z]+_[a-z_]+_(api|bot|worker|gateway|stream|scheduler|cli|webhook)$')

# Infrastructure services that don't follow the pattern (allowed)
INFRASTRUCTURE_SERVICES = {
    'nginx', 'postgres', 'mongodb', 'redis', 'rabbitmq',
    'prometheus', 'grafana', 'jaeger', 'elasticsearch',
    'logstash', 'kibana', 'filebeat', 'adminer'
}


def check_docker_compose_files() -> List[Tuple[str, str]]:
    """
    Check docker-compose files for valid service names.

    Returns:
        List of (filename, service_name) tuples for invalid services
    """
    errors = []
    compose_dir = Path('templates/infrastructure')

    if not compose_dir.exists():
        return errors

    compose_files = list(compose_dir.glob('docker-compose*.yml'))

    for file in compose_files:
        try:
            content = file.read_text()
        except Exception as e:
            errors.append((file.name, f"Error reading file: {e}"))
            continue

        # Find service definitions (services: section)
        in_services = False
        for line in content.split('\n'):
            stripped = line.strip()

            if stripped.startswith('services:'):
                in_services = True
                continue

            # Check if we've left the services section
            if in_services and line and not line[0].isspace():
                in_services = False

            # Parse service name (2 spaces indented under services:)
            if in_services and line.startswith('  ') and not line.startswith('    '):
                match = re.match(r'^  ([a-z_]+):', line)
                if match:
                    service = match.group(1)

                    # Skip infrastructure services
                    if service in INFRASTRUCTURE_SERVICES:
                        continue

                    # Validate service name
                    if not VALID_SERVICE_PATTERN.match(service):
                        errors.append((file.name, service))

    return errors


def check_nginx_configs() -> List[Tuple[str, str]]:
    """
    Check nginx configuration files for valid upstream names.

    Returns:
        List of (filename, upstream_name) tuples for invalid upstreams
    """
    errors = []
    nginx_dir = Path('templates/nginx/conf.d')

    if not nginx_dir.exists():
        return errors

    for file in nginx_dir.glob('*.conf'):
        try:
            content = file.read_text()
        except Exception as e:
            errors.append((file.name, f"Error reading file: {e}"))
            continue

        # Find upstream blocks
        for match in re.finditer(r'^upstream\s+([a-z_]+)\s*\{', content, re.MULTILINE):
            upstream = match.group(1)

            # Skip known infrastructure upstreams
            if upstream in INFRASTRUCTURE_SERVICES or upstream.endswith('_management'):
                continue

            # Validate upstream name
            if not VALID_SERVICE_PATTERN.match(upstream):
                errors.append((file.name, upstream))

    return errors


def check_makefile() -> List[Tuple[str, str]]:
    """
    Check Makefile for service name references.

    Returns:
        List of (filename, service_name) tuples for issues found
    """
    errors = []
    makefile = Path('templates/infrastructure/Makefile')

    if not makefile.exists():
        return errors

    try:
        content = makefile.read_text()
    except Exception as e:
        return [('Makefile', f"Error reading file: {e}")]

    # Look for mkdir commands creating service directories
    for match in re.finditer(r'services/\{([^}]+)\}', content):
        services = match.group(1).split(',')
        for service in services:
            service = service.strip()
            if service and not VALID_SERVICE_PATTERN.match(service):
                errors.append(('Makefile', service))

    return errors


def main() -> int:
    """Run all naming validation checks."""
    print("🔍 Validating service naming conventions...")
    print()

    all_errors = []

    # Check Docker Compose files
    print("Checking Docker Compose files...")
    compose_errors = check_docker_compose_files()
    if compose_errors:
        all_errors.extend([('Docker Compose', f, s) for f, s in compose_errors])
    else:
        print("  ✅ All Docker Compose service names are valid")

    # Check Nginx configs
    print("Checking Nginx configurations...")
    nginx_errors = check_nginx_configs()
    if nginx_errors:
        all_errors.extend([('Nginx Config', f, s) for f, s in nginx_errors])
    else:
        print("  ✅ All Nginx upstream names are valid")

    # Check Makefile
    print("Checking Makefile...")
    make_errors = check_makefile()
    if make_errors:
        all_errors.extend([('Makefile', f, s) for f, s in make_errors])
    else:
        print("  ✅ Makefile service references are valid")

    # Report results
    print()
    if all_errors:
        print("❌ Naming convention violations found:")
        print()
        for category, filename, service in all_errors:
            print(f"  [{category}] {filename}: '{service}'")
            print(f"    ↳ Must follow pattern: {{context}}_{{domain}}_{{type}}")
        print()
        print(f"Total violations: {len(all_errors)}")
        print()
        print("Expected pattern examples:")
        print("  ✅ template_business_api (context=template, domain=business, type=api)")
        print("  ✅ finance_lending_api (context=finance, domain=lending, type=api)")
        print("  ✅ healthcare_telemedicine_bot (context=healthcare, domain=telemedicine, type=bot)")
        print()
        print("See docs/atomic/architecture/naming-conventions.md for details")
        return 1
    else:
        print("✅ All service names follow naming conventions!")
        print()
        print("Pattern: {context}_{domain}_{type}")
        print("Examples: template_business_api, finance_lending_api, healthcare_telemedicine_bot")
        return 0


if __name__ == "__main__":
    sys.exit(main())
