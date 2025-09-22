# Example: Authentication in Business Service

This section demonstrates how to implement JWT authentication in a **Business Service** that has no direct database access. Credential verification and user information retrieval occur through HTTP calls to **Data Service**.

---

## 1. HTTP Client for Data Access

We need a method in `UserDataClient` to get user by username.

`src/clients/user_data_client.py` (addition)
```python
# UserDataClient is now defined in fastapi_service.md
# and includes get_user_by_username.
# This client should be imported and available for use.
```

---

## 2. Authentication Service (`src/services/auth_service.py`)

This service still handles passwords and JWT tokens. Its code remains virtually unchanged, but now it will work in conjunction with `UserDataClient`.

```python
from passlib.context import CryptContext
from jose import jwt
# ... and other imports

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        # ... (token creation logic)
        pass

    def verify_token(self, token: str) -> Optional[str]:
        # ... (token verification logic, returns username)
        pass
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