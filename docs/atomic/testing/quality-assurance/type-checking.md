# Type Checking

Catch type errors before runtime using static type analysis with mypy. Type checking validates function signatures, variable types, and return values to prevent TypeError exceptions and improve code reliability.

This document covers mypy configuration, type hint best practices, gradual typing strategies, and CI/CD integration. Type checking provides early error detection, better IDE support, and improved code documentation.

Type checking validates that function arguments match expected types, return types match declarations, and type conversions are safe. These static checks catch bugs during development that would otherwise cause runtime errors in production.

## Installation and Setup

```bash
# Install mypy
pip install mypy==1.8.0

# Install type stubs for third-party libraries
pip install types-redis types-aiofiles types-PyYAML
```

## Mypy Configuration

### pyproject.toml Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
strict_concatenate = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party_lib.*"
ignore_missing_imports = true
```

### Running Mypy

```bash
# Check entire project
mypy src/

# Check specific file
mypy src/services/user_service.py

# Check with strict mode
mypy --strict src/

# Generate HTML report
mypy src/ --html-report mypy-report/
```

## Type Hints Basics

### Function Annotations

```python
# CORRECT: All function signatures typed
def get_user_by_id(user_id: str) -> User:
    """Get user by ID."""
    return repository.find_by_id(user_id)


async def create_user(email: str, name: str) -> User:
    """Create new user."""
    user = User(email=email, name=name)
    await repository.save(user)
    return user


def process_loan(loan: Loan, approved: bool) -> LoanDecision:
    """Process loan application."""
    if approved:
        return LoanDecision(status="approved", loan=loan)
    return LoanDecision(status="rejected", loan=loan)


# INCORRECT: Missing type hints
def get_user_by_id(user_id):  # Missing parameter and return types
    return repository.find_by_id(user_id)
```

### Variable Annotations

```python
from typing import Optional, List, Dict

# CORRECT: Explicit type annotations
user_id: str = "user-123"
users: List[User] = []
cache: Dict[str, User] = {}
current_user: Optional[User] = None


# Type annotation without assignment
loan_decision: LoanDecision
if approved:
    loan_decision = LoanDecision(status="approved")
else:
    loan_decision = LoanDecision(status="rejected")
```

## Advanced Type Hints

### Optional and Union Types

```python
from typing import Optional, Union

# CORRECT: Use Optional for nullable values
def get_user(user_id: str) -> Optional[User]:
    """Return user or None if not found."""
    return repository.find_by_id(user_id)


# CORRECT: Use Union for multiple possible types
def parse_user_id(value: Union[str, int]) -> str:
    """Accept string or int, return string."""
    return str(value)


# Python 3.10+ syntax (preferred)
def get_user_new(user_id: str) -> User | None:
    """Return user or None if not found."""
    return repository.find_by_id(user_id)


def parse_user_id_new(value: str | int) -> str:
    """Accept string or int, return string."""
    return str(value)
```

### Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')


class Repository(Generic[T]):
    """Generic repository."""

    def find_by_id(self, id: str) -> Optional[T]:
        """Find entity by ID."""
        ...

    def find_all(self) -> List[T]:
        """Find all entities."""
        ...


# Usage
user_repo: Repository[User] = Repository()
loan_repo: Repository[Loan] = Repository()
```

### Protocol and Structural Typing

```python
from typing import Protocol

class Cacheable(Protocol):
    """Protocol for cacheable objects."""

    def cache_key(self) -> str:
        """Return cache key for this object."""
        ...


def cache_object(obj: Cacheable) -> None:
    """Cache any object implementing Cacheable protocol."""
    key = obj.cache_key()
    redis.set(key, serialize(obj))


# Any class with cache_key() method satisfies the protocol
class User:
    def cache_key(self) -> str:
        return f"user:{self.id}"


cache_object(User())  # Type checks!
```

### Literal and TypedDict

```python
from typing import Literal, TypedDict

# Literal types for constrained strings
LoanStatus = Literal["pending", "approved", "rejected"]

def update_loan_status(loan_id: str, status: LoanStatus) -> None:
    """Update loan status."""
    # mypy enforces only these three values
    repository.update(loan_id, status=status)


# TypedDict for structured dictionaries
class UserDict(TypedDict):
    id: str
    email: str
    name: str
    verified: bool


def create_user_from_dict(data: UserDict) -> User:
    """Create user from dictionary."""
    return User(
        id=data["id"],
        email=data["email"],
        name=data["name"],
        verified=data["verified"]
    )
```

## Async Type Hints

```python
from typing import Awaitable

# CORRECT: Async function return types
async def fetch_user(user_id: str) -> User:
    """Fetch user asynchronously."""
    response = await http_client.get(f"/users/{user_id}")
    return User.parse(response.json())


# Async generator
async def stream_users() -> AsyncIterator[User]:
    """Stream users from database."""
    async for row in database.stream("SELECT * FROM users"):
        yield User.from_row(row)


# Function that returns awaitable
def get_user_async(user_id: str) -> Awaitable[User]:
    """Return awaitable user."""
    return fetch_user(user_id)
```

## Common Patterns

### Class Attributes and Methods

```python
from typing import ClassVar

class UserService:
    """User service with typed attributes."""

    max_retries: ClassVar[int] = 3  # Class variable
    _instance: ClassVar[Optional['UserService']] = None  # Singleton

    def __init__(self, repository: UserRepository) -> None:
        self.repository: UserRepository = repository
        self.cache: Dict[str, User] = {}

    @classmethod
    def get_instance(cls) -> 'UserService':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls(UserRepository())
        return cls._instance

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user from cache or repository."""
        if user_id in self.cache:
            return self.cache[user_id]
        return self.repository.find_by_id(user_id)
```

### Callbacks and Callables

```python
from typing import Callable

# Function taking a callback
def process_users(
    users: List[User],
    callback: Callable[[User], None]
) -> None:
    """Process each user with callback."""
    for user in users:
        callback(user)


# Function returning a function
def create_validator(
    min_length: int
) -> Callable[[str], bool]:
    """Create validator function."""
    def validator(value: str) -> bool:
        return len(value) >= min_length
    return validator
```

## Gradual Typing

### Adding Types Incrementally

```python
# Step 1: Start with `# type: ignore`
def legacy_function(data):  # type: ignore
    """Legacy function without types."""
    return process(data)


# Step 2: Add basic type hints
def legacy_function(data: dict) -> dict:
    """Function with basic types."""
    return process(data)


# Step 3: Add specific types
def legacy_function(data: UserDict) -> ProcessedData:
    """Function with specific types."""
    return process(data)
```

### Handling Untyped Libraries

```python
from typing import Any

# CORRECT: Type third-party libraries without stubs
import untyped_library  # type: ignore

def use_untyped_lib(data: str) -> Any:
    """Use library without type stubs."""
    return untyped_library.process(data)


# CORRECT: Create stub files for common libraries
# stubs/untyped_library.pyi
def process(data: str) -> dict: ...
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/type-check.yml
name: Type Check

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install mypy==1.8.0
          pip install types-redis types-aiofiles

      - name: Run mypy
        run: mypy src/ --strict
```

### Makefile Integration

```makefile
# Makefile
.PHONY: typecheck

typecheck:
	@echo "Running type checks..."
	mypy src/ tests/

typecheck-strict:
	@echo "Running strict type checks..."
	mypy src/ --strict

typecheck-report:
	@echo "Generating type check report..."
	mypy src/ --html-report mypy-report/
	@echo "Report generated in mypy-report/index.html"
```

## Best Practices

### DO: Type All Public APIs

```python
# CORRECT: All public functions typed
def create_loan(
    user_id: str,
    amount: int,
    purpose: str,
    term_months: int
) -> Loan:
    """Create loan application."""
    return Loan(
        user_id=user_id,
        amount=amount,
        purpose=purpose,
        term_months=term_months
    )


# INCORRECT: Missing types on public function
def create_loan(user_id, amount, purpose, term_months):
    """WRONG: Public API without types."""
    return Loan(...)
```

### DO: Use Specific Types

```python
# CORRECT: Specific types
from typing import List, Dict

def get_user_loans(user_id: str) -> List[Loan]:
    """Return list of user's loans."""
    return repository.find_loans_by_user(user_id)

def get_loan_stats() -> Dict[str, int]:
    """Return loan statistics."""
    return {"total": 100, "pending": 20, "approved": 80}


# INCORRECT: Using `Any` unnecessarily
from typing import Any

def get_user_loans(user_id: str) -> Any:  # Too vague
    return repository.find_loans_by_user(user_id)
```

### DON'T: Overuse `Any`

```python
from typing import Any

# INCORRECT: Any defeats the purpose of type checking
def process_data(data: Any) -> Any:
    """WRONG: No type safety."""
    return transform(data)


# CORRECT: Specific types or generics
from typing import TypeVar

T = TypeVar('T')

def process_data(data: T) -> T:
    """Preserve input type."""
    return transform(data)
```

## Common mypy Errors

### Fixing "Incompatible return value type"

```python
# ERROR: Incompatible return value type (got "None", expected "User")
def get_user(user_id: str) -> User:
    user = repository.find_by_id(user_id)
    if user is None:
        return None  # ERROR: Can't return None


# FIX: Use Optional
def get_user(user_id: str) -> Optional[User]:
    return repository.find_by_id(user_id)
```

### Fixing "Cannot determine type"

```python
# ERROR: Cannot determine type of 'users'
users = []  # mypy doesn't know the type


# FIX: Annotate variable
users: List[User] = []
```

## Checklist

- [ ] Install mypy and type stubs
- [ ] Configure mypy in pyproject.toml
- [ ] Add type hints to all function signatures
- [ ] Use Optional for nullable return values
- [ ] Use specific types instead of `Any`
- [ ] Type all public API functions
- [ ] Use Protocol for duck typing
- [ ] Add mypy to pre-commit hooks
- [ ] Integrate type checking in CI/CD
- [ ] Fix mypy errors incrementally
- [ ] Document type ignore comments
- [ ] Use strict mode for new code

## Related Documents

- `docs/atomic/testing/quality-assurance/linting-standards.md` — Code linting with Ruff
- `docs/atomic/testing/quality-assurance/code-review-checklist.md` — Code review guidelines
- `docs/atomic/architecture/code-organization.md` — Project structure standards
