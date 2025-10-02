# Migration Guide: 4-Part to 3-Part Service Names

> **Purpose**: Step-by-step guide for migrating existing services from 4-part naming (`{context}_{domain}_{function}_{type}`) to semantic 3-part formula (`{context}_{domain}_{type}`).

## Table of Contents

- [Overview](#overview)
- [When to Migrate](#when-to-migrate)
- [When NOT to Migrate](#when-not-to-migrate)
- [Risk Assessment](#risk-assessment)
- [Migration Process](#migration-process)
- [Automated Tools](#automated-tools)
- [Rollback Procedures](#rollback-procedures)
- [Case Studies](#case-studies)

---

## Overview

### What is Changing?

**From**: 4-part verbose names with redundant function words
```python
finance_lending_matching_api            # 28 chars
finance_payment_processing_worker       # 33 chars
healthcare_telemedicine_consultation_api  # 42 chars
```

**To**: 3-part semantic names where function is implied
```python
finance_lending_api            # 19 chars (-9 chars, -32%)
finance_payment_worker         # 22 chars (-11 chars, -33%)
healthcare_telemedicine_api    # 27 chars (-15 chars, -36%)
```

### Migration Goals

- ✅ Reduce average service name length by 30-40%
- ✅ Improve Kubernetes DNS compatibility (95%+ <30 chars)
- ✅ Maintain 100% code readability (no abbreviations)
- ✅ Zero downtime during migration
- ✅ Preserve all integrations and dependencies

---

## When to Migrate

### ✅ Good Candidates for Migration

**Priority 1: Long Names (>35 chars)**
```python
# High priority - exceeds Kubernetes recommendations:
property_management_house_calculation_api       (45 chars) → property_mgmt_house_api (23 chars)
healthcare_telemedicine_consultation_api        (42 chars) → healthcare_telemedicine_api (27 chars)
communication_email_notification_worker         (39 chars) → communication_email_worker (26 chars)
```

**Priority 2: Redundant Function Words**
```python
# Function is obvious from context+domain:
finance_lending_matching_api            → finance_lending_api
finance_payment_processing_worker       → finance_payment_worker
construction_house_management_bot       → construction_house_bot
```

**Priority 3: Team Consensus**
```python
# Team agrees 3-part is clear:
analytics_dashboard_visualization_api   → analytics_dashboard_api
education_courses_enrollment_api        → education_courses_api
```

---

## When NOT to Migrate

### ❌ Bad Candidates for Migration

**Case 1: Domain is Ambiguous**
```python
# ❌ DON'T migrate - function provides critical clarity:
logistics_fleet_tracking_api            # Tracking vs management vs maintenance
analytics_reporting_generation_api      # Generation vs querying
communication_notification_delivery_worker  # Delivery vs scheduling
```

**Case 2: External Integrations**
```python
# ❌ DON'T migrate - external services use current name:
integration_stripe_payment_webhook      # Stripe configured with this webhook URL
integration_google_auth_callback_api    # Google OAuth redirect configured
```

**Case 3: Production with High Traffic**
```python
# ❌ DON'T migrate - too risky:
user_management_auth_validation_api     # 1M requests/day, critical path
finance_payment_processing_worker       # Handles $10M/day transactions
```

**Case 4: Recently Deployed (<1 month)**
```python
# ❌ WAIT - let it stabilize first:
new_service_just_deployed_api           # Wait 1 month before refactoring
```

---

## Risk Assessment

### Risk Matrix

| Factor | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|-----------|
| **Traffic** | <1k req/day | 1k-100k req/day | >100k req/day |
| **External Deps** | 0 external | 1-3 external | >3 external |
| **Age** | <3 months | 3-12 months | >12 months |
| **Team Familiarity** | New service | Active development | Legacy/stable |
| **Name Length** | >40 chars | 30-40 chars | <30 chars |
| **Function Redundancy** | Obvious | Somewhat clear | Critical clarity |

**Decision Rules:**
- **0-2 High Risk factors** → ✅ Safe to migrate
- **3-4 High Risk factors** → ⚠️ Migrate with caution
- **5+ High Risk factors** → ❌ Don't migrate

### Example Assessments

```python
# Example 1: finance_payment_processing_worker
Risk Assessment:
- Traffic: 50k req/day (Medium)
- External Deps: 2 (Stripe, internal) (Medium)
- Age: 18 months (High)
- Team Familiarity: Active dev (Medium)
- Name Length: 33 chars (Medium)
- Function Redundancy: Obvious (worker=processing) (Low)

Total High Risk: 1
Decision: ✅ Safe to migrate


# Example 2: user_management_auth_validation_api
Risk Assessment:
- Traffic: 1M req/day (High)
- External Deps: 5 (OAuth providers) (High)
- Age: 36 months (High)
- Team Familiarity: Legacy (High)
- Name Length: 37 chars (Medium)
- Function Redundancy: Validation is critical (High)

Total High Risk: 5
Decision: ❌ Don't migrate
```

---

## Migration Process

### Phase 1: Planning (Day 1)

#### Step 1.1: Identify Candidates

```bash
#!/bin/bash
# find_migration_candidates.sh

echo "Finding services with >30 char names..."

find services/ -maxdepth 1 -type d | while read dir; do
    service_name=$(basename "$dir")
    char_count=${#service_name}

    if [ $char_count -gt 30 ]; then
        echo "$char_count chars: $service_name"
    fi
done | sort -rn

# Example output:
# 45 property_management_house_calculation_api
# 42 healthcare_telemedicine_consultation_api
# 39 communication_email_notification_worker
```

#### Step 1.2: Apply Decision Tree

```python
from typing import Tuple

def assess_migration(service_name: str) -> Tuple[bool, str]:
    """
    Assess if service should migrate to 3-part naming.

    Returns:
        (should_migrate: bool, reason: str)
    """
    parts = service_name.split('_')

    if len(parts) != 4:
        return False, "Not a 4-part service name"

    context, domain, function, type_ = parts

    # Check if function is redundant
    if is_function_implied(context, domain, type_):
        return True, f"Function '{function}' is implied by {domain}+{type_}"

    # Check if domain is ambiguous
    if is_domain_ambiguous(context, domain):
        return False, f"Domain '{domain}' is ambiguous without function"

    # Check name length
    if len(service_name) > 35:
        return True, f"Name too long ({len(service_name)} chars)"

    return False, "No clear benefit from migration"


# Example usage:
assess_migration("finance_lending_matching_api")
# Returns: (True, "Function 'matching' is implied by lending+api")

assess_migration("logistics_fleet_tracking_api")
# Returns: (False, "Domain 'fleet' is ambiguous without function")
```

#### Step 1.3: Create Migration Plan

```markdown
# Migration Plan: finance_payment_processing_worker

## Service Details
- Current Name: `finance_payment_processing_worker`
- New Name: `finance_payment_worker`
- Reason: "processing" is implied by "worker" type
- Length Reduction: 33 → 22 chars (-33%)

## Risk Assessment
- Traffic: 50k req/day (Medium Risk)
- External Deps: 2 services (Medium Risk)
- Age: 18 months (High Risk)
- Total High Risk: 1 ✅

## Dependencies
- Internal: finance_lending_api, analytics_reporting_api
- External: Stripe webhook, internal monitoring

## Migration Steps
1. Create new service name alias in DNS
2. Update inter-service communication configs
3. Deploy with both names active (blue-green)
4. Update dependent services
5. Monitor for 24 hours
6. Deprecate old name
7. Remove old name after 1 week

## Rollback Plan
- Revert DNS alias
- Restore old service name
- Estimated rollback time: 15 minutes

## Success Criteria
- Zero errors in logs
- All dependent services connecting successfully
- External webhooks functioning
```

---

### Phase 2: Preparation (Day 2)

#### Step 2.1: Backup Current State

```bash
#!/bin/bash
# backup_before_migration.sh

SERVICE_NAME="$1"
BACKUP_DIR="./migration_backups/$(date +%Y%m%d_%H%M%S)_${SERVICE_NAME}"

mkdir -p "$BACKUP_DIR"

# Backup service directory
cp -r "services/$SERVICE_NAME" "$BACKUP_DIR/service"

# Backup configs
cp docker-compose.yml "$BACKUP_DIR/"
cp -r kubernetes/ "$BACKUP_DIR/"

# Backup inter-service configs
find services/ -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \
    | xargs grep -l "$SERVICE_NAME" \
    | xargs cp --parents -t "$BACKUP_DIR/"

echo "✅ Backup created: $BACKUP_DIR"
```

#### Step 2.2: Update Documentation

```markdown
# MIGRATION_LOG.md

## 2025-01-02: finance_payment_processing_worker → finance_payment_worker

### Context
Migrating to 3-part semantic naming to reduce length and improve clarity.

### Changes
- Service name: `finance_payment_processing_worker` → `finance_payment_worker`
- Folder: `services/finance_payment_processing_worker/` → `services/finance_payment_worker/`
- Python package: `finance_payment_processing_worker` → `finance_payment_worker`
- Docker Compose: `finance_payment_processing_worker` → `finance_payment_worker`
- Kubernetes: `finance-payment-processing-worker` → `finance-payment-worker`

### Timeline
- 2025-01-02 10:00: Migration started
- 2025-01-02 12:00: Blue-green deployment complete
- 2025-01-03 12:00: Monitoring period ends
- 2025-01-09 12:00: Old name deprecated

### Rollback Plan
See `migration_backups/20250102_100000_finance_payment_processing_worker/ROLLBACK.md`
```

---

### Phase 3: Execution (Day 3-4)

#### Step 3.1: Rename Service Files

```bash
#!/bin/bash
# rename_service_files.sh

OLD_NAME="$1"
NEW_NAME="$2"

echo "Renaming: $OLD_NAME → $NEW_NAME"

# 1. Rename service directory
mv "services/$OLD_NAME" "services/$NEW_NAME"
echo "✅ Renamed service directory"

# 2. Rename Python package
mv "services/$NEW_NAME/src/$OLD_NAME" "services/$NEW_NAME/src/$NEW_NAME"
echo "✅ Renamed Python package"

# 3. Update pyproject.toml
sed -i "s/name = \"$OLD_NAME\"/name = \"$NEW_NAME\"/g" \
    "services/$NEW_NAME/pyproject.toml"
echo "✅ Updated pyproject.toml"

# 4. Update __init__.py imports
find "services/$NEW_NAME" -name "*.py" -exec sed -i \
    "s/from $OLD_NAME/from $NEW_NAME/g" {} +
find "services/$NEW_NAME" -name "*.py" -exec sed -i \
    "s/import $OLD_NAME/import $NEW_NAME/g" {} +
echo "✅ Updated Python imports"

echo "✅ File rename complete"
```

#### Step 3.2: Update Dependencies

```bash
#!/bin/bash
# update_dependencies.sh

OLD_NAME="$1"
NEW_NAME="$2"

echo "Updating all dependencies for: $OLD_NAME → $NEW_NAME"

# 1. Update all Python imports across entire project
find services/ -name "*.py" -exec sed -i \
    "s/from $OLD_NAME/from $NEW_NAME/g" {} +
find services/ -name "*.py" -exec sed -i \
    "s/import $OLD_NAME/import $NEW_NAME/g" {} +

# 2. Update Docker Compose
sed -i "s/$OLD_NAME/$NEW_NAME/g" docker-compose.yml
sed -i "s/$OLD_NAME/$NEW_NAME/g" docker-compose.*.yml

# 3. Update Kubernetes manifests
OLD_K8S="${OLD_NAME//_/-}"
NEW_K8S="${NEW_NAME//_/-}"
find kubernetes/ -name "*.yaml" -o -name "*.yml" | xargs sed -i \
    "s/$OLD_K8S/$NEW_K8S/g"

# 4. Update service discovery configs
find services/ -name "config.yaml" -o -name "config.yml" | xargs sed -i \
    "s/$OLD_NAME/$NEW_NAME/g"

echo "✅ Dependencies updated"
```

#### Step 3.3: Blue-Green Deployment

```bash
#!/bin/bash
# deploy_with_alias.sh

NEW_NAME="$1"
OLD_NAME="$2"

# 1. Deploy new service with new name
kubectl apply -f "kubernetes/services/$NEW_NAME/"

# 2. Create DNS alias for old name (backwards compatibility)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: ${OLD_NAME//_/-}
  namespace: default
spec:
  type: ExternalName
  externalName: ${NEW_NAME//_/-}.default.svc.cluster.local
EOF

# 3. Wait for new service to be healthy
kubectl wait --for=condition=ready pod \
    -l app=${NEW_NAME//_/-} \
    --timeout=300s

echo "✅ Blue-green deployment complete"
echo "Both names active: $NEW_NAME (primary), $OLD_NAME (alias)"
```

---

### Phase 4: Validation (Day 5)

#### Step 4.1: Health Checks

```bash
#!/bin/bash
# validate_migration.sh

NEW_NAME="$1"

echo "Validating migration for: $NEW_NAME"

# 1. Check service health
HEALTH_URL="http://${NEW_NAME//_/-}/health"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed (HTTP $HTTP_CODE)"
    exit 1
fi

# 2. Check logs for errors
ERROR_COUNT=$(kubectl logs -l app=${NEW_NAME//_/-} --since=1h \
    | grep -i "error" | wc -l)

if [ "$ERROR_COUNT" -lt 10 ]; then
    echo "✅ Error count acceptable ($ERROR_COUNT in last hour)"
else
    echo "⚠️  High error count: $ERROR_COUNT in last hour"
fi

# 3. Check dependent services
echo "Checking dependent services..."
# (Add specific checks based on your architecture)

echo "✅ Validation complete"
```

#### Step 4.2: Monitoring Dashboard

```yaml
# grafana_migration_dashboard.json
{
  "dashboard": {
    "title": "Migration: finance_payment_worker",
    "panels": [
      {
        "title": "Request Rate (Old vs New)",
        "targets": [
          {
            "expr": "rate(http_requests_total{service=\"finance-payment-processing-worker\"}[5m])",
            "legendFormat": "Old Name"
          },
          {
            "expr": "rate(http_requests_total{service=\"finance-payment-worker\"}[5m])",
            "legendFormat": "New Name"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_errors_total{service=\"finance-payment-worker\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

---

### Phase 5: Cleanup (Day 6-12)

#### Step 5.1: Deprecate Old Name (Day 6)

```yaml
# kubernetes/services/finance-payment-processing-worker/deprecation.yaml
apiVersion: v1
kind: Service
metadata:
  name: finance-payment-processing-worker
  annotations:
    deprecated: "true"
    deprecation-date: "2025-01-08"
    replacement: "finance-payment-worker"
    migration-guide: "https://docs.example.com/migrations/finance-payment-worker"
```

#### Step 5.2: Remove Old Name (Day 12)

```bash
#!/bin/bash
# remove_old_name.sh

OLD_NAME="$1"

echo "⚠️  REMOVING OLD NAME: $OLD_NAME"
echo "Press ENTER to continue, or Ctrl+C to cancel..."
read

# 1. Delete old Kubernetes service alias
kubectl delete service ${OLD_NAME//_/-}

# 2. Remove old DNS entries
# (Add your DNS provider specific commands)

# 3. Remove old monitoring dashboards
# (Add your monitoring tool specific commands)

echo "✅ Old name removed: $OLD_NAME"
echo "Migration complete!"
```

---

## Automated Tools

### All-in-One Migration Script

```bash
#!/bin/bash
# migrate_service_complete.sh

set -e  # Exit on any error

OLD_NAME="$1"
NEW_NAME="$2"

if [ -z "$OLD_NAME" ] || [ -z "$NEW_NAME" ]; then
    echo "Usage: ./migrate_service_complete.sh <old_name> <new_name>"
    exit 1
fi

echo "========================================="
echo "  MIGRATION: $OLD_NAME → $NEW_NAME"
echo "========================================="

# Phase 1: Backup
echo "Phase 1: Creating backup..."
./scripts/backup_before_migration.sh "$OLD_NAME"

# Phase 2: Rename files
echo "Phase 2: Renaming service files..."
./scripts/rename_service_files.sh "$OLD_NAME" "$NEW_NAME"

# Phase 3: Update dependencies
echo "Phase 3: Updating dependencies..."
./scripts/update_dependencies.sh "$OLD_NAME" "$NEW_NAME"

# Phase 4: Deploy
echo "Phase 4: Deploying with blue-green strategy..."
./scripts/deploy_with_alias.sh "$NEW_NAME" "$OLD_NAME"

# Phase 5: Validate
echo "Phase 5: Validating migration..."
sleep 30  # Wait for service to stabilize
./scripts/validate_migration.sh "$NEW_NAME"

echo "========================================="
echo "  ✅ MIGRATION COMPLETE"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Monitor service for 24 hours"
echo "2. Update documentation"
echo "3. Notify team of new service name"
echo "4. Schedule old name removal for $(date -d '+7 days' +%Y-%m-%d)"
```

---

## Rollback Procedures

### Immediate Rollback (<1 hour after migration)

```bash
#!/bin/bash
# rollback_immediate.sh

OLD_NAME="$1"
NEW_NAME="$2"
BACKUP_DIR="$3"

echo "⚠️  ROLLING BACK: $NEW_NAME → $OLD_NAME"

# 1. Restore from backup
cp -r "$BACKUP_DIR/service" "services/$OLD_NAME"
cp "$BACKUP_DIR/docker-compose.yml" .
cp -r "$BACKUP_DIR/kubernetes" .

# 2. Redeploy old service
kubectl apply -f "kubernetes/services/$OLD_NAME/"

# 3. Delete new service
kubectl delete service ${NEW_NAME//_/-}

# 4. Restore git state
git checkout services/
git checkout docker-compose.yml
git checkout kubernetes/

echo "✅ Rollback complete"
```

### Delayed Rollback (>1 hour, <1 week)

```bash
#!/bin/bash
# rollback_delayed.sh

# If new service has been running for hours/days:

# 1. Switch traffic back to old name via DNS
kubectl patch service ${NEW_NAME//_/-} \
    -p '{"spec":{"externalName":"${OLD_NAME//_/-}.default.svc.cluster.local"}}'

# 2. Scale down new service
kubectl scale deployment ${NEW_NAME//_/-} --replicas=0

# 3. Scale up old service (if still exists)
kubectl scale deployment ${OLD_NAME//_/-} --replicas=3

# 4. Monitor for stability
echo "Monitoring for 30 minutes..."
sleep 1800

echo "✅ Traffic switched back to old name"
```

---

## Case Studies

### Case Study 1: Successful Migration

**Service**: `healthcare_telemedicine_consultation_api` → `healthcare_telemedicine_api`

**Timeline**: 3 days

**Results**:
- ✅ Name reduced from 42 → 27 chars (36% reduction)
- ✅ Zero downtime
- ✅ No errors during migration
- ✅ Team consensus: improved clarity

**Lessons Learned**:
- Blue-green deployment critical for zero downtime
- 24-hour monitoring period caught 2 minor config issues
- Early communication with dependent teams prevented surprises

---

### Case Study 2: Aborted Migration

**Service**: `logistics_fleet_tracking_api` (no migration)

**Decision**: Keep 4-part name

**Reasoning**:
- Domain "fleet" is ambiguous (tracking vs management vs maintenance)
- External partners hardcoded service name in their systems
- Function word "tracking" provides critical clarity

**Outcome**: ✅ Correct decision to NOT migrate

---

## Summary Checklist

### Before Migration

- [ ] Service name >30 chars OR function is clearly redundant
- [ ] Risk assessment shows ≤2 high-risk factors
- [ ] Team consensus that 3-part name is clear
- [ ] Backup created
- [ ] Migration plan documented
- [ ] Rollback plan tested

### During Migration

- [ ] Files renamed with script
- [ ] Dependencies updated across all services
- [ ] Blue-green deployment successful
- [ ] Both old and new names active
- [ ] Health checks passing

### After Migration

- [ ] 24-hour monitoring period completed
- [ ] Zero errors in logs
- [ ] All dependent services functioning
- [ ] Documentation updated
- [ ] Team notified
- [ ] Old name scheduled for removal (7 days)

---

## Related Documentation

- **[Semantic Shortening Guide](./SEMANTIC_SHORTENING_GUIDE.md)** — Decision tree for 3-part vs 4-part
- **[Naming Conventions](../atomic/architecture/naming-conventions.md)** — Complete naming standards
- **[Architecture Guide](./ARCHITECTURE_GUIDE.md)** — Service design principles

---

**Last Updated**: 2025-01-02
**Maintainer**: DevOps Team
**Status**: Active
**Version**: 1.0
