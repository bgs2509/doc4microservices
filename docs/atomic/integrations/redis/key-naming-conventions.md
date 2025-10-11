# Redis Key Naming Conventions

Consistent keys prevent collisions and make debugging easier. Follow a three-part schema: `context:entity:identifier`.

## Rules

- **Namespaces** – prefix keys with service or bounded-context names (`chatbot:session:abc123`).
- **Identifiers** – use stable IDs (UUIDs, message IDs) rather than mutable values.
- **Separators** – use colons (`:`); avoid other delimiters to keep keys uniform.
- **Environment** – optionally prepend environment tags (`prod:`) when sharing clusters across stages.

## Examples

| Purpose | Key |
|---------|-----|
| Idempotency | `idempotency:photo_upload:550e8400-e29b-41d4-a716-446655440000` |
| Cache entry | `cache:user_profile:42` |
| Rate limiting | `ratelimit:send_message:chat:1:user:42` |

## Expiration Strategy

- Set TTL for ephemeral keys (idempotency, rate limiting, caches).
- Leave TTL unset for persistent state (feature flags) but document retention and cleanup processes.

## Tooling

- Provide helper functions to assemble keys (`build_cache_key(namespace, *parts)`).
- Validate key format in unit tests to avoid regressions.

## Related Documents

- `docs/atomic/integrations/redis/idempotency-patterns.md`
- `docs/atomic/integrations/redis/caching-strategies.md`
