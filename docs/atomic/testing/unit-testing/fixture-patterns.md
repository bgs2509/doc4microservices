# Test Fixture Patterns

Master pytest fixture patterns to create reusable, composable test components that reduce duplication and improve test maintainability. Fixtures provide a clean way to set up test preconditions, manage resources, and share common test data across your test suite.

This document covers fixture scopes, composition patterns, conftest.py organization, and best practices for Python microservices. Proper fixture design isolates test setup from test logic, enables dependency injection for tests, and ensures consistent test environments across your codebase.

Fixtures are pytest's most powerful feature for test organization. Understanding scope management, yield patterns, and autouse behavior is essential for building maintainable test suites that scale from unit tests to complex integration scenarios.

## Fixture Basics

### Simple Fixtures

```python
# tests/conftest.py
import pytest
from finance_lending_api.domain.services import LoanService


# CORRECT: Simple fixture with clear purpose
@pytest.fixture
def loan_service() -> LoanService:
    """Provide a LoanService instance for testing."""
    return LoanService()


# CORRECT: Fixture with setup logic
@pytest.fixture
def sample_user_data() -> dict:
    """Provide valid user registration data."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "phone": "+1234567890"
    }


# Using fixtures in tests
@pytest.mark.unit
def test_loan_approval(loan_service: LoanService, sample_user_data: dict):
    """Test loan approval with valid user data."""
    result = loan_service.evaluate_loan(
        user=sample_user_data,
        amount=10000,
        credit_score=750
    )
    assert result.approved is True
```

### Fixture Scopes

Control fixture lifecycle with scope parameter:

```python
# CORRECT: Function scope (default) — new instance per test
@pytest.fixture(scope="function")
def user_service():
    """Create new UserService for each test (isolated)."""
    return UserService()


# CORRECT: Class scope — shared across test class
@pytest.fixture(scope="class")
def database_connection():
    """Share database connection across test class."""
    conn = create_connection()
    yield conn
    conn.close()


# CORRECT: Module scope — shared across module
@pytest.fixture(scope="module")
def redis_client():
    """Share Redis client across entire test module."""
    client = Redis.from_url("redis://localhost:6379")
    yield client
    client.close()


# CORRECT: Session scope — shared across entire test run
@pytest.fixture(scope="session")
def docker_services():
    """Start Docker services once for entire test session."""
    compose_file = Path(__file__).parent / "docker-compose.test.yml"
    subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"])
    yield
    subprocess.run(["docker-compose", "-f", compose_file, "down"])


# INCORRECT: Session scope for mutable state (test pollution)
@pytest.fixture(scope="session")
def shared_list():
    """WRONG: Mutable fixture shared across all tests."""
    return []  # Tests will pollute each other's state
```

## Conftest.py Organization

### Directory Structure

```
tests/
├── conftest.py                    # Session/module-level fixtures
├── unit/
│   ├── conftest.py               # Unit test fixtures
│   ├── domain/
│   │   ├── conftest.py          # Domain-specific fixtures
│   │   └── test_user_service.py
│   └── infrastructure/
│       ├── conftest.py          # Infrastructure fixtures
│       └── test_repositories.py
└── integration/
    ├── conftest.py               # Integration test fixtures
    └── test_postgres.py
```

### Root conftest.py

```python
# tests/conftest.py
import pytest
from typing import AsyncGenerator
from redis.asyncio import Redis
from httpx import AsyncClient


# CORRECT: Session-scoped configuration
@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "REDIS_URL": "redis://localhost:6379/1",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "API_BASE_URL": "http://localhost:8000"
    }


# CORRECT: Async fixture for Redis client
@pytest.fixture(scope="module")
async def redis_client(test_config) -> AsyncGenerator[Redis, None]:
    """Provide Redis client for testing."""
    client = Redis.from_url(
        test_config["REDIS_URL"],
        encoding="utf-8",
        decode_responses=True
    )

    yield client

    # Cleanup: flush test database
    await client.flushdb()
    await client.close()


# CORRECT: HTTP client fixture
@pytest.fixture
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP client for testing."""
    async with AsyncClient() as client:
        yield client
```

### Domain conftest.py

```python
# tests/unit/domain/conftest.py
import pytest
from finance_lending_api.domain.services import UserService, LoanService
from finance_lending_api.domain.models import User


@pytest.fixture
def user_service() -> UserService:
    """Provide UserService instance."""
    return UserService()


@pytest.fixture
def loan_service() -> LoanService:
    """Provide LoanService instance."""
    return LoanService()


@pytest.fixture
def sample_user() -> User:
    """Provide sample User instance for testing."""
    return User(
        id="user-123",
        email="test@example.com",
        name="Test User",
        credit_score=750
    )
```

## Fixture Composition

### Fixtures Using Other Fixtures

```python
# CORRECT: Compose fixtures to build complex objects
@pytest.fixture
def database_url(test_config) -> str:
    """Extract database URL from config."""
    return test_config["DATABASE_URL"]


@pytest.fixture
async def database_engine(database_url):
    """Create SQLAlchemy engine from URL."""
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(database_url, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture
async def database_session(database_engine):
    """Create database session from engine."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(
        database_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def user_repository(database_session):
    """Create UserRepository with database session."""
    from finance_lending_api.infrastructure.repositories import UserRepository
    return UserRepository(session=database_session)


# Using composed fixtures
@pytest.mark.asyncio
async def test_user_creation(user_repository):
    """Test user creation through repository."""
    user = await user_repository.create(
        email="test@example.com",
        name="Test User"
    )
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Factory Fixtures

```python
# CORRECT: Factory pattern for creating multiple instances
@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def _create_user(
        email: str = "test@example.com",
        name: str = "Test User",
        credit_score: int = 700
    ) -> User:
        return User(
            id=f"user-{uuid.uuid4()}",
            email=email,
            name=name,
            credit_score=credit_score
        )
    return _create_user


# Using factory fixture
@pytest.mark.unit
def test_multiple_users(user_factory):
    """Test with multiple user instances."""
    user1 = user_factory(email="user1@example.com", credit_score=750)
    user2 = user_factory(email="user2@example.com", credit_score=650)
    user3 = user_factory(email="user3@example.com", credit_score=800)

    assert user1.credit_score > user2.credit_score
    assert user3.credit_score > user1.credit_score


# CORRECT: Async factory fixture
@pytest.fixture
def loan_factory(user_factory):
    """Factory for creating test loans."""
    async def _create_loan(
        user: User | None = None,
        amount: int = 10000,
        term_months: int = 12
    ) -> Loan:
        if user is None:
            user = user_factory()

        return Loan(
            id=f"loan-{uuid.uuid4()}",
            user_id=user.id,
            amount=amount,
            term_months=term_months
        )
    return _create_loan
```

## Yield Fixtures (Setup/Teardown)

```python
# CORRECT: Resource management with yield
@pytest.fixture
async def redis_client():
    """Provide Redis client with cleanup."""
    client = Redis.from_url("redis://localhost:6379/1")

    # Setup complete, provide fixture
    yield client

    # Teardown: cleanup after test
    await client.flushdb()
    await client.close()


# CORRECT: File handling with yield
@pytest.fixture
def temp_file(tmp_path):
    """Create temporary file with cleanup."""
    file_path = tmp_path / "test_data.json"
    file_path.write_text('{"key": "value"}')

    yield file_path

    # Teardown: file automatically cleaned by tmp_path fixture


# CORRECT: Mock patching with yield
@pytest.fixture
def mock_external_api():
    """Mock external API calls."""
    with patch("finance_lending_api.integrations.credit_bureau.CreditBureauClient") as mock:
        mock.return_value.get_credit_score.return_value = 750
        yield mock


# INCORRECT: Using return instead of yield for cleanup
@pytest.fixture
async def bad_redis_client():
    """WRONG: No cleanup performed."""
    client = Redis.from_url("redis://localhost:6379/1")
    return client  # Cleanup never happens!
```

## Autouse Fixtures

```python
# CORRECT: Autouse for logging setup (runs automatically)
@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    """Configure logging for all tests."""
    import logging
    logging.basicConfig(level=logging.DEBUG)


# CORRECT: Autouse for transaction rollback in integration tests
@pytest.fixture(autouse=True, scope="function")
async def transaction_rollback(database_session):
    """Automatically rollback each test's database changes."""
    await database_session.begin()
    yield
    await database_session.rollback()


# CORRECT: Autouse for clearing Redis between tests
@pytest.fixture(autouse=True, scope="function")
async def clear_redis(redis_client):
    """Clear Redis before each test."""
    await redis_client.flushdb()


# INCORRECT: Autouse for expensive operation
@pytest.fixture(autouse=True)
async def expensive_setup():
    """WRONG: Runs for ALL tests, even those that don't need it."""
    await initialize_machine_learning_model()  # Slow!
```

## Parametrized Fixtures

```python
# CORRECT: Parametrize fixture for multiple scenarios
@pytest.fixture(params=[
    ("user@example.com", True),
    ("invalid-email", False),
    ("user@", False),
    ("@example.com", False),
])
def email_validation_case(request):
    """Provide email validation test cases."""
    return request.param


@pytest.mark.unit
def test_email_validation(email_validation_case):
    """Test email validation with multiple cases."""
    email, expected_valid = email_validation_case
    result = is_valid_email(email)
    assert result == expected_valid


# CORRECT: Parametrize fixture for different service types
@pytest.fixture(params=["postgres", "mongo"])
def data_service_client(request):
    """Provide different data service clients."""
    if request.param == "postgres":
        return PostgresDataServiceClient("http://localhost:8001")
    elif request.param == "mongo":
        return MongoDataServiceClient("http://localhost:8002")


# Using parametrized fixture
@pytest.mark.integration
async def test_user_creation_across_services(data_service_client):
    """Test user creation works with both PostgreSQL and MongoDB."""
    user = await data_service_client.create_user({
        "email": "test@example.com",
        "name": "Test User"
    })
    assert user["email"] == "test@example.com"
```

## Async Fixtures

```python
# CORRECT: Async fixture for async resources
@pytest.fixture
async def async_redis_client() -> AsyncGenerator[Redis, None]:
    """Provide async Redis client."""
    client = Redis.from_url("redis://localhost:6379/1")

    # Verify connection
    await client.ping()

    yield client

    await client.flushdb()
    await client.close()


# CORRECT: Async fixture composition
@pytest.fixture
async def user_with_loans(user_factory, loan_factory):
    """Create user with multiple loans."""
    user = user_factory(email="borrower@example.com", credit_score=750)
    loans = [
        await loan_factory(user=user, amount=10000),
        await loan_factory(user=user, amount=5000),
        await loan_factory(user=user, amount=15000),
    ]
    return user, loans


# Using async fixtures
@pytest.mark.asyncio
async def test_user_total_debt(user_with_loans):
    """Test total debt calculation."""
    user, loans = user_with_loans
    total_debt = sum(loan.amount for loan in loans)
    assert total_debt == 30000
```

## Best Practices

### DO: Keep Fixtures Focused

```python
# CORRECT: Single-purpose fixtures
@pytest.fixture
def valid_email() -> str:
    return "test@example.com"


@pytest.fixture
def valid_user_data(valid_email) -> dict:
    return {
        "email": valid_email,
        "name": "Test User",
        "phone": "+1234567890"
    }


# INCORRECT: Fixture doing too much
@pytest.fixture
def everything():
    """WRONG: Fixture provides unrelated things."""
    return {
        "user": User(email="test@example.com"),
        "redis": Redis.from_url("redis://localhost"),
        "config": {"DEBUG": True},
        "random_data": [1, 2, 3]
    }
```

### DO: Use Meaningful Names

```python
# CORRECT: Clear, descriptive names
@pytest.fixture
def authenticated_user() -> User:
    return User(id="user-123", email="auth@example.com")


@pytest.fixture
def expired_token() -> str:
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."


# INCORRECT: Vague names
@pytest.fixture
def data():  # What kind of data?
    return {"key": "value"}


@pytest.fixture
def obj():  # What object?
    return SomeClass()
```

### DO: Document Fixture Purpose

```python
# CORRECT: Clear docstrings
@pytest.fixture
async def postgres_data_service_client(test_config) -> AsyncGenerator[DataServiceClient, None]:
    """Provide HTTP client for PostgreSQL data service.

    Connects to the test instance of template_data_postgres_api service.
    Automatically cleans up test data after each test.

    Yields:
        DataServiceClient configured for PostgreSQL data service
    """
    client = DataServiceClient(base_url=test_config["POSTGRES_SERVICE_URL"])
    yield client
    await client.cleanup_test_data()
    await client.close()
```

### DON'T: Share Mutable State

```python
# INCORRECT: Mutable fixture shared across tests
@pytest.fixture(scope="module")
def shared_cache():
    """WRONG: Tests will pollute each other."""
    return {}  # Mutable dict shared across all tests


# CORRECT: Fresh instance per test
@pytest.fixture(scope="function")
def isolated_cache():
    """Each test gets fresh cache."""
    return {}
```

## Common Patterns for Microservices

### FastAPI Application Fixture

```python
@pytest.fixture
async def app() -> FastAPI:
    """Provide FastAPI application instance."""
    from finance_lending_api.main import create_app
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide HTTP client for FastAPI testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### RabbitMQ Connection Fixture

```python
@pytest.fixture
async def rabbitmq_connection(test_config):
    """Provide RabbitMQ connection for testing."""
    connection = await aio_pika.connect_robust(test_config["RABBITMQ_URL"])
    yield connection
    await connection.close()


@pytest.fixture
async def rabbitmq_channel(rabbitmq_connection):
    """Provide RabbitMQ channel from connection."""
    channel = await rabbitmq_connection.channel()
    yield channel
    await channel.close()
```

### Data Service Client Fixture

```python
@pytest.fixture
async def postgres_client(test_config) -> AsyncGenerator[DataServiceClient, None]:
    """Provide PostgreSQL data service client."""
    client = DataServiceClient(test_config["POSTGRES_SERVICE_URL"])
    yield client
    await client.close()
```

## Checklist

- [ ] Fixtures have appropriate scope (function/class/module/session)
- [ ] Async fixtures use `async def` and `AsyncGenerator` type hints
- [ ] Resource cleanup uses `yield` pattern, not `return`
- [ ] Fixtures have clear, descriptive names
- [ ] Each fixture has a docstring explaining its purpose
- [ ] Conftest.py files organized by test directory hierarchy
- [ ] Autouse fixtures used sparingly (only for cross-cutting concerns)
- [ ] Factory fixtures used for creating multiple instances
- [ ] Fixture composition leverages dependency injection
- [ ] Mutable state not shared across tests via fixtures
- [ ] Parametrized fixtures used for data-driven testing
- [ ] Integration test fixtures clean up resources properly

## Related Documents

- `docs/atomic/testing/unit-testing/pytest-setup.md` — Pytest configuration and basic setup
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies in tests
- `docs/atomic/testing/unit-testing/parametrized-tests.md` — Advanced parametrization techniques
- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Docker-based fixtures for integration tests
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — FastAPI-specific testing patterns
