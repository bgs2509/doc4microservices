# Example: FastAPI Business Service

This document demonstrates the implementation of a **Business Service** using FastAPI following the "Improved Hybrid Approach" architecture. This service **has no direct database access** and implements all patterns from `docs/services/fastapi_rules.mdc` and `docs/architecture/data-access-rules.mdc`.

> **🔗 Related Examples:**
> - **Dependencies**: [PostgreSQL Data Service](./postgres_data_service.md), [MongoDB Data Service](./mongodb_data_service.md)
> - **HTTP Client**: [Shared HTTP Client Module](./shared_http_client.md) (used for all data service communication)
> - **Testing**: [Comprehensive Testing Examples](./comprehensive_testing.md#unit-testing-examples)
> - **Architecture**: [Communication Patterns](./communication_patterns.md) (HTTP + events)

## Key Characteristics
- **Responsibility:** Implementation of business logic (e.g., user management, authentication).
- **Data Access:** Only through HTTP calls to Data Services via standardized HTTP clients.
- **Infrastructure:** Redis for caching, RabbitMQ for event publishing.
- **Compliance:** RFC 7807 error handling, proper middleware, structured logging.
- **Security:** Proper password hashing, JWT authentication, input validation.

---

## 1. Project Structure (api_service)

FastAPI Business Service structure following DDD/Hexagonal architecture principles.

```
services/api_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── auth.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── middleware.py        # Request ID, correlation tracking
│   │   └── errors.py           # RFC 7807 error handling
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # Pydantic models with Field descriptions
│   │   └── errors.py          # RFC 7807 error schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py    # Business logic layer
│   │   └── auth_service.py    # Authentication & JWT handling
│   └── clients/
│       ├── __init__.py
│       ├── base_client.py     # Base HTTP client with error handling
│       └── user_data_client.py # PostgreSQL Data Service client
├── tests/
│   ├── conftest.py           # Test configuration with testcontainers
│   ├── test_user_api.py      # API endpoint tests
│   └── test_user_service.py  # Service layer tests
└── Dockerfile
```

---

## 2. HTTP Client Integration

> **🔗 IMPORTANT**: This service uses the [Shared HTTP Client Module](./shared_http_client.md) to eliminate code duplication and provide enterprise-grade features like circuit breakers, advanced retry logic, and comprehensive error handling.

For complete implementation details of the base HTTP client and DataServiceClient, see [shared_http_client.md](./shared_http_client.md).

## 3. User Data Client (`src/clients/user_data_client.py`)

Specialized client for PostgreSQL Data Service communication, extending the shared DataServiceClient.

```python
from typing import Optional, Dict, Any, List
from shared.http.base_client import DataServiceClient
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..core.config import settings

class UserDataClient(DataServiceClient):
    """Client for PostgreSQL Data Service communication."""

    def __init__(self):
        super().__init__(
            service_name="PostgreSQL Data Service",
            base_url=settings.POSTGRES_DATA_SERVICE_URL,
            timeout=settings.HTTP_CLIENT_TIMEOUT,
            retries=settings.HTTP_CLIENT_RETRIES
        )

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID from data service."""
        return await self.get_typed(
            f"/api/v1/users/{user_id}",
            UserResponse
        )

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username from data service."""
        return await self.get_typed(
            f"/api/v1/users/by-username/{username}",
            UserResponse
        )

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email from data service."""
        return await self.get_typed(
            f"/api/v1/users/by-email/{email}",
            UserResponse
        )

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> Optional[UserResponse]:
        """Create new user via data service with hashed password."""
        # Transform API schema to Data Service schema
        from shared.http.base_client import BaseModel
        from pydantic import Field

        class DataServiceUserCreate(BaseModel):
            email: str
            username: str
            hashed_password: str = Field(..., description="Already hashed password")
            full_name: Optional[str] = None
            bio: Optional[str] = None

        data_service_payload = DataServiceUserCreate(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            bio=user_data.bio
        )

        return await self.post_typed(
            "/api/v1/users",
            UserResponse,
            data_service_payload
        )

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update user via data service."""
        return await self.patch_typed(
            f"/api/v1/users/{user_id}",
            UserResponse,
            user_data
        )

    async def delete_user(self, user_id: int) -> bool:
        """Delete user via data service."""
        return await self.delete(f"/api/v1/users/{user_id}")

    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
        filter_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List users with pagination and filtering."""
        params = {"limit": limit, "offset": offset}
        if filter_active is not None:
            params["active"] = filter_active

        result = await self.get("/api/v1/users", params=params)
        if not result:
            return {"users": [], "total": 0, "limit": limit, "offset": offset}

        return {
            "users": [UserResponse(**user) for user in result["users"]],
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"]
        }

    async def verify_user_credentials(self, username: str, hashed_password: str) -> Optional[UserResponse]:
        """Verify user credentials via data service."""
        result = await self.post("/api/v1/users/verify-credentials", {
            "username": username,
            "hashed_password": hashed_password  # Fixed: use consistent naming
        })
        return UserResponse(**result) if result else None
```

---

## 4. Schemas with Validation (`src/schemas/user.py`)

Pydantic models with proper Field descriptions and validation following fastapi_rules.mdc.

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(
        ...,
        description="User's email address (must be unique)",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric, underscore, hyphen only)",
        example="john_doe"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 chars, will be hashed)",
        example="SecurePassword123!"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's full name",
        example="John Doe"
    )

    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address",
        example="newemail@example.com"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated full name",
        example="John Smith"
    )
    status: Optional[UserStatus] = Field(
        None,
        description="Updated user status"
    )

class UserResponse(BaseModel):
    """Schema for user response data."""

    id: int = Field(
        ...,
        description="Unique user identifier",
        example=123
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        description="Username",
        example="john_doe"
    )
    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        example="John Doe"
    )
    status: UserStatus = Field(
        ...,
        description="Current user status"
    )
    created_at: datetime = Field(
        ...,
        description="User creation timestamp",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp",
        example="2024-01-20T14:45:00Z"
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    users: list[UserResponse] = Field(
        ...,
        description="List of users"
    )
    total: int = Field(
        ...,
        description="Total number of users matching filters",
        example=150
    )
    limit: int = Field(
        ...,
        description="Number of users per page",
        example=20
    )
    offset: int = Field(
        ...,
        description="Number of users skipped",
        example=0
    )
    has_next: bool = Field(
        ...,
        description="Whether there are more users available"
    )
```

## 5. Error Schemas (`src/schemas/errors.py`)

RFC 7807 Problem Details schemas for consistent error handling.

```python
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details schema."""

    type: str = Field(
        ...,
        description="URI identifying the problem type",
        example="https://api.example.com/problems/validation-error"
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem",
        example="Validation Error"
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        example=400
    )
    detail: str = Field(
        ...,
        description="Human-readable explanation of the problem",
        example="The provided email address is already registered"
    )
    instance: str = Field(
        ...,
        description="URI identifying the specific occurrence of the problem",
        example="/api/v1/users/create"
    )
    errors: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
        example={"email": ["Email already exists"]}
    )

class ValidationErrorDetail(ProblemDetail):
    """Validation error with field-specific details."""

    type: str = Field(
        default="https://api.example.com/problems/validation-error",
        description="Validation error type"
    )
    title: str = Field(
        default="Validation Error",
        description="Validation error title"
    )
    status: int = Field(
        default=422,
        description="Unprocessable Entity status"
    )
```

---

## 6. Authentication Service (`src/services/auth_service.py`)

Proper password hashing and JWT handling following security best practices.

```python
import logging
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from ..core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service with proper password hashing and JWT handling."""

    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
```

## 7. User Service (`src/services/user_service.py`)

Business logic layer with proper caching, event publishing, and error handling.

```python
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import orjson
import aio_pika
import redis.asyncio as redis

from ..schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from ..clients.user_data_client import UserDataClient
from ..services.auth_service import AuthService
from ..core.exceptions import UserNotFoundError, UserAlreadyExistsError

logger = logging.getLogger(__name__)

class UserService:
    """User business logic service."""

    def __init__(
        self,
        user_client: UserDataClient,
        auth_service: AuthService,
        redis_client: redis.Redis,
        rabbitmq_channel: aio_pika.Channel
    ):
        self.user_client = user_client
        self.auth_service = auth_service
        self.redis_client = redis_client
        self.rabbitmq_channel = rabbitmq_channel
        self.cache_ttl = 3600  # 1 hour

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create new user with proper validation and security."""
        # Check if user already exists
        existing_user = await self.user_client.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

        existing_username = await self.user_client.get_user_by_username(user_data.username)
        if existing_username:
            raise UserAlreadyExistsError(f"Username {user_data.username} is already taken")

        # Hash password securely
        hashed_password = self.auth_service.hash_password(user_data.password)

        # Create user via data service with properly transformed data
        created_user = await self.user_client.create_user(user_data, hashed_password)
        if not created_user:
            raise RuntimeError("Failed to create user")

        # Cache the new user
        await self._cache_user(created_user)

        # Publish user creation event
        await self._publish_user_event("user.created", created_user.model_dump())

        logger.info(f"User created successfully", extra={
            "user_id": created_user.id,
            "username": created_user.username
        })

        return created_user

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID with caching."""
        # Try cache first
        cached_user = await self._get_cached_user(user_id)
        if cached_user:
            return cached_user

        # Get from data service
        user = await self.user_client.get_user_by_id(user_id)
        if user:
            await self._cache_user(user)

        return user

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username."""
        user = await self.user_client.get_user_by_username(username)
        if user:
            await self._cache_user(user)
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user information."""
        # Verify user exists
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        # Update via data service
        updated_user = await self.user_client.update_user(user_id, user_data)
        if not updated_user:
            raise RuntimeError("Failed to update user")

        # Update cache
        await self._cache_user(updated_user)

        # Publish update event
        await self._publish_user_event("user.updated", {
            "user_id": user_id,
            "changes": user_data.model_dump(exclude_unset=True)
        })

        logger.info(f"User updated successfully", extra={
            "user_id": user_id,
            "changes": user_data.model_dump(exclude_unset=True)
        })

        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        # Verify user exists
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User with ID {user_id} not found")

        # Delete via data service
        success = await self.user_client.delete_user(user_id)
        if not success:
            return False

        # Remove from cache
        await self._remove_cached_user(user_id)

        # Publish deletion event
        await self._publish_user_event("user.deleted", {"user_id": user_id})

        logger.info(f"User deleted successfully", extra={"user_id": user_id})
        return True

    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
        filter_active: Optional[bool] = None
    ) -> UserListResponse:
        """List users with pagination."""
        result = await self.user_client.list_users(
            limit=limit,
            offset=offset,
            filter_active=filter_active
        )

        return UserListResponse(
            users=result["users"],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_next=(result["offset"] + result["limit"]) < result["total"]
        )

    async def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        """Authenticate user credentials."""
        # Hash the provided password to match against stored hash
        password_hash = self.auth_service.hash_password(password)

        # Use the data service's credential verification endpoint
        user = await self.user_client.verify_user_credentials(username, password_hash)
        if not user:
            # Try alternative verification if direct hash comparison fails
            user = await self.get_user_by_username(username)
            if user and self.auth_service.verify_password(password, user.hashed_password):
                return user
            return None

        return user

    async def _cache_user(self, user: UserResponse) -> None:
        """Cache user data."""
        cache_key = f"user:{user.id}"
        try:
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                orjson.dumps(user.model_dump())
            )
        except Exception as e:
            logger.warning(f"Failed to cache user {user.id}: {e}")

    async def _get_cached_user(self, user_id: int) -> Optional[UserResponse]:
        """Get user from cache."""
        cache_key = f"user:{user_id}"
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return UserResponse(**orjson.loads(cached_data))
        except Exception as e:
            logger.warning(f"Failed to get cached user {user_id}: {e}")
        return None

    async def _remove_cached_user(self, user_id: int) -> None:
        """Remove user from cache."""
        cache_key = f"user:{user_id}"
        try:
            await self.redis_client.delete(cache_key)
        except Exception as e:
            logger.warning(f"Failed to remove cached user {user_id}: {e}")

    async def _publish_user_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish user event to RabbitMQ."""
        try:
            message_body = orjson.dumps({
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "api_service",
                "data": event_data
            })

            message = aio_pika.Message(
                body=message_body,
                headers={"event_type": event_type}
            )

            exchange = await self.rabbitmq_channel.declare_exchange(
                "user_events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            await exchange.publish(message, routing_key=f"user.{event_type.split('.')[1]}")

            logger.info(f"Published event: {event_type}", extra={"event_data": event_data})

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
```

---

## 8. Middleware (`src/core/middleware.py`)

Request ID and correlation tracking middleware.

```python
import uuid
import logging
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

# Context variables for request tracking
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

logger = structlog.get_logger(__name__)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request ID and correlation tracking."""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID") or request_id

        # Set context variables
        request_id_token = request_id_ctx.set(request_id)
        correlation_id_token = correlation_id_ctx.set(correlation_id)

        try:
            # Process request
            response = await call_next(request)

            # Add tracking headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            logger.error(
                "Request processing failed",
                exc_info=e,
                request_id=request_id,
                correlation_id=correlation_id,
                path=request.url.path,
                method=request.method
            )
            raise

        finally:
            # Reset context variables
            request_id_ctx.reset(request_id_token)
            correlation_id_ctx.reset(correlation_id_token)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "Unhandled exception",
                exc_info=e,
                path=request.url.path,
                method=request.method
            )
            # Return proper RFC 7807 error response
            from ..core.errors import create_problem_detail
            return create_problem_detail(
                status=500,
                title="Internal Server Error",
                detail="An unexpected error occurred"
            )
```

## 9. Error Handling (`src/core/errors.py`)

RFC 7807 Problem Details error handling.

```python
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from ..schemas.errors import ProblemDetail, ValidationErrorDetail

def create_problem_detail(
    status: int,
    title: str,
    detail: str,
    type_uri: Optional[str] = None,
    instance: Optional[str] = None,
    errors: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create RFC 7807 Problem Details response."""

    if type_uri is None:
        type_uri = f"https://api.example.com/problems/{title.lower().replace(' ', '-')}"

    problem = ProblemDetail(
        type=type_uri,
        title=title,
        status=status,
        detail=detail,
        instance=instance or "",
        errors=errors
    )

    return JSONResponse(
        status_code=status,
        content=problem.model_dump(),
        headers={"Content-Type": "application/problem+json"}
    )

class UserNotFoundError(Exception):
    """User not found error."""
    pass

class UserAlreadyExistsError(Exception):
    """User already exists error."""
    pass

def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation errors."""
    return create_problem_detail(
        status=422,
        title="Validation Error",
        detail=str(exc),
        instance=str(request.url)
    )

def user_not_found_handler(request: Request, exc: UserNotFoundError) -> JSONResponse:
    """Handle user not found errors."""
    return create_problem_detail(
        status=404,
        title="User Not Found",
        detail=str(exc),
        instance=str(request.url)
    )

def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    """Handle user already exists errors."""
    return create_problem_detail(
        status=409,
        title="User Already Exists",
        detail=str(exc),
        instance=str(request.url)
    )
```

## 10. Dependencies (`src/core/dependencies.py`)

Dependency injection for services and clients.

```python
from typing import AsyncGenerator
from fastapi import Depends
import redis.asyncio as redis
import aio_pika

from ..core.config import settings
from ..clients.user_data_client import UserDataClient
from ..services.user_service import UserService
from ..services.auth_service import AuthService

# Global connections (initialized in lifespan)
_redis_client: redis.Redis = None
_rabbitmq_channel: aio_pika.Channel = None

def get_redis_client() -> redis.Redis:
    """Get Redis client dependency."""
    return _redis_client

def get_rabbitmq_channel() -> aio_pika.Channel:
    """Get RabbitMQ channel dependency."""
    return _rabbitmq_channel

def get_user_data_client() -> UserDataClient:
    """Get user data client dependency."""
    return UserDataClient()

def get_auth_service() -> AuthService:
    """Get authentication service dependency."""
    return AuthService()

def get_user_service(
    user_client: UserDataClient = Depends(get_user_data_client),
    auth_service: AuthService = Depends(get_auth_service),
    redis_client: redis.Redis = Depends(get_redis_client),
    rabbitmq_channel: aio_pika.Channel = Depends(get_rabbitmq_channel)
) -> UserService:
    """Get user service dependency."""
    return UserService(
        user_client=user_client,
        auth_service=auth_service,
        redis_client=redis_client,
        rabbitmq_channel=rabbitmq_channel
    )
```

## 11. Main Application (`src/main.py`)

FastAPI application with proper middleware, error handling, and dependency management.

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import aio_pika
import structlog

from .core.config import settings
from .core.middleware import RequestTrackingMiddleware, ErrorHandlingMiddleware
from .core.errors import (
    user_not_found_handler,
    user_already_exists_handler,
    validation_error_handler,
    UserNotFoundError,
    UserAlreadyExistsError
)
from .core import dependencies
from .api.v1 import users, auth

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting API service...")

    # Initialize Redis
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        retry_on_timeout=True,
        socket_keepalive=True,
        socket_keepalive_options={}
    )
    dependencies._redis_client = redis_client

    # Initialize RabbitMQ
    rabbitmq_connection = await aio_pika.connect_robust(
        settings.RABBITMQ_URL,
        heartbeat=30,
        blocked_connection_timeout=30
    )
    rabbitmq_channel = await rabbitmq_connection.channel()
    await rabbitmq_channel.set_qos(prefetch_count=100)
    dependencies._rabbitmq_channel = rabbitmq_channel

    logger.info("API service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down API service...")
    await redis_client.close()
    await rabbitmq_connection.close()
    logger.info("API service shutdown complete")

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="User Management API Service",
        description="Business service for user management with HTTP-only data access",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestTrackingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

    # Add exception handlers
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(ValueError, validation_error_handler)

    # Include routers
    app.include_router(
        users.router,
        prefix="/api/v1/users",
        tags=["Users"]
    )
    app.include_router(
        auth.router,
        prefix="/api/v1/auth",
        tags=["Authentication"]
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "api_service",
            "version": "1.0.0"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # Use structlog configuration
    )
```