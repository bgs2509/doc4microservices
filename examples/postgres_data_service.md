# Example: PostgreSQL Data Service

This document demonstrates the implementation of a **PostgreSQL Data Service** following the "Improved Hybrid Approach" architecture. This service is the single point of access to PostgreSQL database for all business services and implements all patterns from `docs/architecture/data-access-rules.mdc`.

> **🔗 Related Examples:**
> - **Used by**: [FastAPI Business Service](./fastapi_service.md#3-user-data-client), [Aiogram Bot Service](./aiogram_service.md), [Worker Service](./worker_service.md)
> - **HTTP Communication**: [Shared HTTP Client](./shared_http_client.md#usage-examples) (for client implementation)
> - **Companion**: [MongoDB Data Service](./mongodb_data_service.md) (for analytics and documents)
> - **Testing**: [Comprehensive Testing](./comprehensive_testing.md#integration-testing-examples) (real database testing)

## Key Characteristics
- **Technology:** FastAPI + SQLAlchemy 2.x with async support
- **Responsibility:** Data models, CRUD operations, transactions, migrations, pagination
- **Interface:** RESTful HTTP API with RFC 7807 error handling and OpenAPI documentation
- **Isolation:** Complete database interaction encapsulation with repository pattern
- **Features:** Pagination, filtering, sorting, proper error handling, health checks

---

## 🏗️ 1. Project Structure (db_postgres_service)

```
services/db_postgres_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── middleware.py      # Request tracking middleware
│   │   └── errors.py          # RFC 7807 error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # Base model with common fields
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py           # Pydantic schemas with pagination
│   │   ├── common.py         # Common schemas (pagination, filters)
│   │   └── errors.py         # RFC 7807 error schemas
│   └── repositories/
│       ├── __init__.py
│       ├── base_repository.py # Base repository with pagination
│       └── user_repository.py
├── tests/
│   ├── conftest.py           # Test configuration with testcontainers
│   ├── test_user_repository.py
│   └── test_user_api.py
├── alembic/
│   ├── versions/
│   └── env.py
├── alembic.ini
└── Dockerfile
```

---

## 💻 2. Database Models

### Base Model (`src/models/base.py`)
Base model with common fields and utilities.

```python
from datetime import datetime
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    """Base model class with common fields."""
    pass

class TimestampMixin:
    """Mixin for adding timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class BaseModel(Base, TimestampMixin):
    """Abstract base model with ID and timestamps."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
```

### User Model (`src/models/user.py`)
User model with proper constraints, indexes, and validation.

```python
from enum import Enum
from sqlalchemy import String, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel

class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(BaseModel):
    """User model with complete field definitions."""

    __tablename__ = "users"

    # Basic user information
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User profile
    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Status and settings
    status: Mapped[UserStatus] = mapped_column(
        String(20),
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Additional indexes for common queries
    __table_args__ = (
        Index('idx_user_status_created', 'status', 'created_at'),
        Index('idx_user_active_verified', 'status', 'is_verified'),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
```

## 💻 3. Schemas with Pagination (`src/schemas/common.py`)

Common pagination and filtering schemas.

```python
from typing import Optional, Dict, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters."""

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (1-100)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )

class SortParams(BaseModel):
    """Sorting parameters."""

    sort_by: Optional[str] = Field(
        default="created_at",
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc"
    )

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(
        ...,
        description="List of items"
    )
    total: int = Field(
        ...,
        description="Total number of items"
    )
    limit: int = Field(
        ...,
        description="Items per page"
    )
    offset: int = Field(
        ...,
        description="Items skipped"
    )
    has_next: bool = Field(
        ...,
        description="Whether there are more items"
    )
    has_prev: bool = Field(
        ...,
        description="Whether there are previous items"
    )

class FilterParams(BaseModel):
    """Base filter parameters."""

    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search term for text fields"
    )
```

## 💻 4. User Schemas (`src/schemas/user.py`)

Pydantic schemas for user operations.

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserCreate(BaseModel):
    """Schema for creating a user in data service (receives hashed password from business service)."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (3-50 chars, alphanumeric, underscore, hyphen)",
        example="john_doe"
    )
    hashed_password: str = Field(
        ...,
        min_length=60,  # bcrypt hash length
        max_length=255,
        description="User password (already hashed by business service)",
        example="$2b$12$..."
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's full name",
        example="John Doe"
    )
    bio: Optional[str] = Field(
        None,
        max_length=1000,
        description="User biography",
        example="Software developer with 5 years of experience"
    )

class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated full name"
    )
    bio: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated biography"
    )
    status: Optional[UserStatus] = Field(
        None,
        description="Updated user status"
    )
    is_verified: Optional[bool] = Field(
        None,
        description="Updated verification status"
    )
    is_admin: Optional[bool] = Field(
        None,
        description="Updated admin status"
    )

class UserResponse(BaseModel):
    """Schema for user response."""

    id: int = Field(
        ...,
        description="User ID",
        example=123
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    username: str = Field(
        ...,
        description="Username",
        example="john_doe"
    )
    full_name: Optional[str] = Field(
        None,
        description="User's full name",
        example="John Doe"
    )
    bio: Optional[str] = Field(
        None,
        description="User biography"
    )
    status: UserStatus = Field(
        ...,
        description="User status"
    )
    is_verified: bool = Field(
        ...,
        description="Whether user is verified"
    )
    is_admin: bool = Field(
        ...,
        description="Whether user is admin"
    )
    created_at: datetime = Field(
        ...,
        description="User creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    class Config:
        """Pydantic configuration."""
        from_attributes = True

class UserFilterParams(BaseModel):
    """User-specific filter parameters."""

    status: Optional[UserStatus] = Field(
        None,
        description="Filter by user status"
    )
    is_verified: Optional[bool] = Field(
        None,
        description="Filter by verification status"
    )
    is_admin: Optional[bool] = Field(
        None,
        description="Filter by admin status"
    )
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Search in username, email, or full_name"
    )
```

## 💻 5. Base Repository (`src/repositories/base_repository.py`)

Base repository with pagination and common operations.

```python
from typing import TypeVar, Generic, Optional, List, Dict, Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, or_
from sqlalchemy.orm import DeclarativeBase

from ..schemas.common import PaginationParams, SortParams, PaginatedResponse

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations and pagination."""

    def __init__(self, model: type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID."""
        result = await self.db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse[ModelType]:
        """Get all entities with pagination, sorting, and filtering."""

        # Build base query
        query = select(self.model)

        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db_session.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        if hasattr(self.model, sort.sort_by):
            sort_column = getattr(self.model, sort.sort_by)
            if sort.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)

        # Execute query
        result = await self.db_session.execute(query)
        items = result.scalars().all()

        return PaginatedResponse(
            items=items,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_next=(pagination.offset + pagination.limit) < total,
            has_prev=pagination.offset > 0
        )

    async def create(self, **kwargs) -> ModelType:
        """Create new entity."""
        entity = self.model(**kwargs)
        self.db_session.add(entity)
        await self.db_session.commit()
        await self.db_session.refresh(entity)
        return entity

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update entity by ID."""
        entity = await self.get_by_id(id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(entity)
        return entity

    async def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(id)
        if not entity:
            return False

        await self.db_session.delete(entity)
        await self.db_session.commit()
        return True

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query. Override in child classes for custom filtering."""
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        return query

## 💻 6. User Repository (`src/repositories/user_repository.py`)

User-specific repository with custom queries and filtering.

```python
from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository
from ..models.user import User, UserStatus
from ..schemas.user import UserCreate, UserUpdate, UserFilterParams
from ..schemas.common import PaginationParams, SortParams, PaginatedResponse

class UserRepository(BaseRepository[User]):
    """User repository with custom operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db_session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db_session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_users_paginated(
        self,
        pagination: PaginationParams,
        sort: SortParams,
        filters: UserFilterParams
    ) -> PaginatedResponse[User]:
        """Get users with pagination and filtering."""

        # Build base query
        query = select(User)

        # Apply user-specific filters
        if filters.status:
            query = query.where(User.status == filters.status)

        if filters.is_verified is not None:
            query = query.where(User.is_verified == filters.is_verified)

        if filters.is_admin is not None:
            query = query.where(User.is_admin == filters.is_admin)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db_session.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        if hasattr(User, sort.sort_by):
            sort_column = getattr(User, sort.sort_by)
            if sort.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.limit)

        # Execute query
        result = await self.db_session.execute(query)
        items = result.scalars().all()

        return PaginatedResponse(
            items=items,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_next=(pagination.offset + pagination.limit) < total,
            has_prev=pagination.offset > 0
        )

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        return await self.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.hashed_password,  # Already hashed by business service
            full_name=user_data.full_name,
            bio=user_data.bio,
            status=UserStatus.ACTIVE,
            is_verified=False,
            is_admin=False
        )

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_data = user_data.model_dump(exclude_unset=True)
        return await self.update(user_id, **update_data)

    async def verify_credentials(self, username: str, password_hash: str) -> Optional[User]:
        """Verify user credentials (for authentication service)."""
        result = await self.db_session.execute(
            select(User).where(
                User.username == username,
                User.hashed_password == password_hash,
                User.status == UserStatus.ACTIVE
            )
        )
        return result.scalar_one_or_none()
```

### Database Migrations (Alembic)
Alembic is used for managing database schema changes.
- **Configuration:** `alembic.ini` and `alembic/env.py` are configured to work with async driver and SQLAlchemy models.
- **Creating migration:** `alembic revision --autogenerate -m "Create user table"`
- **Applying migration:** `alembic upgrade head`

---

## 💻 3. API Endpoints (`src/api/v1/users.py`)

Endpoints provide HTTP interface for user data access.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserCreate, UserResponse
from ..repositories.user_repository import UserRepository
from ..core.database import get_db_session
# In real service password hashing would be here, but simplified for example
# from ...services.auth_service import get_password_hash 

router = APIRouter()

def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    repo: UserRepository = Depends(get_user_repository)
):
    # Password is already hashed by business service before reaching data service
    db_user = await repo.create_user(user_data)
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

@router.get("/by_username/{username}", response_model=UserResponse)
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

## 🚀 4. Main Application File (`src/main.py`)

```python
from fastapi import FastAPI
from .api.v1 import users
from .core.database import engine, Base

app = FastAPI(
    title="PostgreSQL Data Service",
    description="Service for direct PostgreSQL data access."
)

@app.on_event("startup")
async def startup():
    # In real application Alembic migrations should be here
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

```
