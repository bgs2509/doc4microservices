# Custom Metrics

Implement business-specific custom metrics to monitor domain events, track KPIs, and measure business outcomes beyond generic infrastructure metrics. Custom metrics capture application-specific behavior like loan approvals, payment processing, user signups, and feature usage.

This document covers designing custom metrics, implementing counters/gauges/histograms for business events, naming conventions, labeling strategies, and avoiding high cardinality. Custom metrics enable monitoring what matters to your business, not just technical health.

Custom metrics answer business questions: How many loans were approved today? What's the average loan amount? How long does credit check take? How many users registered this hour? Generic metrics (CPU, memory, request count) don't capture business value—custom metrics do.

## Metric Types

### Counter

```python
from prometheus_client import Counter

# Monotonically increasing count
loans_created_total = Counter(
    'loans_created_total',
    'Total loans created',
    ['status', 'purpose']
)

# Usage
loans_created_total.labels(
    status='approved',
    purpose='business'
).inc()
```

### Gauge

```python
from prometheus_client import Gauge

# Value that can increase or decrease
active_loan_applications = Gauge(
    'active_loan_applications',
    'Number of loans in pending status'
)

# Usage
active_loan_applications.set(42)
active_loan_applications.inc()  # +1
active_loan_applications.dec()  # -1
```

### Histogram

```python
from prometheus_client import Histogram

# Observations (durations, amounts)
loan_amount_dollars = Histogram(
    'loan_amount_dollars',
    'Loan amounts in dollars',
    buckets=[1000, 5000, 10000, 25000, 50000, 100000]
)

credit_check_duration_seconds = Histogram(
    'credit_check_duration_seconds',
    'Credit check duration',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Usage
loan_amount_dollars.observe(15000)

with credit_check_duration_seconds.time():
    await perform_credit_check(user_id)
```

## Business Metrics

```python
# src/metrics/business_metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Loan metrics
loans_created_total = Counter(
    'loans_created_total',
    'Total loan applications',
    ['purpose', 'status']
)

loan_processing_duration_seconds = Histogram(
    'loan_processing_duration_seconds',
    'Loan processing time',
    ['status']
)

active_loans = Gauge(
    'active_loans',
    'Current active loans'
)

# Payment metrics
payments_processed_total = Counter(
    'payments_processed_total',
    'Total payments processed',
    ['status', 'payment_method']
)

payment_amount_dollars = Histogram(
    'payment_amount_dollars',
    'Payment amounts',
    buckets=[10, 50, 100, 500, 1000, 5000]
)

# User metrics
users_registered_total = Counter(
    'users_registered_total',
    'Total user registrations',
    ['source']
)

active_users = Gauge(
    'active_users',
    'Currently logged in users'
)
```

## Implementation

```python
# CORRECT: Instrument business logic
from fastapi import APIRouter
import time

router = APIRouter()


@router.post("/api/loans")
async def create_loan(loan: LoanCreate):
    """Create loan with metrics."""
    start_time = time.time()

    try:
        result = await loan_service.create_loan(loan)

        # Record success
        loans_created_total.labels(
            purpose=loan.purpose,
            status='created'
        ).inc()

        loan_amount_dollars.observe(loan.amount)

        duration = time.time() - start_time
        loan_processing_duration_seconds.labels(
            status='success'
        ).observe(duration)

        return result

    except Exception as e:
        # Record failure
        loans_created_total.labels(
            purpose=loan.purpose,
            status='failed'
        ).inc()

        loan_processing_duration_seconds.labels(
            status='failure'
        ).observe(time.time() - start_time)

        raise
```

## Naming Conventions

```python
# CORRECT: Descriptive names with units
http_requests_total  # Total count
http_request_duration_seconds  # Duration with unit
loan_amount_dollars  # Amount with currency
active_connections  # Current state


# INCORRECT: Ambiguous names
requests  # Total? Per second? Current?
loan_time  # Milliseconds? Seconds?
amount  # Dollars? Cents? Different currency?
```

## Best Practices

### DO: Use Labels for Dimensions

```python
# CORRECT: One metric with labels
loans_total.labels(status='approved', purpose='business').inc()
loans_total.labels(status='rejected', purpose='personal').inc()


# INCORRECT: Separate metrics per dimension
loans_approved_business_total.inc()  # ❌ Too many metrics
loans_rejected_personal_total.inc()
```

### DON'T: High Cardinality Labels

```python
# INCORRECT: User ID as label (millions of values)
requests_total.labels(user_id=user.id).inc()  # ❌ High cardinality


# CORRECT: Aggregate by user type
requests_total.labels(user_type=user.type).inc()  # ✅ Low cardinality
```

## Querying

```promql
# Loan approval rate
rate(loans_created_total{status="approved"}[5m])
/ rate(loans_created_total[5m])

# Average loan amount (last hour)
rate(loan_amount_dollars_sum[1h])
/ rate(loan_amount_dollars_count[1h])

# 95th percentile credit check duration
histogram_quantile(0.95,
  rate(credit_check_duration_seconds_bucket[5m])
)

# Active loan applications
active_loan_applications
```

## Checklist

- [ ] Identify key business metrics
- [ ] Choose appropriate metric types (counter/gauge/histogram)
- [ ] Use descriptive names with units
- [ ] Add meaningful labels
- [ ] Avoid high-cardinality labels
- [ ] Instrument critical business flows
- [ ] Test metric collection
- [ ] Create business dashboards
- [ ] Set up business alerts
- [ ] Document metric meanings

## Related Documents

- `docs/atomic/observability/metrics/prometheus-setup.md` — Prometheus configuration
- `docs/atomic/observability/metrics/service-metrics.md` — Service-level metrics
- `docs/atomic/observability/metrics/golden-signals.md` — Golden signals
- `docs/atomic/observability/metrics/dashboards.md` — Dashboard creation
