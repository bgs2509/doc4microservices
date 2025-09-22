# Пример: Аутентификация в Бизнес-сервисе

Этот раздел демонстрирует, как реализовать JWT-аутентификацию в **Бизнес-сервисе**, который не имеет прямого доступа к базе данных. Проверка учетных данных и получение информации о пользователе происходят через HTTP-вызовы к **Сервису Данных**.

---

## 1. HTTP-клиент для доступа к данным

Нам понадобится метод в `UserDataClient` для получения пользователя по имени пользователя.

`src/clients/user_data_client.py` (дополнение)
```python
class UserDataClient:
    # ... (существующие методы get_user_by_id, create_user)

    async def get_user_by_username(self, username: str, request_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/users/by-username/{username}",
                    headers={"X-Request-ID": request_id}
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP error getting user by username {username}: {e}")
                return None
```

---

## 2. Сервис аутентификации (`src/services/auth_service.py`)

Этот сервис по-прежнему отвечает за работу с паролями и JWT-токенами. Его код практически не меняется, но теперь он будет работать в паре с `UserDataClient`.

```python
from passlib.context import CryptContext
from jose import jwt
# ... и другие импорты

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        # ... (логика создания токена)
        pass

    def verify_token(self, token: str) -> Optional[str]:
        # ... (логика верификации токена, возвращает username)
        pass
```

---

## 3. Зависимость (Dependency) для получения пользователя

Это ключевое изменение. `get_current_user` теперь использует `UserDataClient` для получения данных о пользователе.

`src/core/dependencies.py`
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..clients.user_data_client import UserDataClient
from ..services.auth_service import AuthService
from ..schemas.user import UserResponse # Используем схему для ответа


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
    
    # Получаем пользователя из Сервиса Данных по HTTP
    # request_id нужно пробрасывать из middleware
    user_data = await user_client.get_user_by_username(username, request_id="some-request-id")
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Возвращаем Pydantic модель, а не объект SQLAlchemy
    return UserResponse(**user_data)
```

---

## 4. Эндпоинт для получения токена (`src/api/v1/auth.py`)

Этот эндпоинт также меняется, чтобы использовать `UserDataClient`.

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
    
    # Получаем пользователя из Сервиса Данных
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

Таким образом, бизнес-сервис по-прежнему управляет логикой аутентификации (проверка паролей, создание токенов), но больше не имеет прямого доступа к хранилищу пользователей, полностью полагаясь на API Сервиса Данных.