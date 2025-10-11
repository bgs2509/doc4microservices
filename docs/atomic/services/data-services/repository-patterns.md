# Repository Patterns

Repositories encapsulate persistence logic and expose domain-aware operations to application services.

## SQLAlchemy Example

```python
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.users import User
from src.schemas.users import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
```

## MongoDB Example

```python
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorCollection
from src.schemas.analytics import EventCreate


class AnalyticsRepository:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self._collection = collection

    async def insert_event(self, payload: EventCreate) -> str:
        document = payload.model_dump()
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)
```

## Guidelines

- Define interfaces/protocols for repositories in the domain layer to decouple implementation.
- Keep each repository focused on a single aggregate or bounded context.
- Avoid returning ORM/ODM-specific objects to callers; map to domain models or DTOs.
- Implement pagination helpers returning `items` + `next_cursor`.
- Encapsulate caching logic within repositories if it relates to data access; otherwise move it to application services.

## Testing

- Unit-test repositories with in-memory or fake clients for simple logic.
- Integration-test against real databases using Testcontainers and run migrations beforehand.

## Related Documents

- `docs/atomic/services/data-services/transaction-management.md`
- `docs/atomic/architecture/ddd-hexagonal-principles.md`
