# API Rate Limiting Patterns

Comprehensive guide for implementing rate limiting in external API integrations with Redis-based storage, distributed algorithms, and graceful degradation.

## Core Rate Limiting Service

```python
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import redis.asyncio as redis
from dataclasses import dataclass
import json

class RateLimitAlgorithm(Enum):
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitConfig:
    requests_per_window: int
    window_seconds: int
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    burst_requests: Optional[int] = None  # For token bucket
    recovery_seconds: Optional[int] = None  # For circuit breaker

class RateLimitService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        namespace: str = "api"
    ) -> Tuple[bool, Dict[str, any]]:
        """Check if request is within rate limits"""
        key = f"rate_limit:{namespace}:{identifier}"

        if config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._sliding_window_check(key, config)
        elif config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._token_bucket_check(key, config)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._fixed_window_check(key, config)
        else:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")

    async def _sliding_window_check(self, key: str, config: RateLimitConfig) -> Tuple[bool, Dict]:
        """Sliding window rate limiting with Redis sorted sets"""
        now = datetime.now().timestamp()
        window_start = now - config.window_seconds

        pipe = self.redis.pipeline()
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current requests
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiration
        pipe.expire(key, config.window_seconds + 10)

        results = await pipe.execute()
        current_count = results[1]

        if current_count < config.requests_per_window:
            return True, {
                "allowed": True,
                "current_count": current_count + 1,
                "limit": config.requests_per_window,
                "window_seconds": config.window_seconds,
                "reset_time": now + config.window_seconds
            }
        else:
            # Remove the request we just added since it's not allowed
            await self.redis.zrem(key, str(now))
            return False, {
                "allowed": False,
                "current_count": current_count,
                "limit": config.requests_per_window,
                "window_seconds": config.window_seconds,
                "retry_after": config.window_seconds
            }

    async def _token_bucket_check(self, key: str, config: RateLimitConfig) -> Tuple[bool, Dict]:
        """Token bucket algorithm implementation"""
        bucket_key = f"{key}:bucket"
        now = datetime.now().timestamp()

        # Get current bucket state
        bucket_data = await self.redis.get(bucket_key)
        if bucket_data:
            bucket = json.loads(bucket_data)
            last_refill = bucket["last_refill"]
            tokens = bucket["tokens"]
        else:
            last_refill = now
            tokens = config.burst_requests or config.requests_per_window

        # Calculate tokens to add
        time_passed = now - last_refill
        tokens_to_add = (time_passed / config.window_seconds) * config.requests_per_window
        tokens = min(
            config.burst_requests or config.requests_per_window,
            tokens + tokens_to_add
        )

        if tokens >= 1:
            tokens -= 1
            bucket_data = json.dumps({
                "tokens": tokens,
                "last_refill": now
            })
            await self.redis.setex(bucket_key, config.window_seconds * 2, bucket_data)

            return True, {
                "allowed": True,
                "tokens_remaining": int(tokens),
                "bucket_capacity": config.burst_requests or config.requests_per_window
            }
        else:
            return False, {
                "allowed": False,
                "tokens_remaining": 0,
                "retry_after": (1 - tokens) * (config.window_seconds / config.requests_per_window)
            }

class DistributedRateLimiter:
    """Rate limiter that works across multiple service instances"""

    def __init__(self, redis_client: redis.Redis, service_id: str):
        self.redis = redis_client
        self.service_id = service_id
        self.rate_limit_service = RateLimitService(redis_client)

    async def limit_external_api(
        self,
        api_name: str,
        endpoint: str,
        config: RateLimitConfig,
        user_id: Optional[str] = None
    ) -> Tuple[bool, Dict]:
        """Apply rate limiting for external API calls"""

        # Create hierarchical identifiers
        identifiers = [
            f"api:{api_name}",  # Global API limit
            f"api:{api_name}:endpoint:{endpoint}",  # Per-endpoint limit
        ]

        if user_id:
            identifiers.extend([
                f"user:{user_id}:api:{api_name}",  # Per-user API limit
                f"user:{user_id}:api:{api_name}:endpoint:{endpoint}"  # Per-user endpoint limit
            ])

        # Check all limits - fail if any exceeded
        for identifier in identifiers:
            allowed, info = await self.rate_limit_service.check_rate_limit(
                identifier, config, namespace="external_api"
            )
            if not allowed:
                info["failed_check"] = identifier
                return False, info

        return True, {"allowed": True, "checks_passed": len(identifiers)}
```

## API Client with Rate Limiting

```python
import aiohttp
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta

class RateLimitedAPIClient:
    """HTTP client with built-in rate limiting and retry logic"""

    def __init__(
        self,
        base_url: str,
        rate_limiter: DistributedRateLimiter,
        default_config: RateLimitConfig,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.rate_limiter = rate_limiter
        self.default_config = default_config
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def request(
        self,
        method: str,
        endpoint: str,
        user_id: Optional[str] = None,
        config: Optional[RateLimitConfig] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Make rate-limited API request with retry logic"""

        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        config = config or self.default_config
        api_name = self._extract_api_name(self.base_url)

        for attempt in range(max_retries + 1):
            # Check rate limit
            allowed, limit_info = await self.rate_limiter.limit_external_api(
                api_name, endpoint, config, user_id
            )

            if not allowed:
                if attempt == max_retries:
                    raise RateLimitExceeded(limit_info)

                # Wait before retry
                retry_after = limit_info.get("retry_after", 1)
                await asyncio.sleep(retry_after)
                continue

            try:
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                async with self.session.request(method, url, **kwargs) as response:

                    # Handle API-specific rate limit headers
                    await self._update_from_headers(response.headers, api_name)

                    if response.status == 429:  # Too Many Requests
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < max_retries:
                            await asyncio.sleep(retry_after)
                            continue
                        raise RateLimitExceeded({
                            "status": 429,
                            "retry_after": retry_after,
                            "source": "api_response"
                        })

                    response.raise_for_status()
                    return {
                        "data": await response.json(),
                        "status": response.status,
                        "headers": dict(response.headers),
                        "rate_limit_info": limit_info
                    }

            except aiohttp.ClientError as e:
                if attempt == max_retries:
                    raise APIClientError(f"Request failed after {max_retries} retries: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise APIClientError("Maximum retries exceeded")

    async def _update_from_headers(self, headers: Dict[str, str], api_name: str):
        """Update rate limit state from API response headers"""
        # Common rate limit headers
        remaining = headers.get("X-RateLimit-Remaining") or headers.get("X-Rate-Limit-Remaining")
        reset_time = headers.get("X-RateLimit-Reset") or headers.get("X-Rate-Limit-Reset")

        if remaining and reset_time:
            # Store API's reported rate limit state
            key = f"api_reported:{api_name}:state"
            state = {
                "remaining": int(remaining),
                "reset_time": int(reset_time),
                "updated_at": datetime.now().timestamp()
            }
            await self.rate_limiter.redis.setex(
                key, 3600, json.dumps(state)
            )

    def _extract_api_name(self, url: str) -> str:
        """Extract API name from base URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove common prefixes
        if domain.startswith("api."):
            domain = domain[4:]
        return domain.split('.')[0]

class RateLimitExceeded(Exception):
    def __init__(self, info: Dict[str, Any]):
        self.info = info
        super().__init__(f"Rate limit exceeded: {info}")

class APIClientError(Exception):
    pass
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import redis.asyncio as redis

app = FastAPI()

# Global rate limiter instance
rate_limiter: Optional[DistributedRateLimiter] = None

@app.on_event("startup")
async def startup_event():
    global rate_limiter
    redis_client = redis.Redis.from_url(
        "redis://localhost:6379",
        encoding="utf-8",
        decode_responses=True
    )
    rate_limiter = DistributedRateLimiter(redis_client, "template_business_api")

async def get_rate_limiter() -> DistributedRateLimiter:
    if not rate_limiter:
        raise HTTPException(500, "Rate limiter not initialized")
    return rate_limiter

async def rate_limit_middleware(
    request: Request,
    limiter: DistributedRateLimiter = Depends(get_rate_limiter)
):
    """Apply rate limiting to incoming requests"""

    # Extract client identifier
    client_ip = request.client.host
    user_id = request.headers.get("X-User-ID")  # From auth middleware

    # Configure rate limits based on endpoint
    if request.url.path.startswith("/api/external/"):
        config = RateLimitConfig(
            requests_per_window=100,
            window_seconds=3600,  # 100 requests per hour
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )
    else:
        config = RateLimitConfig(
            requests_per_window=1000,
            window_seconds=3600,  # 1000 requests per hour
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )

    # Check rate limit
    identifier = user_id or client_ip
    allowed, info = await limiter.rate_limit_service.check_rate_limit(
        identifier, config, namespace="incoming"
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(int(info.get("retry_after", 60))),
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(info.get("reset_time", 0)))
            }
        )

    return info

@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit information to response headers"""

    try:
        # Get rate limit info if available
        rate_info = getattr(request.state, "rate_limit_info", None)
        response = await call_next(request)

        if rate_info:
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(
                rate_info["limit"] - rate_info["current_count"]
            )
            if "reset_time" in rate_info:
                response.headers["X-RateLimit-Reset"] = str(int(rate_info["reset_time"]))

        return response

    except Exception as e:
        # Don't let rate limiting break the application
        return await call_next(request)
```

## External API Integration Examples

```python
# Stripe API with rate limiting
class StripeRateLimitedClient(RateLimitedAPIClient):
    def __init__(self, api_key: str, rate_limiter: DistributedRateLimiter):
        config = RateLimitConfig(
            requests_per_window=100,  # Stripe allows 100 req/sec
            window_seconds=1,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            burst_requests=25  # Allow bursts up to 25
        )
        super().__init__(
            "https://api.stripe.com/v1",
            rate_limiter,
            config
        )
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def create_payment_intent(self, amount: int, currency: str, user_id: str):
        return await self.request(
            "POST",
            "payment_intents",
            user_id=user_id,
            json={
                "amount": amount,
                "currency": currency
            },
            headers=self.headers
        )

# SendGrid API with rate limiting
class SendGridRateLimitedClient(RateLimitedAPIClient):
    def __init__(self, api_key: str, rate_limiter: DistributedRateLimiter):
        config = RateLimitConfig(
            requests_per_window=600,  # SendGrid free tier
            window_seconds=60,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )
        super().__init__(
            "https://api.sendgrid.com/v3",
            rate_limiter,
            config
        )
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def send_email(self, to_email: str, subject: str, content: str, user_id: str):
        return await self.request(
            "POST",
            "mail/send",
            user_id=user_id,
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": "noreply@example.com"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": content}]
            },
            headers=self.headers
        )
```

## Circuit Breaker Integration

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerRateLimiter:
    """Combines rate limiting with circuit breaker pattern"""

    def __init__(self, rate_limiter: DistributedRateLimiter):
        self.rate_limiter = rate_limiter

    async def check_with_circuit_breaker(
        self,
        api_name: str,
        endpoint: str,
        config: RateLimitConfig,
        user_id: Optional[str] = None,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit with circuit breaker protection"""

        circuit_key = f"circuit:{api_name}:{endpoint}"

        # Check circuit state
        circuit_data = await self.rate_limiter.redis.get(circuit_key)
        if circuit_data:
            circuit = json.loads(circuit_data)
            state = CircuitState(circuit["state"])

            if state == CircuitState.OPEN:
                # Check if recovery period has passed
                open_time = datetime.fromisoformat(circuit["open_time"])
                if datetime.now() - open_time > timedelta(seconds=recovery_timeout):
                    # Move to half-open
                    circuit["state"] = CircuitState.HALF_OPEN.value
                    await self.rate_limiter.redis.setex(
                        circuit_key, recovery_timeout * 2, json.dumps(circuit)
                    )
                else:
                    return False, {
                        "allowed": False,
                        "reason": "circuit_breaker_open",
                        "retry_after": recovery_timeout
                    }

        # Apply rate limiting
        allowed, rate_info = await self.rate_limiter.limit_external_api(
            api_name, endpoint, config, user_id
        )

        if not allowed:
            # Increment failure count
            await self._record_failure(circuit_key, failure_threshold)

        return allowed, rate_info

    async def _record_failure(self, circuit_key: str, failure_threshold: int):
        """Record API failure and potentially open circuit"""
        failure_key = f"{circuit_key}:failures"

        # Increment failure count
        failures = await self.rate_limiter.redis.incr(failure_key)
        await self.rate_limiter.redis.expire(failure_key, 300)  # 5 minute window

        if failures >= failure_threshold:
            # Open circuit breaker
            circuit_data = {
                "state": CircuitState.OPEN.value,
                "open_time": datetime.now().isoformat(),
                "failure_count": failures
            }
            await self.rate_limiter.redis.setex(
                circuit_key, 3600, json.dumps(circuit_data)
            )
```

## Testing Rate Limiting

```python
import pytest
import redis.asyncio as redis
from unittest.mock import AsyncMock

@pytest.fixture
async def redis_client():
    client = redis.Redis.from_url("redis://localhost:6379/15")  # Test DB
    yield client
    await client.flushdb()  # Clean up
    await client.close()

@pytest.fixture
async def rate_limiter(redis_client):
    return DistributedRateLimiter(redis_client, "test-service")

class TestRateLimiting:

    async def test_sliding_window_allows_requests_within_limit(self, rate_limiter):
        config = RateLimitConfig(
            requests_per_window=5,
            window_seconds=60,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )

        # Should allow first 5 requests
        for i in range(5):
            allowed, info = await rate_limiter.limit_external_api(
                "test-api", "test-endpoint", config, "user123"
            )
            assert allowed
            assert info["allowed"]

    async def test_sliding_window_blocks_requests_over_limit(self, rate_limiter):
        config = RateLimitConfig(
            requests_per_window=3,
            window_seconds=60,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )

        # Allow first 3 requests
        for i in range(3):
            allowed, _ = await rate_limiter.limit_external_api(
                "test-api", "test-endpoint", config, "user123"
            )
            assert allowed

        # Block 4th request
        allowed, info = await rate_limiter.limit_external_api(
            "test-api", "test-endpoint", config, "user123"
        )
        assert not allowed
        assert not info["allowed"]
        assert "retry_after" in info

    async def test_token_bucket_allows_bursts(self, rate_limiter):
        config = RateLimitConfig(
            requests_per_window=5,
            window_seconds=60,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            burst_requests=10
        )

        # Should allow burst up to 10 requests
        for i in range(10):
            allowed, info = await rate_limiter.limit_external_api(
                "test-api", "test-endpoint", config, "user123"
            )
            assert allowed

        # 11th request should be blocked
        allowed, info = await rate_limiter.limit_external_api(
            "test-api", "test-endpoint", config, "user123"
        )
        assert not allowed

    async def test_different_users_have_separate_limits(self, rate_limiter):
        config = RateLimitConfig(
            requests_per_window=2,
            window_seconds=60,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW
        )

        # User 1 uses up their limit
        for i in range(2):
            allowed, _ = await rate_limiter.limit_external_api(
                "test-api", "test-endpoint", config, "user1"
            )
            assert allowed

        # User 1's next request should be blocked
        allowed, _ = await rate_limiter.limit_external_api(
            "test-api", "test-endpoint", config, "user1"
        )
        assert not allowed

        # User 2 should still be allowed
        allowed, _ = await rate_limiter.limit_external_api(
            "test-api", "test-endpoint", config, "user2"
        )
        assert allowed

@pytest.mark.asyncio
async def test_rate_limited_client_retries_on_429():
    # Mock session that returns 429 then 200
    mock_session = AsyncMock()
    mock_response_429 = AsyncMock()
    mock_response_429.status = 429
    mock_response_429.headers = {"Retry-After": "1"}

    mock_response_200 = AsyncMock()
    mock_response_200.status = 200
    mock_response_200.json.return_value = {"success": True}
    mock_response_200.headers = {}

    mock_session.request.side_effect = [
        AsyncMock(__aenter__=AsyncMock(return_value=mock_response_429)),
        AsyncMock(__aenter__=AsyncMock(return_value=mock_response_200))
    ]

    redis_client = AsyncMock()
    rate_limiter = DistributedRateLimiter(redis_client, "test")
    rate_limiter.limit_external_api = AsyncMock(return_value=(True, {"allowed": True}))

    client = RateLimitedAPIClient(
        "https://api.example.com",
        rate_limiter,
        RateLimitConfig(10, 60)
    )
    client.session = mock_session

    # Should retry and succeed
    result = await client.request("GET", "test", max_retries=2)
    assert result["data"]["success"]
    assert mock_session.request.call_count == 2
```

## Related Documentation

- [Authentication & Authorization Guide](../security/authentication-authorization-guide.md) - JWT tokens and user authentication
- [Payment Gateway Integration](payment-gateways.md) - Rate-limited payment processing
- [Communication APIs](communication-apis.md) - Email/SMS rate limiting
- [Webhook Handling](webhook-handling.md) - Webhook rate protection

## Implementation Notes

1. **Redis Storage**: All rate limiting state stored in Redis for distributed consistency
2. **Algorithm Selection**: Choose based on API characteristics and traffic patterns
3. **Circuit Breaker**: Prevents cascade failures when APIs are down
4. **Header Integration**: Respects API-provided rate limit headers
5. **Testing**: Comprehensive test coverage for all algorithms and edge cases
6. **Monitoring**: Log rate limit violations for capacity planning

## Related Documents

- `docs/atomic/services/fastapi/basic-setup.md` — FastAPI service configuration
- `docs/atomic/infrastructure/redis.md` — Redis for rate limit counters
- `docs/atomic/services/fastapi/middleware-configuration.md` — Middleware setup
- `docs/atomic/observability/metrics/service-metrics.md` — Rate limit metrics
