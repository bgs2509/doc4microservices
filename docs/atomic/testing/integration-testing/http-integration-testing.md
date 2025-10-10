# HTTP Integration Testing

Test HTTP client integration with real service endpoints to verify request/response handling, error recovery, retries, and timeouts. Integration tests catch serialization errors, network failures, and protocol issues that mocks cannot detect.

This document covers testing patterns for httpx async client, testing HTTP calls to data services and external APIs, retry logic verification, and timeout handling. HTTP integration tests ensure services communicate correctly over the network.

Real HTTP testing validates that requests serialize correctly, responses deserialize properly, and error handling gracefully recovers from network failures. These tests catch real-world integration issues between services.

## Basic HTTP Testing

```python
# tests/integration/test_http_client.py
import pytest
import httpx
from finance_lending_api.integrations.data_service_client import DataServiceClient


@pytest.mark.integration
async def test_get_request(httpx_mock):
    """Test GET request to data service."""
    # Mock external service
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8001/api/users/123",
        json={"id": "123", "name": "John", "email": "john@example.com"},
        status_code=200
    )

    client = DataServiceClient(base_url="http://localhost:8001")
    user = await client.get_user("123")

    assert user["id"] == "123"
    assert user["name"] == "John"


@pytest.mark.integration
async def test_post_request(httpx_mock):
    """Test POST request creates resource."""
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:8001/api/users",
        json={"id": "new-123", "name": "Jane", "email": "jane@example.com"},
        status_code=201
    )

    client = DataServiceClient(base_url="http://localhost:8001")
    user = await client.create_user({"name": "Jane", "email": "jane@example.com"})

    assert user["id"] == "new-123"
    assert user["name"] == "Jane"
```

## Error Handling

```python
@pytest.mark.integration
async def test_404_not_found():
    """Test 404 error handling."""
    client = DataServiceClient(base_url="http://localhost:8001")

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.get_user("nonexistent")

    assert exc_info.value.response.status_code == 404


@pytest.mark.integration
async def test_500_internal_error():
    """Test 500 error handling."""
    client = DataServiceClient(base_url="http://localhost:8001")

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.create_user({"invalid": "data"})

    assert exc_info.value.response.status_code == 500


@pytest.mark.integration
async def test_network_timeout():
    """Test request timeout handling."""
    client = DataServiceClient(base_url="http://localhost:8001", timeout=1)

    with pytest.raises(httpx.TimeoutException):
        await client.get_user("slow-endpoint")
```

## Retry Logic

```python
@pytest.mark.integration
async def test_retry_on_transient_failure(httpx_mock):
    """Test retry mechanism on transient failures."""
    # First two requests fail, third succeeds
    httpx_mock.add_response(status_code=503)  # Service unavailable
    httpx_mock.add_response(status_code=503)
    httpx_mock.add_response(
        json={"id": "123", "name": "John"},
        status_code=200
    )

    client = DataServiceClient(base_url="http://localhost:8001", max_retries=3)
    user = await client.get_user("123")

    assert user["id"] == "123"
    assert httpx_mock.get_requests().__len__() == 3


@pytest.mark.integration
async def test_no_retry_on_client_error(httpx_mock):
    """Test no retry on 4xx client errors."""
    httpx_mock.add_response(status_code=400)  # Bad request

    client = DataServiceClient(base_url="http://localhost:8001", max_retries=3)

    with pytest.raises(httpx.HTTPStatusError):
        await client.create_user({"invalid": "data"})

    # Only one request made (no retries for 4xx)
    assert httpx_mock.get_requests().__len__() == 1
```

## Request Headers and Authentication

```python
@pytest.mark.integration
async def test_authentication_header(httpx_mock):
    """Test authentication header is included."""
    httpx_mock.add_response(json={"status": "ok"})

    client = DataServiceClient(
        base_url="http://localhost:8001",
        auth_token="secret-token"
    )
    await client.get_user("123")

    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Bearer secret-token"


@pytest.mark.integration
async def test_request_id_propagation(httpx_mock):
    """Test request ID is propagated."""
    httpx_mock.add_response(json={"status": "ok"})

    client = DataServiceClient(base_url="http://localhost:8001")
    await client.get_user("123", request_id="req-abc-123")

    request = httpx_mock.get_request()
    assert request.headers["X-Request-ID"] == "req-abc-123"
```

## Checklist

- [ ] Test GET, POST, PUT, DELETE requests
- [ ] Test error handling (4xx, 5xx)
- [ ] Test timeout handling
- [ ] Test retry logic on transient failures
- [ ] Test authentication headers
- [ ] Test request/response serialization
- [ ] Use pytest-httpx or respx for mocking
- [ ] Mark integration tests with `@pytest.mark.integration`

## Related Documents

- `docs/atomic/integrations/http-communication/http-client-patterns.md` — HTTP client implementation
- `docs/atomic/integrations/http-communication/retry-strategies.md` — Retry logic patterns
- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking HTTP clients in unit tests
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — Testing FastAPI endpoints
