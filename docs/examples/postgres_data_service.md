# Пример: Сервис Данных PostgreSQL

Этот документ демонстрирует реализацию **Сервиса Данных** (`Data Service`) в соответствии с архитектурой "Improved Hybrid Approach". Этот сервис является единственной точкой доступа к базе данных PostgreSQL для всех бизнес-сервисов.

## Ключевые характеристики
- **Технология:** FastAPI.
- **Ответственность:** Управление моделями данных (SQLAlchemy), выполнение CRUD-операций, обеспечение транзакционной целостности.
- **Интерфейс:** Предоставляет RESTful HTTP API для доступа к данным.
- **Изоляция:** Полностью инкапсулирует логику работы с базой данных.

---

## 1. Структура проекта (db_postgres_service)

```
services/db_postgres_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   └── repositories/
│       ├── __init__.py
│       └── user_repository.py
├── tests/
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
└── Dockerfile
```

---

## 2. Модели, Репозиторий и Миграции

### Модель SQLAlchemy (`src/models/user.py`)
Это определение таблицы в базе данных.

```python
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from ..core.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

### Паттерн "Репозиторий" (`src/repositories/user_repository.py`)
Репозиторий инкапсулирует логику доступа к данным, предоставляя чистый интерфейс для работы с моделями.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User
from ..schemas.user import UserCreate
from typing import Optional

class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db_session.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db_session.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
```

### Миграции базы данных (Alembic)
Alembic используется для управления изменениями схемы БД.
- **Настройка:** `alembic.ini` и `alembic/env.py` настраиваются для работы с асинхронным драйвером и моделями SQLAlchemy.
- **Создание миграции:** `alembic revision --autogenerate -m "Create user table"`
- **Применение миграции:** `alembic upgrade head`

---

## 3. API эндпоинты (`src/api/v1/users.py`)

Эндпоинты предоставляют HTTP-интерфейс для доступа к данным пользователя.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserCreate, UserResponse
from ..repositories.user_repository import UserRepository
from ..core.database import get_db_session
# В реальном сервисе тут будет хеширование пароля, но для простоты опустим
# from ...services.auth_service import get_password_hash 

router = APIRouter()

def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    # В реальном приложении пароль должен хешироваться в бизнес-сервисе
    # и передаваться сюда уже в виде хеша.
    # Для упрощения примера, представим, что пароль уже хеширован.
    hashed_password = user_data.password + "_hashed" # Упрощенное "хеширование"
    db_user = await repo.create_user(user_data, hashed_password)
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository)
):
    db_user = await repo.get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    repo: UserRepository = Depends(get_user_repository)
):
    db_user = await repo.get_user_by_username(username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
```

---

## 4. Основной файл приложения (`src/main.py`)

```python
from fastapi import FastAPI
from .api.v1 import users
from .core.database import engine, Base

app = FastAPI(
    title="PostgreSQL Data Service",
    description="Сервис для прямого доступа к данным PostgreSQL."
)

@app.on_event("startup")
async def startup():
    # В реальном приложении здесь должны быть миграции Alembic
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

```
