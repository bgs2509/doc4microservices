# FastAPI Service Testing Patterns

Test FastAPI endpoints with TestClient to verify request handling, response serialization, dependency injection, middleware behavior, and error handling without running a live server. Service-level tests bridge unit tests and end-to-end tests by exercising the full request/response cycle.

This document covers testing patterns for FastAPI applications using TestClient and pytest-asyncio, including endpoint testing, dependency overrides, lifespan event testing, middleware verification, and authentication. FastAPI service tests ensure your API behaves correctly under realistic conditions.

Testing FastAPI services validates that routes handle requests correctly, dependencies inject properly, validation catches bad input, and error handlers return appropriate responses. These tests run quickly while providing confidence in your API's contract with clients.

## Setup and Configuration

### Basic Test Setup

```python
# tests/service/test_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from finance_lending_api.main import app


# CORRECT: Use TestClient for synchronous tests
@pytest.mark.service
def test_health_endpoint_sync():
    """Test health check endpoint with TestClient."""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# CORRECT: Use AsyncClient for async tests
@pytest.mark.service
@pytest.mark.asyncio
async def test_health_endpoint_async():
    """Test health check endpoint with AsyncClient."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
```

### Fixtures for FastAPI Testing

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from finance_lending_api.main import app


@pytest.fixture
def test_client():
    """Provide TestClient for synchronous tests."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Provide AsyncClient for async tests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def override_dependencies():
    """Helper to override FastAPI dependencies."""
    overrides = {}

    def _override(dependency, override_value):
        app.dependency_overrides[dependency] = lambda: override_value
        overrides[dependency] = override_value

    yield _override

    # Cleanup
    for dependency in overrides:
        app.dependency_overrides.pop(dependency, None)
```

## Testing Endpoints

### GET Requests

```python
# CORRECT: Test GET endpoint with query parameters
@pytest.mark.service
def test_list_users_with_filters(test_client):
    """Test listing users with query filters."""
    response = test_client.get("/api/users", params={
        "status": "active",
        "limit": 10,
        "offset": 0
    })

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert len(data["users"]) <= 10


# CORRECT: Test path parameters
@pytest.mark.service
def test_get_user_by_id(test_client):
    """Test retrieving user by ID."""
    response = test_client.get("/api/users/user-123")

    assert response.status_code == 200
    user = response.json()
    assert user["id"] == "user-123"
    assert "email" in user
    assert "name" in user
```

### POST Requests

```python
# CORRECT: Test POST with request body
@pytest.mark.service
def test_create_user(test_client):
    """Test creating new user."""
    payload = {
        "email": "newuser@example.com",
        "name": "New User",
        "credit_score": 750
    }

    response = test_client.post("/api/users", json=payload)

    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == payload["email"]
    assert created_user["name"] == payload["name"]
    assert "id" in created_user
    assert "created_at" in created_user


# CORRECT: Test validation errors
@pytest.mark.service
def test_create_user_validation_error(test_client):
    """Test validation catches invalid data."""
    payload = {
        "email": "invalid-email",  # Invalid format
        "name": "",  # Empty string
        "credit_score": -100  # Negative value
    }

    response = test_client.post("/api/users", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]

    # Check all validation errors present
    error_fields = [e["loc"][-1] for e in errors]
    assert "email" in error_fields
    assert "name" in error_fields
    assert "credit_score" in error_fields
```

### PUT/PATCH Requests

```python
# CORRECT: Test updating resource
@pytest.mark.service
def test_update_user(test_client):
    """Test updating user fields."""
    update_payload = {
        "name": "Updated Name",
        "credit_score": 800
    }

    response = test_client.patch("/api/users/user-123", json=update_payload)

    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["name"] == "Updated Name"
    assert updated_user["credit_score"] == 800


# CORRECT: Test partial updates
@pytest.mark.service
def test_partial_update_user(test_client):
    """Test partial update only changes specified fields."""
    response = test_client.patch(
        "/api/users/user-123",
        json={"name": "Only Name Changed"}
    )

    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Only Name Changed"
    # Other fields unchanged
```

### DELETE Requests

```python
# CORRECT: Test resource deletion
@pytest.mark.service
def test_delete_user(test_client):
    """Test deleting user."""
    response = test_client.delete("/api/users/user-123")

    assert response.status_code == 204

    # Verify deletion
    get_response = test_client.get("/api/users/user-123")
    assert get_response.status_code == 404


# CORRECT: Test deleting non-existent resource
@pytest.mark.service
def test_delete_nonexistent_user(test_client):
    """Test deleting non-existent user returns 404."""
    response = test_client.delete("/api/users/nonexistent")
    assert response.status_code == 404
```

## Testing Dependencies

### Overriding Dependencies

```python
# src/dependencies.py
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncSession:
    """Provide database session."""
    # Production implementation
    pass


async def get_current_user(token: str = Depends(get_token)) -> dict:
    """Get authenticated user from token."""
    # Production implementation
    pass


# CORRECT: Override dependencies in tests
@pytest.mark.service
def test_endpoint_with_mocked_db():
    """Test endpoint with mocked database dependency."""
    from finance_lending_api.main import app
    from finance_lending_api.dependencies import get_db_session
    from unittest.mock import AsyncMock

    # Mock database session
    mock_db = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_db

    client = TestClient(app)
    response = client.get("/api/users")

    assert response.status_code == 200

    # Cleanup
    app.dependency_overrides.clear()


# CORRECT: Override authentication dependency
@pytest.mark.service
def test_protected_endpoint_with_auth():
    """Test protected endpoint with mocked authentication."""
    from finance_lending_api.dependencies import get_current_user

    mock_user = {"id": "user-123", "email": "test@example.com", "role": "admin"}
    app.dependency_overrides[get_current_user] = lambda: mock_user

    client = TestClient(app)
    response = client.get("/api/protected/resource")

    assert response.status_code == 200

    app.dependency_overrides.clear()
```

### Dependency Fixtures

```python
# CORRECT: Use fixtures to manage dependency overrides
@pytest.fixture
def authenticated_client(test_client):
    """Provide client with authenticated user."""
    from finance_lending_api.dependencies import get_current_user

    mock_user = {"id": "user-123", "email": "test@example.com"}
    app.dependency_overrides[get_current_user] = lambda: mock_user

    yield test_client

    app.dependency_overrides.clear()


@pytest.mark.service
def test_with_authenticated_client(authenticated_client):
    """Test using authenticated client fixture."""
    response = authenticated_client.get("/api/protected/data")
    assert response.status_code == 200
```

## Testing Lifespan Events

```python
# CORRECT: Test startup/shutdown events
@pytest.mark.service
@pytest.mark.asyncio
async def test_lifespan_events():
    """Test application lifespan events."""
    from contextlib import asynccontextmanager
    from fastapi import FastAPI

    startup_called = []
    shutdown_called = []

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        startup_called.append(True)
        yield
        # Shutdown
        shutdown_called.append(True)

    test_app = FastAPI(lifespan=lifespan)

    @test_app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    # Use AsyncClient to trigger lifespan
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert len(startup_called) == 1

    # After client closes, shutdown should be called
    assert len(shutdown_called) == 1
```

## Testing Middleware

```python
# CORRECT: Test custom middleware
@pytest.mark.service
def test_request_id_middleware():
    """Test that middleware adds request ID to response headers."""
    client = TestClient(app)

    response = client.get("/api/users")

    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


# CORRECT: Test CORS middleware
@pytest.mark.service
def test_cors_middleware():
    """Test CORS headers are added."""
    client = TestClient(app)

    response = client.options(
        "/api/users",
        headers={"Origin": "http://localhost:3000"}
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers


# CORRECT: Test authentication middleware
@pytest.mark.service
def test_auth_middleware_blocks_unauthenticated():
    """Test middleware blocks requests without token."""
    client = TestClient(app)

    response = client.get("/api/protected/resource")

    assert response.status_code == 401
    assert "detail" in response.json()
```

## Testing Error Handlers

```python
# CORRECT: Test custom exception handlers
@pytest.mark.service
def test_not_found_exception_handler():
    """Test 404 handler returns correct format."""
    client = TestClient(app)

    response = client.get("/api/nonexistent/endpoint")

    assert response.status_code == 404
    error = response.json()
    assert "detail" in error
    assert "timestamp" in error


# CORRECT: Test validation exception handler
@pytest.mark.service
def test_validation_exception_handler():
    """Test validation errors return detailed messages."""
    client = TestClient(app)

    response = client.post("/api/users", json={"invalid": "data"})

    assert response.status_code == 422
    error = response.json()
    assert "detail" in error
    assert isinstance(error["detail"], list)


# CORRECT: Test custom business logic exception
@pytest.mark.service
def test_business_logic_exception_handler():
    """Test custom exceptions return proper HTTP status."""
    from finance_lending_api.exceptions import InsufficientCreditError

    client = TestClient(app)

    # Endpoint that raises InsufficientCreditError
    response = client.post("/api/loans", json={
        "user_id": "user-poor-credit",
        "amount": 50000
    })

    assert response.status_code == 400
    error = response.json()
    assert error["error_code"] == "INSUFFICIENT_CREDIT"
```

## Testing Response Models

```python
# CORRECT: Test response serialization
@pytest.mark.service
def test_response_model_serialization():
    """Test response follows Pydantic model schema."""
    client = TestClient(app)

    response = client.get("/api/users/user-123")

    assert response.status_code == 200
    user = response.json()

    # Verify all required fields present
    required_fields = ["id", "email", "name", "created_at", "updated_at"]
    for field in required_fields:
        assert field in user

    # Verify no extra fields (response_model_exclude_unset)
    assert "password_hash" not in user
    assert "internal_notes" not in user


# CORRECT: Test response model validation
@pytest.mark.service
def test_response_model_validates_types():
    """Test response model enforces type constraints."""
    client = TestClient(app)

    response = client.get("/api/loans/loan-123")
    loan = response.json()

    # Verify types
    assert isinstance(loan["id"], str)
    assert isinstance(loan["amount"], (int, float))
    assert isinstance(loan["interest_rate"], (int, float))
    assert isinstance(loan["approved"], bool)
```

## Testing Authentication and Authorization

```python
# CORRECT: Test JWT authentication
@pytest.mark.service
def test_jwt_authentication():
    """Test endpoint requires valid JWT token."""
    client = TestClient(app)

    # Without token
    response = client.get("/api/protected/data")
    assert response.status_code == 401

    # With invalid token
    response = client.get(
        "/api/protected/data",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401

    # With valid token
    valid_token = "valid-jwt-token-here"
    response = client.get(
        "/api/protected/data",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200


# CORRECT: Test role-based authorization
@pytest.mark.service
def test_admin_only_endpoint():
    """Test endpoint restricted to admin role."""
    from finance_lending_api.dependencies import get_current_user

    client = TestClient(app)

    # Regular user
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "user-123",
        "role": "user"
    }
    response = client.delete("/api/admin/users/other-user")
    assert response.status_code == 403

    # Admin user
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "admin-123",
        "role": "admin"
    }
    response = client.delete("/api/admin/users/other-user")
    assert response.status_code == 204

    app.dependency_overrides.clear()
```

## Testing WebSocket Endpoints

```python
# CORRECT: Test WebSocket connection
@pytest.mark.service
def test_websocket_connection():
    """Test WebSocket endpoint accepts connections."""
    client = TestClient(app)

    with client.websocket_connect("/ws/notifications") as websocket:
        # Send message
        websocket.send_json({"type": "subscribe", "channel": "updates"})

        # Receive response
        data = websocket.receive_json()
        assert data["type"] == "subscribed"
        assert data["channel"] == "updates"


# CORRECT: Test WebSocket message handling
@pytest.mark.service
def test_websocket_message_handling():
    """Test WebSocket handles messages correctly."""
    client = TestClient(app)

    with client.websocket_connect("/ws/chat") as websocket:
        # Send chat message
        websocket.send_json({
            "type": "message",
            "text": "Hello, world!"
        })

        # Receive echo
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["text"] == "Hello, world!"
```

## Best Practices

### DO: Use Dependency Overrides

```python
# CORRECT: Override dependencies to isolate tests
@pytest.mark.service
def test_with_dependency_override():
    """Isolate test by mocking dependencies."""
    from finance_lending_api.dependencies import get_db_session
    from unittest.mock import AsyncMock

    mock_db = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: mock_db

    client = TestClient(app)
    response = client.get("/api/data")

    assert response.status_code == 200
    app.dependency_overrides.clear()


# INCORRECT: Don't call real dependencies in service tests
@pytest.mark.service
def test_without_override():
    """WRONG: Calls real database."""
    client = TestClient(app)
    # This will hit real database if not overridden
    response = client.get("/api/users")
```

### DO: Test Request/Response Contracts

```python
# CORRECT: Verify complete API contract
@pytest.mark.service
def test_api_contract():
    """Test request and response match OpenAPI spec."""
    client = TestClient(app)

    # Valid request
    payload = {
        "email": "user@example.com",
        "name": "Test User",
        "age": 30
    }
    response = client.post("/api/users", json=payload)

    # Verify status code
    assert response.status_code == 201

    # Verify response schema
    user = response.json()
    assert all(key in user for key in ["id", "email", "name", "age", "created_at"])

    # Verify types
    assert isinstance(user["id"], str)
    assert isinstance(user["email"], str)
    assert isinstance(user["age"], int)
```

### DON'T: Mix Service and Integration Tests

```python
# INCORRECT: Service test calling real database
@pytest.mark.service
async def test_mixed_layers():
    """WRONG: Mixes service and integration testing."""
    # Creates real database record
    db_session = await get_real_db_session()
    user = await create_user_in_db(db_session, email="test@example.com")

    # Then tests API
    client = TestClient(app)
    response = client.get(f"/api/users/{user.id}")


# CORRECT: Service test with mocked dependencies
@pytest.mark.service
def test_isolated_service():
    """Service test with all dependencies mocked."""
    from finance_lending_api.dependencies import get_user_service
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.get_user.return_value = {"id": "123", "email": "test@example.com"}

    app.dependency_overrides[get_user_service] = lambda: mock_service

    client = TestClient(app)
    response = client.get("/api/users/123")

    assert response.status_code == 200
    app.dependency_overrides.clear()
```

## Checklist

- [ ] Test all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Test query parameters, path parameters, request bodies
- [ ] Test request validation with invalid data
- [ ] Test response serialization follows models
- [ ] Test authentication and authorization
- [ ] Override dependencies to isolate from external systems
- [ ] Test middleware behavior (CORS, auth, request ID)
- [ ] Test custom exception handlers
- [ ] Test lifespan events (startup/shutdown)
- [ ] Test WebSocket endpoints if applicable
- [ ] Use `@pytest.mark.service` to mark service tests
- [ ] Clean up dependency overrides after tests

## Related Documents

- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Real database containers for integration tests
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking external dependencies
- `docs/atomic/services/fastapi-service/endpoint-patterns.md` — FastAPI endpoint implementation patterns
- `docs/atomic/services/fastapi-service/dependency-injection.md` — FastAPI dependency injection patterns
- `docs/atomic/integrations/http-communication/http-client-patterns.md` — HTTP client patterns for inter-service calls
