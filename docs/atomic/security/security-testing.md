# Security Testing

Comprehensive security testing patterns for microservices architecture following the Improved Hybrid Approach.

## Overview

Security testing ensures that authentication, authorization, and data protection mechanisms work correctly and resist attacks. This guide covers testing strategies specific to the microservices pattern with FastAPI, data services, and cross-service communication.

## Authentication Testing

### 1. JWT Token Testing

```python
# tests/security/test_jwt_authentication.py
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import app
from src.core.config import settings

client = TestClient(app)

class TestJWTAuthentication:
    """Test JWT authentication mechanisms."""

    def test_valid_jwt_token_access(self):
        """Test access with valid JWT token."""
        # Create valid token
        payload = {
            "sub": "user-123",
            "scopes": ["user"],
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

        with patch("src.clients.data_service.UserDataClient.get_user_by_id") as mock_get_user:
            mock_get_user.return_value = {
                "id": "user-123",
                "email": "test@example.com",
                "username": "testuser",
                "is_active": True,
                "roles": ["user"]
            }

            response = client.get(
                "/users/profile",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200

    def test_expired_jwt_token(self):
        """Test rejection of expired JWT token."""
        # Create expired token
        payload = {
            "sub": "user-123",
            "scopes": ["user"],
            "exp": datetime.utcnow() - timedelta(minutes=30),  # Expired
            "iat": datetime.utcnow() - timedelta(hours=1),
            "type": "access"
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_malformed_jwt_token(self):
        """Test rejection of malformed JWT token."""
        response = client.get(
            "/users/profile",
            headers={"Authorization": "Bearer malformed.token.here"}
        )

        assert response.status_code == 401

    def test_jwt_token_with_wrong_secret(self):
        """Test rejection of token signed with wrong secret."""
        payload = {
            "sub": "user-123",
            "scopes": ["user"],
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        # Sign with wrong secret
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401

    def test_jwt_token_without_required_claims(self):
        """Test rejection of token missing required claims."""
        payload = {
            # Missing 'sub' claim
            "scopes": ["user"],
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401

    def test_refresh_token_as_access_token(self):
        """Test rejection of refresh token used as access token."""
        payload = {
            "sub": "user-123",
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
            "type": "refresh"  # Refresh token, not access
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")

        response = client.get(
            "/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401

class TestLoginSecurity:
    """Test login endpoint security."""

    def test_login_rate_limiting(self):
        """Test rate limiting on login attempts."""
        # This test requires rate limiting implementation
        # Make multiple failed login attempts
        for i in range(10):
            response = client.post("/auth/login", data={
                "username": "attacker@example.com",
                "password": "wrong_password"
            })

        # Next attempt should be rate limited
        response = client.post("/auth/login", data={
            "username": "attacker@example.com",
            "password": "wrong_password"
        })

        assert response.status_code == 429  # Too Many Requests

    def test_login_timing_attack_resistance(self):
        """Test resistance to timing attacks."""
        import time

        # Time valid username with wrong password
        start_time = time.time()
        client.post("/auth/login", data={
            "username": "valid@example.com",
            "password": "wrong_password"
        })
        valid_user_time = time.time() - start_time

        # Time invalid username
        start_time = time.time()
        client.post("/auth/login", data={
            "username": "invalid@example.com",
            "password": "wrong_password"
        })
        invalid_user_time = time.time() - start_time

        # Response times should be similar (within reasonable threshold)
        time_difference = abs(valid_user_time - invalid_user_time)
        assert time_difference < 0.1, "Potential timing attack vulnerability"

    def test_password_brute_force_protection(self):
        """Test protection against password brute force attacks."""
        username = "victim@example.com"

        # Attempt multiple failed logins
        for i in range(5):
            response = client.post("/auth/login", data={
                "username": username,
                "password": f"wrong_password_{i}"
            })
            assert response.status_code == 401

        # Account should be locked or additional protection triggered
        response = client.post("/auth/login", data={
            "username": username,
            "password": "correct_password"
        })

        # Should be locked/protected (adjust based on implementation)
        assert response.status_code in [423, 429]  # Locked or Rate Limited

class TestSessionSecurity:
    """Test session management security."""

    @pytest.mark.asyncio
    async def test_session_fixation_protection(self):
        """Test protection against session fixation attacks."""
        # Create initial session
        response1 = client.post("/auth/login", data={
            "username": "user@example.com",
            "password": "correct_password"
        })

        session_id_1 = response1.cookies.get("session_id")

        # Login again - should get new session ID
        response2 = client.post("/auth/login", data={
            "username": "user@example.com",
            "password": "correct_password"
        })

        session_id_2 = response2.cookies.get("session_id")

        # Session IDs should be different
        assert session_id_1 != session_id_2

    @pytest.mark.asyncio
    async def test_session_regeneration_on_privilege_change(self):
        """Test session regeneration when user privileges change."""
        # Login as regular user
        response = client.post("/auth/login", data={
            "username": "user@example.com",
            "password": "correct_password"
        })

        original_token = response.json()["access_token"]

        # Simulate privilege escalation (admin grants admin role)
        # This would trigger session regeneration
        with patch("src.core.auth.get_current_user") as mock_user:
            mock_user.return_value.roles = ["admin"]  # Elevated privileges

            # Make request that triggers privilege check
            response = client.get("/admin/dashboard", headers={
                "Authorization": f"Bearer {original_token}"
            })

            # Should require new authentication
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_concurrent_session_limit(self):
        """Test limit on concurrent sessions per user."""
        user_credentials = {
            "username": "user@example.com",
            "password": "correct_password"
        }

        # Create multiple sessions
        sessions = []
        for i in range(6):  # Assuming limit is 5
            response = client.post("/auth/login", data=user_credentials)
            if response.status_code == 200:
                sessions.append(response.json()["access_token"])

        # Earlier sessions should be invalidated
        # Test first session is no longer valid
        response = client.get("/users/profile", headers={
            "Authorization": f"Bearer {sessions[0]}"
        })

        assert response.status_code == 401
```

### 2. Multi-Factor Authentication Testing

```python
# tests/security/test_mfa.py
import pytest
import pyotp
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestMFASecurity:
    """Test Multi-Factor Authentication security."""

    def test_mfa_setup_requires_authentication(self):
        """Test that MFA setup requires valid authentication."""
        response = client.post("/mfa/setup")
        assert response.status_code == 401

    def test_mfa_secret_generation_unique(self):
        """Test that MFA secrets are unique for each user."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-1"

            with patch("src.core.mfa.MFAManager.generate_secret") as mock_gen:
                mock_gen.side_effect = ["SECRET1", "SECRET2"]

                # Generate secret for user 1
                response1 = client.post("/mfa/setup", headers={
                    "Authorization": "Bearer valid_token_1"
                })

                # Generate secret for user 2 (simulated)
                mock_auth.return_value.id = "user-2"
                response2 = client.post("/mfa/setup", headers={
                    "Authorization": "Bearer valid_token_2"
                })

                # Secrets should be different
                assert mock_gen.call_count == 2

    def test_mfa_totp_validation(self):
        """Test TOTP token validation."""
        secret = "JBSWY3DPEHPK3PXP"  # Test secret
        totp = pyotp.TOTP(secret)
        valid_token = totp.now()

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-123"

            with patch("src.core.mfa.MFAManager.verify_totp") as mock_verify:
                mock_verify.return_value = True

                response = client.post("/mfa/verify",
                    json={"token": valid_token},
                    headers={"Authorization": "Bearer valid_token"}
                )

                assert response.status_code == 200

    def test_mfa_replay_attack_protection(self):
        """Test protection against TOTP replay attacks."""
        secret = "JBSWY3DPEHPK3PXP"
        totp = pyotp.TOTP(secret)
        token = totp.now()

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-123"

            # First use should succeed
            with patch("src.core.mfa.MFAManager.verify_totp") as mock_verify:
                mock_verify.return_value = True

                response1 = client.post("/mfa/verify",
                    json={"token": token},
                    headers={"Authorization": "Bearer valid_token"}
                )
                assert response1.status_code == 200

                # Second use of same token should fail
                mock_verify.return_value = False  # Simulate replay protection

                response2 = client.post("/mfa/verify",
                    json={"token": token},
                    headers={"Authorization": "Bearer valid_token"}
                )
                assert response2.status_code == 400

    def test_mfa_time_window_validation(self):
        """Test TOTP time window validation."""
        secret = "JBSWY3DPEHPK3PXP"

        # Generate token for previous time window
        totp = pyotp.TOTP(secret)
        old_token = totp.at(totp.timecode() - 2)  # 2 time windows ago

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-123"

            with patch("src.core.mfa.MFAManager.verify_totp") as mock_verify:
                mock_verify.return_value = False  # Old token should fail

                response = client.post("/mfa/verify",
                    json={"token": old_token},
                    headers={"Authorization": "Bearer valid_token"}
                )

                assert response.status_code == 400

class TestMFABypassAttempts:
    """Test MFA bypass attack resistance."""

    def test_mfa_bypass_via_direct_endpoint_access(self):
        """Test that MFA-protected endpoints can't be bypassed."""
        # Attempt to access protected resource without MFA
        with patch("src.core.auth.get_current_user") as mock_auth:
            user = mock_auth.return_value
            user.id = "user-123"
            user.mfa_enabled = True
            user.mfa_verified = False  # Not yet verified

            response = client.get("/admin/sensitive-data", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 403
            assert "MFA required" in response.json()["detail"]

    def test_mfa_bypass_via_session_manipulation(self):
        """Test resistance to MFA bypass via session manipulation."""
        # This test would verify that MFA status can't be manipulated
        # in session data or tokens
        with patch("src.core.auth.get_current_user") as mock_auth:
            user = mock_auth.return_value
            user.id = "user-123"
            user.mfa_enabled = True

            # Attempt to manipulate MFA verification status
            malicious_token_payload = {
                "sub": "user-123",
                "mfa_verified": True,  # Attacker tries to set this
                "exp": "future_time"
            }

            # System should not trust this claim without proper verification
            response = client.get("/admin/sensitive-data", headers={
                "Authorization": "Bearer manipulated_token"
            })

            assert response.status_code in [401, 403]
```

## Authorization Testing

### 1. Role-Based Access Control Testing

```python
# tests/security/test_rbac_authorization.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app
from src.core.models import CurrentUser

client = TestClient(app)

class TestRBACAuthorization:
    """Test Role-Based Access Control."""

    def test_admin_access_to_user_management(self):
        """Test admin access to user management endpoints."""
        admin_user = CurrentUser(
            id="admin-123",
            email="admin@example.com",
            username="admin",
            is_active=True,
            roles=["admin"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=admin_user):
            # Admin should access user list
            response = client.get("/users/", headers={
                "Authorization": "Bearer admin_token"
            })
            assert response.status_code == 200

            # Admin should delete users
            response = client.delete("/users/user-456", headers={
                "Authorization": "Bearer admin_token"
            })
            assert response.status_code in [200, 204]

    def test_user_access_restrictions(self):
        """Test regular user access restrictions."""
        regular_user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=regular_user):
            # User should access their own profile
            response = client.get("/users/profile", headers={
                "Authorization": "Bearer user_token"
            })
            assert response.status_code == 200

            # User should NOT access admin endpoints
            response = client.get("/admin/dashboard", headers={
                "Authorization": "Bearer user_token"
            })
            assert response.status_code == 403

            # User should NOT delete other users
            response = client.delete("/users/other-user", headers={
                "Authorization": "Bearer user_token"
            })
            assert response.status_code == 403

    def test_moderator_permissions(self):
        """Test moderator role permissions."""
        moderator_user = CurrentUser(
            id="mod-123",
            email="mod@example.com",
            username="moderator",
            is_active=True,
            roles=["moderator"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=moderator_user):
            # Moderator should manage content
            response = client.post("/content/",
                json={"title": "Test", "body": "Content"},
                headers={"Authorization": "Bearer mod_token"}
            )
            assert response.status_code in [200, 201]

            # Moderator should NOT access user management
            response = client.delete("/users/user-456", headers={
                "Authorization": "Bearer mod_token"
            })
            assert response.status_code == 403

    def test_role_hierarchy_inheritance(self):
        """Test that higher roles inherit lower role permissions."""
        admin_user = CurrentUser(
            id="admin-123",
            email="admin@example.com",
            username="admin",
            is_active=True,
            roles=["admin"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=admin_user):
            # Admin should have user-level permissions
            response = client.get("/users/profile", headers={
                "Authorization": "Bearer admin_token"
            })
            assert response.status_code == 200

            # Admin should have moderator-level permissions
            response = client.post("/content/moderate",
                json={"action": "approve", "content_id": "123"},
                headers={"Authorization": "Bearer admin_token"}
            )
            assert response.status_code == 200

class TestPrivilegeEscalation:
    """Test resistance to privilege escalation attacks."""

    def test_horizontal_privilege_escalation(self):
        """Test protection against horizontal privilege escalation."""
        user1 = CurrentUser(
            id="user-123",
            email="user1@example.com",
            username="user1",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=user1):
            # User 1 should NOT access User 2's data
            response = client.get("/users/user-456/profile", headers={
                "Authorization": "Bearer user1_token"
            })
            assert response.status_code == 403

            # User 1 should NOT modify User 2's resources
            response = client.put("/users/user-456",
                json={"email": "hacked@example.com"},
                headers={"Authorization": "Bearer user1_token"}
            )
            assert response.status_code == 403

    def test_vertical_privilege_escalation(self):
        """Test protection against vertical privilege escalation."""
        user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=user):
            # User should NOT be able to escalate to admin
            response = client.post("/users/promote",
                json={"user_id": "user-123", "role": "admin"},
                headers={"Authorization": "Bearer user_token"}
            )
            assert response.status_code == 403

            # User should NOT access admin-only endpoints
            response = client.get("/admin/system-config", headers={
                "Authorization": "Bearer user_token"
            })
            assert response.status_code == 403

    def test_role_manipulation_in_jwt(self):
        """Test protection against JWT role manipulation."""
        import jwt
        from datetime import datetime, timedelta

        # Create token with manipulated roles
        malicious_payload = {
            "sub": "user-123",
            "scopes": ["admin"],  # User tries to escalate to admin
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "type": "access"
        }

        # Sign with correct secret (simulating token manipulation)
        malicious_token = jwt.encode(malicious_payload, settings.secret_key, algorithm="HS256")

        with patch("src.clients.data_service.UserDataClient.get_user_by_id") as mock_get_user:
            # Data service returns real user roles (not manipulated ones)
            mock_get_user.return_value = {
                "id": "user-123",
                "email": "user@example.com",
                "username": "user",
                "is_active": True,
                "roles": ["user"]  # Real roles from database
            }

            response = client.get("/admin/dashboard", headers={
                "Authorization": f"Bearer {malicious_token}"
            })

            # Should fail because real user roles are checked
            assert response.status_code == 403
```

### 2. Attribute-Based Access Control Testing

```python
# tests/security/test_abac_authorization.py
import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from src.core.abac import ABACEngine, ABACPolicy
from src.core.models import CurrentUser

class TestABACAuthorization:
    """Test Attribute-Based Access Control."""

    @pytest.fixture
    def abac_engine(self):
        """Create ABAC engine with test policies."""
        engine = ABACEngine()

        # Time-based policy
        time_policy = ABACPolicy(
            id="time_restricted",
            name="Time Restricted Access",
            description="Allow access only during business hours",
            conditions=[
                {
                    "operator": "time_range",
                    "attribute": "environment.time",
                    "value": [9, 17]
                }
            ],
            effect="allow",
            priority=50
        )

        # Location-based policy
        location_policy = ABACPolicy(
            id="location_restricted",
            name="Location Restricted Access",
            description="Deny access from external networks",
            conditions=[
                {
                    "operator": "equals",
                    "attribute": "environment.network.network_type",
                    "value": "external"
                },
                {
                    "operator": "equals",
                    "attribute": "resource.classification",
                    "value": "sensitive"
                }
            ],
            effect="deny",
            priority=80
        )

        engine.add_policy(time_policy)
        engine.add_policy(location_policy)

        return engine

    @pytest.mark.asyncio
    async def test_time_based_access_control(self, abac_engine):
        """Test time-based access control."""
        user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        # Test during business hours
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value.hour = 10  # 10 AM

            result = await abac_engine.evaluate(
                user, "document", "doc-123", "read", {}
            )
            assert result is True

        # Test outside business hours
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value.hour = 20  # 8 PM

            result = await abac_engine.evaluate(
                user, "document", "doc-123", "read", {}
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_location_based_access_control(self, abac_engine):
        """Test location-based access control."""
        user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        # Test internal network access to sensitive data
        context = {
            "client_ip": "192.168.1.100"  # Internal IP
        }

        with patch.object(abac_engine, "_get_resource_classification") as mock_class:
            mock_class.return_value = "sensitive"

            result = await abac_engine.evaluate(
                user, "file", "sensitive-file", "read", context
            )
            assert result is False  # Should be denied by location policy

        # Test external network access to public data
        context = {
            "client_ip": "203.0.113.1"  # External IP
        }

        with patch.object(abac_engine, "_get_resource_classification") as mock_class:
            mock_class.return_value = "public"

            result = await abac_engine.evaluate(
                user, "file", "public-file", "read", context
            )
            # Should depend on other policies (not denied by location policy)

    @pytest.mark.asyncio
    async def test_policy_priority_evaluation(self, abac_engine):
        """Test that policies are evaluated in priority order."""
        user = CurrentUser(
            id="admin-123",
            email="admin@example.com",
            username="admin",
            is_active=True,
            roles=["super_admin"],
            scopes=[]
        )

        # Add high-priority allow policy for super_admin
        admin_policy = ABACPolicy(
            id="super_admin_access",
            name="Super Admin Full Access",
            description="Super admins can access everything",
            conditions=[
                {
                    "operator": "in",
                    "attribute": "user.roles",
                    "value": ["super_admin"]
                }
            ],
            effect="allow",
            priority=100
        )

        abac_engine.add_policy(admin_policy)

        # Even with location restrictions, super admin should have access
        context = {
            "client_ip": "203.0.113.1"  # External IP
        }

        result = await abac_engine.evaluate(
            user, "file", "sensitive-file", "read", context
        )
        assert result is True  # High-priority admin policy should override

class TestABACPolicyManipulation:
    """Test resistance to ABAC policy manipulation."""

    @pytest.mark.asyncio
    async def test_policy_injection_attack(self):
        """Test protection against policy injection attacks."""
        malicious_policy_data = {
            "id": "malicious_policy",
            "name": "Backdoor Policy",
            "description": "Allow everything for attacker",
            "conditions": [
                {
                    "operator": "equals",
                    "attribute": "user.id",
                    "value": "attacker-123"
                }
            ],
            "effect": "allow",
            "priority": 999
        }

        # Attempt to inject policy via API endpoint
        regular_user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        with patch("src.core.auth.get_current_user", return_value=regular_user):
            response = client.post("/policies/",
                json=malicious_policy_data,
                headers={"Authorization": "Bearer user_token"}
            )

            # Should be forbidden for regular users
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_condition_bypass_attempt(self):
        """Test protection against condition bypass attempts."""
        user = CurrentUser(
            id="user-123",
            email="user@example.com",
            username="user",
            is_active=True,
            roles=["user"],
            scopes=[]
        )

        # Attempt to bypass conditions with malformed attributes
        malicious_context = {
            "environment.time": "always_allow",  # Invalid time value
            "user.roles": ["admin"],  # Attempt to override user roles
            "resource.classification": None  # Null value injection
        }

        engine = ABACEngine()
        result = await engine.evaluate(
            user, "sensitive_file", "file-123", "read", malicious_context
        )

        # Should not be allowed due to invalid/malicious context
        assert result is False
```

## Input Validation and Injection Testing

### 1. SQL Injection Testing

```python
# tests/security/test_sql_injection.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import app

client = TestClient(app)

class TestSQLInjectionProtection:
    """Test protection against SQL injection attacks."""

    def test_sql_injection_in_user_search(self):
        """Test SQL injection protection in user search."""
        # SQL injection payload
        malicious_query = "'; DROP TABLE users; --"

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["admin"]

            response = client.get(f"/users/search?q={malicious_query}", headers={
                "Authorization": "Bearer admin_token"
            })

            # Should not execute SQL injection
            # Response should be normal (not server error)
            assert response.status_code in [200, 400]  # Not 500

            # Database should still exist (test with subsequent query)
            response2 = client.get("/users/", headers={
                "Authorization": "Bearer admin_token"
            })
            assert response2.status_code == 200

    def test_sql_injection_in_login(self):
        """Test SQL injection protection in login."""
        # SQL injection in username field
        response = client.post("/auth/login", data={
            "username": "admin'--",
            "password": "anything"
        })

        # Should not bypass authentication
        assert response.status_code == 401

    def test_sql_injection_in_user_creation(self):
        """Test SQL injection protection in user creation."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["admin"]

            malicious_user_data = {
                "email": "test@example.com'; DROP TABLE users; --",
                "username": "normal_user",
                "password": "password123"
            }

            response = client.post("/users/",
                json=malicious_user_data,
                headers={"Authorization": "Bearer admin_token"}
            )

            # Should validate and reject malicious input
            assert response.status_code in [400, 422]

class TestNoSQLInjectionProtection:
    """Test protection against NoSQL injection attacks."""

    def test_nosql_injection_in_search(self):
        """Test NoSQL injection protection in search."""
        # MongoDB injection payload
        malicious_query = {"$where": "function() { return true; }"}

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["admin"]

            response = client.post("/search/",
                json={"query": malicious_query},
                headers={"Authorization": "Bearer admin_token"}
            )

            # Should not execute NoSQL injection
            assert response.status_code in [200, 400, 422]  # Not 500

    def test_nosql_injection_in_aggregation(self):
        """Test NoSQL injection protection in aggregation queries."""
        malicious_pipeline = [
            {"$match": {"$where": "this.user == 'admin'"}},
            {"$project": {"password": 1}}  # Attempt to expose passwords
        ]

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["admin"]

            response = client.post("/analytics/aggregate",
                json={"pipeline": malicious_pipeline},
                headers={"Authorization": "Bearer admin_token"}
            )

            # Should validate and reject malicious pipeline
            assert response.status_code in [400, 422]
```

### 2. Cross-Site Scripting (XSS) Testing

```python
# tests/security/test_xss_protection.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

class TestXSSProtection:
    """Test protection against Cross-Site Scripting attacks."""

    def test_stored_xss_in_user_profile(self):
        """Test protection against stored XSS in user profiles."""
        xss_payload = "<script>alert('XSS')</script>"

        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-123"

            # Attempt to store XSS in profile
            response = client.put("/users/profile",
                json={
                    "display_name": xss_payload,
                    "bio": f"Hello {xss_payload} World"
                },
                headers={"Authorization": "Bearer user_token"}
            )

            # Should sanitize or reject malicious input
            if response.status_code == 200:
                # If accepted, verify it's sanitized
                profile_data = response.json()
                assert "<script>" not in profile_data.get("display_name", "")
                assert "<script>" not in profile_data.get("bio", "")

    def test_reflected_xss_in_search(self):
        """Test protection against reflected XSS in search."""
        xss_payload = "<img src=x onerror=alert('XSS')>"

        response = client.get(f"/search?q={xss_payload}", headers={
            "Authorization": "Bearer user_token"
        })

        # Response should not contain unsanitized script
        response_text = response.text
        assert "<img src=x onerror=" not in response_text
        assert "alert('XSS')" not in response_text

    def test_xss_in_content_creation(self):
        """Test XSS protection in content creation."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["user"]

            malicious_content = {
                "title": "<script>document.location='http://evil.com'</script>",
                "body": "Normal content with <iframe src='javascript:alert(1)'></iframe>",
                "tags": ["<svg onload=alert('XSS')>", "normal_tag"]
            }

            response = client.post("/content/",
                json=malicious_content,
                headers={"Authorization": "Bearer user_token"}
            )

            if response.status_code in [200, 201]:
                content_data = response.json()
                # Verify malicious scripts are sanitized
                assert "<script>" not in content_data.get("title", "")
                assert "<iframe" not in content_data.get("body", "")
                assert "<svg onload=" not in str(content_data.get("tags", []))

class TestCSRFProtection:
    """Test Cross-Site Request Forgery protection."""

    def test_csrf_token_required_for_state_changing_operations(self):
        """Test that CSRF tokens are required for state-changing operations."""
        # Attempt state-changing operation without CSRF token
        response = client.post("/users/change-password",
            json={"new_password": "new_password123"},
            headers={"Authorization": "Bearer user_token"}
            # Missing CSRF token header
        )

        # Should require CSRF token for state-changing operations
        # Implementation may vary - could be 403 or require specific header
        assert response.status_code in [403, 400]

    def test_csrf_token_validation(self):
        """Test CSRF token validation."""
        valid_csrf_token = "valid_csrf_token_here"
        invalid_csrf_token = "invalid_csrf_token"

        # Valid CSRF token should work
        response1 = client.post("/users/change-password",
            json={"new_password": "new_password123"},
            headers={
                "Authorization": "Bearer user_token",
                "X-CSRF-Token": valid_csrf_token
            }
        )

        # Invalid CSRF token should fail
        response2 = client.post("/users/change-password",
            json={"new_password": "another_password"},
            headers={
                "Authorization": "Bearer user_token",
                "X-CSRF-Token": invalid_csrf_token
            }
        )

        # Assuming CSRF protection is implemented
        assert response2.status_code == 403
```

## Data Protection Testing

### 1. Data Encryption Testing

```python
# tests/security/test_data_encryption.py
import pytest
from unittest.mock import patch, AsyncMock
from src.core.encryption import FieldEncryption
from src.core.models import User

class TestDataEncryption:
    """Test data encryption and decryption."""

    def test_sensitive_field_encryption(self):
        """Test that sensitive fields are encrypted at rest."""
        encryption = FieldEncryption()

        # Test PII encryption
        ssn = "123-45-6789"
        encrypted_ssn = encryption.encrypt(ssn)

        # Encrypted value should be different from original
        assert encrypted_ssn != ssn
        assert len(encrypted_ssn) > len(ssn)

        # Should decrypt back to original
        decrypted_ssn = encryption.decrypt(encrypted_ssn)
        assert decrypted_ssn == ssn

    def test_password_hashing_irreversibility(self):
        """Test that passwords are hashed irreversibly."""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        password = "secure_password123"
        hashed = pwd_context.hash(password)

        # Hash should be different from password
        assert hashed != password

        # Should verify correctly
        assert pwd_context.verify(password, hashed)

        # Should not verify wrong password
        assert not pwd_context.verify("wrong_password", hashed)

    def test_database_encryption_at_rest(self):
        """Test that sensitive data is encrypted in database."""
        # This test would verify that sensitive fields are encrypted
        # when stored in the database
        with patch("src.clients.data_service.UserDataClient.create_user") as mock_create:
            user_data = {
                "email": "user@example.com",
                "ssn": "123-45-6789",
                "credit_card": "4111-1111-1111-1111"
            }

            # Mock the encrypted storage
            def store_encrypted_user(data):
                # Simulate encryption before storage
                encrypted_data = data.copy()
                if 'ssn' in encrypted_data:
                    encrypted_data['ssn'] = f"encrypted_{encrypted_data['ssn']}"
                if 'credit_card' in encrypted_data:
                    encrypted_data['credit_card'] = f"encrypted_{encrypted_data['credit_card']}"
                return encrypted_data

            mock_create.side_effect = store_encrypted_user

            result = mock_create(user_data)

            # Verify sensitive fields are encrypted
            assert result['ssn'].startswith('encrypted_')
            assert result['credit_card'].startswith('encrypted_')
            assert result['email'] == user_data['email']  # Non-sensitive field unchanged

class TestDataMasking:
    """Test data masking in responses."""

    def test_sensitive_data_masking_in_api_responses(self):
        """Test that sensitive data is masked in API responses."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["user"]

            with patch("src.clients.data_service.UserDataClient.get_user_by_id") as mock_get:
                mock_get.return_value = {
                    "id": "user-123",
                    "email": "user@example.com",
                    "ssn": "123-45-6789",
                    "credit_card": "4111-1111-1111-1111"
                }

                response = client.get("/users/profile", headers={
                    "Authorization": "Bearer user_token"
                })

                if response.status_code == 200:
                    user_data = response.json()

                    # Sensitive fields should be masked
                    if 'ssn' in user_data:
                        assert user_data['ssn'] == "***-**-6789"  # Partially masked
                    if 'credit_card' in user_data:
                        assert user_data['credit_card'] == "****-****-****-1111"

    def test_admin_access_to_unmasked_data(self):
        """Test that admins can access unmasked sensitive data."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["admin"]

            with patch("src.clients.data_service.UserDataClient.get_user_by_id") as mock_get:
                mock_get.return_value = {
                    "id": "user-123",
                    "email": "user@example.com",
                    "ssn": "123-45-6789",
                    "credit_card": "4111-1111-1111-1111"
                }

                response = client.get("/admin/users/user-123", headers={
                    "Authorization": "Bearer admin_token"
                })

                if response.status_code == 200:
                    user_data = response.json()

                    # Admin should see unmasked data
                    assert user_data['ssn'] == "123-45-6789"
                    assert user_data['credit_card'] == "4111-1111-1111-1111"
```

## Security Monitoring and Alerting Testing

### 1. Intrusion Detection Testing

```python
# tests/security/test_intrusion_detection.py
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestIntrusionDetection:
    """Test intrusion detection and alerting."""

    def test_suspicious_login_pattern_detection(self):
        """Test detection of suspicious login patterns."""
        # Simulate rapid login attempts from same IP
        responses = []
        for i in range(10):
            response = client.post("/auth/login", data={
                "username": f"user{i}@example.com",
                "password": "password123"
            })
            responses.append(response)

        # Should trigger rate limiting or alerting
        # Last attempts should be blocked
        assert any(r.status_code == 429 for r in responses[-3:])

    def test_privilege_escalation_attempt_detection(self):
        """Test detection of privilege escalation attempts."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.roles = ["user"]

            # Monitor multiple admin endpoint access attempts
            admin_endpoints = [
                "/admin/dashboard",
                "/admin/users",
                "/admin/system-config",
                "/admin/logs",
                "/admin/security"
            ]

            forbidden_responses = 0
            for endpoint in admin_endpoints:
                response = client.get(endpoint, headers={
                    "Authorization": "Bearer user_token"
                })
                if response.status_code == 403:
                    forbidden_responses += 1

            # All should be forbidden and logged as suspicious activity
            assert forbidden_responses == len(admin_endpoints)

    def test_anomalous_access_pattern_detection(self):
        """Test detection of anomalous access patterns."""
        with patch("src.core.auth.get_current_user") as mock_auth:
            mock_auth.return_value.id = "user-123"

            # Simulate access from unusual location/time
            unusual_context = {
                "client_ip": "1.2.3.4",  # Foreign IP
                "user_agent": "Automated Bot",
                "access_time": "03:00"  # Unusual hour
            }

            with patch("src.core.security.monitor_access") as mock_monitor:
                response = client.get("/users/profile", headers={
                    "Authorization": "Bearer user_token",
                    "X-Forwarded-For": unusual_context["client_ip"],
                    "User-Agent": unusual_context["user_agent"]
                })

                # Should trigger security monitoring
                mock_monitor.assert_called()

class TestSecurityAlerting:
    """Test security alerting mechanisms."""

    @pytest.mark.asyncio
    async def test_critical_security_event_alerting(self):
        """Test alerting for critical security events."""
        with patch("src.core.alerts.SecurityAlerter.send_alert") as mock_alert:
            # Simulate critical security event
            critical_events = [
                "multiple_failed_admin_access",
                "privilege_escalation_attempt",
                "data_breach_attempt",
                "sql_injection_attempt"
            ]

            for event in critical_events:
                # Trigger each type of event
                await trigger_security_event(event)

            # Should send alerts for all critical events
            assert mock_alert.call_count == len(critical_events)

    @pytest.mark.asyncio
    async def test_security_alert_rate_limiting(self):
        """Test that security alerts are rate limited to prevent spam."""
        with patch("src.core.alerts.SecurityAlerter.send_alert") as mock_alert:
            # Trigger many identical events
            for i in range(20):
                await trigger_security_event("failed_login")

            # Should not send 20 alerts - should be rate limited
            assert mock_alert.call_count < 20

async def trigger_security_event(event_type: str):
    """Helper function to trigger security events."""
    # Implementation would depend on your security monitoring system
    pass
```

## Security Configuration Testing

### 1. CORS and Security Headers Testing

```python
# tests/security/test_security_headers.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestSecurityHeaders:
    """Test security headers configuration."""

    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        response = client.get("/health")

        # Check for important security headers
        headers = response.headers

        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]

        assert "X-XSS-Protection" in headers
        assert headers["X-XSS-Protection"] == "1; mode=block"

        if "Strict-Transport-Security" in headers:
            assert "max-age=" in headers["Strict-Transport-Security"]

    def test_cors_configuration(self):
        """Test CORS configuration."""
        # Test preflight request
        response = client.options("/api/v1/users/",
            headers={
                "Origin": "https://allowed-domain.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization"
            }
        )

        # Should allow configured origins
        cors_headers = response.headers
        assert "Access-Control-Allow-Origin" in cors_headers

        # Test disallowed origin
        response = client.options("/api/v1/users/",
            headers={
                "Origin": "https://malicious-domain.com",
                "Access-Control-Request-Method": "POST"
            }
        )

        # Should not allow unconfigured origins
        # (exact behavior depends on CORS configuration)

    def test_content_security_policy(self):
        """Test Content Security Policy headers."""
        response = client.get("/")

        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]

            # Should have restrictive CSP
            assert "default-src 'self'" in csp or "default-src 'none'" in csp

            # Should not allow unsafe inline scripts
            assert "'unsafe-inline'" not in csp or "script-src" in csp

class TestHTTPS:
    """Test HTTPS configuration."""

    def test_https_redirect(self):
        """Test that HTTP requests are redirected to HTTPS."""
        # This test would be relevant in production environment
        # with actual HTTPS configuration
        pass

    def test_secure_cookies(self):
        """Test that cookies are marked as secure."""
        response = client.post("/auth/login", data={
            "username": "user@example.com",
            "password": "password123"
        })

        # Check cookie security flags
        set_cookie_headers = response.headers.get_list("set-cookie")
        for cookie_header in set_cookie_headers:
            if "session" in cookie_header.lower():
                # Session cookies should be secure
                assert "Secure" in cookie_header
                assert "HttpOnly" in cookie_header
                assert "SameSite" in cookie_header
```

## Security Test Automation

### 1. Security Test Pipeline

```python
# tests/security/security_test_suite.py
import pytest
import subprocess
import json
from typing import List, Dict

class SecurityTestSuite:
    """Automated security test suite."""

    def __init__(self):
        self.results = []

    def run_static_analysis(self) -> Dict:
        """Run static security analysis tools."""
        results = {}

        # Run Bandit for Python security issues
        try:
            bandit_result = subprocess.run([
                "bandit", "-r", "src/", "-f", "json"
            ], capture_output=True, text=True)

            if bandit_result.returncode == 0:
                results["bandit"] = json.loads(bandit_result.stdout)
            else:
                results["bandit"] = {"error": bandit_result.stderr}
        except Exception as e:
            results["bandit"] = {"error": str(e)}

        # Run Safety for dependency vulnerabilities
        try:
            safety_result = subprocess.run([
                "safety", "check", "--json"
            ], capture_output=True, text=True)

            results["safety"] = json.loads(safety_result.stdout)
        except Exception as e:
            results["safety"] = {"error": str(e)}

        return results

    def run_dependency_scan(self) -> Dict:
        """Scan dependencies for known vulnerabilities."""
        try:
            # Use pip-audit or similar tool
            audit_result = subprocess.run([
                "pip-audit", "--format=json"
            ], capture_output=True, text=True)

            return json.loads(audit_result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def run_container_security_scan(self) -> Dict:
        """Scan container for security issues."""
        try:
            # Use Docker security scanning
            scan_result = subprocess.run([
                "docker", "scan", "myapp:latest", "--json"
            ], capture_output=True, text=True)

            return json.loads(scan_result.stdout)
        except Exception as e:
            return {"error": str(e)}

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "static_analysis": self.run_static_analysis(),
            "dependency_scan": self.run_dependency_scan(),
            "container_scan": self.run_container_security_scan(),
            "test_results": self.results
        }

        # Calculate security score
        report["security_score"] = self.calculate_security_score(report)

        return report

    def calculate_security_score(self, report: Dict) -> int:
        """Calculate overall security score."""
        score = 100

        # Deduct points for issues found
        static_issues = len(report.get("static_analysis", {}).get("results", []))
        dependency_issues = len(report.get("dependency_scan", []))

        score -= min(static_issues * 5, 30)  # Max 30 points deduction
        score -= min(dependency_issues * 10, 40)  # Max 40 points deduction

        return max(score, 0)

# Pytest integration
@pytest.fixture(scope="session")
def security_test_suite():
    return SecurityTestSuite()

def test_run_security_suite(security_test_suite):
    """Run complete security test suite."""
    report = security_test_suite.generate_security_report()

    # Assert minimum security score
    assert report["security_score"] >= 80, f"Security score too low: {report['security_score']}"

    # Assert no critical vulnerabilities
    critical_issues = []
    for tool_result in report.values():
        if isinstance(tool_result, dict) and "results" in tool_result:
            critical_issues.extend([
                issue for issue in tool_result["results"]
                if issue.get("severity") == "critical"
            ])

    assert len(critical_issues) == 0, f"Critical security issues found: {critical_issues}"
```

## Related Documents

- `docs/atomic/security/authentication-guide.md` - Authentication implementation
- `docs/atomic/security/authorization-patterns.md` - Authorization patterns
- `docs/atomic/services/fastapi/security-patterns.md` - FastAPI security basics
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` - FastAPI testing
- `docs/atomic/architecture/quality-standards.md` - Quality and security standards

## Security Testing Checklist

### Authentication Testing
- [ ] Valid JWT token acceptance
- [ ] Expired token rejection
- [ ] Malformed token rejection
- [ ] Wrong secret detection
- [ ] Missing claims handling
- [ ] Refresh token validation
- [ ] Login rate limiting
- [ ] Timing attack resistance
- [ ] Brute force protection
- [ ] Session fixation protection
- [ ] Session regeneration on privilege change
- [ ] Concurrent session limits

### Authorization Testing
- [ ] Role-based access control
- [ ] Permission inheritance
- [ ] Horizontal privilege escalation protection
- [ ] Vertical privilege escalation protection
- [ ] JWT role manipulation protection
- [ ] Resource-based authorization
- [ ] Context-aware authorization
- [ ] Policy evaluation order
- [ ] Policy injection protection
- [ ] Condition bypass protection

### Input Validation Testing
- [ ] SQL injection protection
- [ ] NoSQL injection protection
- [ ] XSS protection (stored and reflected)
- [ ] CSRF protection
- [ ] Input sanitization
- [ ] File upload validation
- [ ] Parameter pollution protection

### Data Protection Testing
- [ ] Sensitive data encryption
- [ ] Password hashing
- [ ] Data masking in responses
- [ ] Database encryption at rest
- [ ] Transmission encryption
- [ ] Key management security

### Security Configuration Testing
- [ ] Security headers present
- [ ] CORS configuration
- [ ] Content Security Policy
- [ ] HTTPS enforcement
- [ ] Secure cookies
- [ ] Security monitoring
- [ ] Intrusion detection
- [ ] Alert rate limiting

### Automated Security Testing
- [ ] Static analysis integration
- [ ] Dependency vulnerability scanning
- [ ] Container security scanning
- [ ] Security test automation
- [ ] Continuous security monitoring
- [ ] Security score calculation