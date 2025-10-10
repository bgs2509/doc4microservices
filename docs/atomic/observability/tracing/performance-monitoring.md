# Performance Monitoring with Tracing

Leverage distributed tracing to identify performance bottlenecks, optimize slow endpoints, detect inefficient database queries, and improve overall system throughput. Tracing provides visibility into request execution time distribution across services, enabling data-driven performance optimization.

This document covers performance analysis workflows using Jaeger, identifying N+1 query problems, detecting sequential vs parallel execution issues, finding caching opportunities, analyzing database query performance, measuring service dependency latency, and establishing performance baselines with SLOs. Tracing transforms performance optimization from guesswork into science.

Without tracing, performance issues are mysteries: users complain about slowness, but you don't know if it's the API, database, external service, or network. With tracing, you see exactly where time is spent: "95% of request time is waiting for external credit API" leads directly to caching solution.

## Performance Analysis Workflow

### Step 1: Identify Slow Endpoints

```promql
# Query Jaeger for P95 latency by endpoint
# Filter: service=finance_lending_api duration>1s
# Sort by: duration desc

# Results show:
# POST /api/loans           [2.5s avg] ← SLOW
# GET /api/loans/:id/details [1.8s avg] ← SLOW
# GET /api/loans            [0.2s avg] ← FAST
```

### Step 2: Analyze Trace Waterfall

```
Trace: POST /api/loans [2500ms]
├─ validate_user [50ms]
│  └─ GET /api/users/:id [45ms]
├─ credit_check [2300ms] ← BOTTLENECK (92% of total time)
│  └─ POST /external-credit-api [2250ms] ← External API slow
├─ save_loan [100ms]
│  └─ INSERT INTO loans [85ms]
└─ publish_event [20ms]

DIAGNOSIS: External API is the bottleneck
SOLUTION: Add caching + timeout + circuit breaker
```

### Step 3: Implement Optimization

```python
# Before: Always call external API (2250ms)
@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    with tracer.start_as_current_span("credit_check") as span:
        credit_score = await credit_api.get_score(loan.user_id)  # 2250ms
        span.set_attribute("credit.score", credit_score)


# After: Cache credit scores (45ms cache hit, 2250ms cache miss)
@app.post("/api/loans")
async def create_loan(loan: LoanCreate):
    with tracer.start_as_current_span("credit_check") as span:
        # Check Redis cache first
        cached_score = await redis.get(f"credit:{loan.user_id}")

        if cached_score:
            span.add_event("cache_hit")
            credit_score = int(cached_score)
            # 45ms (Redis latency)
        else:
            span.add_event("cache_miss")
            credit_score = await credit_api.get_score(loan.user_id)  # 2250ms
            await redis.setex(f"credit:{loan.user_id}", 3600, credit_score)

        span.set_attribute("credit.score", credit_score)


# Result: 90% cache hit rate → avg latency 250ms (was 2500ms)
# Improvement: 10x faster
```

### Step 4: Verify Improvement

```promql
# Query Jaeger after optimization
# Filter: service=finance_lending_api operation=POST /api/loans
# Time range: Last 1 hour

# Before:  P50=2.0s P95=2.5s P99=3.0s
# After:   P50=0.2s P95=0.5s P99=2.5s (cache misses)

# Cache hit rate from metrics
rate(cache_operations_total{result="hit"}[1h]) / rate(cache_operations_total[1h])
# Result: 0.90 (90% hit rate)
```

## Common Performance Issues

### N+1 Query Problem

```python
# PROBLEM: N+1 queries (1 + N database roundtrips)
@app.get("/api/loans")
async def get_loans():
    """Fetch loans with N+1 query anti-pattern."""
    with tracer.start_as_current_span("get_loans") as span:
        # Query 1: Fetch all loans
        loans = await db.execute("SELECT * FROM loans")  # 50ms

        # Query N: Fetch user for each loan (N separate queries)
        for loan in loans:  # 100 loans
            with tracer.start_as_current_span("get_user") as user_span:
                user = await db.execute(
                    "SELECT * FROM users WHERE id = ?", loan.user_id
                )  # 10ms × 100 = 1000ms
                loan.user = user

        span.set_attribute("loan.count", len(loans))
        return loans


# Trace shows:
# GET /api/loans [1050ms]
# ├─ SELECT * FROM loans [50ms]
# ├─ SELECT * FROM users [10ms] ← Repeated 100 times
# ├─ SELECT * FROM users [10ms]
# ├─ SELECT * FROM users [10ms]
# ... (97 more identical spans)
# └─ SELECT * FROM users [10ms]

# DIAGNOSIS: 100 separate database queries for users
# SOLUTION: Use JOIN or batch query
```

```python
# SOLUTION 1: SQL JOIN (single query)
@app.get("/api/loans")
async def get_loans():
    """Fetch loans with JOIN (optimized)."""
    with tracer.start_as_current_span("get_loans") as span:
        loans = await db.execute("""
            SELECT loans.*, users.*
            FROM loans
            JOIN users ON loans.user_id = users.id
        """)  # 60ms (single query)

        span.set_attribute("loan.count", len(loans))
        return loans


# Trace shows:
# GET /api/loans [60ms]  ← 17x faster
# └─ SELECT loans JOIN users [60ms]

# Improvement: 1050ms → 60ms
```

```python
# SOLUTION 2: Batch query (when JOIN not possible)
@app.get("/api/loans")
async def get_loans():
    """Fetch loans with batch user query."""
    with tracer.start_as_current_span("get_loans") as span:
        # Query 1: Fetch loans
        loans = await db.execute("SELECT * FROM loans")  # 50ms

        # Query 2: Batch fetch all users
        user_ids = [loan.user_id for loan in loans]
        users = await db.execute(
            "SELECT * FROM users WHERE id IN (?)",
            user_ids
        )  # 25ms (single query for all users)

        # Map users to loans
        user_map = {user.id: user for user in users}
        for loan in loans:
            loan.user = user_map[loan.user_id]

        span.set_attribute("loan.count", len(loans))
        return loans


# Trace shows:
# GET /api/loans [75ms]  ← 14x faster
# ├─ SELECT * FROM loans [50ms]
# └─ SELECT * FROM users WHERE id IN (...) [25ms]

# Improvement: 1050ms → 75ms
```

### Sequential vs Parallel Execution

```python
# PROBLEM: Sequential external calls (300ms total)
@app.get("/api/loans/{loan_id}/details")
async def get_loan_details(loan_id: str):
    """Fetch loan details sequentially."""
    with tracer.start_as_current_span("get_loan_details") as span:
        # Sequential calls
        loan = await get_loan(loan_id)         # 100ms
        user = await get_user(loan.user_id)    # 100ms
        documents = await get_documents(loan_id)  # 100ms

        span.set_attribute("loan.id", loan_id)
        return {"loan": loan, "user": user, "documents": documents}


# Trace shows:
# GET /api/loans/:id/details [300ms]
# ├─ get_loan [100ms]
# ├─ get_user [100ms]  ← Wait for get_loan to finish
# └─ get_documents [100ms]  ← Wait for get_user to finish

# DIAGNOSIS: Calls are independent but executed sequentially
# SOLUTION: Parallel execution with asyncio.gather
```

```python
# SOLUTION: Parallel execution (100ms total)
@app.get("/api/loans/{loan_id}/details")
async def get_loan_details(loan_id: str):
    """Fetch loan details in parallel."""
    with tracer.start_as_current_span("get_loan_details") as span:
        # Parallel calls (all 3 start simultaneously)
        loan, user, documents = await asyncio.gather(
            get_loan(loan_id),
            get_user_by_loan(loan_id),  # Can start before loan completes
            get_documents(loan_id)
        )

        span.set_attribute("loan.id", loan_id)
        return {"loan": loan, "user": user, "documents": documents}


# Trace shows:
# GET /api/loans/:id/details [100ms]  ← 3x faster
# ├─ get_loan [100ms]
# ├─ get_user [100ms]  ← Runs in parallel with get_loan
# └─ get_documents [100ms]  ← Runs in parallel with both

# Improvement: 300ms → 100ms
```

### Inefficient Database Queries

```python
# PROBLEM: Missing database index (500ms query)
@app.get("/api/loans")
async def get_loans(user_id: str):
    """Fetch loans by user (slow without index)."""
    with tracer.start_as_current_span("get_loans_by_user") as span:
        loans = await db.execute(
            "SELECT * FROM loans WHERE user_id = ?",
            user_id
        )  # 500ms (full table scan)

        span.set_attribute("user.id", user_id)
        return loans


# Trace shows:
# GET /api/loans [500ms]
# └─ SELECT * FROM loans WHERE user_id = ? [500ms]

# Jaeger span attributes show:
# db.statement: SELECT * FROM loans WHERE user_id = ?
# db.rows_examined: 1000000 ← Full table scan!
# db.rows_returned: 10

# DIAGNOSIS: No index on user_id column
# SOLUTION: Add database index
```

```sql
-- SOLUTION: Create index on user_id
CREATE INDEX idx_loans_user_id ON loans(user_id);
```

```python
# After adding index:
# Trace shows:
# GET /api/loans [15ms]  ← 33x faster
# └─ SELECT * FROM loans WHERE user_id = ? [15ms]

# Span attributes show:
# db.rows_examined: 10 ← Index used, no full scan
# db.rows_returned: 10

# Improvement: 500ms → 15ms
```

### Excessive Data Transfer

```python
# PROBLEM: Fetching too much data (2000ms)
@app.get("/api/loans")
async def get_loans():
    """Fetch all loan data including large documents."""
    with tracer.start_as_current_span("get_loans") as span:
        loans = await db.execute("""
            SELECT loans.*, documents.content
            FROM loans
            JOIN documents ON loans.id = documents.loan_id
        """)  # 2000ms (documents.content is large BLOB)

        span.set_attribute("loan.count", len(loans))
        span.set_attribute("response.size_bytes", len(json.dumps(loans)))
        return loans


# Trace shows:
# GET /api/loans [2000ms]
# └─ SELECT loans, documents.content [2000ms]

# Span attributes show:
# response.size_bytes: 50000000 (50MB response)

# DIAGNOSIS: Returning large document content unnecessarily
# SOLUTION: Return only required fields
```

```python
# SOLUTION: Select only needed columns (150ms)
@app.get("/api/loans")
async def get_loans():
    """Fetch only required loan fields."""
    with tracer.start_as_current_span("get_loans") as span:
        loans = await db.execute("""
            SELECT loans.id, loans.amount, loans.status, loans.user_id
            FROM loans
        """)  # 150ms (no large BLOBs)

        span.set_attribute("loan.count", len(loans))
        span.set_attribute("response.size_bytes", len(json.dumps(loans)))
        return loans


# Trace shows:
# GET /api/loans [150ms]  ← 13x faster
# └─ SELECT loans.id, loans.amount, loans.status [150ms]

# Span attributes show:
# response.size_bytes: 50000 (50KB response)

# Improvement: 2000ms → 150ms, 50MB → 50KB
```

## Performance Baseline and SLOs

### Establishing Baseline

```python
# Query Jaeger for current performance (baseline)
# Time range: Last 7 days
# Service: finance_lending_api

# Results:
# POST /api/loans:
#   P50: 200ms
#   P95: 500ms
#   P99: 1000ms

# GET /api/loans/:id:
#   P50: 50ms
#   P95: 100ms
#   P99: 200ms
```

### Defining SLOs

```yaml
# SLO definition based on baseline
slos:
  - service: finance_lending_api
    endpoint: POST /api/loans
    slo_target:
      p95_latency_ms: 500  # 95% of requests < 500ms
      availability: 99.9   # 99.9% success rate

  - service: finance_lending_api
    endpoint: GET /api/loans/:id
    slo_target:
      p95_latency_ms: 100
      availability: 99.95
```

### SLO Monitoring

```promql
# Query: Is POST /api/loans meeting SLO?
# Target: P95 < 500ms

histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket{
    service="finance_lending_api",
    endpoint="/api/loans"
  }[1h])
) < 0.5  # 0.5 seconds = 500ms

# If result = 1: SLO met
# If result = 0: SLO violated (investigate slow traces)
```

## Jaeger Query Patterns

### Find Slowest Traces

```
# Jaeger UI search:
Service: finance_lending_api
Operation: POST /api/loans
Min Duration: 1s
Limit: 100

# Returns: Top 100 slowest traces
# Click trace → See waterfall → Identify bottleneck
```

### Find Traces with Errors

```
# Jaeger UI search:
Service: finance_lending_api
Tags: error=true
Limit: 100

# Returns: All traces with errors
# Analyze error patterns (same endpoint? same user?)
```

### Compare Before/After Optimization

```
# Query 1: Before optimization (baseline)
Service: finance_lending_api
Lookback: 1d
Time Range: 2024-01-10 00:00 - 2024-01-10 23:59

# Result: P95 = 2500ms

# Query 2: After optimization
Service: finance_lending_api
Lookback: 1d
Time Range: 2024-01-11 00:00 - 2024-01-11 23:59

# Result: P95 = 250ms

# Improvement: 10x faster
```

## Best Practices

### DO: Add Span Attributes for Analysis

```python
# CORRECT: Rich span attributes enable analysis
with tracer.start_as_current_span("database_query") as span:
    span.set_attribute("db.statement", "SELECT * FROM loans WHERE user_id = ?")
    span.set_attribute("db.rows_examined", 1000000)
    span.set_attribute("db.rows_returned", 10)
    span.set_attribute("db.index_used", False)  # ← Key insight

    result = await db.execute(query)


# INCORRECT: No attributes (can't analyze)
with tracer.start_as_current_span("database_query"):  # ❌ No attributes
    result = await db.execute(query)
```

### DO: Measure Before and After

```python
# CORRECT: Baseline → Optimize → Measure improvement
# 1. Query Jaeger for baseline P95
# 2. Implement optimization
# 3. Query Jaeger for new P95
# 4. Calculate improvement %

baseline_p95 = 2500  # ms
optimized_p95 = 250  # ms
improvement = (baseline_p95 - optimized_p95) / baseline_p95 * 100
# Result: 90% improvement


# INCORRECT: Optimize without measuring
# ❌ Don't know if optimization worked
```

### DON'T: Ignore Cache Miss Performance

```python
# INCORRECT: Only optimizing cache hits
# Cache hit: 45ms (fast)
# Cache miss: 2250ms (still slow) ← Ignored

# Users with cache misses still suffer


# CORRECT: Optimize both paths
# Cache hit: 45ms (fast)
# Cache miss: 350ms (added timeout + circuit breaker + fallback)

# All users experience acceptable performance
```

## Checklist

- [ ] Query Jaeger for P95/P99 latency by endpoint
- [ ] Identify endpoints violating SLOs
- [ ] Analyze slow trace waterfalls in Jaeger
- [ ] Detect N+1 query patterns (many identical child spans)
- [ ] Find sequential calls that can be parallelized
- [ ] Check for missing database indexes (high rows_examined)
- [ ] Identify excessive data transfer (large response sizes)
- [ ] Implement caching for frequently accessed data
- [ ] Add timeouts to external service calls
- [ ] Measure performance before and after optimizations
- [ ] Update SLOs based on achievable performance
- [ ] Create alerts for SLO violations

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md` — OpenTelemetry instrumentation
- `docs/atomic/observability/tracing/distributed-tracing.md` — Distributed tracing patterns
- `docs/atomic/observability/tracing/jaeger-configuration.md` — Jaeger backend setup
- `docs/atomic/observability/metrics/golden-signals.md` — Latency SLOs
