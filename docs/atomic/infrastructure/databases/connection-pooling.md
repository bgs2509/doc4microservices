# Database Connection Pooling

Connection pools balance concurrency and resource usage for data services.

## Guidelines

- Use async-capable pools (`sqlalchemy.asyncio.create_async_engine`, Motor connection pools) configured once per process.
- Size pools based on workload: start with `pool_size=10` and `max_overflow=20` for HTTP services; tune using production metrics.
- Set timeouts (`pool_timeout`, `pool_recycle`) to avoid stale connections and detect leaks.
- Monitor pool utilisation (borrowed connections, wait times) and alert on saturation.
- Avoid per-request engine creation; reuse pooled sessions through dependency injection.

## Troubleshooting

- Spikes in `pool_timeout` errors usually indicate blocked transactions or long-running queries—profile and optimize.
- Recycle connections after network hiccups to avoid using stale sockets.
- For read replicas, maintain separate pools to keep workloads isolated.

## Related Documents

- `docs/atomic/services/data-services/transaction-management.md`
- `docs/atomic/architecture/event-loop-management.md`
