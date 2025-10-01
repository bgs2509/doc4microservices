# SQLAlchemy Integration

Comprehensive guide for SQLAlchemy 2.0+ async patterns, model definitions, repository pattern, and best practices for microservices.

## SQLAlchemy 2.0 Setup

### Core Dependencies

```txt
# requirements.txt

sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.5.0
```

### Base Model Configuration

```python
# src/domain/base.py

from datetime import datetime
from typing import Any
from sqlalchemy import MetaData, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Naming conventions for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""

    metadata = metadata

    # Type annotation for better IDE support
    __tablename__: str
    __table_args__: dict[str, Any] = {}


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

## Domain Models

### Simple Entity Example

```python
# src/domain/user.py

from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User entity"""

    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    # Primary key
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Required fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Optional fields
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Boolean flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
```

### Entity with Relationships

```python
# src/domain/order.py

from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String, Numeric, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base import Base, TimestampMixin


class OrderStatus(str, Enum):
    """Order status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base, TimestampMixin):
    """Order entity"""

    __tablename__ = "orders"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Order details
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, number={self.order_number}, status={self.status})>"


class OrderItem(Base, TimestampMixin):
    """Order item entity"""

    __tablename__ = "order_items"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("public.orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    # Item details
    quantity: Mapped[int] = mapped_column(
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
```

## Repository Pattern

### Base Repository

```python
# src/infrastructure/repositories/base.py

from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get all entities with pagination"""
        result = await self.session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total entities"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(self, entity: ModelType) -> ModelType:
        """Create new entity"""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """Update existing entity"""
        await self.session.merge(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        result = await self.session.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id)
        )
        return result.scalar_one() > 0
```

### Specific Repository Example

```python
# src/infrastructure/repositories/user_repository.py

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user import User
from src.infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository with specific queries"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all active users"""
        result = await self.session.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        result = await self.session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None
```

## Use Case Integration

```python
# src/application/use_cases/create_user.py

from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user import User
from src.infrastructure.repositories.user_repository import UserRepository


@dataclass
class CreateUserCommand:
    """Command to create new user"""
    email: str
    username: str
    password: str
    full_name: str | None = None


class CreateUserUseCase:
    """Use case for creating new user"""

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def execute(self, command: CreateUserCommand) -> User:
        """Execute use case"""
        # Check if email exists
        if await self.repository.email_exists(command.email):
            raise ValueError(f"Email {command.email} already registered")

        # Check if username exists
        if await self.repository.get_by_username(command.username):
            raise ValueError(f"Username {command.username} already taken")

        # Hash password (use proper hashing library)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(command.password)

        # Create user entity
        user = User(
            email=command.email,
            username=command.username,
            hashed_password=hashed_password,
            full_name=command.full_name,
        )

        # Persist to database
        user = await self.repository.create(user)

        return user
```

## Transaction Management

### Manual Transaction Control

```python
# src/application/use_cases/transfer_funds.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


async def transfer_funds(
    session: AsyncSession,
    from_account_id: UUID,
    to_account_id: UUID,
    amount: Decimal,
) -> bool:
    """Transfer funds between accounts with explicit transaction control"""

    try:
        # Start transaction (implicit with session)

        # Debit from source account
        await session.execute(
            update(Account)
            .where(Account.id == from_account_id)
            .values(balance=Account.balance - amount)
        )

        # Credit to destination account
        await session.execute(
            update(Account)
            .where(Account.id == to_account_id)
            .values(balance=Account.balance + amount)
        )

        # Commit transaction
        await session.commit()
        return True

    except SQLAlchemyError as e:
        # Rollback on error
        await session.rollback()
        raise RuntimeError(f"Transfer failed: {str(e)}")
```

### Savepoint Pattern

```python
async def complex_operation(session: AsyncSession):
    """Use savepoints for nested transactions"""

    # Main transaction
    user = await create_user(session, email="test@example.com")

    # Nested savepoint
    async with session.begin_nested():
        try:
            await send_welcome_email(user.email)
        except EmailError:
            # Rollback only the email part
            await session.rollback()
            # Continue with user creation

    await session.commit()
```

## Query Optimization Patterns

### Eager Loading

```python
# src/infrastructure/repositories/order_repository.py

from sqlalchemy.orm import selectinload, joinedload

class OrderRepository(BaseRepository[Order]):

    async def get_with_items(self, order_id: UUID) -> Optional[Order]:
        """Get order with all items eagerly loaded"""
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: UUID) -> list[Order]:
        """Get all user orders with items"""
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())
```

### Pagination with Total Count

```python
async def get_paginated_users(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[User], int]:
    """Get paginated users with total count"""

    # Count query
    count_result = await session.execute(
        select(func.count()).select_from(User)
    )
    total = count_result.scalar_one()

    # Data query
    offset = (page - 1) * page_size
    result = await session.execute(
        select(User)
        .offset(offset)
        .limit(page_size)
        .order_by(User.created_at.desc())
    )
    users = list(result.scalars().all())

    return users, total
```

## Alembic Migrations

### Configuration

```python
# alembic/env.py

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import all models
from src.domain.base import Base
from src.domain.user import User
from src.domain.order import Order, OrderItem

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Creating Migrations

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add user and order tables"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

## Testing with SQLAlchemy

```python
# tests/conftest.py

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.domain.base import Base


@pytest_asyncio.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:test@localhost:5432/test_db",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Create test database session"""
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()
```

## Related Documentation

- [PostgreSQL Basic Setup](basic-setup.md) - Initial PostgreSQL configuration
- [Complex Relationship Modeling](../postgresql-advanced/complex-relationship-modeling.md) - Advanced relationships
- [Performance Optimization](../postgresql-advanced/performance-optimization.md) - Query optimization
- [Production Migrations](../postgresql-advanced/production-migrations.md) - Safe migration strategies
- [Repository Patterns](../../services/data-services/repository-patterns.md) - Data access patterns
