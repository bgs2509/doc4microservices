# Data Serialization

Redis stores byte strings; enforce predictable serialization to preserve compatibility across services.

## Formats

- Prefer JSON for structured data; set `encoding="utf-8", decode_responses=True` on the client to store/read strings transparently.
- Use MessagePack or compressed JSON when payload size becomes a bottleneck, but document the format.
- Store small primitives (ints, floats) as plain strings; convert explicitly on read.

## Helpers

```python
import json
from typing import Any


async def cache_json(redis, key: str, value: Any, ttl: int) -> None:
    await redis.setex(key, ttl, json.dumps(value, default=str))


async def read_json(redis, key: str) -> Any | None:
    payload = await redis.get(key)
    return json.loads(payload) if payload else None
```

## Validation

- Validate payloads against Pydantic models both before writing and after reading.
- Include schema version inside the value when compatibility must be preserved across releases.

## Binary Assets

- Avoid storing large binaries directly; store references to object storage and metadata in Redis.
- If binary storage is unavoidable, use `set`/`get` with bytes and document size limits.

## Related Documents

- `docs/atomic/integrations/redis/caching-strategies.md`
- `docs/atomic/services/data-services/repository-patterns.md`
- Legacy reference: `docs/legacy/infrastructure/redis_rules.mdc`
