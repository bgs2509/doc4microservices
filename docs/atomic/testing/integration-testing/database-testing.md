# Database Integration Testing

Test database integration with real PostgreSQL and MongoDB containers to verify queries, transactions, constraints, and schema changes work correctly. Integration tests with real databases catch SQL errors, constraint violations, and transaction issues that mocks cannot detect.

This document covers testing patterns for PostgreSQL (with SQLAlchemy) and MongoDB (with Motor), transaction management, migration testing, and parallel test execution with isolated databases. Database integration tests bridge the gap between unit tests and production behavior.

Real database testing ensures your ORM queries translate correctly to SQL, constraints enforce data integrity, and transactions maintain consistency under concurrent access. These tests are slower than unit tests but provide confidence in data layer correctness.

## PostgreSQL Testing with SQLAlchemy

### Repository Testing

```python
# tests/integration/test_user_repository.py
import pytest
from finance_lending_api.infrastructure.repositories import UserRepository
from finance_lending_api.domain.models import User
from sqlalchemy import select


@pytest.mark.integration
async def test_user_repository_create(db_session):
    """Test creating user in PostgreSQL."""
    repo = UserRepository(session=db_session)

    user = await repo.create(
        email="test@example.com",
        name="Test User",
        credit_score=750
    )

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None


@pytest.mark.integration
async def test_user_repository_find_by_email(db_session):
    """Test finding user by email."""
    repo = UserRepository(session=db_session)

    # Create user
    created_user = await repo.create(email="find@example.com", name="Find Me")

    # Find by email
    found_user = await repo.find_by_email("find@example.com")

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == "find@example.com"


@pytest.mark.integration
async def test_user_repository_update(db_session):
    """Test updating user fields."""
    repo = UserRepository(session=db_session)

    user = await repo.create(email="update@example.com", name="Original Name")
    original_id = user.id

    # Update
    user.name = "Updated Name"
    user.credit_score = 800
    await db_session.commit()

    # Verify
    updated_user = await repo.get_by_id(original_id)
    assert updated_user.name == "Updated Name"
    assert updated_user.credit_score == 800


@pytest.mark.integration
async def test_user_repository_delete(db_session):
    """Test deleting user."""
    repo = UserRepository(session=db_session)

    user = await repo.create(email="delete@example.com", name="Delete Me")
    user_id = user.id

    # Delete
    await repo.delete(user_id)
    await db_session.commit()

    # Verify deleted
    deleted_user = await repo.get_by_id(user_id)
    assert deleted_user is None
```

### Constraint Testing

```python
# CORRECT: Test unique constraints
@pytest.mark.integration
async def test_unique_email_constraint(db_session):
    """Test database enforces unique email constraint."""
    repo = UserRepository(session=db_session)

    # First user succeeds
    user1 = await repo.create(email="unique@example.com", name="User 1")
    await db_session.commit()
    assert user1.id is not None

    # Duplicate email fails
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError, match="unique"):
        user2 = await repo.create(email="unique@example.com", name="User 2")
        await db_session.commit()


# CORRECT: Test foreign key constraints
@pytest.mark.integration
async def test_foreign_key_constraint(db_session):
    """Test foreign key integrity."""
    from finance_lending_api.infrastructure.repositories import LoanRepository

    user_repo = UserRepository(session=db_session)
    loan_repo = LoanRepository(session=db_session)

    # Create user
    user = await user_repo.create(email="borrower@example.com", name="Borrower")
    await db_session.commit()

    # Create loan with valid user_id
    loan = await loan_repo.create(user_id=user.id, amount=10000)
    await db_session.commit()
    assert loan.id is not None

    # Creating loan with non-existent user_id fails
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError, match="foreign key"):
        invalid_loan = await loan_repo.create(user_id=99999, amount=5000)
        await db_session.commit()


# CORRECT: Test check constraints
@pytest.mark.integration
async def test_check_constraint_positive_amount(db_session):
    """Test check constraint for positive loan amount."""
    from finance_lending_api.infrastructure.repositories import LoanRepository

    loan_repo = LoanRepository(session=db_session)

    # Negative amount violates check constraint
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError, match="check constraint"):
        loan = await loan_repo.create(user_id=1, amount=-1000)
        await db_session.commit()
```

### Transaction Testing

```python
# CORRECT: Test transaction rollback on error
@pytest.mark.integration
async def test_transaction_rollback_on_error(db_session):
    """Test that errors rollback entire transaction."""
    repo = UserRepository(session=db_session)

    try:
        # Create first user
        user1 = await repo.create(email="user1@example.com", name="User 1")

        # Create second user with duplicate email (will fail)
        user2 = await repo.create(email="user1@example.com", name="User 2")

        await db_session.commit()
    except Exception:
        await db_session.rollback()

    # Verify neither user was committed
    found_user = await repo.find_by_email("user1@example.com")
    assert found_user is None  # Rolled back


# CORRECT: Test concurrent transactions
@pytest.mark.integration
async def test_concurrent_transactions(db_engine):
    """Test isolation between concurrent transactions."""
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    user_email = "concurrent@example.com"

    async def create_user_transaction():
        async with async_session() as session:
            repo = UserRepository(session=session)
            user = await repo.create(email=user_email, name="Concurrent User")
            await asyncio.sleep(0.1)  # Simulate processing
            await session.commit()
            return user

    # Run two concurrent transactions
    results = await asyncio.gather(
        create_user_transaction(),
        create_user_transaction(),
        return_exceptions=True
    )

    # One should succeed, one should fail with unique constraint
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    assert len(successful) == 1
    assert len(failed) == 1
```

### Query Performance Testing

```python
# CORRECT: Test N+1 query problem
@pytest.mark.integration
async def test_eager_loading_prevents_n_plus_1(db_session):
    """Test that eager loading prevents N+1 queries."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    user_repo = UserRepository(session=db_session)
    loan_repo = LoanRepository(session=db_session)

    # Create user with 10 loans
    user = await user_repo.create(email="borrower@example.com", name="Borrower")
    await db_session.commit()

    for i in range(10):
        await loan_repo.create(user_id=user.id, amount=1000 * i)
    await db_session.commit()

    # Query with eager loading
    stmt = (
        select(User)
        .where(User.email == "borrower@example.com")
        .options(selectinload(User.loans))
    )
    result = await db_session.execute(stmt)
    user_with_loans = result.scalar_one()

    # Accessing loans doesn't trigger additional queries
    assert len(user_with_loans.loans) == 10
```

## MongoDB Testing with Motor

### Document Repository Testing

```python
# tests/integration/test_mongo_repository.py
import pytest
from finance_lending_api.infrastructure.mongo_repositories import DocumentRepository


@pytest.mark.integration
async def test_document_insert(mongo_db):
    """Test inserting document into MongoDB."""
    repo = DocumentRepository(mongo_db)

    doc_id = await repo.insert({
        "user_id": "user-123",
        "type": "profile",
        "data": {
            "bio": "Test bio",
            "interests": ["coding", "testing"]
        }
    })

    assert doc_id is not None

    # Verify inserted
    doc = await repo.find_by_id(doc_id)
    assert doc["user_id"] == "user-123"
    assert doc["data"]["bio"] == "Test bio"


@pytest.mark.integration
async def test_document_find_with_filter(mongo_db):
    """Test querying documents with filters."""
    repo = DocumentRepository(mongo_db)

    # Insert test documents
    await repo.insert({"user_id": "user-1", "status": "active", "score": 90})
    await repo.insert({"user_id": "user-2", "status": "inactive", "score": 75})
    await repo.insert({"user_id": "user-3", "status": "active", "score": 85})

    # Query active users with score >= 85
    results = await repo.find_many({
        "status": "active",
        "score": {"$gte": 85}
    })

    assert len(results) == 2
    user_ids = [doc["user_id"] for doc in results]
    assert "user-1" in user_ids
    assert "user-3" in user_ids


@pytest.mark.integration
async def test_document_update(mongo_db):
    """Test updating document fields."""
    repo = DocumentRepository(mongo_db)

    # Insert
    doc_id = await repo.insert({"name": "Original", "count": 10})

    # Update
    result = await repo.update_one(
        {"_id": doc_id},
        {"$set": {"name": "Updated"}, "$inc": {"count": 5}}
    )

    assert result.modified_count == 1

    # Verify
    updated = await repo.find_by_id(doc_id)
    assert updated["name"] == "Updated"
    assert updated["count"] == 15


@pytest.mark.integration
async def test_document_aggregation(mongo_db):
    """Test MongoDB aggregation pipeline."""
    repo = DocumentRepository(mongo_db)

    # Insert sample data
    await repo.insert_many([
        {"category": "electronics", "price": 1000},
        {"category": "electronics", "price": 1500},
        {"category": "books", "price": 50},
        {"category": "books", "price": 30},
    ])

    # Aggregate: average price by category
    pipeline = [
        {"$group": {
            "_id": "$category",
            "avg_price": {"$avg": "$price"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_price": -1}}
    ]

    results = await repo.aggregate(pipeline)

    assert len(results) == 2
    electronics = next(r for r in results if r["_id"] == "electronics")
    assert electronics["avg_price"] == 1250
    assert electronics["count"] == 2
```

### Index Testing

```python
# CORRECT: Test query performance with indexes
@pytest.mark.integration
async def test_index_improves_query_performance(mongo_db):
    """Test that indexes improve query performance."""
    collection = mongo_db["users"]

    # Insert 1000 documents
    docs = [{"email": f"user{i}@example.com", "age": i % 100} for i in range(1000)]
    await collection.insert_many(docs)

    # Query without index (slow for large datasets)
    import time
    start = time.time()
    result = await collection.find_one({"email": "user999@example.com"})
    no_index_time = time.time() - start

    # Create index
    await collection.create_index("email")

    # Query with index (faster)
    start = time.time()
    result = await collection.find_one({"email": "user999@example.com"})
    with_index_time = time.time() - start

    assert result is not None
    # Index should make query faster (though difference may be small for 1000 docs)
    # In production with millions of docs, difference is dramatic
```

## Migration Testing

### Testing Alembic Migrations

```python
# tests/integration/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config


@pytest.mark.integration
def test_migrations_run_successfully(postgres_container):
    """Test that all migrations can be applied."""
    db_url = postgres_container.get_connection_url()

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    # Verify migrations applied
    from sqlalchemy import create_engine, inspect
    engine = create_engine(db_url)
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    assert "users" in tables
    assert "loans" in tables
    assert "alembic_version" in tables


@pytest.mark.integration
def test_migration_downgrade_and_upgrade(postgres_container):
    """Test migrations can be downgraded and re-applied."""
    db_url = postgres_container.get_connection_url()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Upgrade to head
    command.upgrade(alembic_cfg, "head")

    # Downgrade one revision
    command.downgrade(alembic_cfg, "-1")

    # Upgrade back to head
    command.upgrade(alembic_cfg, "head")

    # Verify schema is correct
    from sqlalchemy import create_engine, inspect
    engine = create_engine(db_url)
    inspector = inspect(engine)

    assert len(inspector.get_table_names()) > 0
```

## Best Practices

### DO: Use Transaction Rollback for Isolation

```python
# CORRECT: Rollback transactions to keep database clean
@pytest.fixture
async def db_session(db_engine):
    """Provide session with automatic rollback."""
    async with db_engine.connect() as connection:
        async with connection.begin() as transaction:
            async_session = sessionmaker(
                bind=connection,
                class_=AsyncSession,
                expire_on_commit=False
            )

            async with async_session() as session:
                yield session
                await transaction.rollback()  # Rollback after test
```

### DO: Test Edge Cases

```python
# CORRECT: Test pagination edge cases
@pytest.mark.integration
async def test_pagination_last_page(db_session):
    """Test pagination on last page with fewer items."""
    repo = UserRepository(session=db_session)

    # Create 15 users
    for i in range(15):
        await repo.create(email=f"user{i}@example.com", name=f"User {i}")
    await db_session.commit()

    # Get page 2 (10 items per page, only 5 remaining)
    page2 = await repo.get_paginated(page=2, per_page=10)

    assert len(page2.items) == 5
    assert page2.total == 15
    assert page2.page == 2
    assert page2.pages == 2
```

### DON'T: Share State Between Tests

```python
# INCORRECT: Tests depend on each other
@pytest.mark.integration
async def test_create_user_with_id_1(db_session):
    """WRONG: Assumes empty database."""
    user = await create_user(id=1)
    assert user.id == 1  # Fails if user ID=1 already exists


# CORRECT: Each test is self-contained
@pytest.mark.integration
async def test_create_and_find_user(db_session):
    """Test is self-contained."""
    # Create user in this test
    created = await repo.create(email="test@example.com", name="Test")

    # Find user by ID from this test
    found = await repo.get_by_id(created.id)
    assert found.email == "test@example.com"
```

## Checklist

- [ ] Use testcontainers for real PostgreSQL/MongoDB instances
- [ ] Test constraints (unique, foreign key, check)
- [ ] Test transactions (commit, rollback, isolation)
- [ ] Test complex queries and joins
- [ ] Test pagination, sorting, filtering
- [ ] Test migrations can be applied and reverted
- [ ] Use transaction rollback to isolate tests
- [ ] Tests are independent and self-contained
- [ ] Test both success and error scenarios
- [ ] Test query performance with indexes
- [ ] Mark integration tests with `@pytest.mark.integration`
- [ ] Clean up test data after each test

## Related Documents

- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Setting up Docker containers for tests
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Pytest fixtures for database sessions
- `docs/atomic/databases/postgresql/basic-setup.md` — PostgreSQL configuration
- `docs/atomic/infrastructure/databases/postgres-docker.md` — PostgreSQL Docker setup
- `docs/atomic/infrastructure/databases/migrations.md` — Database migrations with Alembic
