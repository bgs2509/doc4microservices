# Transaction Management

Data services must guarantee consistent writes and avoid leaking half-committed state to callers.

## SQLAlchemy Transactions

```python
from __future__ import annotations

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@asynccontextmanager
async def unit_of_work(session_factory: async_sessionmaker[AsyncSession]) -> AsyncSession:
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

Usage in endpoints:

```python
async with unit_of_work(session_factory) as session:
    repo = UserRepository(session)
    user = await repo.create(payload)
```

## MongoDB Transactions

- Use multi-document transactions only when necessary (requires replica set).
- For single-document operations, rely on atomic updates and idempotency.

```python
async with await client.start_session() as session:
    async with session.start_transaction():
        await collection.insert_one(doc, session=session)
```

## Patterns

- One transaction per request; avoid nested commits.
- Wrap domain services with units of work to ensure consistency across repositories.
- For eventual consistency, use transactional outbox patterns (write to DB + outbox table within the same transaction, then publish via worker).

## Observability

- Log transaction boundaries (`transaction_started`, `transaction_committed`, `transaction_rolled_back`).
- Monitor rollback rates; spikes indicate upstream issues or validation gaps.

## Related Documents

- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/services/data-services/testing-strategies.md`
- Legacy reference: `docs/legacy/architecture/data-access-rules.mdc`
