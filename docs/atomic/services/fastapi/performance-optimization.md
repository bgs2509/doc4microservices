# Performance Optimization

Tune FastAPI services for predictable latency and throughput while avoiding premature micro-optimisation.

## Baseline Practices

- Use `uvicorn` with `uvloop` and `httptools` in production: `uvicorn src.main:app --http httptools --loop uvloop`.
- Prefer async drivers (`asyncpg`, `httpx.AsyncClient`, `redis.asyncio`) to eliminate blocking calls.
- Enable connection pooling for databases and caches; reuse clients via the DI container.

## Request Handling

- Avoid heavy computations inside request handlers; offload to workers or `asyncio.to_thread` when unavoidable.
- Limit response payload sizes; paginate lists and stream large files with `StreamingResponse`.
- Apply caching for idempotent read endpoints using Redis with explicit TTLs.

## Timeouts & Retries

- Set client timeouts (`httpx.AsyncClient(timeout=Timeout(5.0, connect=1.0))`).
- Implement circuit breakers when cascading failures are possible.
- Expose configuration for timeouts/throttling via settings to allow tuning per environment.

## Profiling & Monitoring

- Track P95/P99 latency via Prometheus and alert on regressions.
- Use `pyinstrument` or `yappi` during performance investigations.
- Capture slow query logs (`statement_timeout` in PostgreSQL) and fix N+1 patterns.

## Load Testing

- Run k6/Locust scenarios before major releases.
- Automate smoke performance tests with representative traffic patterns (auth, data fetch, writes).
- Store baseline metrics; treat regressions as release blockers.

## Related Documents

- `docs/atomic/architecture/quality-standards.md`
- `docs/atomic/services/fastapi/testing-strategies.md`
