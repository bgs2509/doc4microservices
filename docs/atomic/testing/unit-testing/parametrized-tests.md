# Parametrized Tests

Eliminate test duplication by running the same test logic with multiple input variations using pytest parametrization. Parametrized tests enable data-driven testing where a single test function executes multiple times with different argument sets, improving coverage while reducing code duplication.

This document covers pytest.mark.parametrize patterns, fixture parametrization, test case naming strategies, and best practices for validation testing, edge case coverage, and business rule verification. Parametrization turns one test into dozens while keeping your test suite maintainable.

Parametrization is essential for thorough testing of validators, calculators, parsers, and any function with multiple execution paths. Instead of writing 20 nearly-identical test functions, write one parametrized test with 20 test cases.

## Basic Parametrization

### Simple Parametrize

```python
import pytest


# CORRECT: Parametrize with single parameter
@pytest.mark.parametrize("email", [
    "user@example.com",
    "user.name@example.com",
    "user+tag@example.co.uk",
])
@pytest.mark.unit
def test_valid_emails(email: str):
    """Test that valid emails pass validation."""
    from finance_lending_api.domain.validators import is_valid_email
    assert is_valid_email(email) is True


# CORRECT: Parametrize with expected outcome
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("user@", False),
    ("@example.com", False),
    ("user@.com", False),
])
@pytest.mark.unit
def test_email_validation(email: str, expected: bool):
    """Test email validation with valid and invalid inputs."""
    from finance_lending_api.domain.validators import is_valid_email
    assert is_valid_email(email) == expected


# INCORRECT: Writing separate test for each case
@pytest.mark.unit
def test_email_valid_1():  # WRONG: Duplicate test logic
    assert is_valid_email("user@example.com") is True

@pytest.mark.unit
def test_email_valid_2():  # WRONG: Duplicate test logic
    assert is_valid_email("user.name@example.com") is True

@pytest.mark.unit
def test_email_valid_3():  # WRONG: Duplicate test logic
    assert is_valid_email("user+tag@example.co.uk") is True
# ... (repetitive)
```

### Multiple Parameters

```python
# CORRECT: Parametrize with multiple parameters
@pytest.mark.parametrize("principal,rate,years,expected_interest", [
    (10000, 0.05, 1, 500.0),
    (10000, 0.05, 2, 1000.0),
    (5000, 0.10, 1, 500.0),
    (20000, 0.03, 3, 1800.0),
    (0, 0.05, 1, 0.0),
])
@pytest.mark.unit
def test_simple_interest_calculation(
    principal: float,
    rate: float,
    years: int,
    expected_interest: float
):
    """Test simple interest formula: I = P * R * T."""
    from finance_lending_api.domain.calculators import calculate_simple_interest

    result = calculate_simple_interest(
        principal=principal,
        annual_rate=rate,
        years=years
    )

    assert result == pytest.approx(expected_interest, rel=1e-2)
```

## Test Case Naming

### IDs for Readable Output

```python
# CORRECT: Use ids parameter for descriptive test names
@pytest.mark.parametrize(
    "credit_score,expected_approved",
    [
        (800, True),
        (750, True),
        (700, True),
        (650, False),
        (600, False),
        (500, False),
    ],
    ids=[
        "excellent_credit",
        "good_credit",
        "fair_credit_approved",
        "fair_credit_declined",
        "poor_credit",
        "very_poor_credit",
    ]
)
@pytest.mark.unit
def test_loan_approval_by_credit_score(credit_score: int, expected_approved: bool):
    """Test loan approval based on credit score threshold (700+)."""
    from finance_lending_api.domain.services import LoanService

    service = LoanService()
    result = service.evaluate_loan(credit_score=credit_score, income=50000)

    assert result.approved == expected_approved


# Output:
# test_loan_approval_by_credit_score[excellent_credit] PASSED
# test_loan_approval_by_credit_score[good_credit] PASSED
# test_loan_approval_by_credit_score[fair_credit_approved] PASSED
# test_loan_approval_by_credit_score[fair_credit_declined] FAILED


# INCORRECT: No ids (cryptic test output)
@pytest.mark.parametrize(
    "credit_score,expected_approved",
    [(800, True), (750, True), (650, False)]
)
@pytest.mark.unit
def test_loan_approval(credit_score: int, expected_approved: bool):
    # ...
    pass

# Output:
# test_loan_approval[800-True] PASSED  # Hard to understand what this means
# test_loan_approval[750-True] PASSED
# test_loan_approval[650-False] FAILED
```

### Automatic ID Generation

```python
# CORRECT: Use pytest.param with id
@pytest.mark.parametrize(
    "user_data,expected_error",
    [
        pytest.param(
            {"email": "invalid", "name": "John"},
            "Invalid email format",
            id="invalid_email"
        ),
        pytest.param(
            {"email": "john@example.com", "name": ""},
            "Name is required",
            id="missing_name"
        ),
        pytest.param(
            {"email": "john@example.com"},
            "Name is required",
            id="name_field_absent"
        ),
    ]
)
@pytest.mark.unit
def test_user_validation_errors(user_data: dict, expected_error: str):
    """Test user input validation error messages."""
    from finance_lending_api.domain.validators import validate_user_data

    with pytest.raises(ValueError, match=expected_error):
        validate_user_data(user_data)
```

## Parametrizing Fixtures

### Fixture Parametrization

```python
# CORRECT: Parametrize fixture to run tests with different configurations
@pytest.fixture(params=["postgres", "mongo"])
def database_client(request):
    """Provide different database clients."""
    if request.param == "postgres":
        from finance_lending_api.integrations import PostgresClient
        client = PostgresClient("http://localhost:8001")
    elif request.param == "mongo":
        from finance_lending_api.integrations import MongoClient
        client = MongoClient("http://localhost:8002")

    yield client
    # Cleanup after test
    client.close()


@pytest.mark.integration
async def test_user_creation_across_databases(database_client):
    """Test user creation works with both PostgreSQL and MongoDB."""
    user = await database_client.create_user({
        "email": "test@example.com",
        "name": "Test User"
    })

    assert user["email"] == "test@example.com"
    assert "id" in user

# This test runs twice automatically:
# - test_user_creation_across_databases[postgres]
# - test_user_creation_across_databases[mongo]


# CORRECT: Parametrize fixture with IDs
@pytest.fixture(
    params=[
        ("redis://localhost:6379/0", "local"),
        ("redis://redis-test:6379/1", "docker"),
    ],
    ids=["local_redis", "docker_redis"]
)
def redis_url(request):
    """Provide different Redis connection URLs."""
    return request.param[0]
```

## Nested Parametrization

### Multiple Parametrize Decorators

```python
# CORRECT: Combine parametrize decorators (cartesian product)
@pytest.mark.parametrize("credit_score", [650, 700, 750, 800])
@pytest.mark.parametrize("income", [30000, 50000, 70000, 100000])
@pytest.mark.unit
def test_loan_approval_matrix(credit_score: int, income: int):
    """Test loan approval with various credit scores and incomes.

    This creates 4 * 4 = 16 test cases.
    """
    from finance_lending_api.domain.services import LoanService

    service = LoanService()
    result = service.evaluate_loan(
        credit_score=credit_score,
        income=income,
        requested_amount=10000
    )

    # Approval criteria: credit_score >= 700 AND income >= 50000
    should_approve = credit_score >= 700 and income >= 50000
    assert result.approved == should_approve


# Output: 16 test cases
# test_loan_approval_matrix[30000-650] PASSED
# test_loan_approval_matrix[30000-700] PASSED
# ...
# test_loan_approval_matrix[100000-800] PASSED
```

## Complex Test Cases

### Parametrize with Dictionaries

```python
# CORRECT: Use dictionaries for complex test cases
@pytest.mark.parametrize(
    "test_case",
    [
        {
            "id": "approved_high_credit",
            "input": {
                "credit_score": 800,
                "income": 100000,
                "debt_ratio": 0.2,
                "employment_years": 5,
            },
            "expected": {
                "approved": True,
                "interest_rate": 3.5,
                "max_amount": 50000,
            }
        },
        {
            "id": "declined_low_credit",
            "input": {
                "credit_score": 600,
                "income": 50000,
                "debt_ratio": 0.5,
                "employment_years": 1,
            },
            "expected": {
                "approved": False,
                "interest_rate": None,
                "max_amount": 0,
            }
        },
        {
            "id": "approved_medium_risk",
            "input": {
                "credit_score": 720,
                "income": 60000,
                "debt_ratio": 0.35,
                "employment_years": 3,
            },
            "expected": {
                "approved": True,
                "interest_rate": 4.5,
                "max_amount": 25000,
            }
        },
    ],
    ids=lambda tc: tc["id"]
)
@pytest.mark.unit
def test_loan_underwriting(test_case: dict):
    """Test comprehensive loan underwriting logic."""
    from finance_lending_api.domain.services import UnderwritingService

    service = UnderwritingService()
    result = service.evaluate(**test_case["input"])

    assert result.approved == test_case["expected"]["approved"]
    assert result.interest_rate == test_case["expected"]["interest_rate"]
    assert result.max_amount == test_case["expected"]["max_amount"]
```

### Parametrize with Classes

```python
# CORRECT: Parametrize entire test class
@pytest.mark.parametrize(
    "service_type",
    ["fastapi", "aiogram", "worker"],
    ids=["fastapi_service", "aiogram_bot", "asyncio_worker"]
)
class TestServiceHealthChecks:
    """Test health checks across all service types."""

    @pytest.mark.integration
    async def test_health_endpoint_returns_200(self, service_type: str):
        """All services should have working health endpoint."""
        from finance_lending_api.testing.utils import get_service_client

        client = get_service_client(service_type)
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.integration
    async def test_metrics_endpoint_returns_prometheus_format(self, service_type: str):
        """All services should expose Prometheus metrics."""
        from finance_lending_api.testing.utils import get_service_client

        client = get_service_client(service_type)
        response = await client.get("/metrics")

        assert response.status_code == 200
        assert "# TYPE" in response.text  # Prometheus format


# This creates 6 tests (2 test methods * 3 service types):
# TestServiceHealthChecks::test_health_endpoint_returns_200[fastapi_service]
# TestServiceHealthChecks::test_health_endpoint_returns_200[aiogram_bot]
# TestServiceHealthChecks::test_health_endpoint_returns_200[asyncio_worker]
# TestServiceHealthChecks::test_metrics_endpoint_returns_prometheus_format[fastapi_service]
# ...
```

## Edge Cases and Boundary Testing

### Boundary Value Analysis

```python
# CORRECT: Test boundary values explicitly
@pytest.mark.parametrize(
    "age,expected_category",
    [
        (0, "invalid"),
        (1, "child"),
        (17, "child"),
        (18, "adult"),
        (64, "adult"),
        (65, "senior"),
        (120, "senior"),
        (121, "invalid"),
    ],
    ids=[
        "below_minimum",
        "minimum_child",
        "maximum_child",
        "minimum_adult",
        "maximum_adult",
        "minimum_senior",
        "maximum_age",
        "above_maximum",
    ]
)
@pytest.mark.unit
def test_age_category_boundaries(age: int, expected_category: str):
    """Test age categorization at boundary values."""
    from finance_lending_api.domain.utils import categorize_age

    if expected_category == "invalid":
        with pytest.raises(ValueError):
            categorize_age(age)
    else:
        result = categorize_age(age)
        assert result == expected_category
```

## Exception Testing

### Parametrizing Expected Exceptions

```python
# CORRECT: Parametrize exception scenarios
@pytest.mark.parametrize(
    "amount,rate,term,expected_exception,error_message",
    [
        (-1000, 0.05, 12, ValueError, "Amount must be positive"),
        (10000, -0.05, 12, ValueError, "Rate must be positive"),
        (10000, 0.05, 0, ValueError, "Term must be at least 1 month"),
        (0, 0.05, 12, ValueError, "Amount must be positive"),
        (10000, 0, 12, ValueError, "Rate must be positive"),
    ],
    ids=[
        "negative_amount",
        "negative_rate",
        "zero_term",
        "zero_amount",
        "zero_rate",
    ]
)
@pytest.mark.unit
def test_loan_calculator_validation(
    amount: float,
    rate: float,
    term: int,
    expected_exception: type,
    error_message: str
):
    """Test loan calculator input validation."""
    from finance_lending_api.domain.calculators import LoanCalculator

    calculator = LoanCalculator()

    with pytest.raises(expected_exception, match=error_message):
        calculator.calculate_monthly_payment(
            amount=amount,
            annual_rate=rate,
            term_months=term
        )
```

## Async Parametrization

### Parametrizing Async Tests

```python
# CORRECT: Parametrize async tests
@pytest.mark.parametrize(
    "user_id,expected_found",
    [
        ("existing-user-123", True),
        ("non-existent-user", False),
    ],
    ids=["user_exists", "user_not_found"]
)
@pytest.mark.asyncio
async def test_user_lookup(user_id: str, expected_found: bool, mocker):
    """Test user lookup with existing and non-existing users."""
    from finance_lending_api.domain.services import UserService

    # Mock data service
    mock_client = mocker.patch("finance_lending_api.integrations.postgres_client")

    if expected_found:
        mock_client.get.return_value = {"id": user_id, "name": "Test User"}
    else:
        mock_client.get.return_value = None

    service = UserService()
    user = await service.get_user(user_id)

    if expected_found:
        assert user is not None
        assert user["id"] == user_id
    else:
        assert user is None
```

## Best Practices

### DO: Use Descriptive IDs

```python
# CORRECT: IDs explain what is being tested
@pytest.mark.parametrize(
    "input,expected",
    [
        ("+1234567890", True),
        ("+44 20 7946 0958", True),
        ("123", False),
        ("", False),
    ],
    ids=[
        "us_phone_valid",
        "uk_phone_with_spaces_valid",
        "too_short_invalid",
        "empty_string_invalid",
    ]
)
@pytest.mark.unit
def test_phone_validation(input: str, expected: bool):
    """Test international phone number validation."""
    assert is_valid_phone(input) == expected


# INCORRECT: Default IDs are unclear
@pytest.mark.parametrize(
    "input,expected",
    [("+1234567890", True), ("123", False)]
)
@pytest.mark.unit
def test_phone(input: str, expected: bool):
    assert is_valid_phone(input) == expected

# Output:
# test_phone[+1234567890-True] PASSED  # What does this mean?
```

### DO: Group Related Test Cases

```python
# CORRECT: Group related scenarios
valid_emails = [
    "user@example.com",
    "user.name@example.com",
    "user+tag@example.co.uk",
]

invalid_emails = [
    "invalid",
    "user@",
    "@example.com",
    "user@.com",
]

@pytest.mark.parametrize("email", valid_emails)
@pytest.mark.unit
def test_valid_email_formats(email: str):
    """Test that valid email formats pass validation."""
    assert is_valid_email(email) is True


@pytest.mark.parametrize("email", invalid_emails)
@pytest.mark.unit
def test_invalid_email_formats(email: str):
    """Test that invalid email formats fail validation."""
    assert is_valid_email(email) is False
```

### DON'T: Overuse Parametrization

```python
# INCORRECT: Parametrizing unrelated tests
@pytest.mark.parametrize(
    "test_case",
    [
        ("email_validation", "test@example.com", True),
        ("age_validation", 25, True),
        ("loan_calculation", 10000, 500.0),
    ]
)
@pytest.mark.unit
def test_everything(test_case: str, input: Any, expected: Any):
    """WRONG: Unrelated tests forced into parametrization."""
    if test_case == "email_validation":
        assert is_valid_email(input) == expected
    elif test_case == "age_validation":
        assert is_valid_age(input) == expected
    elif test_case == "loan_calculation":
        assert calculate_interest(input) == expected


# CORRECT: Separate tests for unrelated logic
@pytest.mark.unit
def test_email_validation():
    """Test email validation."""
    assert is_valid_email("test@example.com") is True


@pytest.mark.unit
def test_age_validation():
    """Test age validation."""
    assert is_valid_age(25) is True
```

### DO: Test Edge Cases

```python
# CORRECT: Include edge cases in parametrization
@pytest.mark.parametrize(
    "amount,expected_fee",
    [
        (0, 0.0),              # Edge: zero amount
        (0.01, 0.01),          # Edge: minimum amount
        (100, 1.0),            # Normal case
        (999999, 9999.99),     # Edge: large amount
        (1000000, 10000.0),    # Edge: maximum amount
    ],
    ids=["zero", "minimum", "normal", "large", "maximum"]
)
@pytest.mark.unit
def test_transaction_fee_calculation(amount: float, expected_fee: float):
    """Test transaction fee (1%) including edge cases."""
    from finance_lending_api.domain.calculators import calculate_fee

    result = calculate_fee(amount)
    assert result == pytest.approx(expected_fee, rel=1e-2)
```

## Checklist

- [ ] Use `@pytest.mark.parametrize` for tests with multiple input variations
- [ ] Provide descriptive `ids` for test case names
- [ ] Test boundary values explicitly (min, max, zero, negative)
- [ ] Group related test cases in separate variables
- [ ] Use `pytest.param` with custom ids for complex cases
- [ ] Parametrize fixtures for testing with different configurations
- [ ] Combine multiple `@pytest.mark.parametrize` decorators for cartesian product
- [ ] Include edge cases and error scenarios in parametrization
- [ ] Use dictionaries for complex test cases with many fields
- [ ] Don't overuse parametrization for unrelated tests
- [ ] Keep parametrized test logic simple and focused
- [ ] Test both happy path and error scenarios

## Related Documents

- `docs/atomic/testing/unit-testing/pytest-setup.md` — Pytest configuration and basic setup
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Reusable test fixtures (including parametrized fixtures)
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies in parametrized tests
- `docs/atomic/testing/unit-testing/coverage-requirements.md` — Coverage standards and enforcement
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — Parametrizing API endpoint tests
