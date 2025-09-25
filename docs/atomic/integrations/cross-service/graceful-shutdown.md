# Graceful Shutdown

Coordinate shutdown across services to avoid data loss and user-visible errors.

## Checklist

1. Signal receipt (`SIGTERM`, `SIGINT`).
2. Stop accepting new traffic (update readiness endpoints, drain load balancers).
3. Finish in-flight requests/messages or persist state for later recovery.
4. Close external connections (database, Redis, RabbitMQ) cleanly.
5. Log shutdown completion with request IDs for traceability.

## FastAPI

- Use lifespan shutdown hooks to close connection pools and flush background tasks.
- Return 503 from readiness checks while shutting down to reroute traffic.

## Aiogram & Workers

- Use `asyncio.Event` and signal handlers to cancel long-running tasks.
- Acknowledge or requeue messages before closing broker channels.

## Testing

- Simulate shutdown in integration tests (send `SIGTERM` to subprocess) and ensure no messages are lost.
- Measure shutdown duration and keep it below orchestrator grace periods.

## Related Documents

- `docs/atomic/architecture/event-loop-management.md`
- `docs/atomic/services/asyncio-workers/signal-handling.md`
