# Caching Strategies

Redis accelerates read-heavy workflows and rate limiting. Choose caching tactics that balance freshness and cost.

## Patterns

- **Read-through** – fetch from cache first; on miss, load from source and populate cache.
- **Write-through** – update cache immediately after persisting to the data service.
- **Write-behind** – enqueue updates for asynchronous flushing; use only when ordering is controlled.
- **Negative caching** – cache misses (e.g., `None`) briefly to shield the data service from repeated lookups.

## TTL Guidelines

| Use Case | TTL |
|----------|-----|
| User profiles | 5–15 minutes |
| Feature flags | No TTL; invalidate on change |
| Rate limiting | Window duration (e.g., 60 seconds) |

## Consistency

- Invalidate keys on data modifications; keep a helper that derives the key from domain identifiers.
- For multi-entity updates, use pipelines or Lua scripts to mutate all keys atomically.
- Prefer eventual consistency and tolerate slightly stale data unless business rules demand strict accuracy.

## Monitoring

- Track hit rate, evictions, and memory usage via Redis INFO metrics.
- Set alerts for sudden changes in hit rate (indicates cache stampede or invalidation bug).
- Implement jittered TTL to avoid synchronized expirations.

## Related Documents

- `docs/atomic/integrations/http-communication/timeout-retry-patterns.md`
- `docs/atomic/services/data-services/http-api-design.md`
