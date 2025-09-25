# Security Patterns

FastAPI services must enforce authentication, authorization, and data protection at the transport boundary.

## Authentication

- Implement auth dependencies (`Depends(get_current_user)`) per router or endpoint.
- Support token-based schemes (JWT, OAuth2) via `fastapi.security` utilities.
- Reject requests lacking required scopes with `403` Problem Details.

```python
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from src.core.security import get_current_user

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def require_user(token: str = Security(reusable_oauth2)) -> CurrentUser:
    return await get_current_user(token)
```

## Authorization

- Encode roles/scopes in the auth dependency result.
- Perform coarse-grained checks in routers, fine-grained checks in application services.
- Log security-relevant decisions (`user_id`, `scope`, `resource`) without exposing PII.

## Input Hardening

- Enforce payload size limits using FastAPI settings (`app = FastAPI(max_request_size=...)`).
- Validate `Content-Type` headers and reject unexpected media types.
- Sanitise user-generated strings before logging.

## Secrets Handling

- Store secrets in environment variables or secret managers; load via `Settings`.
- Avoid passing secrets to clients or including them in responses.

## CORS

- Default to deny-all; allow origins per environment through configuration.
- Set explicit allowed methods/headers and enable credentials only when necessary.

## Security Testing

- Add tests for auth absence (`401`) and insufficient permissions (`403`).
- Use dependency overrides in tests to simulate authenticated users.
- Run security scanners (`bandit`, dependency audit) in CI.

## Related Documents

- `docs/atomic/services/fastapi/error-handling.md`
- `docs/atomic/architecture/quality-standards.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
