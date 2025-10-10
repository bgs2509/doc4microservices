# Mocking Strategies

Master mocking strategies to isolate units under test from external dependencies, enabling fast, deterministic unit tests that don't rely on databases, external APIs, or other services. Mocks replace real objects with controlled test doubles that verify interactions and return predictable values.

This document covers pytest-mock patterns, AsyncMock for async code, patching strategies, and best practices for mocking Redis, HTTP clients, databases, and RabbitMQ connections in Python microservices. Proper mocking enables true unit testing by eliminating external dependencies while maintaining test realism.

Understanding when to mock (unit tests) versus when to use real dependencies (integration tests) is critical for building a balanced test suite. Mocking reduces test runtime from seconds to milliseconds and eliminates flaky tests caused by external service failures.

## Setup

### Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-mock>=3.12",     # pytest wrapper for unittest.mock
    "pytest-asyncio>=0.23",  # for async tests
    "httpx>=0.27",           # for testing HTTP clients
]
```

### Import Patterns

```python
# CORRECT: Import mocking tools
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
from pytest_mock import MockerFixture


# Using pytest-mock fixture (recommended)
@pytest.mark.unit
def test_with_mocker(mocker: MockerFixture):
    """Mocker fixture provides convenient mocking."""
    mock_redis = mocker.patch("my_module.redis_client")
    mock_redis.get.return_value = "cached_value"


# Using unittest.mock directly (also valid)
@pytest.mark.unit
@patch("my_module.redis_client")
def test_with_patch(mock_redis):
    """Traditional patch decorator."""
    mock_redis.get.return_value = "cached_value"
```

## Basic Mocking Patterns

### Mock vs MagicMock

```python
from unittest.mock import Mock, MagicMock


# CORRECT: Use Mock for simple objects
@pytest.mark.unit
def test_with_mock():
    """Mock provides basic mocking functionality."""
    mock_service = Mock()
    mock_service.get_user.return_value = {"id": "user-123", "name": "Test"}

    result = mock_service.get_user("user-123")
    assert result["name"] == "Test"
    mock_service.get_user.assert_called_once_with("user-123")


# CORRECT: Use MagicMock for objects needing magic methods
@pytest.mark.unit
def test_with_magic_mock():
    """MagicMock supports magic methods like __len__, __iter__."""
    mock_list = MagicMock()
    mock_list.__len__.return_value = 3
    mock_list.__iter__.return_value = iter([1, 2, 3])

    assert len(mock_list) == 3
    assert list(mock_list) == [1, 2, 3]


# INCORRECT: Using Mock when magic methods needed
@pytest.mark.unit
def test_bad_mock():
    """WRONG: Mock doesn't support magic methods by default."""
    mock_list = Mock()
    # len(mock_list)  # TypeError: object of type 'Mock' has no len()
```

### Return Values and Side Effects

```python
# CORRECT: Simple return value
@pytest.mark.unit
def test_return_value():
    """Mock returns fixed value."""
    mock_service = Mock()
    mock_service.calculate_interest.return_value = 150.50

    result = mock_service.calculate_interest(amount=10000, rate=0.05)
    assert result == 150.50


# CORRECT: Different return values for sequential calls
@pytest.mark.unit
def test_side_effect_sequence():
    """Mock returns different values for each call."""
    mock_service = Mock()
    mock_service.get_random_number.side_effect = [1, 2, 3]

    assert mock_service.get_random_number() == 1
    assert mock_service.get_random_number() == 2
    assert mock_service.get_random_number() == 3


# CORRECT: Side effect raises exception
@pytest.mark.unit
def test_side_effect_exception():
    """Mock raises exception."""
    mock_service = Mock()
    mock_service.connect.side_effect = ConnectionError("Connection failed")

    with pytest.raises(ConnectionError, match="Connection failed"):
        mock_service.connect()


# CORRECT: Side effect with custom function
@pytest.mark.unit
def test_side_effect_function():
    """Mock uses function to compute return value."""
    def calculate_total(items: list) -> float:
        return sum(item["price"] for item in items)

    mock_service = Mock()
    mock_service.calculate_total.side_effect = calculate_total

    result = mock_service.calculate_total([
        {"price": 10.0},
        {"price": 20.0},
    ])
    assert result == 30.0
```

## Patching Strategies

### patch() Decorator

```python
# CORRECT: Patch at import location (where it's used, not where it's defined)
@pytest.mark.unit
@patch("finance_lending_api.domain.services.redis_client")
async def test_cache_lookup(mock_redis):
    """Patch Redis client where it's imported."""
    mock_redis.get.return_value = '{"user_id": "user-123"}'

    from finance_lending_api.domain.services import UserService
    service = UserService()
    result = await service.get_cached_user("user-123")

    assert result["user_id"] == "user-123"
    mock_redis.get.assert_called_once_with("user:user-123")


# INCORRECT: Patching where defined instead of where used
@pytest.mark.unit
@patch("redis.asyncio.Redis")  # WRONG: Patches redis library, not our import
async def test_bad_patch(mock_redis):
    """This won't work because UserService imports from different location."""
    from finance_lending_api.domain.services import UserService
    service = UserService()
    # Our redis_client is already imported, patch has no effect
```

### patch.object()

```python
# CORRECT: Patch specific method on object
@pytest.mark.unit
async def test_patch_method():
    """Patch single method without replacing entire object."""
    from finance_lending_api.domain.services import UserService

    service = UserService()

    with patch.object(service, "validate_email", return_value=True):
        result = await service.create_user(email="invalid-email", name="Test")
        # validate_email is mocked to always return True
        assert result is not None


# CORRECT: Patch multiple methods on same object
@pytest.mark.unit
async def test_patch_multiple_methods():
    """Patch multiple methods with patch.object."""
    from finance_lending_api.integrations.http_client import HTTPClient

    client = HTTPClient()

    with patch.object(client, "get", return_value={"status": "ok"}):
        with patch.object(client, "post", return_value={"id": "123"}):
            get_result = await client.get("/api/status")
            post_result = await client.post("/api/users", data={})

            assert get_result["status"] == "ok"
            assert post_result["id"] == "123"
```

### Mocker Fixture (pytest-mock)

```python
# CORRECT: Use mocker fixture (cleaner syntax)
@pytest.mark.unit
async def test_with_mocker(mocker: MockerFixture):
    """Mocker fixture provides convenient patching."""
    # Patch function
    mock_validate = mocker.patch(
        "finance_lending_api.domain.validators.validate_email",
        return_value=True
    )

    # Patch class
    mock_redis = mocker.patch("finance_lending_api.integrations.redis_client.Redis")
    mock_redis.return_value.get.return_value = "cached"

    from finance_lending_api.domain.services import UserService
    service = UserService()
    result = await service.get_user("user-123")

    mock_validate.assert_called()
    mock_redis.return_value.get.assert_called_once()
```

## Async Mocking

### AsyncMock for Async Functions

```python
# CORRECT: Use AsyncMock for async functions
@pytest.mark.asyncio
async def test_async_mock():
    """AsyncMock works with await."""
    mock_service = AsyncMock()
    mock_service.fetch_data.return_value = {"data": "value"}

    result = await mock_service.fetch_data()
    assert result["data"] == "value"
    mock_service.fetch_data.assert_called_once()


# CORRECT: Mock async context manager
@pytest.mark.asyncio
async def test_async_context_manager():
    """Mock async with statement."""
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = {"status": "ok"}

    async with mock_client as client:
        result = await client.get("/status")
        assert result["status"] == "ok"


# INCORRECT: Using regular Mock for async function
@pytest.mark.asyncio
async def test_bad_async_mock():
    """WRONG: Regular Mock doesn't work with await."""
    mock_service = Mock()
    mock_service.fetch_data.return_value = {"data": "value"}

    # result = await mock_service.fetch_data()  # TypeError: object Mock can't be used in 'await'
```

## Mocking External Dependencies

### Redis Mocking

```python
# CORRECT: Mock Redis client
@pytest.mark.unit
@patch("finance_lending_api.integrations.redis_client.Redis")
async def test_redis_cache(mock_redis_class):
    """Mock Redis client for caching logic."""
    mock_redis_instance = AsyncMock()
    mock_redis_class.from_url.return_value = mock_redis_instance

    # Mock cache miss then cache hit
    mock_redis_instance.get.side_effect = [None, '{"user_id": "user-123"}']
    mock_redis_instance.setex.return_value = True

    from finance_lending_api.services.cache import CacheService
    cache = CacheService()

    # First call: cache miss
    result1 = await cache.get_user("user-123")
    assert result1 is None

    # Set cache
    await cache.set_user("user-123", {"user_id": "user-123"})

    # Second call: cache hit
    result2 = await cache.get_user("user-123")
    assert result2["user_id"] == "user-123"

    mock_redis_instance.setex.assert_called_once()
```

### HTTP Client Mocking

```python
# CORRECT: Mock httpx.AsyncClient
@pytest.mark.asyncio
async def test_http_client(mocker: MockerFixture):
    """Mock HTTP calls to external services."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"credit_score": 750}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    from finance_lending_api.integrations.credit_bureau import CreditBureauClient
    bureau = CreditBureauClient()
    score = await bureau.get_credit_score("user-123")

    assert score == 750
    mock_client.get.assert_called_once_with(
        "https://credit-bureau.example.com/api/score/user-123"
    )


# CORRECT: Mock respx for httpx (alternative approach)
import respx

@pytest.mark.asyncio
@respx.mock
async def test_with_respx():
    """Use respx library to mock httpx requests."""
    respx.get("https://api.example.com/users/123").mock(
        return_value=httpx.Response(200, json={"id": "123", "name": "Test"})
    )

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users/123")
        data = response.json()

    assert data["name"] == "Test"
```

### Database Mocking

```python
# CORRECT: Mock database session
@pytest.mark.unit
async def test_repository(mocker: MockerFixture):
    """Mock SQLAlchemy session for repository tests."""
    mock_session = AsyncMock()
    mock_user = Mock()
    mock_user.id = "user-123"
    mock_user.email = "test@example.com"

    # Mock query result
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    from finance_lending_api.infrastructure.repositories import UserRepository
    repo = UserRepository(session=mock_session)
    user = await repo.get_by_id("user-123")

    assert user.email == "test@example.com"
    mock_session.execute.assert_called_once()


# INCORRECT: Don't mock database in integration tests
@pytest.mark.integration  # WRONG: Integration tests should use real database
async def test_bad_integration(mocker: MockerFixture):
    """This defeats the purpose of integration testing."""
    mock_session = mocker.patch("sqlalchemy.orm.Session")
    # Integration tests should use testcontainers or real database
```

### RabbitMQ Mocking

```python
# CORRECT: Mock RabbitMQ channel and queue
@pytest.mark.unit
async def test_rabbitmq_publish(mocker: MockerFixture):
    """Mock RabbitMQ message publishing."""
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_channel.default_exchange = mock_exchange

    mocker.patch(
        "finance_lending_api.integrations.rabbitmq.get_channel",
        return_value=mock_channel
    )

    from finance_lending_api.events.publisher import EventPublisher
    publisher = EventPublisher()
    await publisher.publish_user_created(user_id="user-123")

    mock_exchange.publish.assert_called_once()
    call_args = mock_exchange.publish.call_args
    assert "user-123" in str(call_args)
```

## Assertion Patterns

### Call Assertions

```python
# CORRECT: Assert mock was called correctly
@pytest.mark.unit
def test_call_assertions():
    """Verify mock call patterns."""
    mock_service = Mock()
    mock_service.create_user("user@example.com", "John")

    # Assert called once
    mock_service.create_user.assert_called_once()

    # Assert called with specific arguments
    mock_service.create_user.assert_called_once_with("user@example.com", "John")

    # Assert called with (allows multiple calls)
    mock_service.create_user.assert_called_with("user@example.com", "John")

    # Assert any call (for multiple calls)
    mock_service.create_user("jane@example.com", "Jane")
    mock_service.create_user.assert_any_call("user@example.com", "John")
    mock_service.create_user.assert_any_call("jane@example.com", "Jane")


# CORRECT: Assert call count
@pytest.mark.unit
def test_call_count():
    """Verify number of calls."""
    mock_service = Mock()
    mock_service.notify("user-1")
    mock_service.notify("user-2")
    mock_service.notify("user-3")

    assert mock_service.notify.call_count == 3


# CORRECT: Assert not called
@pytest.mark.unit
def test_not_called():
    """Verify mock was never called."""
    mock_service = Mock()
    # Don't call mock_service.some_method()

    mock_service.some_method.assert_not_called()


# CORRECT: Inspect call arguments
@pytest.mark.unit
def test_call_args():
    """Inspect what arguments were passed."""
    mock_service = Mock()
    mock_service.log_event("user_created", user_id="user-123", timestamp=1234567890)

    # Access call arguments
    call_args = mock_service.log_event.call_args
    assert call_args.args[0] == "user_created"
    assert call_args.kwargs["user_id"] == "user-123"

    # Or use call() helper
    mock_service.log_event.assert_called_with(
        "user_created",
        user_id="user-123",
        timestamp=1234567890
    )
```

## Best Practices

### DO: Mock at the Boundary

```python
# CORRECT: Mock external dependencies (Redis, HTTP, database)
@pytest.mark.unit
async def test_business_logic_mocked_dependencies(mocker: MockerFixture):
    """Unit test: mock external dependencies, test business logic."""
    # Mock Redis
    mocker.patch("finance_lending_api.integrations.redis_client.get", return_value=None)

    # Mock HTTP client
    mock_http = mocker.patch("finance_lending_api.integrations.http_client.post")
    mock_http.return_value = {"approved": True}

    from finance_lending_api.domain.services import LoanService
    service = LoanService()
    result = await service.apply_for_loan(user_id="user-123", amount=10000)

    assert result["approved"] is True


# INCORRECT: Mocking internal business logic
@pytest.mark.unit
async def test_bad_mocking(mocker: MockerFixture):
    """WRONG: Mocking the very logic you're trying to test."""
    mocker.patch(
        "finance_lending_api.domain.services.LoanService.calculate_interest",
        return_value=150.0
    )
    # Now we're not testing calculate_interest at all!
```

### DO: Use Real Objects When Possible

```python
# CORRECT: Use real domain objects, mock only external dependencies
@pytest.mark.unit
async def test_with_real_domain_objects(mocker: MockerFixture):
    """Use real domain objects, mock only integrations."""
    from finance_lending_api.domain.models import User, LoanApplication

    # Real domain objects
    user = User(id="user-123", credit_score=750)
    application = LoanApplication(user_id=user.id, amount=10000)

    # Mock only external service
    mock_credit_bureau = mocker.patch(
        "finance_lending_api.integrations.credit_bureau.get_score",
        return_value=750
    )

    from finance_lending_api.domain.services import LoanService
    service = LoanService()
    result = await service.evaluate_application(application)

    assert result.approved is True
```

### DON'T: Over-Mock

```python
# INCORRECT: Mocking everything (testing nothing)
@pytest.mark.unit
def test_over_mocked(mocker: MockerFixture):
    """WRONG: So much mocking that test has no value."""
    mock_service = mocker.Mock()
    mock_service.process.return_value = "success"

    result = mock_service.process()
    assert result == "success"  # This test proves nothing!


# CORRECT: Test real logic with minimal mocking
@pytest.mark.unit
def test_appropriate_mocking():
    """Test real calculation logic, mock only data source."""
    from finance_lending_api.domain.calculators import InterestCalculator

    calculator = InterestCalculator()
    interest = calculator.calculate(principal=10000, rate=0.05, years=2)

    assert interest == 1000.0  # Tests real calculation logic
```

### DO: Document Why You're Mocking

```python
# CORRECT: Explain why dependency is mocked
@pytest.mark.unit
async def test_user_creation(mocker: MockerFixture):
    """Test user creation logic.

    Mocks:
        - Redis: Avoid external cache dependency for unit test
        - PostgreSQL HTTP client: Data service unavailable in unit test environment
        - RabbitMQ: Event publishing tested separately in integration tests
    """
    mock_redis = mocker.patch("finance_lending_api.integrations.redis.get")
    mock_postgres = mocker.patch("finance_lending_api.integrations.postgres_client.post")
    mock_rabbitmq = mocker.patch("finance_lending_api.events.publish")

    # Test business logic
    ...
```

## Checklist

- [ ] Mock external dependencies (Redis, HTTP, databases, RabbitMQ) in unit tests
- [ ] Use `AsyncMock` for async functions and async context managers
- [ ] Patch at import location (where used), not where defined
- [ ] Use `mocker` fixture (pytest-mock) for cleaner syntax
- [ ] Assert mock calls with `assert_called_once_with()`, `assert_any_call()`, etc.
- [ ] Use real domain objects when possible, mock only boundaries
- [ ] Don't mock the code under test (mock dependencies, not business logic)
- [ ] Document why dependencies are mocked in test docstrings
- [ ] Prefer integration tests with real dependencies when testing integration logic
- [ ] Use `side_effect` for exceptions and sequential return values
- [ ] Reset mocks between tests (pytest-mock does this automatically)
- [ ] Don't over-mock (balance between isolation and realism)

## Related Documents

- `docs/atomic/testing/unit-testing/pytest-setup.md` — Pytest configuration and basic setup
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Reusable test fixtures
- `docs/atomic/testing/unit-testing/parametrized-tests.md` — Data-driven testing with parametrize
- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Use real dependencies with Docker
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — Testing FastAPI endpoints
