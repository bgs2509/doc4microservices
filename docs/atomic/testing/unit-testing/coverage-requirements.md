# Coverage Requirements

Define and enforce test coverage standards to ensure code quality and reduce production defects. Coverage metrics measure which lines, branches, and paths in your code are executed during test runs, providing quantitative insight into test completeness.

This document establishes coverage targets, configuration patterns, and enforcement strategies for Python services in this platform. Proper coverage tracking helps identify untested code paths, supports refactoring confidence, and serves as a quality gate in CI/CD pipelines.

Coverage requirements differ by maturity level: PoC projects may skip coverage entirely, Development projects should target 60%+, Pre-Production 75%+, and Production-ready services must maintain 80%+ coverage with strict enforcement. **See `docs/reference/maturity-levels.md` for definitive thresholds per level.**

## Configuration

### Pytest-Cov Setup

Install pytest-cov and configure it in `pyproject.toml`:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
]
```

Add coverage options to `pytest.ini`:

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py

addopts =
    --verbose
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term
    --cov-report=xml
    --cov-fail-under=80
```

### Coverage Configuration File

Create `.coveragerc` to control coverage behavior:

```ini
# .coveragerc
[run]
source = src
branch = true
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */.venv/*
    */venv/*
    */site-packages/*

[report]
precision = 2
show_missing = true
skip_covered = false

exclude_lines =
    pragma: no cover
    def __repr__
    def __str__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @overload

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

## Coverage Targets by Maturity Level

| Maturity Level | Minimum Coverage | Enforcement | Typical Use Case |
|----------------|------------------|-------------|------------------|
| **Level 1: PoC** | ≥ 60% | None | Proof of concept, rapid prototyping |
| **Level 2: Development** | ≥ 75% | Warning only | Active development, MVP |
| **Level 3: Pre-Production** | ≥ 80% | CI warning | Staging, beta testing |
| **Level 4: Production** | ≥ 85% | **CI failure** | Production services |

> **SSOT**: See `docs/reference/maturity-levels.md` for authoritative thresholds.

### CORRECT: Production Coverage Enforcement

```ini
# pytest.ini for Production services
[pytest]
addopts =
    --cov=src
    --cov-fail-under=80  # Fail CI if below 80%
    --cov-branch          # Include branch coverage
```

### INCORRECT: No Coverage Enforcement for Production

```ini
# pytest.ini — WRONG for Production
[pytest]
addopts =
    --cov=src
    # Missing --cov-fail-under means coverage can drop without CI failure
```

## Excluding Code from Coverage

### Files to Exclude

Always exclude from coverage calculations:

```ini
[run]
omit =
    */tests/*              # Test files themselves
    */migrations/*         # Database migrations (data, not logic)
    */__pycache__/*        # Compiled bytecode
    */conftest.py          # Pytest fixtures (tested implicitly)
    */manage.py            # Django/Flask management scripts
    */.venv/*              # Virtual environment
```

### Code Patterns to Exclude

Use `# pragma: no cover` for specific lines:

```python
# CORRECT: Exclude defensive code that's hard to test
def process_item(item: dict) -> None:
    try:
        validate_and_save(item)
    except Exception as e:  # pragma: no cover
        # Defensive: log unexpected errors but don't fail
        logger.exception("Unexpected error processing item")
        raise


# CORRECT: Exclude __repr__ and __str__ (low value to test)
class User:
    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"


# CORRECT: Exclude TYPE_CHECKING imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from mypy_extensions import TypedDict


# INCORRECT: Overusing pragma to inflate coverage
def critical_business_logic(data: dict) -> bool:
    if not data:  # pragma: no cover — WRONG! This should be tested
        return False
    return validate(data)
```

## Report Formats

### HTML Report (for local development)

Generate interactive HTML coverage report:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

The HTML report highlights:
- **Green lines**: Covered by tests
- **Red lines**: Not covered
- **Yellow lines**: Partially covered branches

### Terminal Report (for quick feedback)

```bash
pytest --cov=src --cov-report=term-missing

# Output:
# Name                      Stmts   Miss Branch BrPart  Cover   Missing
# ---------------------------------------------------------------------
# src/domain/user.py           45      5     12      2    89%   23-25, 67
# src/api/v1/users.py          32      0      8      0   100%
# ---------------------------------------------------------------------
# TOTAL                        77      5     20      2    93%
```

The `Missing` column shows uncovered line numbers.

### XML Report (for CI/CD integration)

```bash
pytest --cov=src --cov-report=xml

# Generates coverage.xml for tools like:
# - Codecov
# - Coveralls
# - SonarQube
# - GitLab CI coverage visualization
```

## CI/CD Enforcement

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e ".[test]"

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
test:
  stage: test
  image: python:3.12
  script:
    - pip install -e ".[test]"
    - pytest --cov=src --cov-report=xml --cov-report=term --cov-fail-under=80
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Best Practices

### Coverage Interpretation

```python
# CORRECT: High coverage with meaningful assertions
@pytest.mark.unit
async def test_user_creation_validates_email():
    """Test email validation during user creation."""
    service = UserService()

    with pytest.raises(ValidationError, match="Invalid email format"):
        await service.create_user(email="invalid", name="John")

    # Also test success case
    user = await service.create_user(email="john@example.com", name="John")
    assert user.email == "john@example.com"
    assert user.name == "John"


# INCORRECT: High coverage with weak assertions (false confidence)
@pytest.mark.unit
async def test_user_creation():
    """Test user creation."""
    service = UserService()
    user = await service.create_user(email="john@example.com", name="John")
    assert user  # Weak: doesn't validate correctness, just that it doesn't crash
```

### Coverage Metrics Guidelines

1. **Line Coverage ≠ Test Quality**: 100% coverage doesn't mean bug-free code
2. **Branch Coverage Matters**: Use `--cov-branch` to ensure all conditional paths tested
3. **Focus on Critical Paths**: Prioritize business logic over boilerplate
4. **Avoid Coverage Theater**: Don't write tests just to increase percentage
5. **Review Uncovered Code**: Low coverage areas may indicate dead code or missing tests

### CORRECT: Balanced Coverage Strategy

```python
# High-value test for critical business logic
@pytest.mark.unit
async def test_loan_approval_logic():
    """Test loan approval criteria (critical business rule)."""
    service = LoanService()

    # Test approval
    result = await service.evaluate_loan(
        credit_score=750,
        income=80000,
        debt_ratio=0.2
    )
    assert result.approved is True
    assert result.interest_rate == 4.5

    # Test rejection
    result = await service.evaluate_loan(
        credit_score=550,
        income=30000,
        debt_ratio=0.6
    )
    assert result.approved is False
    assert result.rejection_reason == "Credit score below minimum"
```

### INCORRECT: Low-Value Coverage Padding

```python
# Low-value test that inflates coverage without real benefit
@pytest.mark.unit
def test_user_class_exists():
    """Test that User class can be imported."""
    from finance_lending_api.domain.models import User
    assert User  # Pointless test


# Low-value test for simple property
@pytest.mark.unit
def test_user_email_property():
    """Test user email property."""
    user = User(email="test@example.com", name="Test")
    assert user.email == "test@example.com"  # No logic, just data storage
```

## Monitoring Coverage Trends

Track coverage over time to detect regressions:

```bash
# Store coverage percentage in CI artifacts
pytest --cov=src --cov-report=term | tee coverage.txt
grep "TOTAL" coverage.txt | awk '{print $NF}' > coverage_percentage.txt
```

Set up alerts if coverage drops below threshold:

```bash
# In CI script
CURRENT_COVERAGE=$(grep "TOTAL" coverage.txt | awk '{print $NF}' | tr -d '%')
if (( $(echo "$CURRENT_COVERAGE < 80" | bc -l) )); then
    echo "❌ Coverage dropped below 80%: ${CURRENT_COVERAGE}%"
    exit 1
fi
```

## Running Coverage Checks

```bash
# Local development: generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# CI/CD: enforce minimum coverage
pytest --cov=src --cov-report=xml --cov-fail-under=80

# Check specific module coverage
pytest tests/unit/domain/ --cov=src/domain --cov-report=term-missing

# Branch coverage (recommended for Production)
pytest --cov=src --cov-branch --cov-report=term-missing
```

## Checklist

- [ ] `pytest-cov` installed and configured in `pyproject.toml`
- [ ] `.coveragerc` excludes tests, migrations, virtual environments
- [ ] Coverage target set appropriately for maturity level (80%+ for Production)
- [ ] `--cov-fail-under` configured in `pytest.ini` or CI script
- [ ] Branch coverage enabled with `--cov-branch`
- [ ] HTML report generated for local development
- [ ] XML report generated for CI/CD integration
- [ ] Coverage trends monitored over time
- [ ] CI pipeline fails on coverage regression
- [ ] `# pragma: no cover` used sparingly and justified

## Related Documents

- `docs/atomic/testing/unit-testing/pytest-setup.md` — Pytest configuration and basic setup
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Pytest fixture patterns for reusable test components
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies to isolate units
- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Integration testing with real dependencies
- `docs/atomic/testing/quality-assurance/linting-standards.md` — Code quality standards and enforcement
