# Example: Authentication in Business Service

This section demonstrates how to implement JWT authentication in a **Business Service** following the "Improved Hybrid Approach" architecture. This service has no direct database access and uses the unified HTTP client approach defined in [`fastapi_service.md`](./fastapi_service.md).

## Key Changes from Standard Authentication
- **No Direct Database Access**: Uses `UserDataClient` for all user data operations
- **Centralized HTTP Client**: Reuses the unified client architecture
- **Security Best Practices**: Proper password hashing, JWT handling, and error responses
- **RFC 7807 Compliance**: Standardized error responses for authentication failures

---

## 1. Unified Client Usage

The authentication service uses the `UserDataClient` defined in [`fastapi_service.md`](./fastapi_service.md). This client provides all necessary methods:

- `get_user_by_username(username: str) -> Optional[UserResponse]`
- `get_user_by_email(email: str) -> Optional[UserResponse]`
- `verify_user_credentials(username: str, password_hash: str) -> Optional[UserResponse]`

> **📋 IMPORTANT**: This example builds upon the FastAPI service implementation. Ensure you have reviewed [`fastapi_service.md`](./fastapi_service.md) for the complete client implementation.

---

## 2. Authentication Service Reference

The `AuthService` class is fully implemented in [`fastapi_service.md`](./fastapi_service.md#6-authentication-service-srcservicesauth_servicepy). It provides:

- **Password Hashing**: Secure bcrypt-based password hashing
- **JWT Token Management**: Creation and verification of JWT tokens
- **Security Best Practices**: Proper salt generation and token validation

The implementation includes:
```python
class AuthService:
    def hash_password(self, password: str) -> str
    def verify_password(self, plain_password: str, hashed_password: str) -> bool
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str
    def verify_token(self, token: str) -> Optional[str]
```

---

## 3. Dependency for Getting Current User

This is the key change. `get_current_user` now uses `UserDataClient` to retrieve user data.

`src/core/dependencies.py`
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..clients.user_data_client import UserDataClient
from ..services.auth_service import AuthService
from ..schemas.user import UserResponse # Use response schema


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_user_data_client() -> UserDataClient:
    return UserDataClient()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_client: UserDataClient = Depends(get_user_data_client)
) -> UserResponse:
    auth_service = AuthService()
    
    username = auth_service.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Get user from Data Service via HTTP
    # request_id should be passed from middleware
    user_data = await user_client.get_user_by_username(username, request_id="some-request-id")

    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Return Pydantic model, not SQLAlchemy object
    return UserResponse(**user_data)
```

---

## 4. Token Endpoint (`src/api/v1/auth.py`)

This endpoint also changes to use `UserDataClient`.

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ...services.auth_service import AuthService
from ...clients.user_data_client import UserDataClient
from ...core.dependencies import get_user_data_client

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_client: UserDataClient = Depends(get_user_data_client)
):
    auth_service = AuthService()
    
    # Get user from Data Service
    user_data = await user_client.get_user_by_username(form_data.username, request_id="some-request-id")
    
    if not user_data or not auth_service.verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth_service.create_access_token(
        data={"sub": user_data["username"]}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

Thus, the business service still manages authentication logic (password verification, token creation), but no longer has direct access to user storage, relying entirely on the Data Service API.