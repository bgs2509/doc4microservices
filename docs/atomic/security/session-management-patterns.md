# Session Management Patterns

Advanced session management strategies for microservices with Redis and distributed environments.

## Prerequisites

- [Redis Connection Management](../integrations/redis/connection-management.md)
- [Authentication & Authorization Guide](authentication-authorization-guide.md)
- Understanding of distributed systems concepts

## Session Storage Strategies

### Redis-Based Session Store

```python
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import redis.asyncio as redis

class DistributedSessionManager:
    def __init__(
        self,
        redis_client: redis.Redis,
        default_ttl: timedelta = timedelta(hours=24),
        max_sessions_per_user: int = 5
    ):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.max_sessions_per_user = max_sessions_per_user

    async def create_session(
        self,
        user_id: str,
        session_data: Dict,
        ttl: Optional[timedelta] = None
    ) -> str:
        session_id = str(uuid.uuid4())
        session_ttl = ttl or self.default_ttl

        # Enforce session limit
        await self._enforce_session_limit(user_id)

        session_payload = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + session_ttl).isoformat(),
            "ip_address": session_data.get("ip_address"),
            "user_agent": session_data.get("user_agent"),
            "device_fingerprint": session_data.get("device_fingerprint"),
            "metadata": session_data.get("metadata", {})
        }

        # Store session data
        session_key = f"session:{session_id}"
        await self.redis.setex(
            session_key,
            int(session_ttl.total_seconds()),
            json.dumps(session_payload)
        )

        # Add to user's active sessions
        user_sessions_key = f"user_sessions:{user_id}"
        await self.redis.sadd(user_sessions_key, session_id)
        await self.redis.expire(user_sessions_key, int(session_ttl.total_seconds()))

        # Track session creation
        await self._track_session_event(session_id, "created", session_data)

        return session_id

    async def get_session(
        self,
        session_id: str,
        update_activity: bool = True
    ) -> Optional[Dict]:
        session_key = f"session:{session_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return None

        session = json.loads(session_data)

        # Check if session is expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.invalidate_session(session_id)
            return None

        if update_activity:
            # Update last activity
            session["last_activity"] = datetime.utcnow().isoformat()
            await self.redis.setex(
                session_key,
                int(self.default_ttl.total_seconds()),
                json.dumps(session)
            )

            await self._track_session_event(session_id, "activity_updated")

        return session

    async def update_session(
        self,
        session_id: str,
        updates: Dict
    ) -> bool:
        session = await self.get_session(session_id, update_activity=False)

        if not session:
            return False

        # Update session data
        session["metadata"].update(updates.get("metadata", {}))

        # Update other allowed fields
        allowed_updates = ["ip_address", "user_agent", "device_fingerprint"]
        for field in allowed_updates:
            if field in updates:
                session[field] = updates[field]

        session["last_activity"] = datetime.utcnow().isoformat()

        session_key = f"session:{session_id}"
        await self.redis.setex(
            session_key,
            int(self.default_ttl.total_seconds()),
            json.dumps(session)
        )

        await self._track_session_event(session_id, "updated", updates)
        return True

    async def invalidate_session(self, session_id: str) -> bool:
        session = await self.get_session(session_id, update_activity=False)

        if not session:
            return False

        user_id = session["user_id"]

        # Remove from user's active sessions
        await self.redis.srem(f"user_sessions:{user_id}", session_id)

        # Delete session data
        await self.redis.delete(f"session:{session_id}")

        await self._track_session_event(session_id, "invalidated")
        return True

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)

        count = 0
        for session_id in session_ids:
            if await self.invalidate_session(session_id):
                count += 1

        await self.redis.delete(user_sessions_key)
        await self._track_session_event(None, "all_user_sessions_invalidated", {"user_id": user_id})

        return count

    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session = await self.get_session(session_id, update_activity=False)
            if session:
                sessions.append(session)

        return sorted(sessions, key=lambda x: x["last_activity"], reverse=True)

    async def _enforce_session_limit(self, user_id: str):
        sessions = await self.get_user_sessions(user_id)

        if len(sessions) >= self.max_sessions_per_user:
            # Remove oldest sessions
            sessions_to_remove = len(sessions) - self.max_sessions_per_user + 1
            oldest_sessions = sorted(sessions, key=lambda x: x["last_activity"])

            for session in oldest_sessions[:sessions_to_remove]:
                await self.invalidate_session(session["session_id"])

    async def _track_session_event(
        self,
        session_id: Optional[str],
        event_type: str,
        event_data: Optional[Dict] = None
    ):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "event_type": event_type,
            "data": event_data or {}
        }

        # Store in audit log (implement according to your logging strategy)
        audit_key = f"session_audit:{datetime.utcnow().strftime('%Y-%m-%d')}"
        await self.redis.lpush(audit_key, json.dumps(event))
        await self.redis.expire(audit_key, 7 * 24 * 60 * 60)  # Keep for 7 days
```

## Session Security Patterns

### Concurrent Session Detection

```python
class SessionSecurityManager:
    def __init__(self, session_manager: DistributedSessionManager):
        self.session_manager = session_manager

    async def detect_concurrent_sessions(
        self,
        user_id: str,
        current_session_id: str
    ) -> Dict:
        sessions = await self.session_manager.get_user_sessions(user_id)

        other_sessions = [s for s in sessions if s["session_id"] != current_session_id]
        concurrent_count = len(other_sessions)

        if concurrent_count > 0:
            # Check for suspicious patterns
            suspicious_patterns = await self._analyze_session_patterns(other_sessions)

            return {
                "concurrent_sessions": concurrent_count,
                "suspicious_activity": suspicious_patterns,
                "sessions": other_sessions
            }

        return {"concurrent_sessions": 0, "suspicious_activity": False}

    async def _analyze_session_patterns(self, sessions: List[Dict]) -> bool:
        # Check for multiple different IP addresses
        ip_addresses = set(s.get("ip_address") for s in sessions if s.get("ip_address"))

        # Check for multiple different user agents
        user_agents = set(s.get("user_agent") for s in sessions if s.get("user_agent"))

        # Check for rapid session creation
        creation_times = [
            datetime.fromisoformat(s["created_at"])
            for s in sessions
        ]

        if len(creation_times) > 1:
            time_diff = max(creation_times) - min(creation_times)
            rapid_creation = time_diff < timedelta(minutes=5)
        else:
            rapid_creation = False

        # Define suspicious criteria
        return (
            len(ip_addresses) > 2 or  # More than 2 different IPs
            len(user_agents) > 3 or   # More than 3 different user agents
            rapid_creation             # Rapid session creation
        )

    async def force_reauthentication(self, user_id: str, reason: str) -> bool:
        # Invalidate all sessions except current
        count = await self.session_manager.invalidate_all_user_sessions(user_id)

        # Log security event
        await self._log_security_event(user_id, "force_reauthentication", {
            "reason": reason,
            "sessions_invalidated": count
        })

        return count > 0

    async def _log_security_event(self, user_id: str, event_type: str, data: Dict):
        # Implement according to your security logging strategy
        pass
```

### Session Fingerprinting

```python
import hashlib
from typing import Dict

class SessionFingerprinting:
    @staticmethod
    def generate_device_fingerprint(request_data: Dict) -> str:
        """Generate a device fingerprint from request headers and metadata."""

        fingerprint_data = {
            "user_agent": request_data.get("user_agent", ""),
            "accept_language": request_data.get("accept_language", ""),
            "accept_encoding": request_data.get("accept_encoding", ""),
            "screen_resolution": request_data.get("screen_resolution", ""),
            "timezone": request_data.get("timezone", ""),
            "platform": request_data.get("platform", "")
        }

        # Create a consistent string representation
        fingerprint_string = "|".join(
            f"{k}:{v}" for k, v in sorted(fingerprint_data.items())
        )

        # Hash the fingerprint
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    @staticmethod
    def validate_fingerprint(
        stored_fingerprint: str,
        current_fingerprint: str,
        tolerance: float = 0.8
    ) -> bool:
        """Validate if current fingerprint matches stored one with tolerance."""

        if stored_fingerprint == current_fingerprint:
            return True

        # Calculate similarity (simple example)
        # In practice, you might want more sophisticated comparison
        return SessionFingerprinting._calculate_similarity(
            stored_fingerprint,
            current_fingerprint
        ) >= tolerance

    @staticmethod
    def _calculate_similarity(fp1: str, fp2: str) -> float:
        """Calculate similarity between two fingerprints."""
        # Simple character-based similarity
        if not fp1 or not fp2:
            return 0.0

        max_len = max(len(fp1), len(fp2))
        matches = sum(c1 == c2 for c1, c2 in zip(fp1, fp2))

        return matches / max_len
```

## Session Cleanup and Maintenance

### Automatic Session Cleanup

```python
import asyncio
from datetime import datetime, timedelta

class SessionCleanupService:
    def __init__(
        self,
        session_manager: DistributedSessionManager,
        cleanup_interval: timedelta = timedelta(hours=1)
    ):
        self.session_manager = session_manager
        self.cleanup_interval = cleanup_interval
        self.running = False

    async def start_cleanup_service(self):
        """Start the background cleanup service."""
        self.running = True

        while self.running:
            try:
                await self._cleanup_expired_sessions()
                await asyncio.sleep(self.cleanup_interval.total_seconds())
            except Exception as e:
                # Log error but continue running
                print(f"Session cleanup error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def stop_cleanup_service(self):
        """Stop the background cleanup service."""
        self.running = False

    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions and orphaned data."""

        # Find all session keys
        session_keys = []
        cursor = 0

        while True:
            cursor, keys = await self.session_manager.redis.scan(
                cursor=cursor,
                match="session:*",
                count=100
            )
            session_keys.extend(keys)

            if cursor == 0:
                break

        expired_count = 0
        orphaned_count = 0

        for key in session_keys:
            session_data = await self.session_manager.redis.get(key)

            if not session_data:
                continue

            try:
                session = json.loads(session_data)
                expires_at = datetime.fromisoformat(session["expires_at"])

                if datetime.utcnow() > expires_at:
                    session_id = session["session_id"]
                    await self.session_manager.invalidate_session(session_id)
                    expired_count += 1

            except (json.JSONDecodeError, KeyError, ValueError):
                # Malformed session data, remove it
                await self.session_manager.redis.delete(key)
                orphaned_count += 1

        if expired_count > 0 or orphaned_count > 0:
            print(f"Cleaned up {expired_count} expired and {orphaned_count} orphaned sessions")

    async def cleanup_user_session_sets(self):
        """Clean up user session sets that may have orphaned session IDs."""

        cursor = 0
        while True:
            cursor, keys = await self.session_manager.redis.scan(
                cursor=cursor,
                match="user_sessions:*",
                count=100
            )

            for key in keys:
                session_ids = await self.session_manager.redis.smembers(key)
                valid_sessions = []

                for session_id in session_ids:
                    session_exists = await self.session_manager.redis.exists(f"session:{session_id}")
                    if session_exists:
                        valid_sessions.append(session_id)
                    else:
                        # Remove orphaned session ID
                        await self.session_manager.redis.srem(key, session_id)

                # If no valid sessions remain, delete the set
                if not valid_sessions:
                    await self.session_manager.redis.delete(key)

            if cursor == 0:
                break
```

## FastAPI Integration

### Session Middleware

```python
from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        session_manager: DistributedSessionManager,
        security_manager: SessionSecurityManager
    ):
        super().__init__(app)
        self.session_manager = session_manager
        self.security_manager = security_manager

    async def dispatch(self, request: Request, call_next):
        # Extract session ID from header or cookie
        session_id = request.headers.get("X-Session-ID") or request.cookies.get("session_id")

        if session_id:
            session = await self.session_manager.get_session(session_id)

            if session:
                request.state.session = session
                request.state.user_id = session["user_id"]

                # Check for suspicious activity
                security_check = await self.security_manager.detect_concurrent_sessions(
                    session["user_id"],
                    session_id
                )

                if security_check["suspicious_activity"]:
                    # Log and potentially require re-authentication
                    request.state.requires_security_check = True
            else:
                request.state.session = None
        else:
            request.state.session = None

        response = await call_next(request)
        return response

# Usage in FastAPI app
from fastapi import FastAPI, Depends

app = FastAPI()

# Initialize services
session_manager = DistributedSessionManager(redis_client)
security_manager = SessionSecurityManager(session_manager)

# Add middleware
app.add_middleware(SessionMiddleware, session_manager, security_manager)

def get_current_session(request: Request) -> Optional[Dict]:
    return getattr(request.state, "session", None)

def require_session(request: Request) -> Dict:
    session = get_current_session(request)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid session required"
        )
    return session

@app.get("/profile")
async def get_profile(session: Dict = Depends(require_session)):
    return {"user_id": session["user_id"], "session_id": session["session_id"]}

@app.post("/logout")
async def logout(session: Dict = Depends(require_session)):
    await session_manager.invalidate_session(session["session_id"])
    return {"message": "Successfully logged out"}

@app.get("/sessions")
async def get_user_sessions(session: Dict = Depends(require_session)):
    sessions = await session_manager.get_user_sessions(session["user_id"])
    return {"sessions": sessions}
```

## Related Documentation

- [Authentication & Authorization Guide](authentication-authorization-guide.md)
- [Redis Integration Guide](../integrations/redis/connection-management.md)
- [Security Testing Guide](security-testing-guide.md)

## Best Practices

1. **Session Storage**:
   - Use Redis for distributed session storage
   - Implement proper TTL management
   - Store minimal session data

2. **Security**:
   - Generate unique session IDs
   - Implement session fingerprinting
   - Monitor for concurrent sessions

3. **Performance**:
   - Use connection pooling for Redis
   - Implement efficient cleanup processes
   - Cache frequently accessed session data

4. **Monitoring**:
   - Track session creation and invalidation
   - Monitor for suspicious patterns
   - Log security-related events