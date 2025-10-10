# Event Loop Management

All services in the platform rely on Python's asynchronous runtimes. Mismanaging event loops leads to deadlocks, duplicate tasks, and hard-to-diagnose outages. This document defines how to own, share, and monitor event loops across service types.

## Core Principles

- **Single loop per process.** Every container runs exactly one event loop. Do not create ad-hoc loops with `asyncio.new_event_loop()` unless you run fully isolated worker pools.
- **Async all the way down.** Mixing blocking I/O with the event loop stalls the entire service. Prefer async clients (`asyncpg`, `httpx`, `aio-pika`, `redis.asyncio`).
- **Explicit lifecycle management.** Startup and shutdown hooks manage background tasks, connection pools, and signal handlers.
- **Graceful degradation.** On fatal errors, cancel running tasks, close connections, and exit cleanly so orchestrators can restart the service.

## Service Type Guidelines

### FastAPI Services

- Use the [lifespan protocol](https://fastapi.tiangolo.com/advanced/events/) (see `docs/atomic/services/fastapi/lifespan-management.md`).
- Register background tasks through dependency injection rather than `asyncio.create_task` in route handlers.
- Shield startup tasks with timeouts to prevent hanging containers (`asyncio.wait_for(init(), timeout=30)`).

### Aiogram Bots

- Instantiate the Dispatcher once and reuse it; rely on Aiogram's polling/webhook loop.
- Handle shutdown signals to cancel pending updates and close HTTP sessions.
- Keep long-running business logic in dedicated services; the bot should remain responsive.

### AsyncIO Workers

- Wrap `asyncio.run(main())` in `if __name__ == "__main__"` blocks.
- Use `asyncio.TaskGroup` (Python 3.12+) or `asyncio.gather` with graceful cancellation to coordinate jobs.
- Ensure signal handlers (`SIGTERM`, `SIGINT`) set shutdown flags and await task completion before closing.

## Patterns and Anti-Patterns

| Do | Avoid |
|----|-------|
| Create connection pools during startup and reuse them. | Creating new connections on each handler invocation. |
| Use `asyncio.create_task` only inside supervised contexts (TaskGroup, background workers). | Fire-and-forget tasks without cancellation or exception handling. |
| Wrap long CPU-bound operations in `run_in_executor`. | Blocking the loop with synchronous heavy computations. |
| Propagate cancellation (use `asyncio.current_task().cancel()`). | Swallowing `CancelledError`, which prevents clean shutdown. |

## Observability

- Emit metrics for event loop lag (`uvloop.loop.time() - asyncio.get_running_loop().time()` samples) to detect blocking calls.
- Use structured logging for lifecycle events (startup, shutdown, signal received, task cancelled).
- Trace background tasks with manual spans when they are long-lived jobs.

## Troubleshooting Checklist

1. Check for blocking stack traces in logs (`BlockingIOError`, warnings from `asyncio`).
2. Confirm only one loop is running (`asyncio.get_running_loop()` from debug endpoints).
3. Verify connection pools are closed on shutdown (use `atexit` or lifespan hooks).
4. In workers, assert that `TaskGroup` exits cleanly and no tasks remain pending in debug logs.

## Related Documents

- `docs/atomic/services/fastapi/lifespan-management.md`
- `docs/atomic/services/asyncio-workers/signal-handling.md`
- `docs/atomic/integrations/rabbitmq/asyncio-integration.md`
- Legacy reference: `docs/legacy/architecture/ms_best_practices_rules.mdc`
