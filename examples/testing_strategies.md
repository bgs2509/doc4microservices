# Testing Strategies and Examples

This document demonstrates comprehensive testing strategies for microservices following the "Improved Hybrid Approach" architecture. All examples use testcontainers for real database testing and achieve 100% coverage for critical paths.

## Testing Architecture Overview

### Testing Principles
- **Real Infrastructure**: Use testcontainers for PostgreSQL, MongoDB, Redis, and RabbitMQ
- **Isolation**: Each test gets a fresh database/infrastructure state
- **Fast Feedback**: Parallel test execution with proper resource management
- **Complete Coverage**: Unit tests for business logic, integration tests for APIs, end-to-end tests for workflows

### Test Categories
1. **Unit Tests**: Service layer business logic with mocked dependencies
2. **Integration Tests**: API endpoints with real database via testcontainers
3. **Repository Tests**: Database operations with real PostgreSQL
4. **Client Tests**: HTTP client behavior with mock servers
5. **End-to-End Tests**: Complete workflows across multiple services

---

## 1. Test Configuration (`conftest.py`)

### PostgreSQL Data Service Test Setup

```python
# services/db_postgres_service/tests/conftest.py
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from src.main import app
from src.core.database import get_db_session, Base
from src.core.config import settings

# Global test container and engine
postgres_container = None
test_engine = None
TestSessionLocal = None

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def postgres_url():
    """Start PostgreSQL container and return connection URL."""
    global postgres_container

    postgres_container = PostgresContainer(
        image="postgres:15-alpine",
        port=5432,
        username="test_user",
        password="test_password",
        dbname="test_db"
    )

    postgres_container.start()

    # Get connection URL and convert to async
    sync_url = postgres_container.get_connection_url()
    async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://")

    yield async_url

    postgres_container.stop()

@pytest.fixture(scope="session")
async def test_db_engine(postgres_url):
    """Create test database engine."""
    global test_engine

    test_engine = create_async_engine(
        postgres_url,
        echo=settings.DEBUG,
        pool_pre_ping=True
    )

    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()

@pytest.fixture(scope="session")
def test_session_factory(test_db_engine):
    """Create test session factory."""
    global TestSessionLocal

    TestSessionLocal = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    return TestSessionLocal

@pytest.fixture
async def db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Create isolated test database session with transaction rollback."""
    async with test_session_factory() as session:
        # Start transaction
        transaction = await session.begin()

        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await transaction.rollback()
            await session.close()

@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database dependency override."""

    def override_get_db():
        return db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

### Business Service Test Setup

```python
# services/api_service/tests/conftest.py
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
from testcontainers.compose import DockerCompose
import redis.asyncio as redis
import aio_pika

from src.main import app
from src.core import dependencies
from src.clients.user_data_client import UserDataClient

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def infrastructure():
    """Start infrastructure services via Docker Compose."""
    with DockerCompose("./", compose_file_name="docker-compose.test.yml") as compose:
        # Start Redis and RabbitMQ
        compose.start()

        # Wait for services to be ready
        redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        await redis_client.ping()

        rabbitmq_connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672")

        yield {
            "redis_url": "redis://localhost:6379",
            "rabbitmq_url": "amqp://guest:guest@localhost:5672"
        }

        await redis_client.close()
        await rabbitmq_connection.close()

@pytest.fixture
async def mock_user_data_client():
    """Create mock user data client."""
    client = AsyncMock(spec=UserDataClient)

    # Set up default mock responses
    client.get_user_by_id.return_value = None
    client.get_user_by_username.return_value = None
    client.get_user_by_email.return_value = None
    client.create_user.return_value = None
    client.update_user.return_value = None
    client.delete_user.return_value = False
    client.list_users.return_value = {"users": [], "total": 0, "limit": 20, "offset": 0}

    return client

@pytest.fixture
async def mock_redis_client():
    """Create mock Redis client."""
    client = AsyncMock(spec=redis.Redis)
    client.get.return_value = None
    client.setex.return_value = True
    client.delete.return_value = 1
    return client

@pytest.fixture
async def mock_rabbitmq_channel():
    """Create mock RabbitMQ channel."""
    channel = AsyncMock(spec=aio_pika.Channel)
    exchange = AsyncMock()
    channel.declare_exchange.return_value = exchange
    return channel

@pytest.fixture
async def async_client(
    mock_user_data_client,
    mock_redis_client,
    mock_rabbitmq_channel
) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with mocked dependencies."""

    def override_user_data_client():
        return mock_user_data_client

    def override_redis_client():
        return mock_redis_client

    def override_rabbitmq_channel():
        return mock_rabbitmq_channel

    app.dependency_overrides[dependencies.get_user_data_client] = override_user_data_client
    app.dependency_overrides[dependencies.get_redis_client] = override_redis_client
    app.dependency_overrides[dependencies.get_rabbitmq_channel] = override_rabbitmq_channel

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

---

## 2. PostgreSQL Data Service Testing

### Repository Testing

```python
# services/db_postgres_service/tests/test_user_repository.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate, UserFilterParams
from src.schemas.common import PaginationParams, SortParams
from src.models.user import UserStatus

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation in repository."""
    repo = UserRepository(db_session)

    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="$2b$12$hashed_password",
        full_name="Test User"
    )

    user = await repo.create_user(user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.status == UserStatus.ACTIVE
    assert user.is_verified is False
    assert user.is_admin is False

@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """Test getting user by email."""
    repo = UserRepository(db_session)

    # Create user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="$2b$12$hashed_password"
    )
    created_user = await repo.create_user(user_data)

    # Get by email
    found_user = await repo.get_by_email("test@example.com")

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_users_paginated(db_session: AsyncSession):
    """Test paginated user retrieval with filtering."""
    repo = UserRepository(db_session)

    # Create multiple users
    users_data = [
        UserCreate(email=f"user{i}@example.com", username=f"user{i}", password="$2b$12$hash")
        for i in range(25)
    ]

    for user_data in users_data:
        await repo.create_user(user_data)

    # Test pagination
    pagination = PaginationParams(limit=10, offset=0)
    sort = SortParams(sort_by="created_at", sort_order="desc")
    filters = UserFilterParams(status=UserStatus.ACTIVE)

    result = await repo.get_users_paginated(pagination, sort, filters)

    assert len(result.items) == 10
    assert result.total == 25
    assert result.has_next is True
    assert result.has_prev is False
    assert result.limit == 10
    assert result.offset == 0

@pytest.mark.asyncio
async def test_search_users(db_session: AsyncSession):
    """Test user search functionality."""
    repo = UserRepository(db_session)

    # Create users with different names
    await repo.create_user(UserCreate(
        email="john@example.com", username="john_doe", password="$2b$12$hash", full_name="John Doe"
    ))
    await repo.create_user(UserCreate(
        email="jane@example.com", username="jane_smith", password="$2b$12$hash", full_name="Jane Smith"
    ))
    await repo.create_user(UserCreate(
        email="bob@example.com", username="bob_wilson", password="$2b$12$hash", full_name="Bob Wilson"
    ))

    # Search for "john"
    pagination = PaginationParams(limit=10, offset=0)
    sort = SortParams()
    filters = UserFilterParams(search="john")

    result = await repo.get_users_paginated(pagination, sort, filters)

    assert len(result.items) == 1
    assert result.items[0].username == "john_doe"

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test user update functionality."""
    repo = UserRepository(db_session)

    # Create user
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="$2b$12$hash"
    )
    user = await repo.create_user(user_data)

    # Update user
    update_data = UserUpdate(
        full_name="Updated Name",
        status=UserStatus.INACTIVE
    )
    updated_user = await repo.update_user(user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.status == UserStatus.INACTIVE
    assert updated_user.email == "test@example.com"  # Unchanged

@pytest.mark.asyncio
async def test_verify_credentials(db_session: AsyncSession):
    """Test credential verification."""
    repo = UserRepository(db_session)

    password_hash = "$2b$12$test_hash"
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password=password_hash
    )
    user = await repo.create_user(user_data)

    # Test valid credentials
    verified_user = await repo.verify_credentials("testuser", password_hash)
    assert verified_user is not None
    assert verified_user.id == user.id

    # Test invalid password
    invalid_user = await repo.verify_credentials("testuser", "wrong_hash")
    assert invalid_user is None

    # Test inactive user
    await repo.update_user(user.id, UserUpdate(status=UserStatus.INACTIVE))
    inactive_user = await repo.verify_credentials("testuser", password_hash)
    assert inactive_user is None
```

### API Endpoint Testing

```python
# services/db_postgres_service/tests/test_user_api.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_create_user_api(async_client: AsyncClient):
    """Test user creation via API."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "$2b$12$hashed_password",
        "full_name": "Test User"
    }

    response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201
    assert response.headers["content-type"] == "application/json"

    user = response.json()
    assert user["email"] == "test@example.com"
    assert user["username"] == "testuser"
    assert user["full_name"] == "Test User"
    assert "id" in user
    assert "created_at" in user
    assert "hashed_password" not in user  # Should not be exposed

@pytest.mark.asyncio
async def test_get_user_api(async_client: AsyncClient, db_session: AsyncSession):
    """Test getting user via API."""
    # Create user directly in database
    repo = UserRepository(db_session)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="$2b$12$hash"
    )
    created_user = await repo.create_user(user_data)

    # Get user via API
    response = await async_client.get(f"/api/v1/users/{created_user.id}")

    assert response.status_code == 200

    user = response.json()
    assert user["id"] == created_user.id
    assert user["email"] == "test@example.com"
    assert user["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_nonexistent_user_api(async_client: AsyncClient):
    """Test getting non-existent user returns RFC 7807 error."""
    response = await async_client.get("/api/v1/users/99999")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"

    error = response.json()
    assert error["type"].endswith("user-not-found")
    assert error["title"] == "User Not Found"
    assert error["status"] == 404
    assert "instance" in error

@pytest.mark.asyncio
async def test_list_users_api(async_client: AsyncClient, db_session: AsyncSession):
    """Test listing users with pagination."""
    repo = UserRepository(db_session)

    # Create multiple users
    for i in range(15):
        user_data = UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="$2b$12$hash"
        )
        await repo.create_user(user_data)

    # Test pagination
    response = await async_client.get("/api/v1/users/?limit=10&offset=5")

    assert response.status_code == 200

    result = response.json()
    assert "items" in result
    assert "total" in result
    assert "has_next" in result
    assert "has_prev" in result
    assert len(result["items"]) == 10
    assert result["total"] == 15
    assert result["has_next"] is False
    assert result["has_prev"] is True

@pytest.mark.asyncio
async def test_validation_error_api(async_client: AsyncClient):
    """Test validation error returns RFC 7807 format."""
    invalid_user_data = {
        "email": "invalid-email",
        "username": "ab",  # Too short
        "password": "123"  # Too short
    }

    response = await async_client.post("/api/v1/users/", json=invalid_user_data)

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"

    error = response.json()
    assert error["type"].endswith("validation-error")
    assert error["title"] == "Validation Error"
    assert error["status"] == 422
    assert "errors" in error
```

### Aiogram Bot Testing
```python
# tests/test_bot_handlers.py
import pytest
from unittest.mock import AsyncMock, Mock
from aiogram.types import Message, User, Chat
from aiogram import Bot

from src.bot.handlers.start import handle_start

@pytest.fixture
def mock_message():
    """Mock Telegram message."""
    user = User(id=123, is_bot=False, first_name="Test", username="testuser")
    chat = Chat(id=123, type="private")

    message = Mock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()
    message.bot = Mock(spec=Bot)

    return message

@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test /start command handler."""
    await handle_start(mock_message)

    mock_message.reply.assert_called_once()
    call_args = mock_message.reply.call_args[0][0]
    assert "Welcome" in call_args
    assert "testuser" in call_args
```

### Worker Service Testing
```python
# tests/test_media_processor.py
import pytest
from unittest.mock import AsyncMock, Mock
from io import BytesIO
from PIL import Image

from src.workers.media_processor import MediaProcessor

@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.setex = AsyncMock()
    redis_mock.get = AsyncMock()
    return redis_mock

@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel."""
    channel_mock = AsyncMock()
    channel_mock.declare_exchange = AsyncMock()
    channel_mock.declare_queue = AsyncMock()
    return channel_mock

@pytest.fixture
def sample_image_data():
    """Create sample image data."""
    image = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return buffer.getvalue()

@pytest.mark.asyncio
async def test_process_image(mock_redis, mock_rabbitmq_channel, sample_image_data):
    """Test image processing."""
    processor = MediaProcessor(mock_redis, mock_rabbitmq_channel)

    result = await processor._process_image(
        file_data=sample_image_data,
        processing_id="test-123",
        user_id=456
    )

    assert result["success"] is True
    assert "thumbnail_key" in result
    assert "compressed_key" in result
    assert "metadata" in result
    assert result["original_size"] > 0
    assert result["compressed_size"] > 0
    assert 0 < result["compression_ratio"] <= 1

    # Verify Redis calls
    assert mock_redis.setex.call_count == 2  # thumbnail + compressed
```
