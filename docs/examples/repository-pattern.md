## Паттерн "Репозиторий"

Паттерн "Репозиторий" используется для изоляции слоя бизнес-логики (сервисов) от слоя доступа к данным. Он предоставляет интерфейс для работы с сущностями домена, скрывая детали реализации (например, используется ли SQLAlchemy, MongoDB или другая ORM/библиотека).

### Преимущества

- **Абстракция:** Сервисы не знают, как данные хранятся и извлекаются.
- **Тестируемость:** Слой доступа к данным можно легко подменить (mock) в тестах для изоляции бизнес-логики.
- **Гибкость:** Можно сменить библиотеку для работы с БД, не изменяя бизнес-логику.

### 1. Абстрактный базовый репозиторий

Создадим абстрактный класс с использованием `ABC` и `abstractmethod`, который определяет основной контракт для всех репозиториев.

`src/repositories/base.py`
```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AbstractRepository(Generic[T], ABC):
    """Абстрактный базовый класс для репозитория."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @abstractmethod
    async def create(self, instance: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, instance: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, instance: T) -> None:
        raise NotImplementedError
```

### 2. Конкретная реализация для SQLAlchemy

Теперь создадим конкретный репозиторий для SQLAlchemy, который будет реализовывать базовый класс.

`src/repositories/sqlalchemy_repository.py`
```python
from __future__ import annotations

from typing import Generic, TypeVar, List, Optional, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import AbstractRepository

ModelType = TypeVar("ModelType")


class SQLAlchemyRepository(AbstractRepository[ModelType]):
    """Конкретная реализация репозитория для SQLAlchemy."""

    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        super().__init__(session)
        self.model = model

    async def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, instance: ModelType) -> ModelType:
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.commit()

```

### 3. Реализация репозитория для конкретной модели

Теперь можно легко создавать репозитории для конкретных моделей, наследуясь от `SQLAlchemyRepository`.

`src/repositories/user_repository.py`
```python
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .sqlalchemy_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    # Здесь можно добавить специфичные для пользователя методы
    # Например, поиск по email или username
    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()
```

### 4. Использование в сервисе

В сервисном слое мы работаем с `UserRepository`, который предоставляет удобный и типизированный API для доступа к данным.

`src/services/user_service.py`
```python
# ... (imports)
from ..repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository, ...) -> None:
        self.user_repository = user_repository
        # ...

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # ...
        # Проверка, существует ли пользователь
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already registered")

        user = User(...)
        created_user = await self.user_repository.create(user)
        # ...
        return UserResponse.model_validate(created_user)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        # ...
```
