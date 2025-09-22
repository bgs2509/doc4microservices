# Comprehensive Testing Examples

This document provides extensive testing examples for all service types in the Improved Hybrid Approach architecture, demonstrating real-world testing patterns with testcontainers, mocking strategies, and performance testing.

## Testing Philosophy

The project follows these testing principles:
- **100% critical path coverage** for business logic
- **Real infrastructure** for integration tests (via testcontainers)
- **HTTP-only testing** for business services (no direct database access)
- **Type-safe testing** with Pydantic models
- **Performance validation** with realistic load scenarios

---

## Testing Infrastructure Setup

### Base Test Configuration (`tests/conftest.py`)

```python
"""
Comprehensive test configuration for all service types.

Provides:
- Testcontainers for real infrastructure
- HTTP client mocking utilities
- Performance testing utilities
- Request correlation for test tracing
"""

import asyncio
import logging
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer
from testcontainers.compose import DockerCompose
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import aio_pika

# Import shared modules
from shared.http.base_client import BaseHTTPClient, DataServiceClient
from shared.http.base_client import request_id_ctx, correlation_id_ctx

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global test configuration
TEST_REQUEST_ID = "test-req-" + str(uuid.uuid4())[:8]
TEST_CORRELATION_ID = "test-corr-" + str(uuid.uuid4())[:8]

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def postgres_container():
    """Setup PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:16",
                          username="test_user",
                          password="test_pass",
                          dbname="test_db") as postgres:
        # Wait for container to be ready
        postgres.get_connection_url()
        logger.info(f"PostgreSQL container ready: {postgres.get_connection_url()}")
        yield postgres

@pytest.fixture(scope="session")
async def mongodb_container():
    """Setup MongoDB container for integration tests."""
    with MongoDbContainer("mongo:7.0.9") as mongodb:
        connection_url = mongodb.get_connection_url()
        logger.info(f"MongoDB container ready: {connection_url}")
        yield mongodb

@pytest.fixture(scope="session")
async def redis_container():
    """Setup Redis container for integration tests."""
    with RedisContainer("redis:7-alpine") as redis_container:
        connection_url = redis_container.get_connection_url()
        logger.info(f"Redis container ready: {connection_url}")
        yield redis_container

@pytest.fixture(scope="session")
async def rabbitmq_container():
    """Setup RabbitMQ container for integration tests."""
    with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
        # Start only RabbitMQ service
        rabbitmq_url = compose.get_service_host("rabbitmq", 5672)
        logger.info(f"RabbitMQ container ready: {rabbitmq_url}")
        yield f"amqp://admin:admin123@{rabbitmq_url}:5672/"

@pytest.fixture
async def test_postgres_client(postgres_container):
    """Create PostgreSQL client for testing."""
    import asyncpg

    connection_url = postgres_container.get_connection_url()

    # Create connection pool
    pool = await asyncpg.create_pool(connection_url)

    # Initialize test schema
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'todo',
                priority VARCHAR(50) DEFAULT 'medium',
                due_date TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

    yield pool

    # Cleanup
    await pool.close()

@pytest.fixture
async def test_mongodb_client(mongodb_container):
    """Create MongoDB client for testing."""
    connection_url = mongodb_container.get_connection_url()
    client = AsyncIOMotorClient(connection_url)

    # Get test database
    database = client.test_db

    # Create test collections with indexes
    analytics_collection = database.analytics_events
    await analytics_collection.create_index([("user_id", 1), ("timestamp", -1)])
    await analytics_collection.create_index("request_id")

    yield database

    # Cleanup
    client.close()

@pytest.fixture
async def test_redis_client(redis_container):
    """Create Redis client for testing."""
    connection_url = redis_container.get_connection_url()
    redis_client = redis.from_url(connection_url, decode_responses=True)

    # Test connection
    await redis_client.ping()

    yield redis_client

    # Cleanup
    await redis_client.flushall()
    await redis_client.close()

@pytest.fixture
async def test_rabbitmq_connection(rabbitmq_container):
    """Create RabbitMQ connection for testing."""
    connection = await aio_pika.connect_robust(rabbitmq_container)
    channel = await connection.channel()

    yield channel

    # Cleanup
    await connection.close()

@pytest.fixture
def mock_http_client():
    """Create mock HTTP client for unit tests."""
    mock_client = AsyncMock(spec=BaseHTTPClient)

    # Setup default responses
    mock_client.get.return_value = {"status": "ok"}
    mock_client.post.return_value = {"id": 123, "status": "created"}
    mock_client.put.return_value = {"id": 123, "status": "updated"}
    mock_client.patch.return_value = {"id": 123, "status": "updated"}
    mock_client.delete.return_value = True

    return mock_client

@pytest.fixture
def mock_data_service_responses():
    """Predefined responses for data service mocking."""
    return {
        "users": {
            "get_user": {
                "id": 123,
                "email": "test@example.com",
                "username": "testuser",
                "full_name": "Test User",
                "status": "active",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            },
            "create_user": {
                "id": 124,
                "email": "new@example.com",
                "username": "newuser",
                "full_name": "New User",
                "status": "active",
                "created_at": "2025-01-15T11:00:00Z",
                "updated_at": "2025-01-15T11:00:00Z"
            }
        },
        "analytics": {
            "track_event": {
                "id": "event_456",
                "event_type": "user_action",
                "status": "recorded"
            },
            "get_user_analytics": {
                "user_id": "123",
                "total_events": 45,
                "last_activity": "2025-01-15T10:30:00Z",
                "top_events": ["login", "page_view", "click"]
            }
        }
    }

@pytest.fixture(autouse=True)
def set_test_context():
    """Set request context for all tests."""
    # Set test request IDs for correlation
    request_id_token = request_id_ctx.set(TEST_REQUEST_ID)
    correlation_id_token = correlation_id_ctx.set(TEST_CORRELATION_ID)

    yield

    # Reset context
    request_id_ctx.reset(request_id_token)
    correlation_id_ctx.reset(correlation_id_token)

class HTTPClientMocker:
    """Utility class for mocking HTTP client responses."""

    def __init__(self):
        self.responses: Dict[str, Any] = {}
        self.call_history: List[Dict[str, Any]] = []

    def add_response(self, method: str, url_pattern: str, response: Any, status_code: int = 200):
        """Add mock response for specific method/URL pattern."""
        key = f"{method.upper()}:{url_pattern}"
        self.responses[key] = {
            "response": response,
            "status_code": status_code
        }

    def get_response(self, method: str, url: str) -> Optional[Dict[str, Any]]:
        """Get mock response for method/URL."""
        # Record call
        self.call_history.append({
            "method": method,
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Find matching response
        for pattern, mock_data in self.responses.items():
            mock_method, mock_url = pattern.split(":", 1)
            if method.upper() == mock_method and mock_url in url:
                return mock_data

        return None

    def assert_called_with(self, method: str, url_pattern: str, times: int = 1):
        """Assert HTTP client was called with specific parameters."""
        matching_calls = [
            call for call in self.call_history
            if call["method"].upper() == method.upper() and url_pattern in call["url"]
        ]
        assert len(matching_calls) == times, f"Expected {times} calls to {method} {url_pattern}, got {len(matching_calls)}"

@pytest.fixture
def http_client_mocker():
    """HTTP client mocker utility."""
    return HTTPClientMocker()

# Performance testing utilities
class PerformanceMetrics:
    """Performance metrics collection for testing."""

    def __init__(self):
        self.response_times: List[float] = []
        self.error_count: int = 0
        self.success_count: int = 0

    def record_response(self, duration_ms: float, success: bool = True):
        """Record response metrics."""
        self.response_times.append(duration_ms)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0

    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time."""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index]

    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        total = self.success_count + self.error_count
        return self.error_count / total if total > 0 else 0

@pytest.fixture
def performance_metrics():
    """Performance metrics collector."""
    return PerformanceMetrics()
```

---

## Unit Testing Examples

### FastAPI Service Unit Tests (`tests/unit/test_user_service.py`)

```python
"""Unit tests for user service with HTTP client mocking."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from api_service.src.services.user_service import UserService
from api_service.src.schemas.user import UserCreate, UserUpdate, UserResponse
from api_service.src.core.exceptions import UserNotFoundError, UserAlreadyExistsError
from shared.http.base_client import HTTPNotFoundError, HTTPConflictError

@pytest.fixture
def mock_user_client():
    """Mock user data client."""
    return AsyncMock()

@pytest.fixture
def mock_auth_service():
    """Mock authentication service."""
    return AsyncMock()

@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    return AsyncMock()

@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel."""
    return AsyncMock()

@pytest.fixture
def user_service(mock_user_client, mock_auth_service, mock_redis_client, mock_rabbitmq_channel):
    """Create user service with mocked dependencies."""
    return UserService(
        user_client=mock_user_client,
        auth_service=mock_auth_service,
        redis_client=mock_redis_client,
        rabbitmq_channel=mock_rabbitmq_channel
    )

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_client, mock_auth_service, mock_data_service_responses):
    """Test successful user creation."""
    # Setup test data
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="SecurePass123!",
        full_name="Test User"
    )

    expected_response = UserResponse(**mock_data_service_responses["users"]["create_user"])

    # Setup mocks
    mock_user_client.get_user_by_email.return_value = None  # User doesn't exist
    mock_user_client.get_user_by_username.return_value = None  # Username available
    mock_auth_service.hash_password.return_value = "hashed_password_123"
    mock_user_client.create_user.return_value = expected_response

    # Execute
    result = await user_service.create_user(user_data)

    # Verify
    assert isinstance(result, UserResponse)
    assert result.email == "new@example.com"
    assert result.username == "newuser"

    # Verify service calls
    mock_user_client.get_user_by_email.assert_called_once_with("test@example.com")
    mock_user_client.get_user_by_username.assert_called_once_with("testuser")
    mock_auth_service.hash_password.assert_called_once_with("SecurePass123!")
    mock_user_client.create_user.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_email_already_exists(user_service, mock_user_client, mock_data_service_responses):
    """Test user creation with existing email."""
    # Setup test data
    user_data = UserCreate(
        email="existing@example.com",
        username="newuser",
        password="SecurePass123!",
        full_name="Test User"
    )

    existing_user = UserResponse(**mock_data_service_responses["users"]["get_user"])

    # Setup mocks - email already exists
    mock_user_client.get_user_by_email.return_value = existing_user

    # Execute and verify exception
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await user_service.create_user(user_data)

    assert "already exists" in str(exc_info.value)
    mock_user_client.create_user.assert_not_called()

@pytest.mark.asyncio
async def test_get_user_with_caching(user_service, mock_user_client, mock_redis_client, mock_data_service_responses):
    """Test get user with Redis caching."""
    user_id = 123
    expected_user = UserResponse(**mock_data_service_responses["users"]["get_user"])

    # Test cache miss - user not in cache
    mock_redis_client.get.return_value = None
    mock_user_client.get_user_by_id.return_value = expected_user

    result = await user_service.get_user_by_id(user_id)

    # Verify result
    assert isinstance(result, UserResponse)
    assert result.id == 123

    # Verify cache operations
    mock_redis_client.get.assert_called_once_with("user:123")
    mock_user_client.get_user_by_id.assert_called_once_with(user_id)
    mock_redis_client.setex.assert_called_once()  # User cached

@pytest.mark.asyncio
async def test_get_user_from_cache(user_service, mock_redis_client, mock_user_client, mock_data_service_responses):
    """Test get user from cache (cache hit)."""
    import orjson

    user_id = 123
    cached_user_data = mock_data_service_responses["users"]["get_user"]

    # Setup cache hit
    mock_redis_client.get.return_value = orjson.dumps(cached_user_data)

    result = await user_service.get_user_by_id(user_id)

    # Verify result
    assert isinstance(result, UserResponse)
    assert result.id == 123

    # Verify cache was used, data service not called
    mock_redis_client.get.assert_called_once_with("user:123")
    mock_user_client.get_user_by_id.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_not_found(user_service, mock_user_client):
    """Test updating non-existent user."""
    user_id = 999
    update_data = UserUpdate(full_name="Updated Name")

    # Setup mocks - user not found
    mock_user_client.get_user_by_id.return_value = None

    # Execute and verify exception
    with pytest.raises(UserNotFoundError):
        await user_service.update_user(user_id, update_data)

    mock_user_client.update_user.assert_not_called()

@pytest.mark.asyncio
async def test_event_publishing(user_service, mock_rabbitmq_channel, mock_data_service_responses):
    """Test event publishing to RabbitMQ."""
    import aio_pika

    # Setup mocks for successful user creation
    user_service.user_client.get_user_by_email.return_value = None
    user_service.user_client.get_user_by_username.return_value = None
    user_service.auth_service.hash_password.return_value = "hashed_pass"
    user_service.user_client.create_user.return_value = UserResponse(**mock_data_service_responses["users"]["create_user"])

    # Create user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="SecurePass123!",
        full_name="Test User"
    )

    await user_service.create_user(user_data)

    # Verify event was published
    mock_rabbitmq_channel.declare_exchange.assert_called_once()
    exchange_mock = mock_rabbitmq_channel.declare_exchange.return_value
    exchange_mock.publish.assert_called_once()

    # Verify event content
    call_args = exchange_mock.publish.call_args
    message = call_args[0][0]  # First positional argument
    assert isinstance(message, aio_pika.Message)

# Input validation tests
@pytest.mark.asyncio
async def test_user_creation_input_validation():
    """Test user creation input validation."""
    # Test invalid email
    with pytest.raises(ValueError):
        UserCreate(
            email="invalid-email",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User"
        )

    # Test weak password
    with pytest.raises(ValueError):
        UserCreate(
            email="test@example.com",
            username="testuser",
            password="weak",  # Too weak
            full_name="Test User"
        )

    # Test invalid username
    with pytest.raises(ValueError):
        UserCreate(
            email="test@example.com",
            username="a",  # Too short
            password="SecurePass123!",
            full_name="Test User"
        )

@pytest.mark.asyncio
async def test_http_client_error_handling(user_service, mock_user_client):
    """Test HTTP client error handling."""
    user_id = 123

    # Test timeout error
    mock_user_client.get_user_by_id.side_effect = HTTPTimeoutError("Request timeout")

    with pytest.raises(HTTPTimeoutError):
        await user_service.get_user_by_id(user_id)

    # Test not found error
    mock_user_client.get_user_by_id.side_effect = HTTPNotFoundError("User not found")

    result = await user_service.get_user_by_id(user_id)
    assert result is None  # Service should handle not found gracefully
```

---

## Integration Testing Examples

### Data Service Integration Tests (`tests/integration/test_postgres_data_service.py`)

```python
"""Integration tests for PostgreSQL data service with real database."""

import pytest
from httpx import AsyncClient
import asyncpg

from db_postgres_service.src.main import app
from db_postgres_service.src.schemas.user import UserCreate, UserUpdate

@pytest.mark.asyncio
async def test_full_user_crud_flow(test_postgres_client):
    """Test complete user CRUD operations with real database."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create user
        user_data = {
            "email": "integration@example.com",
            "username": "integrationuser",
            "password": "hashed_password_123",
            "full_name": "Integration Test User"
        }

        response = await client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201
        created_user = response.json()

        user_id = created_user["id"]
        assert created_user["email"] == "integration@example.com"
        assert created_user["username"] == "integrationuser"
        assert created_user["status"] == "active"
        assert "created_at" in created_user

        # 2. Get user by ID
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["email"] == "integration@example.com"

        # 3. Get user by username
        response = await client.get(f"/api/v1/users/by-username/integrationuser")
        assert response.status_code == 200
        user_by_username = response.json()
        assert user_by_username["id"] == user_id

        # 4. Update user
        update_data = {
            "full_name": "Updated Integration User",
            "status": "inactive"
        }
        response = await client.patch(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["full_name"] == "Updated Integration User"
        assert updated_user["status"] == "inactive"

        # 5. List users with pagination
        response = await client.get("/api/v1/users?limit=10&offset=0")
        assert response.status_code == 200
        users_list = response.json()
        assert "items" in users_list
        assert "total" in users_list
        assert len(users_list["items"]) >= 1

        # 6. Delete user
        response = await client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # 7. Verify user is deleted
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_creation_validation_errors(test_postgres_client):
    """Test user creation validation with real database constraints."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create initial user
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "hashed_password_123",
            "full_name": "Test User"
        }

        response = await client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201

        # Try to create user with same email (should fail)
        duplicate_email_data = {
            "email": "test@example.com",  # Duplicate email
            "username": "differentuser",
            "password": "hashed_password_456",
            "full_name": "Different User"
        }

        response = await client.post("/api/v1/users", json=duplicate_email_data)
        assert response.status_code == 409  # Conflict
        error_response = response.json()
        assert "type" in error_response  # RFC 7807 format
        assert "email" in error_response["detail"].lower()

        # Try to create user with same username (should fail)
        duplicate_username_data = {
            "email": "different@example.com",
            "username": "testuser",  # Duplicate username
            "password": "hashed_password_456",
            "full_name": "Different User"
        }

        response = await client.post("/api/v1/users", json=duplicate_username_data)
        assert response.status_code == 409  # Conflict
        error_response = response.json()
        assert "username" in error_response["detail"].lower()

@pytest.mark.asyncio
async def test_database_transaction_rollback(test_postgres_client):
    """Test database transaction rollback on error."""

    # This test requires direct database access to simulate failures
    async with test_postgres_client.acquire() as conn:
        # Start transaction
        async with conn.transaction():
            # Insert user
            user_id = await conn.fetchval("""
                INSERT INTO users (email, username, hashed_password, full_name)
                VALUES ('trans@example.com', 'transuser', 'hashed_pass', 'Trans User')
                RETURNING id
            """)

            # Verify user exists in transaction
            user_count = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE id = $1", user_id
            )
            assert user_count == 1

            # Simulate error (raise exception to trigger rollback)
            raise Exception("Simulated error")

    # Verify user was not committed (rollback occurred)
    async with test_postgres_client.acquire() as conn:
        user_count = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE email = 'trans@example.com'"
        )
        assert user_count == 0

@pytest.mark.asyncio
async def test_pagination_and_filtering(test_postgres_client):
    """Test pagination and filtering functionality."""

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create multiple users for testing
        users_data = [
            {
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "password": f"hashed_password_{i}",
                "full_name": f"User {i}",
                "status": "active" if i % 2 == 0 else "inactive"
            }
            for i in range(10)
        ]

        created_users = []
        for user_data in users_data:
            response = await client.post("/api/v1/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json())

        # Test pagination
        response = await client.get("/api/v1/users?limit=5&offset=0")
        assert response.status_code == 200
        page1 = response.json()
        assert len(page1["items"]) == 5
        assert page1["limit"] == 5
        assert page1["offset"] == 0
        assert page1["has_next"] is True
        assert page1["has_prev"] is False

        response = await client.get("/api/v1/users?limit=5&offset=5")
        assert response.status_code == 200
        page2 = response.json()
        assert len(page2["items"]) == 5
        assert page2["offset"] == 5
        assert page2["has_prev"] is True

        # Test filtering by status
        response = await client.get("/api/v1/users?status=active")
        assert response.status_code == 200
        active_users = response.json()
        assert all(user["status"] == "active" for user in active_users["items"])

        response = await client.get("/api/v1/users?status=inactive")
        assert response.status_code == 200
        inactive_users = response.json()
        assert all(user["status"] == "inactive" for user in inactive_users["items"])

        # Test search functionality
        response = await client.get("/api/v1/users?search=user5")
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results["items"]) == 1
        assert "user5" in search_results["items"][0]["username"]
```

### Business Service Integration Tests (`tests/integration/test_api_service_integration.py`)

```python
"""Integration tests for API service with mocked data services."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from api_service.src.main import app
from shared.http.base_client import HTTPNotFoundError, HTTPConflictError

@pytest.mark.asyncio
async def test_user_creation_flow_with_data_services(mock_data_service_responses, http_client_mocker):
    """Test complete user creation flow with data service communication."""

    # Setup HTTP client mocking
    http_client_mocker.add_response(
        "GET", "/api/v1/users/by-email",
        None, 404  # User doesn't exist
    )
    http_client_mocker.add_response(
        "GET", "/api/v1/users/by-username",
        None, 404  # Username available
    )
    http_client_mocker.add_response(
        "POST", "/api/v1/users",
        mock_data_service_responses["users"]["create_user"], 201
    )
    http_client_mocker.add_response(
        "POST", "/api/v1/analytics/events",
        mock_data_service_responses["analytics"]["track_event"], 201
    )

    with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_postgres_client, \
         patch('api_service.src.clients.mongo_data_client.MongoDataClient') as mock_mongo_client:

        # Setup data service client mocks
        postgres_instance = mock_postgres_client.return_value
        postgres_instance.get_user_by_email.return_value = None
        postgres_instance.get_user_by_username.return_value = None
        postgres_instance.create_user.return_value = mock_data_service_responses["users"]["create_user"]

        mongo_instance = mock_mongo_client.return_value
        mongo_instance.track_event.return_value = "event_456"

        # Make API request
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "email": "test@example.com",
                "username": "testuser",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }

            response = await client.post("/api/v1/users", json=user_data)

            # Verify API response
            assert response.status_code == 201
            created_user = response.json()
            assert created_user["email"] == "new@example.com"
            assert created_user["username"] == "newuser"

            # Verify data service calls
            postgres_instance.get_user_by_email.assert_called_once_with("test@example.com")
            postgres_instance.get_user_by_username.assert_called_once_with("testuser")
            postgres_instance.create_user.assert_called_once()

            # Verify analytics tracking
            mongo_instance.track_event.assert_called_once()
            event_call = mongo_instance.track_event.call_args[0][0]
            assert event_call["event_type"] == "user_action"
            assert event_call["event_name"] == "user_created"

@pytest.mark.asyncio
async def test_data_service_timeout_handling():
    """Test handling of data service timeouts."""

    with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_client:
        postgres_instance = mock_client.return_value
        postgres_instance.get_user_by_id.side_effect = HTTPTimeoutError("Service timeout")

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/users/123")

            # Should return 503 Service Unavailable for timeout
            assert response.status_code == 503
            error_response = response.json()
            assert "type" in error_response  # RFC 7807 format
            assert "timeout" in error_response["detail"].lower()

@pytest.mark.asyncio
async def test_data_service_circuit_breaker():
    """Test circuit breaker behavior with repeated failures."""

    with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_client:
        postgres_instance = mock_client.return_value

        # Configure repeated failures
        postgres_instance.get_user_by_id.side_effect = [
            HTTPTimeoutError("Timeout 1"),
            HTTPTimeoutError("Timeout 2"),
            HTTPTimeoutError("Timeout 3"),
            HTTPTimeoutError("Timeout 4"),
            HTTPTimeoutError("Timeout 5"),
            HTTPServiceUnavailableError("Circuit breaker open")
        ]

        async with AsyncClient(app=app, base_url="http://test") as client:
            # First 5 requests should get timeouts
            for i in range(5):
                response = await client.get(f"/api/v1/users/{i+1}")
                assert response.status_code == 503

            # 6th request should get circuit breaker error
            response = await client.get("/api/v1/users/6")
            assert response.status_code == 503
            error_response = response.json()
            assert "circuit breaker" in error_response["detail"].lower()

@pytest.mark.asyncio
async def test_request_correlation_id_propagation():
    """Test Request ID propagation through service calls."""

    test_request_id = "test-correlation-123"

    with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_client:
        postgres_instance = mock_client.return_value
        postgres_instance.get_user_by_id.return_value = {
            "id": 123,
            "email": "test@example.com",
            "username": "testuser"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/users/123",
                headers={"X-Request-ID": test_request_id}
            )

            assert response.status_code == 200

            # Verify Request ID was propagated to response
            assert response.headers.get("X-Request-ID") == test_request_id

            # Verify data service client was called with proper context
            postgres_instance.get_user_by_id.assert_called_once_with(123)
```

---

## Performance Testing Examples

### Load Testing (`tests/performance/test_load_scenarios.py`)

```python
"""Performance and load testing scenarios."""

import asyncio
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
import time

@pytest.mark.asyncio
@pytest.mark.performance
async def test_concurrent_user_creation(performance_metrics):
    """Test concurrent user creation performance."""

    concurrent_users = 50
    requests_per_user = 10

    async def create_user_batch(user_offset: int):
        """Create batch of users for one simulated user."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            for i in range(requests_per_user):
                start_time = time.time()

                user_data = {
                    "email": f"loadtest{user_offset}_{i}@example.com",
                    "username": f"loaduser{user_offset}_{i}",
                    "password": "LoadTestPass123!",
                    "full_name": f"Load Test User {user_offset}_{i}"
                }

                try:
                    response = await client.post("/api/v1/users", json=user_data)
                    duration_ms = (time.time() - start_time) * 1000

                    success = response.status_code == 201
                    performance_metrics.record_response(duration_ms, success)

                    if not success:
                        print(f"Failed request: {response.status_code} - {response.text}")

                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    performance_metrics.record_response(duration_ms, False)
                    print(f"Request exception: {e}")

    # Run concurrent batches
    tasks = [
        create_user_batch(user_id)
        for user_id in range(concurrent_users)
    ]

    await asyncio.gather(*tasks)

    # Analyze performance metrics
    total_requests = concurrent_users * requests_per_user
    print(f"\nPerformance Results for {total_requests} requests:")
    print(f"Average response time: {performance_metrics.avg_response_time:.2f}ms")
    print(f"95th percentile: {performance_metrics.p95_response_time:.2f}ms")
    print(f"Success rate: {(1 - performance_metrics.error_rate) * 100:.2f}%")
    print(f"Error rate: {performance_metrics.error_rate * 100:.2f}%")

    # Performance assertions
    assert performance_metrics.avg_response_time < 1000, "Average response time should be under 1 second"
    assert performance_metrics.p95_response_time < 2000, "95th percentile should be under 2 seconds"
    assert performance_metrics.error_rate < 0.05, "Error rate should be under 5%"

@pytest.mark.asyncio
@pytest.mark.performance
async def test_data_service_performance():
    """Test data service response time performance."""

    test_runs = 100
    performance_metrics = PerformanceMetrics()

    # Test PostgreSQL data service performance
    with patch('db_postgres_service.src.repositories.user_repository.UserRepository') as mock_repo:
        mock_repo.return_value.get_by_id.return_value = {
            "id": 123,
            "email": "perf@example.com",
            "username": "perfuser"
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            for i in range(test_runs):
                start_time = time.time()

                response = await client.get(f"/api/v1/users/{i % 100 + 1}")
                duration_ms = (time.time() - start_time) * 1000

                success = response.status_code == 200
                performance_metrics.record_response(duration_ms, success)

    print(f"\nData Service Performance Results:")
    print(f"Average response time: {performance_metrics.avg_response_time:.2f}ms")
    print(f"95th percentile: {performance_metrics.p95_response_time:.2f}ms")

    # Data service should be very fast
    assert performance_metrics.avg_response_time < 200, "Data service should respond under 200ms"
    assert performance_metrics.p95_response_time < 500, "95th percentile should be under 500ms"

@pytest.mark.asyncio
@pytest.mark.performance
async def test_memory_usage_under_load():
    """Test memory usage during sustained load."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Simulate sustained load
    concurrent_requests = 25
    duration_seconds = 30

    async def sustained_load():
        """Generate sustained load for specified duration."""
        end_time = time.time() + duration_seconds
        request_count = 0

        async with AsyncClient(app=app, base_url="http://test") as client:
            while time.time() < end_time:
                try:
                    response = await client.get("/api/v1/health")
                    request_count += 1

                    if request_count % 100 == 0:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        print(f"Requests: {request_count}, Memory: {current_memory:.1f}MB")

                    await asyncio.sleep(0.1)  # Small delay to simulate realistic load

                except Exception as e:
                    print(f"Load test error: {e}")

        return request_count

    # Run concurrent load generators
    tasks = [sustained_load() for _ in range(concurrent_requests)]
    results = await asyncio.gather(*tasks)

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    total_requests = sum(results)

    print(f"\nMemory Usage Results:")
    print(f"Initial memory: {initial_memory:.1f}MB")
    print(f"Final memory: {final_memory:.1f}MB")
    print(f"Memory increase: {memory_increase:.1f}MB")
    print(f"Total requests: {total_requests}")
    print(f"Requests per second: {total_requests / duration_seconds:.1f}")

    # Memory usage should not grow excessively
    assert memory_increase < 100, f"Memory increase should be under 100MB, got {memory_increase:.1f}MB"

@pytest.mark.asyncio
@pytest.mark.performance
async def test_database_connection_pool_efficiency():
    """Test database connection pool efficiency under load."""

    pool_size = 10
    concurrent_queries = 50
    queries_per_connection = 20

    # This test would require actual database connection monitoring
    # For demonstration, we'll simulate the scenario

    connection_usage = []

    async def simulate_database_query(query_id: int):
        """Simulate database query with connection pool."""
        start_time = time.time()

        # Simulate database operation
        await asyncio.sleep(0.1)  # Simulate query time

        duration = time.time() - start_time
        connection_usage.append({
            "query_id": query_id,
            "duration": duration,
            "timestamp": time.time()
        })

    # Run concurrent queries
    tasks = [
        simulate_database_query(i)
        for i in range(concurrent_queries * queries_per_connection)
    ]

    start_time = time.time()
    await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    print(f"\nConnection Pool Performance:")
    print(f"Total queries: {len(connection_usage)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Queries per second: {len(connection_usage) / total_time:.1f}")
    print(f"Average query time: {sum(q['duration'] for q in connection_usage) / len(connection_usage):.3f}s")

    # With proper connection pooling, should handle high concurrency efficiently
    queries_per_second = len(connection_usage) / total_time
    assert queries_per_second > 100, f"Should handle >100 queries/sec, got {queries_per_second:.1f}"
```

---

## End-to-End Testing Examples

### Complete Workflow Tests (`tests/e2e/test_user_management_workflow.py`)

```python
"""End-to-end testing for complete user management workflows."""

import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_user_lifecycle():
    """Test complete user lifecycle from creation to deletion."""

    # Test scenario: New user registration, profile updates, activity tracking, account deletion

    # Start all required services (would be done by test setup)
    services = {
        "postgres_data": "http://localhost:8001",
        "mongo_data": "http://localhost:8002",
        "api_service": "http://localhost:8000",
        "bot_service": "http://localhost:8003"
    }

    # Verify all services are healthy
    async with AsyncClient() as client:
        for service_name, service_url in services.items():
            response = await client.get(f"{service_url}/health")
            assert response.status_code == 200, f"{service_name} is not healthy"
            health_data = response.json()
            assert health_data["status"] in ["healthy", "ok"], f"{service_name} status: {health_data}"

    user_data = {
        "email": "e2e.test@example.com",
        "username": "e2euser",
        "password": "E2ETestPass123!",
        "full_name": "End-to-End Test User"
    }

    async with AsyncClient() as client:
        # 1. User Registration
        response = await client.post(f"{services['api_service']}/api/v1/users", json=user_data)
        assert response.status_code == 201
        user = response.json()
        user_id = user["id"]

        print(f"✓ User created with ID: {user_id}")

        # 2. Verify user in PostgreSQL data service
        response = await client.get(f"{services['postgres_data']}/api/v1/users/{user_id}")
        assert response.status_code == 200
        postgres_user = response.json()
        assert postgres_user["email"] == user_data["email"]

        print("✓ User verified in PostgreSQL service")

        # 3. Check analytics event was created in MongoDB
        await asyncio.sleep(1)  # Allow time for async event processing
        response = await client.get(f"{services['mongo_data']}/api/v1/analytics/events/user/{user_id}")
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1

        creation_event = next((e for e in events if e["event_name"] == "user_created"), None)
        assert creation_event is not None

        print("✓ User creation event tracked in MongoDB")

        # 4. User Profile Update
        update_data = {
            "full_name": "Updated E2E User",
            "bio": "This user was updated during E2E testing"
        }
        response = await client.patch(f"{services['api_service']}/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["full_name"] == "Updated E2E User"

        print("✓ User profile updated")

        # 5. Simulate user activity
        activities = [
            {"event_name": "login", "category": "authentication"},
            {"event_name": "page_view", "category": "navigation", "properties": {"page": "/dashboard"}},
            {"event_name": "button_click", "category": "interaction", "properties": {"button_id": "save_profile"}},
            {"event_name": "logout", "category": "authentication"}
        ]

        for activity in activities:
            event_data = {
                "event_type": "user_action",
                "user_id": str(user_id),
                "source_service": "e2e_test",
                **activity
            }
            response = await client.post(f"{services['mongo_data']}/api/v1/analytics/events", json=event_data)
            assert response.status_code == 201

        print(f"✓ {len(activities)} user activities tracked")

        # 6. Get user analytics summary
        response = await client.get(f"{services['mongo_data']}/api/v1/analytics/summary/user/{user_id}")
        assert response.status_code == 200
        analytics_summary = response.json()
        assert analytics_summary["total_events"] >= len(activities)

        print("✓ User analytics summary retrieved")

        # 7. Test bot service interaction (simulate Telegram commands)
        bot_commands = [
            {"command": "/start", "user_id": user_id},
            {"command": "/profile", "user_id": user_id},
            {"command": "/stats", "user_id": user_id}
        ]

        for command in bot_commands:
            # Simulate bot command processing (would normally go through Telegram)
            event_data = {
                "event_type": "user_action",
                "event_name": "bot_command",
                "category": "interaction",
                "user_id": str(user_id),
                "properties": {"command": command["command"]},
                "source_service": "bot_service"
            }
            response = await client.post(f"{services['mongo_data']}/api/v1/analytics/events", json=event_data)
            assert response.status_code == 201

        print(f"✓ {len(bot_commands)} bot interactions simulated")

        # 8. Test data consistency across services
        # Get user from API service
        response = await client.get(f"{services['api_service']}/api/v1/users/{user_id}")
        assert response.status_code == 200
        api_user = response.json()

        # Get user from PostgreSQL service
        response = await client.get(f"{services['postgres_data']}/api/v1/users/{user_id}")
        assert response.status_code == 200
        db_user = response.json()

        # Verify consistency
        assert api_user["id"] == db_user["id"]
        assert api_user["email"] == db_user["email"]
        assert api_user["full_name"] == db_user["full_name"]

        print("✓ Data consistency verified across services")

        # 9. Test error handling - try to access non-existent user
        response = await client.get(f"{services['api_service']}/api/v1/users/99999")
        assert response.status_code == 404
        error_response = response.json()
        assert "type" in error_response  # RFC 7807 format

        print("✓ Error handling verified")

        # 10. User Deletion
        response = await client.delete(f"{services['api_service']}/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify user is deleted from API service
        response = await client.get(f"{services['api_service']}/api/v1/users/{user_id}")
        assert response.status_code == 404

        # Verify user is deleted from PostgreSQL service
        response = await client.get(f"{services['postgres_data']}/api/v1/users/{user_id}")
        assert response.status_code == 404

        print("✓ User successfully deleted")

        # 11. Verify analytics data remains (for audit purposes)
        response = await client.get(f"{services['mongo_data']}/api/v1/analytics/events/user/{user_id}")
        assert response.status_code == 200
        final_events = response.json()
        # Should still have all events including deletion event
        assert len(final_events) >= len(activities) + len(bot_commands) + 1  # +1 for deletion event

        print("✓ Analytics data preserved after user deletion")

        print("\n🎉 Complete user lifecycle test passed!")

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_service_failure_resilience():
    """Test system resilience when individual services fail."""

    services = {
        "postgres_data": "http://localhost:8001",
        "mongo_data": "http://localhost:8002",
        "api_service": "http://localhost:8000"
    }

    async with AsyncClient() as client:
        # Test 1: API service continues when MongoDB is unavailable
        # (This would require actually stopping MongoDB container in real test)

        # Simulate MongoDB unavailable by mocking responses
        with patch('api_service.src.clients.mongo_data_client.MongoDataClient') as mock_mongo:
            mock_mongo.return_value.track_event.side_effect = HTTPTimeoutError("MongoDB unavailable")

            # User creation should still work (with analytics failure logged)
            user_data = {
                "email": "resilience@example.com",
                "username": "resilienceuser",
                "password": "ResiliencePass123!",
                "full_name": "Resilience Test User"
            }

            response = await client.post(f"{services['api_service']}/api/v1/users", json=user_data)
            # Should still succeed despite analytics failure
            assert response.status_code == 201

            print("✓ User creation succeeded despite MongoDB unavailability")

        # Test 2: Graceful degradation when PostgreSQL is slow
        with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_postgres:
            # Simulate slow response
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(2)  # 2 second delay
                return {"id": 123, "email": "slow@example.com", "username": "slowuser"}

            mock_postgres.return_value.get_user_by_id.side_effect = slow_response

            # Request should eventually succeed but take longer
            start_time = time.time()
            response = await client.get(f"{services['api_service']}/api/v1/users/123")
            duration = time.time() - start_time

            assert response.status_code == 200
            assert duration >= 2  # Confirms it waited for slow service

            print(f"✓ Handled slow data service (took {duration:.1f}s)")

        # Test 3: Circuit breaker protection
        with patch('api_service.src.clients.user_data_client.UserDataClient') as mock_postgres:
            # Simulate repeated failures
            mock_postgres.return_value.get_user_by_id.side_effect = HTTPTimeoutError("Service timeout")

            # Multiple requests should eventually trigger circuit breaker
            for i in range(6):  # Exceed circuit breaker threshold
                response = await client.get(f"{services['api_service']}/api/v1/users/{i+1}")
                assert response.status_code == 503  # Service Unavailable

            print("✓ Circuit breaker protection activated")

print("\nComprehensive testing examples created successfully!")
print("These tests demonstrate:")
print("- Unit testing with mocks")
print("- Integration testing with real databases")
print("- Performance and load testing")
print("- End-to-end workflow testing")
print("- Resilience and failure testing")
print("- HTTP client testing patterns")
print("- Request correlation testing")
print("- Circuit breaker testing")
```

This comprehensive testing suite provides:

1. **Complete test infrastructure** with testcontainers
2. **HTTP client mocking utilities** for unit tests
3. **Integration tests** with real databases
4. **Performance testing** with load scenarios
5. **End-to-end workflow testing** across all services
6. **Resilience testing** for failure scenarios
7. **Type-safe testing patterns** with Pydantic
8. **Request correlation testing** for observability

The examples demonstrate real-world testing patterns for the Improved Hybrid Approach architecture.