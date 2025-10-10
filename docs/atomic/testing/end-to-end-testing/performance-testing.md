# End-to-End Performance Testing

Test system performance under realistic load conditions to verify scalability, identify bottlenecks, and establish performance baselines. Performance tests validate that the system meets response time, throughput, and resource usage requirements under expected and peak loads.

This document covers performance testing patterns using Locust and k6, load testing strategies, stress testing, metrics collection, and CI/CD integration. Performance tests ensure your microservices handle production traffic without degradation.

Performance testing validates that services respond quickly under load, scale horizontally as needed, maintain data consistency under concurrent access, and gracefully handle peak traffic spikes. These tests prevent production outages caused by performance issues.

## Performance Testing Types

### Load Testing
Test system behavior under expected production load. Verify the system handles target concurrent users and request rates without performance degradation.

### Stress Testing
Push system beyond normal capacity to find breaking points. Identify maximum load the system can handle before failure.

### Spike Testing
Sudden dramatic increase in load to test elasticity. Verify auto-scaling and graceful degradation under traffic spikes.

### Soak Testing
Sustained load over extended period (hours/days) to detect memory leaks, resource exhaustion, and performance degradation over time.

## Load Testing with Locust

### Basic Locust Setup

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random


class LoanApplicationUser(HttpUser):
    """Simulate users applying for loans."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "http://localhost:8000"

    def on_start(self):
        """Execute once when user starts."""
        # Login or get auth token
        response = self.client.post("/api/auth/login", json={
            "email": f"user{random.randint(1, 1000)}@test.com",
            "password": "testpass"
        })
        self.auth_token = response.json().get("token")

    @task(3)
    def view_dashboard(self):
        """View dashboard (most common action)."""
        self.client.get("/api/dashboard", headers={
            "Authorization": f"Bearer {self.auth_token}"
        })

    @task(2)
    def list_loans(self):
        """List user's loans."""
        self.client.get("/api/loans", headers={
            "Authorization": f"Bearer {self.auth_token}"
        })

    @task(1)
    def apply_for_loan(self):
        """Apply for a loan (less frequent)."""
        self.client.post("/api/loans", json={
            "amount": random.randint(5000, 50000),
            "purpose": random.choice(["business", "personal", "education"]),
            "term_months": random.choice([12, 24, 36])
        }, headers={
            "Authorization": f"Bearer {self.auth_token}"
        })


# Run: locust -f locustfile.py --users 100 --spawn-rate 10
```

### Advanced Locust Patterns

```python
# CORRECT: Test multiple user types
class AdminUser(HttpUser):
    """Simulate admin users."""
    wait_time = between(2, 5)
    weight = 1  # 10% of users

    @task
    def approve_loans(self):
        """Approve pending loans."""
        response = self.client.get("/api/loans?status=pending")
        loans = response.json()["loans"]
        if loans:
            loan_id = random.choice(loans)["id"]
            self.client.post(f"/api/loans/{loan_id}/approve")


class RegularUser(HttpUser):
    """Simulate regular users."""
    wait_time = between(1, 3)
    weight = 9  # 90% of users

    @task(5)
    def browse(self):
        self.client.get("/api/products")

    @task(1)
    def purchase(self):
        self.client.post("/api/orders", json={"product_id": "prod-1"})


# CORRECT: Sequential task execution
from locust import SequentialTaskSet

class CheckoutFlow(SequentialTaskSet):
    """Execute tasks in order."""

    @task
    def view_product(self):
        self.client.get("/api/products/1")

    @task
    def add_to_cart(self):
        self.client.post("/api/cart", json={"product_id": 1, "quantity": 1})

    @task
    def checkout(self):
        self.client.post("/api/checkout")
```

### Running Locust Tests

```bash
# Local execution
locust -f tests/performance/locustfile.py \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless

# With custom host
locust -f locustfile.py --host https://staging.example.com

# Generate HTML report
locust -f locustfile.py --users 100 --run-time 5m --html report.html
```

## Load Testing with k6

### Basic k6 Script

```javascript
// tests/performance/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metric
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],  // Error rate < 1%
    errors: ['rate<0.1'],
  },
};

export default function () {
  // Test loan application endpoint
  const payload = JSON.stringify({
    amount: 10000,
    purpose: 'business',
    term_months: 24,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer test-token',
    },
  };

  const response = http.post('http://localhost:8000/api/loans', payload, params);

  // Validate response
  const success = check(response, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has loan_id': (r) => JSON.parse(r.body).id !== undefined,
  });

  errorRate.add(!success);

  sleep(1);
}

// Run: k6 run load_test.js
```

### Stress Testing with k6

```javascript
// tests/performance/stress_test.js
export const options = {
  stages: [
    { duration: '5m', target: 100 },   // Normal load
    { duration: '5m', target: 200 },   // Above normal
    { duration: '5m', target: 300 },   // Stress
    { duration: '5m', target: 400 },   // Heavy stress
    { duration: '5m', target: 0 },     // Recovery
  ],
};

export default function () {
  // Test critical endpoints under stress
  const responses = http.batch([
    ['GET', 'http://localhost:8000/api/users'],
    ['GET', 'http://localhost:8000/api/loans'],
    ['POST', 'http://localhost:8000/api/transactions', JSON.stringify({amount: 100})],
  ]);

  // Check if any request failed
  responses.forEach((response, index) => {
    check(response, {
      [`request ${index} succeeded`]: (r) => r.status < 400,
    });
  });
}
```

### Spike Testing

```javascript
// tests/performance/spike_test.js
export const options = {
  stages: [
    { duration: '1m', target: 50 },    // Normal load
    { duration: '30s', target: 500 },  // Sudden spike
    { duration: '1m', target: 500 },   // Sustain spike
    { duration: '1m', target: 50 },    // Return to normal
  ],
};

export default function () {
  http.get('http://localhost:8000/api/products');
  sleep(1);
}
```

## Metrics Collection

### Key Performance Metrics

```yaml
# Performance thresholds
performance_requirements:
  response_time:
    p50: <200ms  # Median response time
    p95: <500ms  # 95th percentile
    p99: <1000ms # 99th percentile

  throughput:
    target_rps: 1000  # Requests per second

  error_rate:
    max_rate: 1%      # Maximum 1% errors

  resource_usage:
    cpu_max: 80%      # Maximum CPU utilization
    memory_max: 80%   # Maximum memory utilization
    database_connections_max: 80%
```

### Monitoring During Tests

```python
# CORRECT: Collect metrics during load test
import prometheus_client
from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Start metrics collection."""
    print("Starting metrics collection...")
    # Start Prometheus scraping

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    """Track individual requests."""
    if response_time > 1000:
        print(f"Slow request: {name} took {response_time}ms")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate performance report."""
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Median response time: {stats.total.median_response_time}ms")
    print(f"95th percentile: {stats.total.get_response_time_percentile(0.95)}ms")
```

## Database Performance Testing

### Testing Database Under Load

```python
@task
def complex_query(self):
    """Test expensive database query under load."""
    self.client.get("/api/reports/user-analytics", params={
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "group_by": "day"
    })


@task
def concurrent_writes(self):
    """Test concurrent writes to database."""
    self.client.post("/api/transactions", json={
        "user_id": f"user-{random.randint(1, 1000)}",
        "amount": random.randint(10, 1000)
    })
```

## CI/CD Integration

### GitHub Actions Performance Tests

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start services
        run: docker-compose -f docker-compose.perf.yml up -d

      - name: Run k6 tests
        uses: grafana/k6-action@v0.3.0
        with:
          filename: tests/performance/load_test.js
          cloud: false

      - name: Check performance thresholds
        run: |
          if [ ${{ steps.k6.outputs.exit_code }} -ne 0 ]; then
            echo "Performance thresholds not met!"
            exit 1
          fi

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: summary.json
```

## Best Practices

### DO: Test Realistic Scenarios

```python
# CORRECT: Realistic user behavior
class RealisticUser(HttpUser):
    """Simulate realistic user behavior."""

    @task
    def user_journey(self):
        # Login
        self.client.post("/api/auth/login", json={...})
        self.wait()

        # Browse products
        self.client.get("/api/products")
        self.wait()

        # View product details
        self.client.get("/api/products/123")
        self.wait()

        # Add to cart
        self.client.post("/api/cart", json={...})
        self.wait()

        # Checkout
        self.client.post("/api/orders", json={...})

    def wait(self):
        """Realistic think time."""
        sleep(random.uniform(2, 5))


# INCORRECT: Unrealistic constant hammering
class UnrealisticUser(HttpUser):
    """WRONG: Unrealistic load pattern."""

    @task
    def hammer_endpoint(self):
        for _ in range(100):
            self.client.get("/api/products")  # No wait time
```

### DO: Establish Baselines

```bash
# CORRECT: Run baseline before changes
k6 run tests/performance/baseline.js --out json=baseline.json

# Make code changes

# Run comparison test
k6 run tests/performance/baseline.js --out json=after_changes.json

# Compare results
python scripts/compare_performance.py baseline.json after_changes.json
```

### DON'T: Test Production

```python
# INCORRECT: Testing production
locust -f locustfile.py --host https://api.production.com


# CORRECT: Test staging or dedicated perf environment
locust -f locustfile.py --host https://api.staging.com
```

## Checklist

- [ ] Define performance requirements (response time, throughput, error rate)
- [ ] Set up load testing tool (Locust, k6, JMeter)
- [ ] Create realistic user scenarios
- [ ] Test under expected load
- [ ] Test under peak load (stress testing)
- [ ] Test sudden traffic spikes (spike testing)
- [ ] Test sustained load (soak testing)
- [ ] Monitor resource usage (CPU, memory, database connections)
- [ ] Collect and analyze metrics
- [ ] Establish performance baselines
- [ ] Integrate tests into CI/CD
- [ ] Test with production-like data volumes
- [ ] Identify and document bottlenecks

## Related Documents

- `docs/atomic/testing/end-to-end-testing/e2e-test-setup.md` — E2E test infrastructure
- `docs/atomic/testing/end-to-end-testing/user-journey-testing.md` — User workflow testing
- `docs/atomic/observability/metrics/prometheus-integration.md` — Metrics collection
- `docs/atomic/infrastructure/docker/docker-compose-patterns.md` — Service orchestration
