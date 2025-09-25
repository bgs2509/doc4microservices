# Timeout and Retry Patterns

Use aggressive timeouts and controlled retries to avoid cascading failures.

## Timeouts

- Set connect timeout ≤1s for in-cluster calls; adjust read timeout based on endpoint SLA.
- Use per-call overrides for long-running operations instead of raising global limits.
- Detect slow responses via metrics (P95/P99 latency) and alert when thresholds breach.

## Retries

- Retry only idempotent operations (GET, HEAD) by default; allow POST/PUT when coupled with idempotency keys.
- Apply exponential backoff with jitter (`1s, 2s, 4s up to max 10s`).
- Limit total attempts (usually 3) and record retry count in logs/metrics.

## Circuit Breakers

- Trip the breaker after successive failures and fail fast for a cool-down period.
- Expose breaker state via health endpoints for observability.

## Implementation Helpers

- Wrap HTTP clients with libraries such as `tenacity` or implement custom decorators.
- Ensure retry logic respects deadline budgets so requests do not exceed overall timeout.

## Related Documents

- `docs/atomic/integrations/http-communication/error-handling-strategies.md`
- `docs/atomic/integrations/http-communication/request-tracing.md`
