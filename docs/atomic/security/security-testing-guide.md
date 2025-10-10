# Security Testing Guide

Comprehensive guide for testing authentication, authorization, and security features in microservices.

## Prerequisites

- [Authentication & Authorization Guide](authentication-authorization-guide.md)
- [Session Management Patterns](session-management-patterns.md)
- [Pytest Setup](../testing/unit-testing/pytest-setup.md)
- [Integration Testing](../testing/integration-testing/testcontainers-setup.md)

## Authentication Testing

### JWT Token Testing

```python
import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from your_app.security.token_service import TokenService, AuthConfig

@pytest.fixture
def auth_config():
    return AuthConfig(
        SECRET_KEY="test-secret-key",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        REFRESH_TOKEN_EXPIRE_DAYS=7
    )

@pytest.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.setex = AsyncMock()
    redis_mock.get = AsyncMock()
    redis_mock.delete = AsyncMock()
    return redis_mock

@pytest.fixture
def token_service(mock_redis, auth_config):
    return TokenService(mock_redis, auth_config)

class TestTokenService:
    @pytest.mark.asyncio
    async def test_create_access_token(self, token_service, mock_redis):
        user_id = "user123"
        username = "testuser"
        roles = ["user", "admin"]

        token = await token_service.create_access_token(user_id, username, roles)

        # Verify token structure
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify payload
        payload = jwt.decode(
            token,
            token_service.config.SECRET_KEY,
            algorithms=[token_service.config.ALGORITHM]
        )

        assert payload["user_id"] == user_id
        assert payload["username"] == username
        assert payload["roles"] == roles
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

        # Verify Redis call
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, token_service, mock_redis):
        user_id = "user123"
        username = "testuser"
        roles = ["user"]

        # Create token
        token = await token_service.create_access_token(user_id, username, roles)

        # Mock Redis responses
        payload = jwt.decode(
            token,
            token_service.config.SECRET_KEY,
            algorithms=[token_service.config.ALGORITHM]
        )
        jti = payload["jti"]

        mock_redis.get.side_effect = [
            None,  # blacklist check
            user_id.encode()  # token exists check
        ]

        # Verify token
        result = await token_service.verify_token(token)

        assert result is not None
        assert result["user_id"] == user_id
        assert result["username"] == username
        assert result["roles"] == roles

    @pytest.mark.asyncio
    async def test_verify_expired_token(self, token_service, auth_config):
        # Create expired token
        now = datetime.utcnow()
        expired_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["user"],
            "exp": now - timedelta(minutes=1),  # Expired
            "iat": now - timedelta(minutes=31),
            "jti": "test-jti",
            "type": "access"
        }

        expired_token = jwt.encode(
            expired_payload,
            auth_config.SECRET_KEY,
            algorithm=auth_config.ALGORITHM
        )

        result = await token_service.verify_token(expired_token)
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_blacklisted_token(self, token_service, mock_redis):
        user_id = "user123"
        username = "testuser"
        roles = ["user"]

        token = await token_service.create_access_token(user_id, username, roles)

        # Mock blacklisted token
        mock_redis.get.side_effect = [
            "1".encode(),  # blacklist check returns value
        ]

        result = await token_service.verify_token(token)
        assert result is None

    @pytest.mark.asyncio
    async def test_blacklist_token(self, token_service, mock_redis):
        user_id = "user123"
        username = "testuser"
        roles = ["user"]

        token = await token_service.create_access_token(user_id, username, roles)

        await token_service.blacklist_token(token)

        # Verify Redis setex was called for blacklisting
        assert mock_redis.setex.call_count >= 2  # Create + blacklist calls

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, token_service):
        invalid_token = "invalid.token.format"

        result = await token_service.verify_token(invalid_token)
        assert result is None
```

### Authorization Testing

```python
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from your_app.security.auth_dependency import AuthDependency, Permission, Role
from your_app.security.token_service import TokenService

class TestAuthDependency:
    @pytest.fixture
    def mock_token_service(self):
        return AsyncMock(spec=TokenService)

    @pytest.fixture
    def auth_dependency(self, mock_token_service):
        return AuthDependency(mock_token_service)

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, auth_dependency, mock_token_service):
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid.jwt.token"

        expected_payload = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["user", "admin"]
        }

        mock_token_service.verify_token.return_value = expected_payload

        result = await auth_dependency.get_current_user(mock_credentials)

        assert result == expected_payload
        mock_token_service.verify_token.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, auth_dependency, mock_token_service):
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid.token"

        mock_token_service.verify_token.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await auth_dependency.get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_permissions_sufficient(self, auth_dependency):
        required_permissions = {Permission.READ_USERS}

        permission_checker = auth_dependency.require_permissions(required_permissions)

        current_user = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["admin"]  # Admin has READ_USERS permission
        }

        result = await permission_checker(current_user)
        assert result == current_user

    @pytest.mark.asyncio
    async def test_require_permissions_insufficient(self, auth_dependency):
        required_permissions = {Permission.DELETE_USERS}

        permission_checker = auth_dependency.require_permissions(required_permissions)

        current_user = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["user"]  # User doesn't have DELETE_USERS permission
        }

        with pytest.raises(HTTPException) as exc_info:
            await permission_checker(current_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_require_roles_valid(self, auth_dependency):
        required_roles = {Role.ADMIN}

        role_checker = auth_dependency.require_roles(required_roles)

        current_user = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["admin", "user"]
        }

        result = await role_checker(current_user)
        assert result == current_user

    @pytest.mark.asyncio
    async def test_require_roles_invalid(self, auth_dependency):
        required_roles = {Role.ADMIN}

        role_checker = auth_dependency.require_roles(required_roles)

        current_user = {
            "user_id": "user123",
            "username": "testuser",
            "roles": ["user"]
        }

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient role privileges" in str(exc_info.value.detail)
```

## Session Management Testing

### Session Storage Testing

```python
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from your_app.security.session_manager import DistributedSessionManager

class TestDistributedSessionManager:
    @pytest.fixture
    def mock_redis(self):
        redis_mock = AsyncMock()
        redis_mock.setex = AsyncMock()
        redis_mock.get = AsyncMock()
        redis_mock.delete = AsyncMock()
        redis_mock.sadd = AsyncMock()
        redis_mock.srem = AsyncMock()
        redis_mock.smembers = AsyncMock()
        redis_mock.expire = AsyncMock()
        redis_mock.lpush = AsyncMock()
        return redis_mock

    @pytest.fixture
    def session_manager(self, mock_redis):
        return DistributedSessionManager(
            redis_client=mock_redis,
            default_ttl=timedelta(hours=24),
            max_sessions_per_user=5
        )

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager, mock_redis):
        user_id = "user123"
        session_data = {
            "ip_address": "192.168.1.1",
            "user_agent": "TestAgent/1.0",
            "metadata": {"device": "mobile"}
        }

        # Mock existing sessions check
        mock_redis.smembers.return_value = []

        session_id = await session_manager.create_session(user_id, session_data)

        assert isinstance(session_id, str)
        assert len(session_id) > 0

        # Verify Redis calls
        mock_redis.setex.assert_called()
        mock_redis.sadd.assert_called_with(f"user_sessions:{user_id}", session_id)
        mock_redis.expire.assert_called()
        mock_redis.lpush.assert_called()  # Audit log

    @pytest.mark.asyncio
    async def test_get_session_valid(self, session_manager, mock_redis):
        session_id = "test-session-id"
        user_id = "user123"

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "ip_address": "192.168.1.1",
            "metadata": {}
        }

        mock_redis.get.return_value = json.dumps(session_data)

        result = await session_manager.get_session(session_id)

        assert result is not None
        assert result["session_id"] == session_id
        assert result["user_id"] == user_id

        # Verify activity update
        mock_redis.setex.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_expired(self, session_manager, mock_redis):
        session_id = "test-session-id"

        expired_session_data = {
            "session_id": session_id,
            "user_id": "user123",
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),  # Expired
            "metadata": {}
        }

        mock_redis.get.return_value = json.dumps(expired_session_data)

        result = await session_manager.get_session(session_id)

        assert result is None

        # Verify session was invalidated
        mock_redis.delete.assert_called()

    @pytest.mark.asyncio
    async def test_invalidate_session(self, session_manager, mock_redis):
        session_id = "test-session-id"
        user_id = "user123"

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "metadata": {}
        }

        mock_redis.get.return_value = json.dumps(session_data)

        result = await session_manager.invalidate_session(session_id)

        assert result is True

        # Verify Redis calls
        mock_redis.srem.assert_called_with(f"user_sessions:{user_id}", session_id)
        mock_redis.delete.assert_called_with(f"session:{session_id}")

    @pytest.mark.asyncio
    async def test_session_limit_enforcement(self, session_manager, mock_redis):
        user_id = "user123"

        # Mock 5 existing sessions (at limit)
        existing_sessions = [f"session_{i}" for i in range(5)]
        mock_redis.smembers.return_value = existing_sessions

        # Mock session data for cleanup
        for i, session_id in enumerate(existing_sessions):
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "metadata": {}
            }

            if i == 0:  # First call for enforcement check
                mock_redis.get.return_value = json.dumps(session_data)
            else:
                # Additional calls for get_user_sessions
                mock_redis.get.return_value = json.dumps(session_data)

        session_data = {
            "ip_address": "192.168.1.1",
            "user_agent": "TestAgent/1.0"
        }

        await session_manager.create_session(user_id, session_data)

        # Should have invalidated the oldest session
        assert mock_redis.delete.call_count >= 1
```

## MFA Testing

### TOTP Testing

```python
import pytest
import pyotp
from unittest.mock import AsyncMock, patch

from your_app.security.mfa_service import MFAService

class TestMFAService:
    @pytest.fixture
    def mock_redis(self):
        redis_mock = AsyncMock()
        redis_mock.setex = AsyncMock()
        redis_mock.get = AsyncMock()
        redis_mock.set = AsyncMock()
        redis_mock.delete = AsyncMock()
        return redis_mock

    @pytest.fixture
    def mfa_service(self, mock_redis):
        return MFAService(mock_redis)

    @pytest.mark.asyncio
    async def test_setup_totp(self, mfa_service, mock_redis):
        user_id = "user123"
        app_name = "TestApp"

        with patch('pyotp.random_base32') as mock_random:
            mock_random.return_value = "JBSWY3DPEHPK3PXP"

            result = await mfa_service.setup_totp(user_id, app_name)

            assert "secret" in result
            assert "qr_code" in result
            assert "totp_uri" in result

            # Verify Redis call
            mock_redis.setex.assert_called_with(
                f"mfa_setup:{user_id}",
                300,
                "JBSWY3DPEHPK3PXP"
            )

    @pytest.mark.asyncio
    async def test_confirm_totp_setup_valid(self, mfa_service, mock_redis):
        user_id = "user123"
        secret = "JBSWY3DPEHPK3PXP"

        mock_redis.get.return_value = secret.encode()

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        result = await mfa_service.confirm_totp_setup(user_id, valid_code)

        assert result is True

        # Verify Redis calls
        mock_redis.set.assert_called_with(f"mfa_secret:{user_id}", secret)
        mock_redis.delete.assert_called_with(f"mfa_setup:{user_id}")

    @pytest.mark.asyncio
    async def test_confirm_totp_setup_invalid_code(self, mfa_service, mock_redis):
        user_id = "user123"
        secret = "JBSWY3DPEHPK3PXP"

        mock_redis.get.return_value = secret.encode()

        invalid_code = "000000"

        result = await mfa_service.confirm_totp_setup(user_id, invalid_code)

        assert result is False

        # Verify secret was not saved
        mock_redis.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_totp_valid(self, mfa_service, mock_redis):
        user_id = "user123"
        secret = "JBSWY3DPEHPK3PXP"

        mock_redis.get.return_value = secret.encode()

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        result = await mfa_service.verify_totp(user_id, valid_code)

        assert result is True

    @pytest.mark.asyncio
    async def test_verify_totp_no_secret(self, mfa_service, mock_redis):
        user_id = "user123"

        mock_redis.get.return_value = None

        result = await mfa_service.verify_totp(user_id, "123456")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_mfa_enabled(self, mfa_service, mock_redis):
        user_id = "user123"

        # Test enabled
        mock_redis.get.return_value = "secret".encode()
        result = await mfa_service.is_mfa_enabled(user_id)
        assert result is True

        # Test disabled
        mock_redis.get.return_value = None
        result = await mfa_service.is_mfa_enabled(user_id)
        assert result is False
```

## FastAPI Integration Testing

### Authentication Endpoints Testing

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from your_app.main import app
from your_app.security.token_service import TokenService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_token_service():
    return AsyncMock(spec=TokenService)

class TestAuthenticationEndpoints:
    def test_login_valid_credentials(self, client):
        with patch('your_app.main.validate_user_credentials') as mock_validate, \
             patch('your_app.main.token_service') as mock_token_service, \
             patch('your_app.main.mfa_service') as mock_mfa_service, \
             patch('your_app.main.session_manager') as mock_session_manager:

            # Mock user validation
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_user.username = "testuser"
            mock_user.roles = ["user"]
            mock_validate.return_value = mock_user

            # Mock MFA disabled
            mock_mfa_service.is_mfa_enabled.return_value = False

            # Mock token creation
            mock_token_service.create_access_token.return_value = "access_token"
            mock_token_service.create_refresh_token.return_value = "refresh_token"

            # Mock session creation
            mock_session_manager.create_session.return_value = "session_id"

            response = client.post("/auth/login", json={
                "username": "testuser",
                "password": "testpass"
            })

            assert response.status_code == 200
            data = response.json()

            assert "access_token" in data
            assert "refresh_token" in data
            assert "session_id" in data
            assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        with patch('your_app.main.validate_user_credentials') as mock_validate:
            mock_validate.return_value = None

            response = client.post("/auth/login", json={
                "username": "invalid",
                "password": "invalid"
            })

            assert response.status_code == 401
            assert "Invalid credentials" in response.json()["detail"]

    def test_login_with_mfa_required(self, client):
        with patch('your_app.main.validate_user_credentials') as mock_validate, \
             patch('your_app.main.token_service') as mock_token_service, \
             patch('your_app.main.mfa_service') as mock_mfa_service:

            # Mock user validation
            mock_user = MagicMock()
            mock_user.id = "user123"
            mock_user.username = "testuser"
            mock_user.roles = ["user"]
            mock_validate.return_value = mock_user

            # Mock MFA enabled
            mock_mfa_service.is_mfa_enabled.return_value = True

            # Mock temporary token creation
            mock_token_service.create_access_token.return_value = "temp_token"

            response = client.post("/auth/login", json={
                "username": "testuser",
                "password": "testpass"
            })

            assert response.status_code == 200
            data = response.json()

            assert data["requires_mfa"] is True
            assert "temp_token" in data

    def test_protected_endpoint_with_valid_token(self, client):
        with patch('your_app.main.auth_dependency.get_current_user') as mock_get_user:
            mock_get_user.return_value = {
                "user_id": "user123",
                "username": "testuser",
                "roles": ["user"]
            }

            response = client.get(
                "/users/profile",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["user_id"] == "user123"
            assert data["username"] == "testuser"

    def test_protected_endpoint_without_token(self, client):
        response = client.get("/users/profile")

        assert response.status_code == 403  # No Authorization header

    def test_protected_endpoint_invalid_token(self, client):
        with patch('your_app.main.auth_dependency.get_current_user') as mock_get_user:
            mock_get_user.side_effect = HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

            response = client.get(
                "/users/profile",
                headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == 401
```

## Security Load Testing

### Authentication Load Testing

```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

class SecurityLoadTester:
    def __init__(self, base_url: str, max_concurrent: int = 100):
        self.base_url = base_url
        self.max_concurrent = max_concurrent

    async def test_login_performance(self, credentials_list: list, duration_seconds: int = 60):
        """Test login endpoint performance under load."""

        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "errors": []
        }

        start_time = time.time()
        response_times = []

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def make_request(session, credentials):
            async with semaphore:
                try:
                    start = time.time()
                    async with session.post(
                        f"{self.base_url}/auth/login",
                        json=credentials,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        await response.text()
                        response_time = time.time() - start
                        response_times.append(response_time)

                        results["total_requests"] += 1

                        if response.status == 200:
                            results["successful_requests"] += 1
                        else:
                            results["failed_requests"] += 1

                except Exception as e:
                    results["total_requests"] += 1
                    results["failed_requests"] += 1
                    results["errors"].append(str(e))

        async with aiohttp.ClientSession() as session:
            tasks = []

            while time.time() - start_time < duration_seconds:
                for credentials in credentials_list:
                    if time.time() - start_time >= duration_seconds:
                        break

                    task = asyncio.create_task(make_request(session, credentials))
                    tasks.append(task)

                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.01)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

        if response_times:
            results["avg_response_time"] = sum(response_times) / len(response_times)

        return results

    async def test_token_verification_performance(self, tokens: list, duration_seconds: int = 60):
        """Test token verification performance."""

        results = {"total_requests": 0, "successful_requests": 0, "failed_requests": 0}

        start_time = time.time()
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def verify_token(session, token):
            async with semaphore:
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        f"{self.base_url}/users/profile",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        results["total_requests"] += 1

                        if response.status == 200:
                            results["successful_requests"] += 1
                        else:
                            results["failed_requests"] += 1

                except Exception:
                    results["total_requests"] += 1
                    results["failed_requests"] += 1

        async with aiohttp.ClientSession() as session:
            tasks = []

            while time.time() - start_time < duration_seconds:
                for token in tokens:
                    if time.time() - start_time >= duration_seconds:
                        break

                    task = asyncio.create_task(verify_token(session, token))
                    tasks.append(task)

                    await asyncio.sleep(0.001)

            await asyncio.gather(*tasks, return_exceptions=True)

        return results

# Usage example
async def run_security_load_tests():
    tester = SecurityLoadTester("http://localhost:8000")

    credentials = [
        {"username": f"user{i}", "password": "password"}
        for i in range(10)
    ]

    print("Testing login performance...")
    login_results = await tester.test_login_performance(credentials, 30)
    print(f"Login test results: {login_results}")

    # Create some valid tokens for testing
    # (In real tests, you'd get these from actual login requests)
    tokens = ["valid_token_1", "valid_token_2", "valid_token_3"]

    print("Testing token verification performance...")
    token_results = await tester.test_token_verification_performance(tokens, 30)
    print(f"Token verification results: {token_results}")

if __name__ == "__main__":
    asyncio.run(run_security_load_tests())
```

## Related Documentation

- [Authentication & Authorization Guide](authentication-authorization-guide.md)
- [Session Management Patterns](session-management-patterns.md)
- [Pytest Setup](../testing/unit-testing/pytest-setup.md)
- [Integration Testing](../testing/integration-testing/testcontainers-setup.md)

## Best Practices

1. **Test Coverage**:
   - Test all authentication flows
   - Test authorization scenarios
   - Test token lifecycle
   - Test session management

2. **Security Scenarios**:
   - Test with expired tokens
   - Test with malformed tokens
   - Test concurrent sessions
   - Test MFA flows

3. **Performance Testing**:
   - Load test authentication endpoints
   - Test token verification performance
   - Monitor response times under load

4. **Integration Testing**:
   - Test with real Redis instances
   - Test cross-service authentication
   - Test security middleware

## Related Documents

- `docs/atomic/security/authentication-authorization-guide.md` — Auth testing
- `docs/atomic/testing/security-testing.md` — Security test patterns
- `docs/atomic/testing/integration-testing.md` — Integration security tests
- `docs/atomic/infrastructure/ci-cd-pipeline.md` — Security scans in CI
