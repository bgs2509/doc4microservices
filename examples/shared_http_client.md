# Shared HTTP Client Module

This document provides a reusable HTTP client module that eliminates duplication across service examples and implements all patterns from the Improved Hybrid Approach architecture.

## Purpose

Instead of duplicating HTTP client code in each service example, this shared module provides:
- **Standardized error handling** with RFC 7807 compliance
- **Request correlation** with proper Request ID propagation
- **Retry logic** with exponential backoff
- **Circuit breaker patterns** for resilience
- **Performance optimization** with connection pooling
- **Type safety** with full async/await support

---

## Shared HTTP Client Implementation

### Base HTTP Client (`shared/http/base_client.py`)

```python
"""
Shared HTTP Client Module for Improved Hybrid Approach Architecture.

Provides standardized HTTP communication between business services and data services
with proper error handling, retries, and observability integration.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, TypeVar, Generic
from contextvars import ContextVar
from datetime import datetime, timedelta
from enum import Enum

import httpx
import orjson
from pydantic import BaseModel, Field

# Context variable for request ID (set by middleware)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class HTTPMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class HTTPTimeoutError(HTTPClientError):
    """HTTP timeout error."""
    pass

class HTTPServiceUnavailableError(HTTPClientError):
    """Service unavailable error."""
    pass

class HTTPValidationError(HTTPClientError):
    """Validation error from API."""
    pass

class HTTPNotFoundError(HTTPClientError):
    """Resource not found error."""
    pass

class HTTPConflictError(HTTPClientError):
    """Resource conflict error."""
    pass

class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = HTTPClientError
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise HTTPServiceUnavailableError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        """Handle successful request."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class RequestMetrics:
    """Request metrics tracking."""

    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.request_size: int = 0
        self.response_size: int = 0
        self.status_code: Optional[int] = None

    def start(self):
        """Start timing request."""
        self.start_time = datetime.utcnow()

    def end(self, status_code: int, response_size: int = 0):
        """End timing request."""
        self.end_time = datetime.utcnow()
        self.status_code = status_code
        self.response_size = response_size

    @property
    def duration_ms(self) -> Optional[float]:
        """Get request duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

class BaseHTTPClient:
    """
    Base HTTP client with standardized error handling, retries, and observability.

    Features:
    - RFC 7807 error response handling
    - Request correlation with Request ID propagation
    - Exponential backoff retry logic
    - Circuit breaker pattern for resilience
    - Connection pooling and timeouts
    - Performance metrics collection
    - Type-safe response handling
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        retries: int = 3,
        retry_backoff_factor: float = 2.0,
        max_retry_delay: float = 60.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff_factor = retry_backoff_factor
        self.max_retry_delay = max_retry_delay

        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=circuit_breaker_timeout
        )

        # HTTP client configuration
        self.client_config = {
            "timeout": httpx.Timeout(timeout),
            "limits": httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            ),
            "follow_redirects": True
        }

    def _get_request_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build standard request headers with correlation IDs."""
        request_id = request_id_ctx.get() or "unknown"
        correlation_id = correlation_id_ctx.get() or request_id

        headers = {
            "X-Request-ID": request_id,
            "X-Correlation-ID": correlation_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "BusinessService-HTTPClient/1.0"
        }

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _parse_error_response(self, response: httpx.Response) -> HTTPClientError:
        """Parse error response and create appropriate exception."""
        try:
            error_data = response.json()

            # Check for RFC 7807 Problem Details format
            if isinstance(error_data, dict) and "type" in error_data:
                message = error_data.get("detail", error_data.get("title", "API Error"))

                # Map HTTP status codes to specific exceptions
                if response.status_code == 404:
                    return HTTPNotFoundError(message, response.status_code, error_data)
                elif response.status_code == 409:
                    return HTTPConflictError(message, response.status_code, error_data)
                elif response.status_code == 422:
                    return HTTPValidationError(message, response.status_code, error_data)
                elif response.status_code >= 500:
                    return HTTPServiceUnavailableError(message, response.status_code, error_data)
                else:
                    return HTTPClientError(message, response.status_code, error_data)
            else:
                # Non-RFC 7807 error response
                message = str(error_data) if error_data else f"HTTP {response.status_code}"
                return HTTPClientError(message, response.status_code, error_data)

        except (ValueError, TypeError):
            # Failed to parse JSON error response
            message = f"HTTP {response.status_code}: {response.text[:200]}"
            return HTTPClientError(message, response.status_code)

    async def _make_request_with_retries(
        self,
        method: HTTPMethod,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and circuit breaker."""

        async def _single_request():
            return await self._make_single_request(method, endpoint, **kwargs)

        # Use circuit breaker
        return await self.circuit_breaker.call(_single_request)

    async def _make_single_request(
        self,
        method: HTTPMethod,
        endpoint: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make single HTTP request with proper error handling."""
        url = f"{self.base_url}{endpoint}"
        request_id = request_id_ctx.get() or "unknown"

        # Setup headers
        headers = self._get_request_headers(kwargs.get("headers"))
        kwargs["headers"] = headers

        # Initialize metrics
        metrics = RequestMetrics()
        metrics.start()

        # Calculate request size for metrics
        if "json" in kwargs:
            metrics.request_size = len(orjson.dumps(kwargs["json"]))
        elif "data" in kwargs:
            metrics.request_size = len(str(kwargs["data"]))

        for attempt in range(self.retries + 1):
            try:
                logger.debug(
                    f"Making {method} request to {url}",
                    extra={
                        "request_id": request_id,
                        "attempt": attempt + 1,
                        "max_attempts": self.retries + 1,
                        "url": url,
                        "method": method
                    }
                )

                async with httpx.AsyncClient(**self.client_config) as client:
                    response = await client.request(method.value, url, **kwargs)

                    # Update metrics
                    response_size = len(response.content) if response.content else 0
                    metrics.end(response.status_code, response_size)

                    # Log request metrics
                    logger.info(
                        f"{method} {url} - {response.status_code}",
                        extra={
                            "request_id": request_id,
                            "method": method,
                            "url": url,
                            "status_code": response.status_code,
                            "duration_ms": metrics.duration_ms,
                            "request_size": metrics.request_size,
                            "response_size": metrics.response_size,
                            "attempt": attempt + 1
                        }
                    )

                    # Handle different response types
                    if response.status_code == 404:
                        return None

                    if response.status_code == 204:
                        return {}

                    # Handle error responses
                    if response.status_code >= 400:
                        error = self._parse_error_response(response)

                        # Don't retry client errors (4xx), except 429 (rate limit)
                        if 400 <= response.status_code < 500 and response.status_code != 429:
                            logger.error(
                                f"Client error: {error}",
                                extra={
                                    "request_id": request_id,
                                    "status_code": response.status_code,
                                    "url": url,
                                    "attempt": attempt + 1
                                }
                            )
                            raise error

                        # Retry server errors (5xx) and rate limits (429)
                        if attempt == self.retries:
                            logger.error(
                                f"Server error after {self.retries + 1} attempts: {error}",
                                extra={
                                    "request_id": request_id,
                                    "status_code": response.status_code,
                                    "url": url,
                                    "final_attempt": True
                                }
                            )
                            raise error
                        else:
                            logger.warning(
                                f"Server error, will retry: {error}",
                                extra={
                                    "request_id": request_id,
                                    "status_code": response.status_code,
                                    "url": url,
                                    "attempt": attempt + 1,
                                    "retries_left": self.retries - attempt
                                }
                            )

                    else:
                        # Success response
                        response.raise_for_status()

                        # Parse JSON response
                        try:
                            return response.json()
                        except ValueError:
                            # Non-JSON response, return empty dict for success
                            return {}

            except httpx.TimeoutException as e:
                if attempt == self.retries:
                    logger.error(
                        f"Request timeout after {self.retries + 1} attempts",
                        extra={
                            "request_id": request_id,
                            "url": url,
                            "timeout": self.timeout,
                            "error": str(e)
                        }
                    )
                    raise HTTPTimeoutError(f"Request timeout: {url}")
                else:
                    logger.warning(
                        f"Request timeout, will retry",
                        extra={
                            "request_id": request_id,
                            "url": url,
                            "attempt": attempt + 1,
                            "retries_left": self.retries - attempt
                        }
                    )

            except httpx.HTTPStatusError as e:
                # Already handled above, but catch any that slip through
                if attempt == self.retries or 400 <= e.response.status_code < 500:
                    raise HTTPClientError(f"HTTP error: {e}")

            except Exception as e:
                logger.error(
                    f"Unexpected error: {e}",
                    extra={
                        "request_id": request_id,
                        "url": url,
                        "attempt": attempt + 1,
                        "error": str(e)
                    }
                )
                if attempt == self.retries:
                    raise HTTPClientError(f"Unexpected error: {e}")

            # Exponential backoff for retries
            if attempt < self.retries:
                delay = min(
                    self.retry_backoff_factor ** attempt,
                    self.max_retry_delay
                )
                logger.debug(
                    f"Retrying in {delay}s",
                    extra={
                        "request_id": request_id,
                        "delay_seconds": delay,
                        "attempt": attempt + 1
                    }
                )
                await asyncio.sleep(delay)

        return None

    # Public HTTP methods
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        return await self._make_request_with_retries(
            HTTPMethod.GET,
            endpoint,
            params=params,
            headers=headers
        )

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        return await self._make_request_with_retries(
            HTTPMethod.POST,
            endpoint,
            data=data,
            json=json,
            headers=headers
        )

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make PUT request."""
        return await self._make_request_with_retries(
            HTTPMethod.PUT,
            endpoint,
            data=data,
            json=json,
            headers=headers
        )

    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make PATCH request."""
        return await self._make_request_with_retries(
            HTTPMethod.PATCH,
            endpoint,
            data=data,
            json=json,
            headers=headers
        )

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Make DELETE request."""
        result = await self._make_request_with_retries(
            HTTPMethod.DELETE,
            endpoint,
            headers=headers
        )
        return result is not None

    # Type-safe methods for Pydantic models
    async def get_typed(
        self,
        endpoint: str,
        response_model: type[T],
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[T]:
        """Make GET request with typed response."""
        response_data = await self.get(endpoint, params, headers)
        if response_data is None:
            return None
        return response_model(**response_data)

    async def post_typed(
        self,
        endpoint: str,
        response_model: type[T],
        data: Optional[BaseModel] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[T]:
        """Make POST request with typed request/response."""
        json_data = data.dict() if data else None
        response_data = await self.post(endpoint, json=json_data, headers=headers)
        if response_data is None:
            return None
        return response_model(**response_data)

    async def put_typed(
        self,
        endpoint: str,
        response_model: type[T],
        data: Optional[BaseModel] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[T]:
        """Make PUT request with typed request/response."""
        json_data = data.dict() if data else None
        response_data = await self.put(endpoint, json=json_data, headers=headers)
        if response_data is None:
            return None
        return response_model(**response_data)

    async def patch_typed(
        self,
        endpoint: str,
        response_model: type[T],
        data: Optional[BaseModel] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[T]:
        """Make PATCH request with typed request/response."""
        json_data = data.dict(exclude_unset=True) if data else None
        response_data = await self.patch(endpoint, json=json_data, headers=headers)
        if response_data is None:
            return None
        return response_model(**response_data)

class DataServiceClient(BaseHTTPClient):
    """Base class for data service clients."""

    def __init__(self, service_name: str, base_url: str, **kwargs):
        super().__init__(base_url, **kwargs)
        self.service_name = service_name

    async def health_check(self) -> Dict[str, Any]:
        """Check data service health."""
        try:
            response = await self.get("/health")
            return response or {"status": "unknown"}
        except Exception as e:
            logger.error(f"{self.service_name} health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def readiness_check(self) -> bool:
        """Check data service readiness."""
        try:
            response = await self.get("/ready")
            return response is not None and response.get("status") == "ready"
        except Exception:
            return False
```

---

## Usage Examples

### Using the Shared Client in Business Services

#### 1. FastAPI Service Integration (`api_service/src/clients/data_clients.py`)

```python
"""Data service clients using shared HTTP client module."""

from typing import Optional, List, Dict, Any
from shared.http.base_client import DataServiceClient, HTTPNotFoundError
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..core.config import settings

class UserDataClient(DataServiceClient):
    """Client for PostgreSQL data service."""

    def __init__(self):
        super().__init__(
            service_name="PostgreSQL Data Service",
            base_url=settings.POSTGRES_DATA_SERVICE_URL,
            timeout=settings.HTTP_CLIENT_TIMEOUT,
            retries=settings.HTTP_CLIENT_RETRIES
        )

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        try:
            return await self.get_typed(
                f"/api/v1/users/{user_id}",
                UserResponse
            )
        except HTTPNotFoundError:
            return None

    async def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Create new user."""
        return await self.post_typed(
            "/api/v1/users",
            UserResponse,
            user_data
        )

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user."""
        return await self.patch_typed(
            f"/api/v1/users/{user_id}",
            UserResponse,
            user_data
        )

    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        return await self.delete(f"/api/v1/users/{user_id}")

class AnalyticsDataClient(DataServiceClient):
    """Client for MongoDB data service."""

    def __init__(self):
        super().__init__(
            service_name="MongoDB Data Service",
            base_url=settings.MONGODB_DATA_SERVICE_URL,
            timeout=settings.HTTP_CLIENT_TIMEOUT,
            retries=settings.HTTP_CLIENT_RETRIES
        )

    async def track_event(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Track analytics event."""
        response = await self.post(
            "/api/v1/analytics/events",
            json=event_data
        )
        return response.get("id") if response else None

    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get user analytics summary."""
        response = await self.get(f"/api/v1/analytics/users/{user_id}")
        return response or {}
```

#### 2. Dependency Injection in FastAPI (`api_service/src/core/dependencies.py`)

```python
"""Dependency injection for data service clients."""

from functools import lru_cache
from .data_clients import UserDataClient, AnalyticsDataClient

@lru_cache()
def get_user_data_client() -> UserDataClient:
    """Get PostgreSQL data service client."""
    return UserDataClient()

@lru_cache()
def get_analytics_data_client() -> AnalyticsDataClient:
    """Get MongoDB data service client."""
    return AnalyticsDataClient()
```

#### 3. Using in FastAPI Endpoints (`api_service/src/api/v1/users.py`)

```python
"""User management endpoints using shared HTTP client."""

from fastapi import APIRouter, Depends, HTTPException
from ...clients.data_clients import UserDataClient, AnalyticsDataClient
from ...core.dependencies import get_user_data_client, get_analytics_data_client
from ...schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_data_client: UserDataClient = Depends(get_user_data_client),
    analytics_client: AnalyticsDataClient = Depends(get_analytics_data_client)
):
    """Create new user with analytics tracking."""

    # Create user via PostgreSQL service
    user = await user_data_client.create_user(user_data)
    if not user:
        raise HTTPException(status_code=400, detail="Failed to create user")

    # Track user creation event via MongoDB service
    await analytics_client.track_event({
        "event_type": "user_action",
        "event_name": "user_created",
        "user_id": str(user.id),
        "properties": {"registration_method": "api"}
    })

    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_data_client: UserDataClient = Depends(get_user_data_client)
):
    """Get user by ID."""
    user = await user_data_client.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Testing the Shared Client

### Unit Tests (`tests/test_shared_http_client.py`)

```python
"""Tests for shared HTTP client module."""

import pytest
from unittest.mock import AsyncMock, patch
import httpx
from shared.http.base_client import (
    BaseHTTPClient,
    HTTPClientError,
    HTTPTimeoutError,
    HTTPNotFoundError,
    CircuitBreaker,
    CircuitBreakerState
)

@pytest.fixture
def http_client():
    """Create HTTP client for testing."""
    return BaseHTTPClient(
        base_url="http://test-service:8000",
        timeout=10.0,
        retries=2
    )

@pytest.mark.asyncio
async def test_successful_get_request(http_client):
    """Test successful GET request."""
    mock_response = {
        "id": 123,
        "name": "test_user",
        "email": "test@example.com"
    }

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock
        mock_context = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_context
        mock_context.request.return_value.status_code = 200
        mock_context.request.return_value.json.return_value = mock_response
        mock_context.request.return_value.content = b'{"data":"test"}'

        # Make request
        result = await http_client.get("/api/v1/users/123")

        # Verify
        assert result == mock_response
        mock_context.request.assert_called_once()

@pytest.mark.asyncio
async def test_not_found_returns_none(http_client):
    """Test that 404 responses return None."""
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock for 404
        mock_context = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_context
        mock_context.request.return_value.status_code = 404

        # Make request
        result = await http_client.get("/api/v1/users/999")

        # Verify
        assert result is None

@pytest.mark.asyncio
async def test_timeout_error_with_retries(http_client):
    """Test timeout error handling with retries."""
    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock to always timeout
        mock_context = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_context
        mock_context.request.side_effect = httpx.TimeoutException("Request timeout")

        # Should raise timeout error after retries
        with pytest.raises(HTTPTimeoutError):
            await http_client.get("/api/v1/users/123")

        # Should have been called retries + 1 times
        assert mock_context.request.call_count == 3  # 2 retries + 1 initial

@pytest.mark.asyncio
async def test_rfc_7807_error_handling(http_client):
    """Test RFC 7807 error response parsing."""
    error_response = {
        "type": "https://api.example.com/problems/validation-error",
        "title": "Validation Error",
        "status": 422,
        "detail": "Email address is already registered",
        "instance": "/api/v1/users"
    }

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock for validation error
        mock_context = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_context
        mock_response = mock_context.request.return_value
        mock_response.status_code = 422
        mock_response.json.return_value = error_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "422 Unprocessable Entity", request=None, response=mock_response
        )

        # Should raise typed validation error
        with pytest.raises(HTTPClientError) as exc_info:
            await http_client.post("/api/v1/users", json={"email": "test@example.com"})

        assert exc_info.value.status_code == 422
        assert "Email address is already registered" in str(exc_info.value)

@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    # Simulate failing function
    async def failing_function():
        raise HTTPClientError("Service error")

    # First failure
    with pytest.raises(HTTPClientError):
        await circuit_breaker.call(failing_function)
    assert circuit_breaker.state == CircuitBreakerState.CLOSED

    # Second failure - should open circuit
    with pytest.raises(HTTPClientError):
        await circuit_breaker.call(failing_function)
    assert circuit_breaker.state == CircuitBreakerState.OPEN

    # Third call should be blocked
    with pytest.raises(HTTPServiceUnavailableError):
        await circuit_breaker.call(failing_function)

@pytest.mark.asyncio
async def test_typed_responses(http_client):
    """Test type-safe response handling."""
    from pydantic import BaseModel

    class UserResponse(BaseModel):
        id: int
        name: str
        email: str

    mock_response = {
        "id": 123,
        "name": "test_user",
        "email": "test@example.com"
    }

    with patch("httpx.AsyncClient") as mock_client:
        # Setup mock
        mock_context = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_context
        mock_context.request.return_value.status_code = 200
        mock_context.request.return_value.json.return_value = mock_response
        mock_context.request.return_value.content = b'{"data":"test"}'

        # Make typed request
        result = await http_client.get_typed("/api/v1/users/123", UserResponse)

        # Verify type and content
        assert isinstance(result, UserResponse)
        assert result.id == 123
        assert result.name == "test_user"
        assert result.email == "test@example.com"
```

---

## Benefits of the Shared Client

### 1. **Eliminates Code Duplication**
- Single implementation of HTTP client logic
- Consistent error handling across all services
- Standardized retry and timeout behavior

### 2. **Improved Reliability**
- Built-in circuit breaker pattern
- Exponential backoff retry logic
- Proper connection pooling and timeouts

### 3. **Better Observability**
- Request correlation with Request ID propagation
- Comprehensive logging and metrics
- Performance tracking for all HTTP calls

### 4. **Type Safety**
- Type-safe methods for Pydantic models
- Compile-time error detection
- Better IDE support and autocompletion

### 5. **RFC 7807 Compliance**
- Standardized error response handling
- Proper HTTP status code mapping
- Consistent error propagation

### 6. **Easy Testing**
- Mock-friendly design
- Dependency injection support
- Comprehensive test coverage

---

## Integration Instructions

### Step 1: Update Existing Examples
Replace duplicated HTTP client code in existing examples with imports from shared module:

```python
# Instead of duplicating BaseHTTPClient code
from shared.http.base_client import DataServiceClient

class UserDataClient(DataServiceClient):
    def __init__(self):
        super().__init__(
            service_name="PostgreSQL Data Service",
            base_url=settings.DB_POSTGRES_SERVICE_URL
        )
```

### Step 2: Update Documentation
Add references to shared module in all service examples:

```markdown
## HTTP Client Integration

This service uses the shared HTTP client module for data service communication.
The complete implementation details are provided above in this document.
```

### Step 3: Testing Integration
Use shared test utilities for HTTP client testing:

```python
from shared.http.base_client import BaseHTTPClient
from tests.shared.http_client_fixtures import mock_http_client

@pytest.fixture
def data_client(mock_http_client):
    return UserDataClient()
```

This shared HTTP client module eliminates duplication while providing enterprise-grade reliability, observability, and type safety for all service-to-service communication in the Improved Hybrid Approach architecture.