# Error Grouping

Implement error grouping strategies to reduce noise and identify patterns in production errors. Error grouping consolidates similar errors into issues, making it easier to prioritize fixes and track error trends.

This document covers fingerprinting rules, custom grouping logic, and error deduplication. Proper error grouping transforms thousands of error events into manageable issues.

Without grouping, every error is noise. With smart grouping, you see patterns: "500 instances of database timeout" instead of 500 separate alerts.

## Custom Fingerprinting

```python
# src/core/error_grouping.py
import sentry_sdk
import hashlib

def custom_fingerprint(error: Exception, context: dict) -> list[str]:
    """Generate custom fingerprint for error grouping."""
    if isinstance(error, DatabaseError):
        # Group database errors by query
        return ["database", error.query]
    
    elif isinstance(error, HTTPException):
        # Group HTTP errors by status and endpoint
        return ["http", str(error.status_code), context.get("endpoint", "unknown")]
    
    elif isinstance(error, ValidationError):
        # Group validation errors by field
        return ["validation", error.field_name]
    
    else:
        # Default grouping by error type and message
        return [error.__class__.__name__, str(error)]

# Apply fingerprint before sending
def before_send(event, hint):
    """Add custom fingerprint to Sentry event."""
    if "exc_info" in hint:
        error = hint["exc_info"][1]
        context = event.get("extra", {})
        event["fingerprint"] = custom_fingerprint(error, context)
    return event

sentry_sdk.init(before_send=before_send)
```

## Grouping Rules

```python
# Group similar database errors
class DatabaseErrorGrouper:
    @staticmethod
    def normalize_query(query: str) -> str:
        """Normalize SQL for grouping."""
        # Replace values with placeholders
        import re
        query = re.sub(r'\d+', '?', query)  # Numbers
        query = re.sub(r"'[^']*'", '?', query)  # Strings
        return query

# Group by normalized query
fingerprint = ["db_error", DatabaseErrorGrouper.normalize_query(error.query)]
```

## Error Deduplication

```python
from collections import deque
from datetime import datetime, timedelta

class ErrorDeduplicator:
    def __init__(self, window_seconds: int = 60):
        self.recent_errors = deque(maxlen=1000)
        self.window = timedelta(seconds=window_seconds)
    
    def should_report(self, error: Exception) -> bool:
        """Check if error should be reported."""
        now = datetime.now()
        error_hash = self._hash_error(error)
        
        # Remove old errors
        while self.recent_errors and (now - self.recent_errors[0][1]) > self.window:
            self.recent_errors.popleft()
        
        # Check for duplicate
        for stored_hash, _ in self.recent_errors:
            if stored_hash == error_hash:
                return False
        
        # New error
        self.recent_errors.append((error_hash, now))
        return True
    
    def _hash_error(self, error: Exception) -> str:
        """Generate hash for error."""
        key = f"{error.__class__.__name__}:{str(error)}"
        return hashlib.md5(key.encode()).hexdigest()

deduplicator = ErrorDeduplicator(window_seconds=60)

if deduplicator.should_report(error):
    sentry_sdk.capture_exception(error)
```

## Best Practices

### DO: Group by Root Cause

```python
# CORRECT: Group by root cause
if "Connection pool exhausted" in str(error):
    fingerprint = ["database", "connection_pool_exhausted"]
```

### DON'T: Over-Granular Grouping

```python
# INCORRECT: Too specific (creates many groups)
fingerprint = [str(error), timestamp, user_id]  # ❌

# CORRECT: Appropriate grouping
fingerprint = [error.__class__.__name__, endpoint]  # ✅
```

## Checklist

- [ ] Implement custom fingerprinting logic
- [ ] Create grouping rules by error type
- [ ] Set up deduplication for noisy errors
- [ ] Test grouping with sample errors
- [ ] Monitor group cardinality
- [ ] Document grouping patterns

## Related Documents

- `docs/atomic/observability/error-tracking/sentry-integration.md` — Sentry setup
- `docs/atomic/observability/error-tracking/alerting-patterns.md` — Alert configuration
