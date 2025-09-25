# Database Performance Optimization

Optimise databases proactively to maintain low latency and predictable throughput.

## Monitoring

- Track query latency, lock time, cache hit ratios, and replication lag via exporters.
- Instrument application code with metrics for slow queries and connection pool waits.

## PostgreSQL Tips

- Use `EXPLAIN (ANALYZE, BUFFERS)` to profile heavy queries.
- Create composite indexes aligned with filter/order clauses.
- Vacuum and analyse regularly; configure autovacuum thresholds for large tables.
- Limit long-running transactions to avoid blocking vacuum and index maintenance.

## MongoDB Tips

- Use the profiler sparingly to capture slow query plans.
- Maintain compound indexes that match query predicates and sort orders.
- Avoid unbounded array growth in documents; normalize to separate collections when needed.

## Capacity Planning

- Record baseline performance and growth trends; review quarterly.
- Scale vertically when CPU or memory saturates; scale horizontally (read replicas, sharding) when needed.

## Related Documents

- `docs/atomic/services/data-services/testing-strategies.md`
- `docs/atomic/infrastructure/databases/connection-pooling.md`
