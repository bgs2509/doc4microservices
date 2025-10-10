# Python Naming Conventions

This guide covers Python naming patterns for classes, functions, variables, and file organization in the doc4microservices framework. It follows PEP 8 with specific adaptations for microservices architecture.

**Key Principle**: Use snake_case for all Python elements except classes (PascalCase). File names match their primary class in snake_case.

---

## Classes

### Naming Pattern

`{Noun}{Suffix}`

Classes use PascalCase with descriptive suffixes indicating their architectural role.

### Standard Suffixes

| Suffix | Purpose | Example |
|--------|---------|---------|
| `Service` | Business logic layer | `UserService`, `LendingService` |
| `Repository` | Data access layer | `UserRepository`, `OrderRepository` |
| `DTO` | Data Transfer Object | `UserDTO`, `LoanApplicationDTO` |
| `Handler` | Event/message handler | `PaymentEventHandler`, `NotificationHandler` |
| `Router` | FastAPI route controller | `UserRouter`, `HealthRouter` |
| `Client` | External service client | `DataServiceClient`, `PaymentGatewayClient` |
| `Manager` | Resource/lifecycle manager | `ConnectionManager`, `SessionManager` |
| `Factory` | Object creation | `ServiceFactory`, `ClientFactory` |
| `Validator` | Input validation | `UserValidator`, `LoanValidator` |
| `Mapper` | Data transformation | `DTOMapper`, `EntityMapper` |

### Examples

```python
# Business logic
class LendingService:
    """Handles lending business logic."""
    pass

# Data access
class UserRepository:
    """Manages user data persistence."""
    pass

# Data transfer
class LoanApplicationDTO:
    """Loan application data structure."""
    user_id: str
    amount: Decimal
    term_months: int

# External integration
class PaymentGatewayClient:
    """Client for payment processing service."""
    pass
```

---

## Functions

### Naming Pattern

`{verb}_{noun}[_qualifier]`

Functions use snake_case starting with a verb, describing the action performed.

### Common Verbs

| Verb | Usage | Example |
|------|-------|---------|
| `get` | Retrieve single item | `get_user_by_id()` |
| `list` | Retrieve multiple items | `list_active_loans()` |
| `create` | Create new item | `create_loan_application()` |
| `update` | Modify existing item | `update_user_profile()` |
| `delete` | Remove item | `delete_expired_sessions()` |
| `validate` | Check validity | `validate_loan_eligibility()` |
| `process` | Handle/transform | `process_payment()` |
| `send` | Dispatch message/request | `send_notification()` |
| `fetch` | Get from external source | `fetch_credit_score()` |
| `calculate` | Compute value | `calculate_interest_rate()` |

### Examples

```python
async def get_user_by_id(user_id: str) -> UserDTO:
    """Retrieve user by ID."""
    pass

async def list_pending_applications(limit: int = 100) -> List[ApplicationDTO]:
    """List pending loan applications."""
    pass

def validate_loan_amount(amount: Decimal, user_profile: UserDTO) -> bool:
    """Validate loan amount against user profile."""
    pass

async def process_loan_approval(application_id: str) -> ApprovalResult:
    """Process loan approval workflow."""
    pass
```

### Async Functions

Prefix with `async` keyword, no special naming:

```python
async def fetch_external_data() -> dict:  # ✅ Correct
    pass

async def async_fetch_data() -> dict:  # ❌ Don't prefix with async_
    pass
```

---

## Variables and Parameters

### Naming Pattern

`{noun}[_qualifier]`

Variables use snake_case, descriptive nouns without type prefixes.

### Common Patterns

| Pattern | Example | Usage |
|---------|---------|-------|
| Simple noun | `user`, `loan`, `payment` | Single entities |
| Qualified noun | `user_id`, `loan_amount` | Specific attributes |
| Boolean flag | `is_active`, `has_permission` | Boolean states |
| Collection | `users`, `pending_loans` | Multiple items |
| Configuration | `max_retries`, `timeout_seconds` | Config values |

### Examples

```python
# Good variable names
user_id: str = "usr_123"
is_verified: bool = True
pending_applications: List[ApplicationDTO] = []
max_loan_amount: Decimal = Decimal("50000.00")

# Bad variable names (avoid)
u = "usr_123"  # Too short
userIdentifier = "usr_123"  # camelCase
str_user_id = "usr_123"  # Type prefix
```

### Function Parameters

```python
async def create_loan(
    user_id: str,
    amount: Decimal,
    term_months: int,
    is_urgent: bool = False,
    metadata: Optional[dict] = None
) -> LoanDTO:
    """Create new loan application."""
    pass
```

---

## Constants

### Naming Pattern

`{NOUN}_{QUALIFIER}`

Constants use SCREAMING_SNAKE_CASE for module-level constants.

```python
# Configuration constants
DATABASE_URL = "postgresql://localhost/db"
REDIS_URL = "redis://localhost:6379"
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30

# Business constants
MIN_LOAN_AMOUNT = Decimal("1000.00")
MAX_LOAN_TERM_MONTHS = 60
INTEREST_RATE_ANNUAL = Decimal("0.12")

# Status codes
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
```

---

## Files and Modules

### File Naming

Files use snake_case matching their primary class:

| Class | File |
|-------|------|
| `UserService` | `user_service.py` |
| `LoanRepository` | `loan_repository.py` |
| `PaymentDTO` | `payment_dto.py` |
| `EventHandler` | `event_handler.py` |

### Module Structure

```
finance_lending_api/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration class
│   │   └── dependencies.py   # Dependency injection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── lending_service.py    # LendingService class
│   │   └── user_service.py       # UserService class
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── loan_repository.py    # LoanRepository class
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_dto.py          # UserDTO class
│   │   └── loan_dto.py          # LoanDTO class
│   └── routers/
│       ├── __init__.py
│       └── lending_router.py    # LendingRouter class
```

---

## Private Elements

Use single underscore prefix for internal elements:

```python
class UserService:
    def __init__(self):
        self._cache = {}  # Private attribute

    def _validate_user(self, user_id: str) -> bool:
        """Private method for internal validation."""
        pass

    def get_user(self, user_id: str) -> UserDTO:
        """Public method."""
        if not self._validate_user(user_id):
            raise ValueError("Invalid user")
        return self._fetch_from_cache(user_id)
```

---

## Checklist

- [ ] Classes use PascalCase with appropriate suffix
- [ ] Functions start with verb in snake_case
- [ ] Variables use descriptive snake_case
- [ ] Constants use SCREAMING_SNAKE_CASE
- [ ] Files match primary class in snake_case
- [ ] No type prefixes in variable names
- [ ] Boolean flags start with `is_` or `has_`
- [ ] Private elements use `_` prefix
- [ ] Async functions not prefixed with `async_`

---

## Related Documents

- `../README.md` — Main naming conventions hub
- `naming-services.md` — Service naming patterns
- `naming-databases.md` — Database naming conventions
- `../../guides/PYTHON_STYLE_GUIDE.md` — Complete Python style guide