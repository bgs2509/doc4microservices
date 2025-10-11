# Idempotency Patterns

Redis enforces idempotency for HTTP handlers, bot commands, and worker tasks.

## Workflow

1. Generate or propagate a request ID (`X-Request-ID`, message ID).
2. Build a deterministic key (`idempotency:<operation>:<request-id>`).
3. Attempt `SETNX` to reserve the operation; set TTL to expire stale entries.
4. Proceed only when the key is new; otherwise treat as duplicate and short-circuit.

```python
async def check_idempotency(redis, key: str, ttl: int = 3600) -> bool:
    if await redis.setnx(key, "processed"):
        await redis.expire(key, ttl)
        return True
    return False
```

## Considerations

- TTL should exceed the maximum expected retry window (for example, 1 hour for HTTP, a day for async workflows).
- Store metadata (status, response snapshot) when clients need deterministic replay.
- Clean up keys proactively if operations fail so that retries can proceed.

## Use Cases

- HTTP POST endpoints invoked by clients using retry logic.
- Telegram bots receiving duplicate updates because of Telegram retries.
- Workers processing messages from at-least-once queues.

## Related Documents

- `docs/atomic/integrations/redis/key-naming-conventions.md`
- `docs/atomic/services/fastapi/performance-optimization.md`
