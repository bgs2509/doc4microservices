# Linting Standards

Enforce consistent code style, detect common errors, and maintain code quality through automated linting tools. Linting standards ensure codebase consistency, prevent bugs, and improve maintainability across all services.

This document covers linting tool configuration for Python projects using Ruff, flake8, black, isort, and pre-commit hooks. Linting standards automate code quality checks and enforce team-wide consistency without manual review overhead.

Linting tools validate code style (formatting, naming, imports), detect potential bugs (unused variables, undefined names), and enforce best practices (complexity limits, docstring requirements). These automated checks catch issues before code review.

## Recommended Tools

### Primary Tools
- **Ruff**: Fast all-in-one linter (replaces flake8, isort, pyupgrade, autoflake)
- **Black**: Opinionated code formatter
- **mypy**: Static type checker (see type-checking.md)

### Legacy Tools (Being Replaced by Ruff)
- **flake8**: Style guide enforcement (being replaced by Ruff)
- **isort**: Import sorting (being replaced by Ruff)
- **pylint**: Comprehensive linter (optional, slower than Ruff)

## Ruff Configuration

### Installation

```bash
pip install ruff==0.1.9
```

### Configuration File

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100
fix = true

# Enable rule categories
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort (import sorting)
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "YTT",   # flake8-2020
    "S",     # flake8-bandit (security)
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "DTZ",   # flake8-datetimez
    "T10",   # flake8-debugger
    "EM",    # flake8-errmsg
    "ISC",   # flake8-implicit-str-concat
    "ICN",   # flake8-import-conventions
    "G",     # flake8-logging-format
    "PIE",   # flake8-pie
    "T20",   # flake8-print
    "PT",    # flake8-pytest-style
    "Q",     # flake8-quotes
    "RET",   # flake8-return
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "ERA",   # eradicate (commented code)
    "PL",    # pylint
    "TRY",   # tryceratops
    "RUF",   # Ruff-specific rules
]

# Ignore specific rules
ignore = [
    "E501",   # Line too long (handled by formatter)
    "S101",   # Use of assert (OK in tests)
    "PLR0913", # Too many arguments (sometimes necessary)
]

[tool.ruff.per-file-ignores]
# Ignore specific rules in tests
"tests/**/*.py" = [
    "S101",    # assert usage
    "PLR2004", # magic values
    "ARG",     # unused arguments
]

# Ignore import rules in __init__.py
"**/__init__.py" = ["F401"]

[tool.ruff.isort]
known-first-party = ["finance_lending_api", "finance_data_postgres_api"]
force-single-line = false
split-on-trailing-comma = true

[tool.ruff.mccabe]
max-complexity = 10

[tool.ruff.pylint]
max-args = 7
max-branches = 12
max-returns = 6
max-statements = 50
```

### Running Ruff

```bash
# Check code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/

# Check specific file
ruff check src/services/user_service.py
```

## Black Configuration

### Installation

```bash
pip install black==24.1.0
```

### Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ["py312"]
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''
```

### Running Black

```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/ tests/

# Format specific file
black src/services/user_service.py
```

## Pre-commit Hooks

### Setup

```bash
pip install pre-commit
pre-commit install
```

### Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      # Run linter
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      # Run formatter
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml", "-r", "src"]
        additional_dependencies: ["bandit[toml]"]
```

### Running Pre-commit

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Skip hooks for emergency commit
git commit --no-verify -m "Emergency fix"
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install ruff==0.1.9 black==24.1.0

      - name: Run Ruff
        run: ruff check src/ tests/

      - name: Run Black
        run: black --check src/ tests/
```

### Makefile Commands

```makefile
# Makefile
.PHONY: lint format check

lint:
	@echo "Running linters..."
	ruff check src/ tests/
	black --check src/ tests/

format:
	@echo "Formatting code..."
	ruff check --fix src/ tests/
	black src/ tests/

check: lint
	@echo "All checks passed!"
```

## Common Linting Rules

### Code Style Rules

```python
# CORRECT: Follow PEP 8 naming conventions
class UserService:
    """Service for user management."""

    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID."""
        return self.repository.find_by_id(user_id)


# INCORRECT: Inconsistent naming
class userService:  # Class names should be PascalCase
    def GetUserByID(self, UserID):  # Methods should be snake_case
        return self.Repository.findByID(UserID)
```

### Import Organization

```python
# CORRECT: Imports organized by Ruff/isort
import asyncio
import json
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from finance_lending_api.config import settings
from finance_lending_api.services.user_service import UserService


# INCORRECT: Disorganized imports
from finance_lending_api.services.user_service import UserService
import json
from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
import httpx
```

### Line Length

```python
# CORRECT: Lines under 100 characters
user = UserService().get_user_by_email(
    email=user_email,
    include_loans=True,
    include_transactions=True
)


# INCORRECT: Line too long
user = UserService().get_user_by_email(email=user_email, include_loans=True, include_transactions=True, include_profile=True)
```

### Complexity Limits

```python
# CORRECT: Low complexity function
def process_loan_application(loan: Loan) -> LoanDecision:
    """Process loan application."""
    if not loan.is_valid():
        return LoanDecision.rejected("Invalid loan data")

    credit_score = get_credit_score(loan.user_id)
    if credit_score < settings.MIN_CREDIT_SCORE:
        return LoanDecision.rejected("Insufficient credit score")

    return LoanDecision.approved()


# INCORRECT: High complexity (McCabe > 10)
def process_loan_application_complex(loan):
    if loan.amount > 50000:
        if loan.credit_score > 750:
            if loan.income > 100000:
                if loan.debt_ratio < 0.3:
                    return "approved"
    # ... many more nested conditions
```

## Exception to Rules

### Allowed in Tests

```python
# OK: Magic numbers in tests
assert response.status_code == 201  # OK
assert len(users) == 5  # OK

# OK: Long lines in parametrize
@pytest.mark.parametrize(
    "email,password,expected_status",
    [
        ("user1@test.com", "pass123", 200),  # OK: test data
        ("user2@test.com", "pass456", 200),
        ("invalid-email", "pass789", 422),
    ]
)
def test_login(email, password, expected_status):
    ...
```

### Allowed in Configuration

```python
# OK: Long URLs in settings
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname?pool_size=20&max_overflow=10"  # noqa: E501
```

## Best Practices

### DO: Fix Issues Incrementally

```bash
# CORRECT: Fix one rule at a time
ruff check --select F --fix src/
ruff check --select E --fix src/
ruff check --select I --fix src/


# INCORRECT: Don't ignore all issues
# pyproject.toml
[tool.ruff]
ignore = ["E", "F", "I", "N", "UP", "S", "B"]  # Too permissive
```

### DO: Use noqa Sparingly

```python
# CORRECT: Justified noqa comment
long_url = "https://api.example.com/v1/users?include=profile,loans,transactions"  # noqa: E501

# INCORRECT: Overusing noqa
def bad_function():  # noqa
    x = 1  # noqa
    return x  # noqa
```

### DON'T: Commit Unformatted Code

```bash
# CORRECT: Format before commit
git add src/
make format
git commit -m "Add feature"


# INCORRECT: Skip formatting
git commit --no-verify -m "Quick fix"  # Skips pre-commit hooks
```

## Checklist

- [ ] Install Ruff and Black
- [ ] Configure pyproject.toml with project-specific rules
- [ ] Set up pre-commit hooks
- [ ] Configure CI/CD linting checks
- [ ] Run linters before committing code
- [ ] Fix linting issues incrementally
- [ ] Document exceptions with noqa comments
- [ ] Keep line length under 100 characters
- [ ] Organize imports consistently
- [ ] Limit function complexity (McCabe < 10)
- [ ] Use meaningful variable names
- [ ] Remove commented-out code

## Related Documents

- `docs/atomic/testing/quality-assurance/type-checking.md` — Static type checking with mypy
- `docs/atomic/testing/quality-assurance/code-review-checklist.md` — Code review guidelines
- `docs/atomic/architecture/code-organization.md` — Project structure standards
