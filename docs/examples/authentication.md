## Аутентификация и авторизация

Этот раздел демонстрирует реализацию JWT-аутентификации в FastAPI для защиты эндпоинтов. Мы создадим сервис для работы с токенами и `dependency` для проверки токена и получения текущего пользователя.

### 1. Настройки

Убедитесь, что в вашем файле конфигурации (`src/core/config.py`) определены секретный ключ, алгоритм и время жизни токена.

```python
# src/core/config.py
class Settings(BaseSettings):
    # ...
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiry")
```

### 2. Сервис для работы с JWT

Этот сервис будет отвечать за создание и верификацию токенов, а также за проверку паролей.

`src/services/auth_service.py`
```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import settings
from ..models.user import User
from ..schemas.auth import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Сервис для аутентификации и авторизации."""

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить, что обычный пароль соответствует хешу."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Получить хеш пароля."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создать JWT токен доступа."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Проверить токен и извлечь из него данные."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            username: Optional[str] = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
        except JWTError:
            return None
        return token_data
```

### 3. Зависимость (Dependency) для получения пользователя

Эта `dependency` будет использоваться в защищенных эндпоинтах. Она извлекает токен из заголовка, проверяет его и возвращает модель пользователя из базы данных.

`src/api/dependencies.py`
```python
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db_session
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Зависимость для получения текущего аутентифицированного пользователя."""
    auth_service = AuthService()
    user_repository = UserRepository(db)

    token_data = auth_service.verify_token(token)
    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repository.get_by_username(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
```

### 4. Защищенный эндпоинт

Теперь мы можем использовать `get_current_user` для защиты эндпоинтов. FastAPI автоматически обработает получение токена и вызовет нашу `dependency`.

`src/api/v1/users.py`
```python
# ... (imports)
from ..dependencies import get_current_user
from ...models.user import User
from ...schemas.user import UserResponse

router = APIRouter(prefix="/users")

# ... (другие эндпоинты: create_user, get_user)

@router.get("/me", response_model=UserResponse, summary="Get current user")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """Получить информацию о текущем пользователе."""
    return current_user

@router.put("/me", response_model=UserResponse, summary="Update current user")
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Обновить информацию о текущем пользователе."""
    updated_user = await user_service.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user
```

### 5. Эндпоинт для получения токена

Наконец, нужен эндпоинт, куда пользователи будут отправлять свои `username` и `password` для получения токена.

`src/api/v1/auth.py`
```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db_session
from ...repositories.user_repository import UserRepository
from ...services.auth_service import AuthService
from ...schemas.auth import Token

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """Получение JWT токена по имени пользователя и паролю."""
    auth_service = AuthService()
    user_repository = UserRepository(db)

    user = await user_repository.get_by_username(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```
