# Pytest Setup

Configure pytest for unit testing with proper fixtures, markers, and coverage reporting. Pytest is the standard testing framework for Python services in this platform, providing powerful fixtures, parametrization, and plugin ecosystem.

## Configuration

Create `pytest.ini` in your project root to define test discovery patterns, markers, and default options:

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    --verbose
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80

markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require databases, Redis, RabbitMQ)
    slow: Slow tests (> 1 second)
    asyncio: Async tests requiring asyncio event loop
```

### Coverage Configuration

Add `.coveragerc` to configure coverage reporting:

```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

## Project Structure

Organize tests to mirror your source code structure:

```
project/
├── src/
│   └── finance_lending_api/
│       ├── domain/
│       │   └── user_service.py
│       ├── infrastructure/
│       │   └── repositories.py
│       └── api/
│           └── routers.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   └── test_user_service.py
│   │   └── infrastructure/
│   │       └── test_repositories.py
│   ├── integration/
│   │   └── test_postgres_integration.py
│   └── conftest.py
├── pytest.ini
├── .coveragerc
└── pyproject.toml
```

## Dependencies

Add pytest and plugins to `pyproject.toml`:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "pytest-mock>=3.12",
    "pytest-xdist>=3.5",  # parallel test execution
    "httpx>=0.27",        # for testing async HTTP
]
```

Install test dependencies:

```bash
pip install -e ".[test]"
```

## Basic Test Example

```python
# tests/unit/domain/test_user_service.py
import pytest
from finance_lending_api.domain.user_service import UserService
from finance_lending_api.domain.models import User


# CORRECT: Clear test name, async, proper fixtures
@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_validates_email():
    """Test that create_user validates email format."""
    service = UserService()

    with pytest.raises(ValueError, match="Invalid email"):
        await service.create_user(email="invalid-email", name="John Doe")


# CORRECT: Parametrized test for multiple cases
@pytest.mark.unit
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid", False),
    ("user@", False),
    ("@example.com", False),
])
def test_email_validation(email: str, expected: bool):
    """Test email validation with various inputs."""
    from finance_lending_api.utils import is_valid_email
    assert is_valid_email(email) == expected


# INCORRECT: No markers, unclear name, not async
def test_user():
    user = create_user("test")
    assert user  # What are we testing?
```

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Run specific file
pytest tests/unit/domain/test_user_service.py

# Run specific test
pytest tests/unit/domain/test_user_service.py::test_create_user_validates_email

# Run with verbose output
pytest -vv

# Stop on first failure
pytest -x
```

## Markers Usage

Mark tests appropriately for selective execution:

```python
import pytest

@pytest.mark.unit
def test_fast_operation():
    """Fast test with no external dependencies."""
    pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_operation():
    """Integration test requiring database."""
    pass

@pytest.mark.slow
def test_expensive_computation():
    """Test that takes > 1 second."""
    pass

# Custom markers defined in pytest.ini
@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_function():
    """Async test requiring event loop."""
    result = await some_async_function()
    assert result is not None
```

## Checklist

- [ ] `pytest.ini` configured with test paths and markers
- [ ] `.coveragerc` configured for coverage reporting
- [ ] Test structure mirrors source code structure
- [ ] All tests have descriptive names (`test_<what>_<scenario>`)
- [ ] Tests marked appropriately (`@pytest.mark.unit`, etc.)
- [ ] Async tests use `@pytest.mark.asyncio`
- [ ] Coverage target set (typically 80%+)
- [ ] Tests run successfully: `pytest -m unit`

## Related Documents

- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Pytest fixture patterns and best practices
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies in tests
- `docs/atomic/testing/unit-testing/parametrized-tests.md` — Advanced parametrization techniques
- `docs/atomic/testing/unit-testing/coverage-requirements.md` — Coverage standards and enforcement
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — Testing FastAPI services
