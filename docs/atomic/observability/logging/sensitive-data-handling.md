# Sensitive Data Handling in Logs

Prevent sensitive data exposure in logs by implementing data masking, redaction, and filtering strategies. Sensitive data handling protects personally identifiable information (PII), authentication credentials, payment data, and confidential business information from accidental logging while maintaining debuggability.

This document covers identifying sensitive data types, implementing masking strategies, configuring automatic redaction, handling structured log fields, sanitizing error messages, and complying with GDPR/CCPA data protection regulations. Proper sensitive data handling prevents security breaches, regulatory violations, and customer trust erosion.

Sensitive data in logs creates security and compliance risks: leaked credentials enable unauthorized access, exposed PII violates privacy regulations (GDPR fines up to 4% of global revenue), payment card data logging violates PCI DSS, and confidential business data in logs can be accessed by unauthorized personnel or external attackers if logging infrastructure is compromised.

## Sensitive Data Categories

### Never Log These

```python
# ❌ NEVER log these data types:

# Authentication
- Passwords (plaintext or hashed)
- API keys and tokens
- JWT tokens
- OAuth tokens
- Session IDs (full values)
- Security questions/answers

# Payment Data
- Credit card numbers
- CVV codes
- Bank account numbers
- Cryptocurrency private keys

# Personal Identifiable Information (PII)
- Social Security Numbers
- Passport numbers
- Driver's license numbers
- Full addresses (without consent)
- Phone numbers (without masking)
- Email addresses (mask by default)
- Biometric data

# Health Information
- Medical records
- Health insurance IDs
- Prescription information

# Confidential Business Data
- Trade secrets
- Proprietary algorithms
- Internal pricing
- Unannounced product plans
```

## Data Masking Strategies

### Email Masking

```python
# CORRECT: Mask email addresses
import re

def mask_email(email: str) -> str:
    """Mask email preserving domain."""
    if "@" not in email:
        return "***@***"
    local, domain = email.split("@")
    if len(local) <= 3:
        return f"{local[0]}***@{domain}"
    return f"{local[:2]}***{local[-1]}@{domain}"

# Examples:
mask_email("user@example.com")  # "us***r@example.com"
mask_email("a@example.com")  # "a***@example.com"


# Usage in logging
logger.info(
    "user_logged_in",
    user_id="user-123",
    email=mask_email(user.email)  # Masked
)
```

### Credit Card Masking

```python
# CORRECT: Show only last 4 digits
def mask_credit_card(card_number: str) -> str:
    """Mask credit card showing last 4 digits."""
    cleaned = card_number.replace(" ", "").replace("-", "")
    return f"****-****-****-{cleaned[-4:]}"

# Example:
mask_credit_card("4111111111111111")  # "****-****-****-1111"


# Usage
logger.info(
    "payment_processed",
    payment_id="pay-123",
    card_last_four=card_number[-4:],  # Only last 4
    amount=99.99
)
```

### Token Masking

```python
# CORRECT: Show prefix only
def mask_token(token: str) -> str:
    """Mask token showing first 8 chars."""
    if len(token) <= 12:
        return "***"
    return f"{token[:8]}...{token[-4:]}"

# Example:
mask_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")  # "eyJhbGci...VCJ9"


# Usage
logger.info(
    "api_call_authenticated",
    user_id="user-123",
    token_prefix=token[:8]  # Only prefix
)
```

## Automatic Redaction

### Structlog Processor

```python
# CORRECT: Automatic redaction processor
import structlog
from typing import Any, Dict

SENSITIVE_KEYS = {
    "password", "token", "api_key", "secret",
    "credit_card", "ssn", "passport"
}

def redact_sensitive_processor(
    logger: Any, method_name: str, event_dict: Dict
) -> Dict:
    """Redact sensitive fields from logs."""
    for key in list(event_dict.keys()):
        # Check if key contains sensitive word
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "***REDACTED***"

    return event_dict


# Configure structlog
structlog.configure(
    processors=[
        redact_sensitive_processor,  # Add first
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)


# Usage - automatic redaction
logger.info(
    "user_created",
    user_id="user-123",
    email="user@example.com",
    password="secret123"  # Automatically redacted
)

# Output:
{
    "event": "user_created",
    "user_id": "user-123",
    "email": "user@example.com",
    "password": "***REDACTED***"  # Redacted automatically
}
```

### Regex-Based Redaction

```python
# CORRECT: Pattern-based redaction
import re

def redact_patterns(text: str) -> str:
    """Redact sensitive patterns in text."""
    # Credit cards
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****', text)

    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)

    # API keys (example pattern)
    text = re.sub(r'\b[A-Za-z0-9]{32,}\b', '***API_KEY***', text)

    return text
```

## Exception Handling

### Safe Error Logging

```python
# CORRECT: Sanitize exception messages
import structlog

logger = structlog.get_logger()

try:
    result = authenticate_user(username, password)
except AuthenticationError as e:
    logger.error(
        "authentication_failed",
        user_id=user.id,
        error_type="AuthenticationError",
        # ❌ DON'T: error_message=str(e)  # May contain password
        error_code="INVALID_CREDENTIALS"  # Generic message
    )
```

### Redact Stack Traces

```python
# CORRECT: Redact sensitive data from stack traces
def sanitize_exception_info(exc_info: tuple) -> str:
    """Sanitize exception traceback."""
    import traceback
    tb_lines = traceback.format_exception(*exc_info)
    sanitized = []

    for line in tb_lines:
        # Redact password parameters
        line = re.sub(r'password=["\'].*?["\']', 'password=***', line)
        # Redact tokens
        line = re.sub(r'token=["\'].*?["\']', 'token=***', line)
        sanitized.append(line)

    return ''.join(sanitized)
```

## Configuration

### Environment Variables

```python
# CORRECT: Mask sensitive config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""

    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    API_KEY: str

    def log_safe_config(self):
        """Log configuration without secrets."""
        return {
            "DATABASE_URL": self.mask_connection_string(self.DATABASE_URL),
            "REDIS_URL": self.mask_connection_string(self.REDIS_URL),
            "SECRET_KEY": "***",
            "API_KEY": f"{self.API_KEY[:8]}***"
        }

    @staticmethod
    def mask_connection_string(url: str) -> str:
        """Mask password in connection string."""
        return re.sub(r':([^@]+)@', ':***@', url)


# Usage
settings = Settings()
logger.info("app_starting", config=settings.log_safe_config())
```

## Best Practices

### DO: Mask by Default

```python
# CORRECT: Mask all potentially sensitive fields
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    phone: str

    def to_log_dict(self) -> dict:
        """Safe representation for logging."""
        return {
            "id": self.id,
            "email": mask_email(self.email),
            "phone": mask_phone(self.phone)
        }


logger.info("user_fetched", user=user.to_log_dict())
```

### DON'T: Log Request/Response Bodies

```python
# INCORRECT: Logging entire request body
@app.post("/api/users")
async def create_user(user: UserCreate):
    logger.info("request_received", body=user.dict())  # ❌ May contain password


# CORRECT: Log specific safe fields
@app.post("/api/users")
async def create_user(user: UserCreate):
    logger.info(
        "user_creation_requested",
        email=mask_email(user.email),
        role=user.role
    )
```

### DON'T: Include Sensitive Data in Error Messages

```python
# INCORRECT: Exposing sensitive data in errors
if not verify_password(password, user.password_hash):
    raise HTTPException(
        status_code=401,
        detail=f"Password {password} is incorrect"  # ❌ Exposes password
    )


# CORRECT: Generic error message
if not verify_password(password, user.password_hash):
    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"  # Generic
    )
```

## Compliance

### GDPR Compliance

```python
# Right to be forgotten: Don't log identifiable data
logger.info(
    "user_action",
    user_id="user-123",  # ID is OK (can be deleted)
    action="profile_updated"
    # ❌ DON'T: email, name, phone (hard to remove from logs)
)
```

### PCI DSS Compliance

```python
# NEVER log full card details
logger.info(
    "payment_processed",
    payment_id="pay-123",
    card_last_four="1111",  # ✅ OK (last 4 digits)
    amount=99.99,
    # ❌ card_number=card.number  # PCI DSS violation
)
```

## Testing

```python
# CORRECT: Test redaction
def test_password_redaction():
    """Test passwords are redacted."""
    cap = LogCapture()
    structlog.configure(processors=[redact_sensitive_processor, cap])

    logger = structlog.get_logger()
    logger.info("test", password="secret123")

    assert cap.entries[0]["password"] == "***REDACTED***"
```

## Checklist

- [ ] Identify all sensitive data types in application
- [ ] Implement masking functions (email, phone, cards)
- [ ] Configure automatic redaction processor
- [ ] Never log passwords, tokens, API keys
- [ ] Mask credit card numbers (show last 4 only)
- [ ] Redact sensitive data in exception messages
- [ ] Mask connection strings in config logs
- [ ] Avoid logging full request/response bodies
- [ ] Use generic error messages
- [ ] Test redaction in unit tests
- [ ] Audit logs regularly for leaks
- [ ] Train team on sensitive data handling
- [ ] Document what data is safe to log

## Related Documents

- `docs/atomic/observability/logging/structured-logging.md` — Structured logging implementation
- `docs/atomic/observability/logging/log-formatting.md` — Log formatting standards
- `docs/atomic/security/authentication/api-key-management.md` — API key best practices
