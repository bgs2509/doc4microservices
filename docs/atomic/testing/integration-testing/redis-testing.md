# Redis Integration Testing

Test Redis caching, idempotency keys, distributed locks, and pub/sub messaging with real Redis containers to verify cache behavior, TTL expiration, and concurrent access patterns. Integration tests catch timing issues, serialization errors, and race conditions that mocks cannot detect.

This document covers caching patterns, idempotency enforcement, distributed locking, TTL verification, and pub/sub testing with testcontainers-python. Redis integration tests ensure cache invalidation works correctly and concurrent operations maintain data consistency.

Redis testing validates that cache keys expire correctly, idempotency prevents duplicate operations, and distributed locks coordinate access across multiple processes. These tests run against real Redis to catch protocol-specific issues.

## Cache Testing

### Basic Cache Operations

```python
# tests/integration/test_redis_cache.py
import pytest
from finance_lending_api.services.cache import CacheService


@pytest.mark.integration
async def test_cache_set_and_get(redis_client):
    """Test setting and retrieving cached values."""
    cache = CacheService(redis_client)

    # Set value
    await cache.set("user:123", {"id": "123", "name": "John"}, ttl=60)

    # Get value
    result = await cache.get("user:123")

    assert result is not None
    assert result["id"] == "123"
    assert result["name"] == "John"


@pytest.mark.integration
async def test_cache_miss_returns_none(redis_client):
    """Test that cache miss returns None."""
    cache = CacheService(redis_client)

    result = await cache.get("nonexistent:key")
    assert result is None


@pytest.mark.integration
async def test_cache_delete(redis_client):
    """Test deleting cached value."""
    cache = CacheService(redis_client)

    # Set value
    await cache.set("temp:key", "value")

    # Verify exists
    assert await cache.get("temp:key") == "value"

    # Delete
    await cache.delete("temp:key")

    # Verify deleted
    assert await cache.get("temp:key") is None
```

### TTL and Expiration

```python
# CORRECT: Test cache expiration
@pytest.mark.integration
async def test_cache_expiration(redis_client):
    """Test that cached values expire after TTL."""
    cache = CacheService(redis_client)

    # Set with 1 second TTL
    await cache.set("expire:key", "value", ttl=1)

    # Value exists immediately
    assert await cache.get("expire:key") == "value"

    # Wait for expiration
    import asyncio
    await asyncio.sleep(1.5)

    # Value expired
    assert await cache.get("expire:key") is None


# CORRECT: Test TTL extension
@pytest.mark.integration
async def test_extend_ttl(redis_client):
    """Test extending TTL of cached value."""
    # Set with 2 second TTL
    await redis_client.setex("extend:key", 2, "value")

    # Wait 1 second
    import asyncio
    await asyncio.sleep(1)

    # Extend TTL by another 2 seconds
    await redis_client.expire("extend:key", 2)

    # Wait 1.5 more seconds (would have expired without extension)
    await asyncio.sleep(1.5)

    # Value still exists
    result = await redis_client.get("extend:key")
    assert result == "value"
```

### Cache Invalidation Patterns

```python
# CORRECT: Test cache invalidation on update
@pytest.mark.integration
async def test_cache_invalidation_on_user_update(redis_client, db_session):
    """Test that cache is invalidated when user is updated."""
    from finance_lending_api.services.user_service import UserService

    service = UserService(db_session=db_session, cache=redis_client)

    # Create user (cached)
    user = await service.create_user(email="test@example.com", name="John")
    user_id = user.id

    # Cache populated
    cached = await redis_client.get(f"user:{user_id}")
    assert cached is not None

    # Update user (should invalidate cache)
    await service.update_user(user_id, name="Jane")

    # Cache invalidated
    cached_after = await redis_client.get(f"user:{user_id}")
    assert cached_after is None
```

## Idempotency Key Testing

### Request Deduplication

```python
# CORRECT: Test idempotency key prevents duplicate requests
@pytest.mark.integration
async def test_idempotency_key_prevents_duplicates(redis_client):
    """Test that idempotency keys prevent duplicate operations."""
    from finance_lending_api.middleware.idempotency import IdempotencyService

    service = IdempotencyService(redis_client)
    request_id = "req-12345"

    # First request: not seen before
    is_duplicate = await service.is_duplicate(request_id)
    assert is_duplicate is False

    # Store request result
    await service.store_request(request_id, {"result": "processed", "amount": 100})

    # Second request: duplicate detected
    is_duplicate = await service.is_duplicate(request_id)
    assert is_duplicate is True

    # Get cached result
    cached_result = await service.get_result(request_id)
    assert cached_result["result"] == "processed"
    assert cached_result["amount"] == 100


# CORRECT: Test idempotency key expiration
@pytest.mark.integration
async def test_idempotency_key_expires(redis_client):
    """Test that idempotency keys expire after TTL."""
    from finance_lending_api.middleware.idempotency import IdempotencyService

    service = IdempotencyService(redis_client, ttl=1)  # 1 second TTL
    request_id = "req-expire"

    # Store request
    await service.store_request(request_id, {"result": "ok"})

    # Immediately recognized as duplicate
    assert await service.is_duplicate(request_id) is True

    # Wait for expiration
    import asyncio
    await asyncio.sleep(1.5)

    # No longer recognized as duplicate
    assert await service.is_duplicate(request_id) is False
```

## Distributed Lock Testing

### Lock Acquisition and Release

```python
# CORRECT: Test distributed lock prevents concurrent access
@pytest.mark.integration
async def test_distributed_lock(redis_client):
    """Test that distributed lock prevents concurrent access."""
    from finance_lending_api.infrastructure.redis_lock import RedisLock

    lock = RedisLock(redis_client, "resource:123", timeout=5)

    # Acquire lock
    acquired = await lock.acquire()
    assert acquired is True

    # Second attempt fails (already locked)
    lock2 = RedisLock(redis_client, "resource:123", timeout=5)
    acquired2 = await lock2.acquire()
    assert acquired2 is False

    # Release lock
    await lock.release()

    # Now can acquire
    acquired3 = await lock2.acquire()
    assert acquired3 is True
    await lock2.release()


# CORRECT: Test lock auto-expires
@pytest.mark.integration
async def test_lock_auto_expiration(redis_client):
    """Test that locks auto-expire after timeout."""
    from finance_lending_api.infrastructure.redis_lock import RedisLock

    lock = RedisLock(redis_client, "expire:lock", timeout=1)

    # Acquire lock
    await lock.acquire()

    # Wait for expiration
    import asyncio
    await asyncio.sleep(1.5)

    # Another process can acquire (lock expired)
    lock2 = RedisLock(redis_client, "expire:lock", timeout=1)
    acquired = await lock2.acquire()
    assert acquired is True
    await lock2.release()


# CORRECT: Test concurrent lock attempts
@pytest.mark.integration
async def test_concurrent_lock_acquisition(redis_client):
    """Test that only one of concurrent attempts acquires lock."""
    import asyncio
    from finance_lending_api.infrastructure.redis_lock import RedisLock

    lock_key = "concurrent:lock"
    results = []

    async def try_lock(id: int):
        lock = RedisLock(redis_client, lock_key, timeout=1)
        acquired = await lock.acquire()
        if acquired:
            results.append(f"worker-{id}")
            await asyncio.sleep(0.1)
            await lock.release()
        return acquired

    # 5 workers try to acquire lock simultaneously
    tasks = [try_lock(i) for i in range(5)]
    outcomes = await asyncio.gather(*tasks)

    # Only one worker acquired lock
    assert sum(outcomes) == 1
    assert len(results) == 1
```

## Rate Limiting Testing

```python
# CORRECT: Test rate limiting with Redis
@pytest.mark.integration
async def test_rate_limiting(redis_client):
    """Test rate limiting with sliding window."""
    from finance_lending_api.middleware.rate_limit import RateLimiter

    limiter = RateLimiter(redis_client, max_requests=3, window_seconds=1)
    user_id = "user-123"

    # First 3 requests allowed
    for i in range(3):
        allowed = await limiter.is_allowed(user_id)
        assert allowed is True

    # 4th request blocked
    allowed = await limiter.is_allowed(user_id)
    assert allowed is False

    # Wait for window to slide
    import asyncio
    await asyncio.sleep(1.1)

    # Requests allowed again
    allowed = await limiter.is_allowed(user_id)
    assert allowed is True
```

## Pub/Sub Testing

```python
# CORRECT: Test Redis pub/sub messaging
@pytest.mark.integration
async def test_pubsub_messaging(redis_client):
    """Test publishing and subscribing to Redis channels."""
    import asyncio
    import json

    channel = "events:user"
    message_received = []

    # Subscribe
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    # Subscriber task
    async def listen():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                message_received.append(data)
                break

    listener_task = asyncio.create_task(listen())

    # Small delay to ensure subscription registered
    await asyncio.sleep(0.1)

    # Publish message
    await redis_client.publish(channel, json.dumps({"event": "user_created", "user_id": "123"}))

    # Wait for message
    await asyncio.wait_for(listener_task, timeout=2)

    # Verify received
    assert len(message_received) == 1
    assert message_received[0]["event"] == "user_created"
    assert message_received[0]["user_id"] == "123"

    await pubsub.unsubscribe(channel)
    await pubsub.close()
```

## Serialization Testing

```python
# CORRECT: Test JSON serialization/deserialization
@pytest.mark.integration
async def test_cache_json_serialization(redis_client):
    """Test that complex objects are serialized correctly."""
    cache = CacheService(redis_client)

    complex_data = {
        "user": {"id": "123", "name": "John"},
        "loans": [
            {"id": "loan-1", "amount": 10000},
            {"id": "loan-2", "amount": 5000},
        ],
        "metadata": {"created_at": "2025-01-15T10:00:00Z"}
    }

    # Store
    await cache.set("complex:data", complex_data)

    # Retrieve
    retrieved = await cache.get("complex:data")

    assert retrieved["user"]["id"] == "123"
    assert len(retrieved["loans"]) == 2
    assert retrieved["loans"][0]["amount"] == 10000
    assert retrieved["metadata"]["created_at"] == "2025-01-15T10:00:00Z"
```

## Pipeline Testing

```python
# CORRECT: Test Redis pipeline for batch operations
@pytest.mark.integration
async def test_redis_pipeline(redis_client):
    """Test Redis pipeline for efficient batch operations."""
    # Create pipeline
    pipe = redis_client.pipeline()

    # Queue multiple operations
    await pipe.set("key1", "value1")
    await pipe.set("key2", "value2")
    await pipe.set("key3", "value3")
    await pipe.get("key1")
    await pipe.get("key2")

    # Execute all at once
    results = await pipe.execute()

    # All operations executed
    assert results[0] is True  # set key1
    assert results[1] is True  # set key2
    assert results[2] is True  # set key3
    assert results[3] == "value1"  # get key1
    assert results[4] == "value2"  # get key2
```

## Best Practices

### DO: Use Real Redis for Integration Tests

```python
# CORRECT: Use testcontainers Redis
@pytest.fixture(scope="module")
def redis_container():
    """Provide Redis container for integration tests."""
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7-alpine") as container:
        yield container


# INCORRECT: Using fake Redis for integration tests
import fakeredis

@pytest.fixture
def fake_redis():  # WRONG: Not testing real Redis behavior
    return fakeredis.FakeRedis()
```

### DO: Clean Redis Between Tests

```python
# CORRECT: Flush database after each test
@pytest.fixture
async def redis_client(redis_container):
    """Provide clean Redis client for each test."""
    from redis.asyncio import Redis

    client = Redis.from_url(
        redis_container.get_connection_url(),
        encoding="utf-8",
        decode_responses=True
    )

    yield client

    # Cleanup
    await client.flushdb()
    await client.close()
```

### DON'T: Share Keys Between Tests

```python
# INCORRECT: Tests share keys
@pytest.mark.integration
async def test_set_user_cache(redis_client):
    """WRONG: Uses hardcoded key."""
    await redis_client.set("user:1", "John")
    assert await redis_client.get("user:1") == "John"


@pytest.mark.integration
async def test_get_user_cache(redis_client):
    """WRONG: Depends on previous test."""
    # Assumes "user:1" exists from previous test
    assert await redis_client.get("user:1") == "John"


# CORRECT: Each test is independent
@pytest.mark.integration
async def test_user_cache_lifecycle(redis_client):
    """Test is self-contained."""
    # Set in this test
    await redis_client.set("user:test123", "John")

    # Get in this test
    assert await redis_client.get("user:test123") == "John"
```

## Checklist

- [ ] Use testcontainers for real Redis instances
- [ ] Test cache set, get, delete operations
- [ ] Test TTL expiration with asyncio.sleep
- [ ] Test idempotency key storage and checking
- [ ] Test distributed locks prevent concurrent access
- [ ] Test rate limiting with sliding windows
- [ ] Test pub/sub message delivery
- [ ] Test JSON serialization/deserialization
- [ ] Test Redis pipelines for batch operations
- [ ] Flush Redis database after each test
- [ ] Tests are independent and self-contained
- [ ] Mark integration tests with `@pytest.mark.integration`

## Related Documents

- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Setting up Docker containers for tests
- `docs/atomic/integrations/redis/connection-management.md` — Redis client configuration
- `docs/atomic/integrations/redis/caching-strategies.md` — Caching patterns
- `docs/atomic/integrations/redis/idempotency-keys.md` — Idempotency implementation
- `docs/atomic/integrations/redis/distributed-locks.md` — Distributed locking patterns
