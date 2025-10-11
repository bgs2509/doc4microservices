# Idempotency Patterns

RabbitMQ guarantees at-least-once delivery; consumers must handle duplicates gracefully.

## Strategies

- **Deduplication store** – persist processed message IDs (Redis, database). Skip processing when ID already exists.
- **Transactional outbox** – write events to an outbox table within the same transaction as state changes, then publish once; consumers treat events as authoritative.
- **Message versioning** – include `event_id` and `event_version` so consumers can ignore stale updates.

## Implementation

```python
async def process_event(event, redis):
    key = f"events:processed:{event.event_id}"
    is_new = await redis.setnx(key, "1")
    if not is_new:
        return
    await redis.expire(key, 24 * 3600)
    await handler(event)
```

## Considerations

- Ensure deduplication keys expire eventually to prevent unbounded storage.
- Keep deduplication atomic; use Redis transactions or Lua when incrementing counters.
- Log duplicate detections to aid debugging.

## Related Documents

- `docs/atomic/integrations/redis/idempotency-patterns.md`
- `docs/atomic/services/asyncio-workers/task-management.md`
