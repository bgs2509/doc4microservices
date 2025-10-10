# Data Service Testing Patterns

Test data service HTTP endpoints to verify CRUD operations, query parameters, pagination, filtering, and error handling without connecting to external business services. Data service tests validate the HTTP API layer over PostgreSQL and MongoDB repositories in isolation.

This document covers testing patterns for FastAPI data services (template_data_postgres_api, template_data_mongo_api) using TestClient, testing CRUD endpoints, query parameter validation, pagination, and database error handling. Data service tests ensure your HTTP layer correctly exposes database operations.

Testing data services validates that endpoints handle requests correctly, repositories interact properly with databases, query parameters filter and paginate results, and errors return appropriate HTTP status codes. These tests bridge unit tests and integration tests by exercising the full HTTP request cycle with mocked or real databases.

## Setup and Configuration

### Basic Data Service Test Setup

```python
# tests/service/test_data_service.py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.fixture
def test_client():
    """Provide TestClient for data service."""
    from finance_data_postgres_api.main import app
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Provide AsyncClient for async tests."""
    from finance_data_postgres_api.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_repository():
    """Provide mocked repository."""
    return AsyncMock()
```

### Overriding Database Dependencies

```python
# CORRECT: Override database dependency
@pytest.fixture
def client_with_mock_db(test_client):
    """Provide client with mocked database."""
    from finance_data_postgres_api.main import app
    from finance_data_postgres_api.dependencies import get_db_session
    from unittest.mock import AsyncMock

    mock_db = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_db

    yield test_client

    app.dependency_overrides.clear()
```

## Testing CRUD Operations

### Create (POST) Endpoint Testing

```python
# CORRECT: Test POST creates resource
@pytest.mark.service
def test_create_user(test_client):
    """Test POST /users creates new user."""
    payload = {
        "email": "newuser@example.com",
        "name": "New User",
        "age": 30
    }

    response = test_client.post("/api/users", json=payload)

    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == payload["email"]
    assert created_user["name"] == payload["name"]
    assert "id" in created_user
    assert "created_at" in created_user


# CORRECT: Test POST validation
@pytest.mark.service
def test_create_user_validation_error(test_client):
    """Test POST with invalid data returns 422."""
    payload = {
        "email": "invalid-email",
        "name": "",
        "age": -5
    }

    response = test_client.post("/api/users", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    error_fields = [e["loc"][-1] for e in errors]
    assert "email" in error_fields
    assert "name" in error_fields
    assert "age" in error_fields
```

### Read (GET) Endpoint Testing

```python
# CORRECT: Test GET by ID
@pytest.mark.service
def test_get_user_by_id(test_client):
    """Test GET /users/{id} returns user."""
    response = test_client.get("/api/users/user-123")

    assert response.status_code == 200
    user = response.json()
    assert user["id"] == "user-123"
    assert "email" in user
    assert "name" in user


# CORRECT: Test GET not found
@pytest.mark.service
def test_get_user_not_found(test_client):
    """Test GET non-existent user returns 404."""
    response = test_client.get("/api/users/nonexistent")

    assert response.status_code == 404
    error = response.json()
    assert "detail" in error


# CORRECT: Test GET list
@pytest.mark.service
def test_list_users(test_client):
    """Test GET /users returns list."""
    response = test_client.get("/api/users")

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert isinstance(data["users"], list)
```

### Update (PUT/PATCH) Endpoint Testing

```python
# CORRECT: Test PUT updates entire resource
@pytest.mark.service
def test_update_user_put(test_client):
    """Test PUT /users/{id} updates user."""
    payload = {
        "email": "updated@example.com",
        "name": "Updated Name",
        "age": 35
    }

    response = test_client.put("/api/users/user-123", json=payload)

    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == payload["email"]
    assert updated_user["name"] == payload["name"]
    assert updated_user["age"] == payload["age"]


# CORRECT: Test PATCH partial update
@pytest.mark.service
def test_update_user_patch(test_client):
    """Test PATCH /users/{id} partial update."""
    payload = {"name": "Only Name Changed"}

    response = test_client.patch("/api/users/user-123", json=payload)

    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Only Name Changed"


# CORRECT: Test update non-existent resource
@pytest.mark.service
def test_update_nonexistent_user(test_client):
    """Test updating non-existent user returns 404."""
    payload = {"name": "New Name"}

    response = test_client.patch("/api/users/nonexistent", json=payload)

    assert response.status_code == 404
```

### Delete (DELETE) Endpoint Testing

```python
# CORRECT: Test DELETE removes resource
@pytest.mark.service
def test_delete_user(test_client):
    """Test DELETE /users/{id} removes user."""
    response = test_client.delete("/api/users/user-123")

    assert response.status_code == 204

    # Verify deletion
    get_response = test_client.get("/api/users/user-123")
    assert get_response.status_code == 404


# CORRECT: Test delete non-existent resource
@pytest.mark.service
def test_delete_nonexistent_user(test_client):
    """Test deleting non-existent user returns 404."""
    response = test_client.delete("/api/users/nonexistent")

    assert response.status_code == 404
```

## Testing Query Parameters

### Filtering

```python
# CORRECT: Test filtering by field
@pytest.mark.service
def test_filter_users_by_status(test_client):
    """Test filtering users by status."""
    response = test_client.get("/api/users", params={"status": "active"})

    assert response.status_code == 200
    data = response.json()
    assert all(user["status"] == "active" for user in data["users"])


# CORRECT: Test multiple filters
@pytest.mark.service
def test_filter_users_multiple_criteria(test_client):
    """Test filtering with multiple criteria."""
    response = test_client.get("/api/users", params={
        "status": "active",
        "min_age": 18,
        "max_age": 65
    })

    assert response.status_code == 200
    data = response.json()
    for user in data["users"]:
        assert user["status"] == "active"
        assert 18 <= user["age"] <= 65
```

### Sorting

```python
# CORRECT: Test sorting by field
@pytest.mark.service
def test_sort_users_by_name(test_client):
    """Test sorting users by name."""
    response = test_client.get("/api/users", params={"sort": "name"})

    assert response.status_code == 200
    users = response.json()["users"]

    # Verify sorted order
    names = [u["name"] for u in users]
    assert names == sorted(names)


# CORRECT: Test descending sort
@pytest.mark.service
def test_sort_users_descending(test_client):
    """Test sorting users in descending order."""
    response = test_client.get("/api/users", params={"sort": "-created_at"})

    assert response.status_code == 200
    users = response.json()["users"]

    # Verify descending order
    timestamps = [u["created_at"] for u in users]
    assert timestamps == sorted(timestamps, reverse=True)
```

### Pagination

```python
# CORRECT: Test pagination
@pytest.mark.service
def test_paginate_users(test_client):
    """Test pagination returns correct page."""
    response = test_client.get("/api/users", params={
        "page": 2,
        "per_page": 10
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) <= 10
    assert data["page"] == 2
    assert data["per_page"] == 10
    assert "total" in data
    assert "pages" in data


# CORRECT: Test pagination boundaries
@pytest.mark.service
def test_pagination_last_page(test_client):
    """Test pagination on last page with fewer items."""
    # Assuming 25 total users
    response = test_client.get("/api/users", params={
        "page": 3,
        "per_page": 10
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 5  # Last 5 items
    assert data["total"] == 25
    assert data["pages"] == 3


# CORRECT: Test invalid page number
@pytest.mark.service
def test_pagination_invalid_page(test_client):
    """Test requesting page beyond total returns empty."""
    response = test_client.get("/api/users", params={
        "page": 999,
        "per_page": 10
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 0
```

## Testing PostgreSQL Data Service

### Repository Integration Testing

```python
# CORRECT: Test endpoint with mocked repository
@pytest.mark.service
def test_create_user_with_mock_repo():
    """Test create endpoint with mocked repository."""
    from fastapi.testclient import TestClient
    from finance_data_postgres_api.main import app
    from finance_data_postgres_api.dependencies import get_user_repository
    from unittest.mock import AsyncMock

    mock_repo = AsyncMock()
    mock_repo.create.return_value = {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User"
    }

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    client = TestClient(app)
    response = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })

    assert response.status_code == 201
    mock_repo.create.assert_called_once()

    app.dependency_overrides.clear()
```

### Testing Unique Constraints

```python
# CORRECT: Test unique constraint violation
@pytest.mark.service
def test_create_duplicate_email(test_client):
    """Test creating user with duplicate email fails."""
    payload = {"email": "duplicate@example.com", "name": "User 1"}

    # First create succeeds
    response1 = test_client.post("/api/users", json=payload)
    assert response1.status_code == 201

    # Second create fails (duplicate email)
    response2 = test_client.post("/api/users", json=payload)
    assert response2.status_code == 409
    error = response2.json()
    assert "already exists" in error["detail"].lower()
```

## Testing MongoDB Data Service

### Document Query Testing

```python
# CORRECT: Test MongoDB document filtering
@pytest.mark.service
def test_filter_documents_by_field(test_client):
    """Test filtering MongoDB documents."""
    response = test_client.get("/api/documents", params={
        "category": "finance",
        "status": "published"
    })

    assert response.status_code == 200
    documents = response.json()["documents"]
    assert all(d["category"] == "finance" for d in documents)
    assert all(d["status"] == "published" for d in documents)


# CORRECT: Test MongoDB aggregation endpoint
@pytest.mark.service
def test_aggregate_documents(test_client):
    """Test aggregation endpoint."""
    response = test_client.get("/api/documents/stats", params={
        "group_by": "category"
    })

    assert response.status_code == 200
    stats = response.json()
    assert "categories" in stats
    for category_stat in stats["categories"]:
        assert "category" in category_stat
        assert "count" in category_stat
```

### Testing Nested Document Updates

```python
# CORRECT: Test updating nested document fields
@pytest.mark.service
def test_update_nested_field(test_client):
    """Test updating nested document field."""
    payload = {
        "metadata.tags": ["updated", "finance"],
        "metadata.priority": "high"
    }

    response = test_client.patch("/api/documents/doc-123", json=payload)

    assert response.status_code == 200
    document = response.json()
    assert "updated" in document["metadata"]["tags"]
    assert document["metadata"]["priority"] == "high"
```

## Testing Error Handling

### Database Connection Errors

```python
# CORRECT: Test database connection error handling
@pytest.mark.service
def test_database_connection_error():
    """Test graceful handling of database connection errors."""
    from fastapi.testclient import TestClient
    from finance_data_postgres_api.main import app
    from finance_data_postgres_api.dependencies import get_db_session
    from sqlalchemy.exc import OperationalError

    async def failing_db_session():
        raise OperationalError("Connection failed", None, None)

    app.dependency_overrides[get_db_session] = failing_db_session

    client = TestClient(app)
    response = client.get("/api/users")

    assert response.status_code == 503
    error = response.json()
    assert "database" in error["detail"].lower()

    app.dependency_overrides.clear()
```

### Validation Errors

```python
# CORRECT: Test validation error responses
@pytest.mark.service
def test_validation_error_format(test_client):
    """Test validation errors return detailed messages."""
    payload = {
        "email": "not-an-email",
        "age": "not-a-number"
    }

    response = test_client.post("/api/users", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]

    # Verify error structure
    assert isinstance(errors, list)
    for error in errors:
        assert "loc" in error
        assert "msg" in error
        assert "type" in error
```

## Testing Transaction Handling

### Atomic Operations

```python
# CORRECT: Test transaction rollback on error
@pytest.mark.service
@pytest.mark.asyncio
async def test_transaction_rollback():
    """Test transaction rolls back on error."""
    from finance_data_postgres_api.services.user_service import UserService
    from unittest.mock import AsyncMock

    mock_db = AsyncMock()
    mock_db.commit.side_effect = Exception("Database error")

    service = UserService(db=mock_db)

    with pytest.raises(Exception):
        await service.create_user_with_profile(
            email="test@example.com",
            name="Test User"
        )

    # Verify rollback called
    mock_db.rollback.assert_called_once()
```

## Best Practices

### DO: Test HTTP Layer Only

```python
# CORRECT: Test data service HTTP endpoints
@pytest.mark.service
def test_endpoint_with_mocked_repo():
    """Test HTTP layer with mocked repository."""
    from finance_data_postgres_api.dependencies import get_user_repository
    from unittest.mock import AsyncMock

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = {"id": "123", "name": "Test"}

    app.dependency_overrides[get_user_repository] = lambda: mock_repo

    response = test_client.get("/api/users/123")
    assert response.status_code == 200


# INCORRECT: Don't test repository logic in service tests
@pytest.mark.service
def test_repository_directly():
    """WRONG: Tests repository, not HTTP layer."""
    repo = UserRepository(session=db_session)
    user = await repo.create(email="test@example.com")
    # This is integration testing, not service testing
```

### DO: Test All HTTP Status Codes

```python
# CORRECT: Test success and error responses
@pytest.mark.service
def test_all_status_codes():
    """Test endpoint returns correct status codes."""
    # 200 OK
    response = test_client.get("/api/users/existing")
    assert response.status_code == 200

    # 404 Not Found
    response = test_client.get("/api/users/nonexistent")
    assert response.status_code == 404

    # 422 Validation Error
    response = test_client.post("/api/users", json={"invalid": "data"})
    assert response.status_code == 422
```

### DON'T: Make Real Database Calls

```python
# INCORRECT: Service test making real database calls
@pytest.mark.service
async def test_with_real_database():
    """WRONG: Makes real database queries."""
    # This should be integration test, not service test
    real_db = await create_real_db_connection()
    await real_db.execute("INSERT INTO users...")


# CORRECT: Mock database dependencies
@pytest.mark.service
def test_with_mocked_database():
    """Mock database for service tests."""
    mock_db = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_db
    # Test HTTP layer only
```

## Checklist

- [ ] Test all CRUD operations (POST, GET, PUT/PATCH, DELETE)
- [ ] Test query parameters (filtering, sorting, pagination)
- [ ] Test request validation with invalid data
- [ ] Test response serialization follows models
- [ ] Test error responses (404, 422, 500, 503)
- [ ] Test unique constraint violations
- [ ] Test database connection error handling
- [ ] Mock repositories and database sessions
- [ ] Test transaction rollback on errors
- [ ] Use `@pytest.mark.service` for service tests
- [ ] Clean up dependency overrides after tests

## Related Documents

- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — FastAPI testing patterns
- `docs/atomic/testing/integration-testing/database-testing.md` — Integration tests with real databases
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking repositories and database sessions
- `docs/atomic/services/fastapi-service/endpoint-patterns.md` — Data service endpoint implementation
- `docs/atomic/databases/postgresql/repository-patterns.md` — PostgreSQL repository patterns
