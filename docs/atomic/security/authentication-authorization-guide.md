# Authentication & Authorization Guide

Comprehensive guide for implementing authentication and authorization in microservices using FastAPI, JWT tokens, and Redis.

## Prerequisites

- FastAPI service setup ([FastAPI Basic Setup](../services/fastapi/basic-setup.md))
- Redis integration ([Redis Connection Management](../integrations/redis/connection-management.md))
- Understanding of JWT concepts

## JWT Implementation with FastAPI

### Token Structure

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel

class TokenData(BaseModel):
    user_id: str
    username: str
    roles: list[str]
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for blacklisting

class AuthConfig:
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

### Token Generation Service

```python
import uuid
from datetime import datetime, timedelta
import jwt
import redis.asyncio as redis

class TokenService:
    def __init__(self, redis_client: redis.Redis, config: AuthConfig):
        self.redis = redis_client
        self.config = config

    async def create_access_token(
        self,
        user_id: str,
        username: str,
        roles: list[str]
    ) -> str:
        now = datetime.utcnow()
        jti = str(uuid.uuid4())

        payload = {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "exp": now + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now,
            "jti": jti,
            "type": "access"
        }

        token = jwt.encode(payload, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)

        # Store in Redis for tracking
        await self.redis.setex(
            f"token:access:{jti}",
            self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id
        )

        return token

    async def create_refresh_token(self, user_id: str) -> str:
        now = datetime.utcnow()
        jti = str(uuid.uuid4())

        payload = {
            "user_id": user_id,
            "exp": now + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now,
            "jti": jti,
            "type": "refresh"
        }

        token = jwt.encode(payload, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)

        # Store in Redis
        await self.redis.setex(
            f"token:refresh:{jti}",
            self.config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            user_id
        )

        return token

    async def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM]
            )

            if payload.get("type") != token_type:
                return None

            jti = payload.get("jti")
            if not jti:
                return None

            # Check if token is blacklisted
            if await self.redis.get(f"blacklist:{jti}"):
                return None

            # Check if token exists in Redis
            stored_user_id = await self.redis.get(f"token:{token_type}:{jti}")
            if not stored_user_id:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def blacklist_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
                options={"verify_exp": False}
            )

            jti = payload.get("jti")
            if jti:
                # Add to blacklist with remaining TTL
                exp = payload.get("exp", 0)
                current_time = datetime.utcnow().timestamp()
                ttl = max(int(exp - current_time), 1)

                await self.redis.setex(f"blacklist:{jti}", ttl, "1")

        except jwt.InvalidTokenError:
            pass
```

## RBAC Patterns and Examples

### Role Definition

```python
from enum import Enum
from typing import Set

class Permission(Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_ORDERS = "read:orders"
    WRITE_ORDERS = "write:orders"
    ADMIN_ACCESS = "admin:access"

class Role(Enum):
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    Role.GUEST: {Permission.READ_ORDERS},
    Role.USER: {
        Permission.READ_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS
    },
    Role.MODERATOR: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
    },
    Role.ADMIN: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_ORDERS,
        Permission.WRITE_ORDERS,
        Permission.ADMIN_ACCESS,
    }
}

def get_permissions_for_roles(roles: list[str]) -> Set[Permission]:
    permissions = set()
    for role_str in roles:
        try:
            role = Role(role_str)
            permissions.update(ROLE_PERMISSIONS.get(role, set()))
        except ValueError:
            continue
    return permissions
```

### Authorization Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class AuthDependency:
    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        token = credentials.credentials
        payload = await self.token_service.verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    def require_permissions(self, required_permissions: Set[Permission]):
        async def permission_checker(
            current_user: dict = Depends(self.get_current_user)
        ):
            user_roles = current_user.get("roles", [])
            user_permissions = get_permissions_for_roles(user_roles)

            if not required_permissions.issubset(user_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

            return current_user

        return permission_checker

    def require_roles(self, required_roles: Set[Role]):
        async def role_checker(
            current_user: dict = Depends(self.get_current_user)
        ):
            user_roles = {Role(role) for role in current_user.get("roles", []) if role in [r.value for r in Role]}

            if not required_roles.intersection(user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role privileges"
                )

            return current_user

        return role_checker
```

## Session Management with Redis

### Session Storage

```python
import json
from datetime import timedelta

class SessionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_ttl = timedelta(hours=24)

    async def create_session(self, user_id: str, session_data: dict) -> str:
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"

        session_payload = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            **session_data
        }

        await self.redis.setex(
            session_key,
            int(self.session_ttl.total_seconds()),
            json.dumps(session_payload)
        )

        # Track active sessions for user
        await self.redis.sadd(f"user_sessions:{user_id}", session_id)
        await self.redis.expire(f"user_sessions:{user_id}", int(self.session_ttl.total_seconds()))

        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        session_data = await self.redis.get(f"session:{session_id}")

        if not session_data:
            return None

        session = json.loads(session_data)

        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()
        await self.redis.setex(
            f"session:{session_id}",
            int(self.session_ttl.total_seconds()),
            json.dumps(session)
        )

        return session

    async def invalidate_session(self, session_id: str):
        session_data = await self.redis.get(f"session:{session_id}")
        if session_data:
            session = json.loads(session_data)
            user_id = session.get("user_id")

            if user_id:
                await self.redis.srem(f"user_sessions:{user_id}", session_id)

        await self.redis.delete(f"session:{session_id}")

    async def invalidate_all_user_sessions(self, user_id: str):
        session_ids = await self.redis.smembers(f"user_sessions:{user_id}")

        for session_id in session_ids:
            await self.redis.delete(f"session:{session_id}")

        await self.redis.delete(f"user_sessions:{user_id}")
```

## MFA Integration Examples

### TOTP Implementation

```python
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def generate_secret(self, user_id: str) -> str:
        secret = pyotp.random_base32()
        return secret

    async def setup_totp(self, user_id: str, app_name: str = "YourApp") -> dict:
        secret = self.generate_secret(user_id)

        # Store temporary secret (not confirmed yet)
        await self.redis.setex(
            f"mfa_setup:{user_id}",
            300,  # 5 minutes
            secret
        )

        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name=app_name
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "secret": secret,
            "qr_code": qr_code_base64,
            "totp_uri": totp_uri
        }

    async def confirm_totp_setup(self, user_id: str, verification_code: str) -> bool:
        secret = await self.redis.get(f"mfa_setup:{user_id}")

        if not secret:
            return False

        totp = pyotp.TOTP(secret)

        if totp.verify(verification_code, valid_window=1):
            # Save confirmed secret
            await self.redis.set(f"mfa_secret:{user_id}", secret)
            # Remove setup secret
            await self.redis.delete(f"mfa_setup:{user_id}")
            return True

        return False

    async def verify_totp(self, user_id: str, verification_code: str) -> bool:
        secret = await self.redis.get(f"mfa_secret:{user_id}")

        if not secret:
            return False

        totp = pyotp.TOTP(secret)
        return totp.verify(verification_code, valid_window=1)

    async def is_mfa_enabled(self, user_id: str) -> bool:
        secret = await self.redis.get(f"mfa_secret:{user_id}")
        return secret is not None
```

## FastAPI Integration

### Complete Authentication Setup

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Secure Microservice")

# Initialize services
auth_config = AuthConfig()
redis_client = redis.from_url("redis://localhost:6379/0")
token_service = TokenService(redis_client, auth_config)
session_manager = SessionManager(redis_client)
mfa_service = MFAService(redis_client)
auth_dependency = AuthDependency(token_service)

# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Validate user credentials (implement your user validation)
    user = await validate_user_credentials(credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check if MFA is enabled
    if await mfa_service.is_mfa_enabled(user.id):
        # Return temporary token for MFA verification
        temp_token = await token_service.create_access_token(
            user_id=user.id,
            username=user.username,
            roles=["mfa_pending"]
        )
        return {"requires_mfa": True, "temp_token": temp_token}

    # Create full access tokens
    access_token = await token_service.create_access_token(
        user_id=user.id,
        username=user.username,
        roles=user.roles
    )
    refresh_token = await token_service.create_refresh_token(user.id)

    # Create session
    session_id = await session_manager.create_session(
        user_id=user.id,
        session_data={"ip": "request.client.host", "user_agent": "request.headers.get('user-agent')"}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_id": session_id,
        "token_type": "bearer"
    }

@app.post("/auth/verify-mfa")
async def verify_mfa(
    mfa_request: MFAVerificationRequest,
    temp_user: dict = Depends(auth_dependency.require_roles({Role.GUEST}))
):
    user_id = temp_user["user_id"]

    if not await mfa_service.verify_totp(user_id, mfa_request.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    # Get full user data and create proper tokens
    user = await get_user_by_id(user_id)

    access_token = await token_service.create_access_token(
        user_id=user.id,
        username=user.username,
        roles=user.roles
    )
    refresh_token = await token_service.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Protected endpoint example
@app.get("/users/profile")
async def get_profile(
    current_user: dict = Depends(auth_dependency.require_permissions({Permission.READ_USERS}))
):
    return {"user_id": current_user["user_id"], "username": current_user["username"]}

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(auth_dependency.require_permissions({Permission.DELETE_USERS}))
):
    # Implement user deletion
    return {"message": f"User {user_id} deleted by {current_user['username']}"}
```

## Related Documentation

- [FastAPI Security Patterns](../services/fastapi/security-patterns.md)
- [Redis Integration Guide](../integrations/redis/connection-management.md)
- [Session Management Patterns](session-management-patterns.md)
- [Security Testing Guide](security-testing-guide.md)

## Best Practices

1. **Token Security**:
   - Use strong, randomly generated secrets
   - Implement proper token rotation
   - Store tokens securely in Redis with appropriate TTL

2. **Role-Based Access**:
   - Design granular permissions
   - Use principle of least privilege
   - Implement role inheritance when appropriate

3. **Session Management**:
   - Track active sessions per user
   - Implement session invalidation on security events
   - Monitor for concurrent sessions

4. **MFA Implementation**:
   - Provide backup codes for recovery
   - Implement rate limiting for MFA attempts
   - Use secure secret storage

5. **Monitoring and Logging**:
   - Log all authentication attempts
   - Monitor for brute force attacks
   - Track session anomalies

## Related Documents

- `docs/atomic/security/session-management-patterns.md` — Session handling
- `docs/atomic/services/fastapi/security-patterns.md` — FastAPI security
- `docs/atomic/infrastructure/secrets-management.md` — Secret storage
- `docs/atomic/security/security-testing-guide.md` — Security testing
