# Testcontainers Setup

Use Testcontainers to provision real Docker containers for integration tests, eliminating the gap between test and production environments. Testcontainers manages container lifecycle automatically, ensuring consistent, isolated test environments with production-like dependencies (PostgreSQL, Redis, MongoDB, RabbitMQ).

This document covers testcontainers-python setup, container configuration patterns, wait strategies for service readiness, and pytest fixtures for container management. Integration tests with Testcontainers provide confidence that code works with real databases and message brokers, not mocks.

Testcontainers bridges the gap between unit tests (mocked dependencies) and manual testing (shared dev environments). Each test run gets fresh containers, preventing test pollution and race conditions while maintaining test speed with container reuse strategies.

## Why Testcontainers

### Benefits Over Mocking

```python
# MOCKING (unit test): Fast but unrealistic
@pytest.mark.unit
async def test_user_creation_mocked(mocker):
    """Test with mocked PostgreSQL."""
    mock_session = mocker.patch("sqlalchemy.orm.Session")
    mock_session.execute.return_value = Mock(scalar_one_or_none=Mock(id="user-123"))
    # Fast, but doesn't test real SQL, transactions, constraints


# TESTCONTAINERS (integration test): Realistic and reliable
@pytest.mark.integration
async def test_user_creation_real_database(postgres_container):
    """Test with real PostgreSQL container."""
    async with get_session(postgres_container.get_connection_url()) as session:
        user = User(email="test@example.com", name="Test")
        session.add(user)
        await session.commit()
        # Tests real SQL, transactions, unique constraints, triggers
```

### Benefits Over Shared Test Databases

| Approach | Isolation | Consistency | Setup Complexity |
|----------|-----------|-------------|------------------|
| **Shared test DB** | ❌ Tests pollute each other | ❌ State accumulates | ✅ Simple |
| **Testcontainers** | ✅ Fresh per test run | ✅ Clean state | ✅ Automated |
| **Manual Docker** | ⚠️ Manual cleanup | ⚠️ Requires discipline | ❌ Complex scripts |

## Setup

### Installation

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "testcontainers>=4.0",
    # Database drivers
    "asyncpg>=0.29",         # PostgreSQL async driver
    "redis>=5.0",            # Redis client
    "motor>=3.3",            # MongoDB async driver
    "aio-pika>=9.3",         # RabbitMQ async client
]
```

Install with:

```bash
pip install -e ".[test]"
```

### Prerequisites

- **Docker installed and running** (testcontainers controls Docker daemon)
- Docker daemon accessible (usually `unix:///var/run/docker.sock`)
- Sufficient Docker resources (disk space, memory for multiple containers)

Verify Docker is running:

```bash
docker info
# Should show Docker version and running containers
```

## PostgreSQL Container

### Basic Setup

```python
# tests/integration/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# CORRECT: Module-scoped container (shared across module tests)
@pytest.fixture(scope="module")
def postgres_container():
    """Provide PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


# CORRECT: Async database engine from container
@pytest.fixture(scope="module")
async def db_engine(postgres_container):
    """Create async SQLAlchemy engine from container."""
    # Get connection URL from container
    db_url = postgres_container.get_connection_url().replace(
        "psycopg2", "asyncpg"  # Use async driver
    )

    engine = create_async_engine(db_url, echo=True)

    # Create tables
    from finance_lending_api.infrastructure.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


# CORRECT: Fresh session per test
@pytest.fixture
async def db_session(db_engine):
    """Provide fresh database session for each test."""
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback to keep container clean
```

### Using PostgreSQL in Tests

```python
# tests/integration/test_user_repository.py
import pytest
from finance_lending_api.infrastructure.repositories import UserRepository
from finance_lending_api.domain.models import User


@pytest.mark.integration
async def test_user_crud_operations(db_session):
    """Test user CRUD with real PostgreSQL."""
    repo = UserRepository(session=db_session)

    # Create
    user = await repo.create(email="test@example.com", name="Test User")
    assert user.id is not None

    # Read
    found_user = await repo.get_by_id(user.id)
    assert found_user.email == "test@example.com"

    # Update
    found_user.name = "Updated Name"
    await db_session.commit()
    updated_user = await repo.get_by_id(user.id)
    assert updated_user.name == "Updated Name"

    # Delete
    await repo.delete(user.id)
    deleted_user = await repo.get_by_id(user.id)
    assert deleted_user is None


@pytest.mark.integration
async def test_unique_email_constraint(db_session):
    """Test database enforces unique email constraint."""
    repo = UserRepository(session=db_session)

    # Create first user
    user1 = await repo.create(email="unique@example.com", name="User 1")
    assert user1.id is not None

    # Attempt to create duplicate email
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError, match="unique constraint"):
        await repo.create(email="unique@example.com", name="User 2")
        await db_session.commit()
```

## Redis Container

### Setup

```python
# tests/integration/conftest.py
import pytest
from testcontainers.redis import RedisContainer
from redis.asyncio import Redis


@pytest.fixture(scope="module")
def redis_container():
    """Provide Redis container for integration tests."""
    with RedisContainer("redis:7-alpine") as container:
        yield container


@pytest.fixture
async def redis_client(redis_container):
    """Provide Redis client connected to container."""
    client = Redis.from_url(
        redis_container.get_connection_url(),
        encoding="utf-8",
        decode_responses=True
    )

    yield client

    # Cleanup: flush database after each test
    await client.flushdb()
    await client.close()
```

### Using Redis in Tests

```python
# tests/integration/test_cache_service.py
import pytest
from finance_lending_api.services.cache import CacheService


@pytest.mark.integration
async def test_cache_set_and_get(redis_client):
    """Test Redis cache operations."""
    cache = CacheService(redis_client)

    # Set value
    await cache.set("user:123", {"name": "Test", "email": "test@example.com"}, ttl=60)

    # Get value
    result = await cache.get("user:123")
    assert result["name"] == "Test"
    assert result["email"] == "test@example.com"


@pytest.mark.integration
async def test_cache_expiration(redis_client):
    """Test cache TTL and expiration."""
    cache = CacheService(redis_client)

    # Set with short TTL
    await cache.set("temp:key", "value", ttl=1)

    # Value exists immediately
    result = await cache.get("temp:key")
    assert result == "value"

    # Wait for expiration
    import asyncio
    await asyncio.sleep(2)

    # Value expired
    result = await cache.get("temp:key")
    assert result is None


@pytest.mark.integration
async def test_idempotency_key_check(redis_client):
    """Test idempotency key storage and checking."""
    from finance_lending_api.middleware.idempotency import IdempotencyService

    service = IdempotencyService(redis_client)
    request_id = "req-12345"

    # First request: not seen before
    is_duplicate = await service.is_duplicate(request_id)
    assert is_duplicate is False

    # Store request
    await service.store_request(request_id, {"result": "processed"})

    # Second request: duplicate
    is_duplicate = await service.is_duplicate(request_id)
    assert is_duplicate is True
```

## MongoDB Container

### Setup

```python
# tests/integration/conftest.py
import pytest
from testcontainers.mongodb import MongoDbContainer
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope="module")
def mongo_container():
    """Provide MongoDB container for integration tests."""
    with MongoDbContainer("mongo:7") as container:
        yield container


@pytest.fixture
async def mongo_client(mongo_container):
    """Provide MongoDB client connected to container."""
    client = AsyncIOMotorClient(mongo_container.get_connection_url())

    yield client

    # Cleanup: drop database after tests
    await client.drop_database("test_db")
    client.close()


@pytest.fixture
async def mongo_db(mongo_client):
    """Provide MongoDB database for tests."""
    return mongo_client["test_db"]
```

### Using MongoDB in Tests

```python
# tests/integration/test_document_repository.py
import pytest
from finance_lending_api.infrastructure.mongo_repositories import DocumentRepository


@pytest.mark.integration
async def test_document_insert_and_find(mongo_db):
    """Test MongoDB document operations."""
    repo = DocumentRepository(mongo_db)

    # Insert document
    doc_id = await repo.insert({
        "user_id": "user-123",
        "type": "profile",
        "data": {"bio": "Test bio"}
    })
    assert doc_id is not None

    # Find document
    doc = await repo.find_by_id(doc_id)
    assert doc["user_id"] == "user-123"
    assert doc["data"]["bio"] == "Test bio"


@pytest.mark.integration
async def test_document_query_with_filter(mongo_db):
    """Test MongoDB queries with filters."""
    repo = DocumentRepository(mongo_db)

    # Insert multiple documents
    await repo.insert({"user_id": "user-1", "status": "active", "score": 90})
    await repo.insert({"user_id": "user-2", "status": "inactive", "score": 75})
    await repo.insert({"user_id": "user-3", "status": "active", "score": 85})

    # Query active users with score > 80
    results = await repo.find_many({
        "status": "active",
        "score": {"$gt": 80}
    })

    assert len(results) == 2
    assert all(doc["status"] == "active" for doc in results)
    assert all(doc["score"] > 80 for doc in results)
```

## RabbitMQ Container

### Setup

```python
# tests/integration/conftest.py
import pytest
from testcontainers.rabbitmq import RabbitMqContainer
import aio_pika


@pytest.fixture(scope="module")
def rabbitmq_container():
    """Provide RabbitMQ container for integration tests."""
    with RabbitMqContainer("rabbitmq:3-management-alpine") as container:
        yield container


@pytest.fixture
async def rabbitmq_connection(rabbitmq_container):
    """Provide RabbitMQ connection."""
    connection = await aio_pika.connect_robust(
        rabbitmq_container.get_connection_url()
    )

    yield connection

    await connection.close()


@pytest.fixture
async def rabbitmq_channel(rabbitmq_connection):
    """Provide RabbitMQ channel."""
    channel = await rabbitmq_connection.channel()
    yield channel
    await channel.close()
```

### Using RabbitMQ in Tests

```python
# tests/integration/test_event_publisher.py
import pytest
import json
from finance_lending_api.events.publisher import EventPublisher


@pytest.mark.integration
async def test_publish_and_consume_event(rabbitmq_channel):
    """Test RabbitMQ message publishing and consumption."""
    # Declare queue
    queue = await rabbitmq_channel.declare_queue("test.events", auto_delete=True)

    # Publish event
    publisher = EventPublisher(rabbitmq_channel)
    await publisher.publish_user_created(user_id="user-123", email="test@example.com")

    # Consume event
    message = await queue.get(timeout=5)
    assert message is not None

    event_data = json.loads(message.body.decode())
    assert event_data["user_id"] == "user-123"
    assert event_data["email"] == "test@example.com"

    await message.ack()


@pytest.mark.integration
async def test_event_routing_by_topic(rabbitmq_channel):
    """Test topic-based routing in RabbitMQ."""
    # Declare topic exchange
    exchange = await rabbitmq_channel.declare_exchange(
        "events",
        type=aio_pika.ExchangeType.TOPIC,
        auto_delete=True
    )

    # Bind queues with routing patterns
    user_queue = await rabbitmq_channel.declare_queue("user.events", auto_delete=True)
    await user_queue.bind(exchange, routing_key="user.*")

    loan_queue = await rabbitmq_channel.declare_queue("loan.events", auto_delete=True)
    await loan_queue.bind(exchange, routing_key="loan.*")

    # Publish user event
    await exchange.publish(
        aio_pika.Message(body=b'{"event": "user_created"}'),
        routing_key="user.created"
    )

    # Only user queue receives it
    user_message = await user_queue.get(timeout=1)
    assert user_message is not None

    # Loan queue is empty
    with pytest.raises(aio_pika.exceptions.QueueEmpty):
        await loan_queue.get(timeout=1, fail=True)
```

## Multiple Containers Composition

### Docker Compose with Testcontainers

```python
# tests/integration/conftest.py
import pytest
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def docker_compose():
    """Start all services with docker-compose for integration tests."""
    compose_path = Path(__file__).parent / "docker-compose.test.yml"

    with DockerCompose(
        filepath=compose_path.parent,
        compose_file_name=compose_path.name,
        pull=True
    ) as compose:
        # Wait for services to be ready
        compose.wait_for("http://localhost:5432")  # PostgreSQL
        compose.wait_for("http://localhost:6379")  # Redis
        compose.wait_for("http://localhost:27017")  # MongoDB
        compose.wait_for("http://localhost:5672")  # RabbitMQ

        yield compose
```

```yaml
# tests/integration/docker-compose.test.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user"]
      interval: 1s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 1s
      timeout: 3s
      retries: 10

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 1s
      timeout: 3s
      retries: 10

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 1s
      timeout: 3s
      retries: 10
```

## Wait Strategies

### Custom Wait Strategies

```python
# CORRECT: Wait for service to be ready
from testcontainers.core.waiting_utils import wait_for_logs


@pytest.fixture(scope="module")
def postgres_container():
    """PostgreSQL container with wait strategy."""
    container = PostgresContainer("postgres:16-alpine")
    container.start()

    # Wait for PostgreSQL to be ready
    wait_for_logs(container, "database system is ready to accept connections", timeout=30)

    yield container
    container.stop()


# CORRECT: Custom health check
from testcontainers.core.generic import DbContainer


@pytest.fixture(scope="module")
def custom_container():
    """Container with custom readiness check."""
    container = DbContainer("my-custom-service:latest")
    container.with_exposed_ports(8080)
    container.start()

    # Custom wait: poll health endpoint
    import time
    import requests
    from requests.exceptions import RequestException

    port = container.get_exposed_port(8080)
    health_url = f"http://localhost:{port}/health"

    for attempt in range(30):
        try:
            response = requests.get(health_url, timeout=1)
            if response.status_code == 200:
                break
        except RequestException:
            pass
        time.sleep(1)
    else:
        raise TimeoutError("Service did not become healthy")

    yield container
    container.stop()
```

## Performance Optimization

### Container Reuse Strategies

```python
# CORRECT: Module scope for container reuse across tests
@pytest.fixture(scope="module")
def postgres_container():
    """Reuse PostgreSQL container for all tests in module."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container
    # Container stopped after all module tests complete


# CORRECT: Session scope for maximum reuse
@pytest.fixture(scope="session")
def redis_container():
    """Reuse Redis container for entire test session."""
    with RedisContainer("redis:7-alpine") as container:
        yield container
    # Container stopped after all tests complete


# INCORRECT: Function scope (slow - new container per test)
@pytest.fixture(scope="function")
def slow_postgres_container():
    """WRONG: Creates new container for every single test."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container
    # Very slow for test suites with many tests
```

### Transaction Rollback for Speed

```python
# CORRECT: Use transaction rollback instead of recreating data
@pytest.fixture
async def db_session(db_engine):
    """Provide session with automatic rollback."""
    async with db_engine.begin() as connection:
        async_session = sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            yield session
            # Implicit rollback - changes don't persist to container
```

## Best Practices

### DO: Use Appropriate Scopes

```python
# CORRECT: Session scope for expensive containers
@pytest.fixture(scope="session")
def postgres_container():
    """Start PostgreSQL once for all tests."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


# CORRECT: Function scope for test isolation needs
@pytest.fixture(scope="function")
async def clean_redis(redis_client):
    """Flush Redis before each test for isolation."""
    await redis_client.flushdb()
    yield redis_client
```

### DO: Clean Up Between Tests

```python
# CORRECT: Explicit cleanup in fixture
@pytest.fixture
async def mongo_collection(mongo_db):
    """Provide clean collection for each test."""
    collection = mongo_db["users"]

    yield collection

    # Cleanup: drop collection after test
    await collection.drop()
```

### DON'T: Rely on Container State

```python
# INCORRECT: Tests depend on execution order
@pytest.mark.integration
async def test_create_user(db_session):
    """Create user with ID=1."""
    user = await create_user(id=1, email="test@example.com")
    assert user.id == 1


@pytest.mark.integration
async def test_find_user(db_session):
    """WRONG: Assumes test_create_user ran first."""
    user = await find_user(id=1)  # Might not exist!
    assert user.email == "test@example.com"


# CORRECT: Each test is self-contained
@pytest.mark.integration
async def test_find_user_independent(db_session):
    """Test is self-contained with its own setup."""
    # Setup: create user in this test
    await create_user(id=1, email="test@example.com")

    # Test: find user
    user = await find_user(id=1)
    assert user.email == "test@example.com"
```

## Checklist

- [ ] Docker installed and running on test machine
- [ ] `testcontainers` package installed in test dependencies
- [ ] Containers use module or session scope for reuse
- [ ] Wait strategies ensure services are ready before tests run
- [ ] Cleanup performed after each test (rollback, flush, drop)
- [ ] Tests are independent and don't rely on execution order
- [ ] Container images pinned to specific versions (e.g., `postgres:16`, not `postgres:latest`)
- [ ] Health checks configured for containers
- [ ] Connection URLs obtained from containers dynamically
- [ ] Async drivers used for async tests (asyncpg, motor, etc.)
- [ ] CI/CD environment has Docker available
- [ ] Integration tests marked with `@pytest.mark.integration`

## Related Documents

- `docs/atomic/testing/integration-testing/database-testing.md` — Testing with PostgreSQL and MongoDB
- `docs/atomic/testing/integration-testing/redis-testing.md` — Testing Redis caching and idempotency
- `docs/atomic/testing/integration-testing/rabbitmq-testing.md` — Testing RabbitMQ messaging
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Pytest fixture patterns
- `docs/atomic/testing/unit-testing/pytest-setup.md` — Pytest configuration
