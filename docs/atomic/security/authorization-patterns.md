# Authorization Patterns

Advanced authorization patterns and implementations for microservices architecture following the Improved Hybrid Approach.

## Overview

Authorization patterns define how permissions and access control are implemented across business and data services. This document covers advanced RBAC, ABAC, and resource-based authorization patterns.

## Advanced RBAC Patterns

### 1. Hierarchical Roles

```python
# src/core/rbac.py
from typing import Dict, Set, List
from enum import Enum

class RoleHierarchy:
    """Hierarchical role management with inheritance."""

    def __init__(self):
        self.hierarchy = {
            "super_admin": ["admin", "moderator", "user"],
            "admin": ["moderator", "user"],
            "moderator": ["user"],
            "user": []
        }

        self.role_permissions = {
            "super_admin": {"*"},  # All permissions
            "admin": {
                "user:create", "user:read", "user:update", "user:delete",
                "content:manage", "reports:view", "system:configure"
            },
            "moderator": {
                "user:read", "content:manage", "content:moderate"
            },
            "user": {
                "user:read_own", "content:create", "content:read"
            }
        }

    def get_effective_permissions(self, roles: List[str]) -> Set[str]:
        """Get all permissions including inherited from role hierarchy."""
        effective_permissions = set()

        for role in roles:
            # Add direct permissions
            if role in self.role_permissions:
                effective_permissions.update(self.role_permissions[role])

            # Add inherited permissions
            inherited_roles = self.hierarchy.get(role, [])
            for inherited_role in inherited_roles:
                if inherited_role in self.role_permissions:
                    effective_permissions.update(self.role_permissions[inherited_role])

        return effective_permissions

    def has_permission(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission through roles."""
        effective_permissions = self.get_effective_permissions(user_roles)

        # Check for wildcard permission
        if "*" in effective_permissions:
            return True

        # Check for exact permission
        if required_permission in effective_permissions:
            return True

        # Check for wildcard patterns
        for permission in effective_permissions:
            if permission.endswith(":*"):
                permission_prefix = permission[:-2]
                if required_permission.startswith(permission_prefix + ":"):
                    return True

        return False

# Dependency injection for role hierarchy
role_hierarchy = RoleHierarchy()

def get_role_hierarchy() -> RoleHierarchy:
    return role_hierarchy
```

### 2. Context-Aware Authorization

```python
# src/core/context_auth.py
from typing import Dict, Any, Optional
from dataclasses import dataclass
from fastapi import Request, Depends
from src.core.auth import get_current_user
from src.core.models import CurrentUser

@dataclass
class AuthorizationContext:
    """Authorization context with request and resource information."""
    user: CurrentUser
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    request: Optional[Request] = None
    additional_context: Optional[Dict[str, Any]] = None

class ContextualAuthorizer:
    """Context-aware authorization engine."""

    def __init__(self, role_hierarchy: RoleHierarchy):
        self.role_hierarchy = role_hierarchy
        self.resource_policies = {}
        self.register_default_policies()

    def register_default_policies(self):
        """Register default resource-based policies."""

        # User resource policies
        self.resource_policies["user"] = {
            "read": self._user_read_policy,
            "update": self._user_update_policy,
            "delete": self._user_delete_policy
        }

        # Content resource policies
        self.resource_policies["content"] = {
            "read": self._content_read_policy,
            "update": self._content_update_policy,
            "delete": self._content_delete_policy
        }

    async def authorize(self, context: AuthorizationContext) -> bool:
        """Main authorization method."""

        # Check role-based permissions first
        permission = f"{context.resource_type}:{context.action}"
        if self.role_hierarchy.has_permission(context.user.roles, permission):
            return True

        # Check resource-specific policies
        if context.resource_type in self.resource_policies:
            resource_policies = self.resource_policies[context.resource_type]
            if context.action in resource_policies:
                policy_func = resource_policies[context.action]
                return await policy_func(context)

        return False

    async def _user_read_policy(self, context: AuthorizationContext) -> bool:
        """User read policy - can read own profile or with user:read permission."""
        if context.resource_id == context.user.id:
            return True
        return self.role_hierarchy.has_permission(context.user.roles, "user:read")

    async def _user_update_policy(self, context: AuthorizationContext) -> bool:
        """User update policy - can update own profile or with user:update permission."""
        if context.resource_id == context.user.id:
            return True
        return self.role_hierarchy.has_permission(context.user.roles, "user:update")

    async def _user_delete_policy(self, context: AuthorizationContext) -> bool:
        """User delete policy - only with user:delete permission."""
        return self.role_hierarchy.has_permission(context.user.roles, "user:delete")

    async def _content_read_policy(self, context: AuthorizationContext) -> bool:
        """Content read policy - public content or own content."""
        # Get content metadata (implement based on your data service)
        content_data = await self._get_content_metadata(context.resource_id)

        if content_data.get("is_public"):
            return True

        if content_data.get("owner_id") == context.user.id:
            return True

        return self.role_hierarchy.has_permission(context.user.roles, "content:read_all")

    async def _content_update_policy(self, context: AuthorizationContext) -> bool:
        """Content update policy - owner or content:manage permission."""
        content_data = await self._get_content_metadata(context.resource_id)

        if content_data.get("owner_id") == context.user.id:
            return True

        return self.role_hierarchy.has_permission(context.user.roles, "content:manage")

    async def _content_delete_policy(self, context: AuthorizationContext) -> bool:
        """Content delete policy - owner or content:manage permission."""
        return await self._content_update_policy(context)

    async def _get_content_metadata(self, content_id: str) -> Dict[str, Any]:
        """Get content metadata from data service."""
        # Implement call to data service
        # This is a placeholder - implement according to your data service API
        return {
            "id": content_id,
            "owner_id": "some-user-id",
            "is_public": False
        }

# Dependency for contextual authorizer
def get_contextual_authorizer(
    role_hierarchy: RoleHierarchy = Depends(get_role_hierarchy)
) -> ContextualAuthorizer:
    return ContextualAuthorizer(role_hierarchy)
```

### 3. Resource-Based Authorization Decorator

```python
# src/core/decorators.py
from functools import wraps
from typing import Callable, Optional
from fastapi import Depends, HTTPException, status, Request
from src.core.context_auth import AuthorizationContext, ContextualAuthorizer, get_contextual_authorizer
from src.core.auth import get_current_user
from src.core.models import CurrentUser

def authorize_resource(
    resource_type: str,
    action: str,
    resource_id_param: str = "resource_id"
):
    """Decorator for resource-based authorization."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from kwargs
            current_user = None
            authorizer = None
            request = None

            for key, value in kwargs.items():
                if isinstance(value, CurrentUser):
                    current_user = value
                elif isinstance(value, ContextualAuthorizer):
                    authorizer = value
                elif isinstance(value, Request):
                    request = value

            if not current_user or not authorizer:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authorization dependencies not found"
                )

            # Get resource ID from path parameters
            resource_id = kwargs.get(resource_id_param)

            # Create authorization context
            context = AuthorizationContext(
                user=current_user,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                request=request
            )

            # Check authorization
            if not await authorizer.authorize(context):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions for {action} on {resource_type}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Attribute-Based Access Control (ABAC)

### 1. Policy Engine

```python
# src/core/abac.py
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class ABACAttribute:
    """ABAC attribute definition."""
    name: str
    value: Any
    type: str  # "user", "resource", "environment", "action"

@dataclass
class ABACPolicy:
    """ABAC policy definition."""
    id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    effect: str  # "allow" or "deny"
    priority: int = 0

class ABACEngine:
    """Attribute-Based Access Control engine."""

    def __init__(self):
        self.policies: List[ABACPolicy] = []
        self.attribute_providers = {}
        self.register_default_providers()

    def register_default_providers(self):
        """Register default attribute providers."""
        self.attribute_providers.update({
            "user.roles": self._get_user_roles,
            "user.department": self._get_user_department,
            "user.clearance_level": self._get_user_clearance,
            "resource.owner": self._get_resource_owner,
            "resource.classification": self._get_resource_classification,
            "environment.time": self._get_current_time,
            "environment.location": self._get_user_location,
            "environment.network": self._get_network_info
        })

    def add_policy(self, policy: ABACPolicy):
        """Add ABAC policy."""
        self.policies.append(policy)
        # Sort by priority (higher priority first)
        self.policies.sort(key=lambda p: p.priority, reverse=True)

    async def evaluate(
        self,
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """Evaluate ABAC policies."""

        # Collect all attributes
        attributes = await self._collect_attributes(
            user, resource_type, resource_id, action, context or {}
        )

        # Evaluate policies in priority order
        for policy in self.policies:
            result = await self._evaluate_policy(policy, attributes)
            if result is not None:
                return result == "allow"

        # Default deny
        return False

    async def _collect_attributes(
        self,
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect all attributes from providers."""

        attributes = {
            # User attributes
            "user.id": user.id,
            "user.email": user.email,
            "user.roles": user.roles,

            # Resource attributes
            "resource.type": resource_type,
            "resource.id": resource_id,

            # Action attributes
            "action.name": action,

            # Environment attributes
            "environment.timestamp": datetime.utcnow().isoformat(),

            # Context attributes
            **{f"context.{k}": v for k, v in context.items()}
        }

        # Call attribute providers
        for attr_name, provider in self.attribute_providers.items():
            try:
                attributes[attr_name] = await provider(user, resource_id, context)
            except Exception as e:
                # Log error but continue
                attributes[attr_name] = None

        return attributes

    async def _evaluate_policy(
        self,
        policy: ABACPolicy,
        attributes: Dict[str, Any]
    ) -> Optional[str]:
        """Evaluate single policy against attributes."""

        for condition in policy.conditions:
            if not await self._evaluate_condition(condition, attributes):
                return None  # Policy doesn't match

        return policy.effect

    async def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        attributes: Dict[str, Any]
    ) -> bool:
        """Evaluate single condition."""

        operator = condition.get("operator")
        attribute = condition.get("attribute")
        value = condition.get("value")

        if attribute not in attributes:
            return False

        attr_value = attributes[attribute]

        if operator == "equals":
            return attr_value == value
        elif operator == "not_equals":
            return attr_value != value
        elif operator == "in":
            return attr_value in value
        elif operator == "not_in":
            return attr_value not in value
        elif operator == "contains":
            return value in attr_value if attr_value else False
        elif operator == "greater_than":
            return attr_value > value
        elif operator == "less_than":
            return attr_value < value
        elif operator == "regex":
            import re
            return bool(re.match(value, str(attr_value)))
        elif operator == "time_range":
            current_hour = datetime.utcnow().hour
            start_hour, end_hour = value
            if start_hour <= end_hour:
                return start_hour <= current_hour <= end_hour
            else:  # Overnight range
                return current_hour >= start_hour or current_hour <= end_hour

        return False

    # Attribute provider methods
    async def _get_user_roles(self, user: CurrentUser, resource_id: str, context: Dict) -> List[str]:
        return user.roles

    async def _get_user_department(self, user: CurrentUser, resource_id: str, context: Dict) -> str:
        # Get from user service or user attributes
        return getattr(user, 'department', 'unknown')

    async def _get_user_clearance(self, user: CurrentUser, resource_id: str, context: Dict) -> int:
        # Get security clearance level
        return getattr(user, 'clearance_level', 0)

    async def _get_resource_owner(self, user: CurrentUser, resource_id: str, context: Dict) -> str:
        # Get resource owner from data service
        return "resource-owner-id"  # Placeholder

    async def _get_resource_classification(self, user: CurrentUser, resource_id: str, context: Dict) -> str:
        # Get resource classification level
        return "public"  # Placeholder

    async def _get_current_time(self, user: CurrentUser, resource_id: str, context: Dict) -> int:
        return datetime.utcnow().hour

    async def _get_user_location(self, user: CurrentUser, resource_id: str, context: Dict) -> str:
        # Get user location from request or user profile
        return context.get("location", "unknown")

    async def _get_network_info(self, user: CurrentUser, resource_id: str, context: Dict) -> Dict[str, str]:
        # Get network information
        return {
            "ip": context.get("client_ip", "unknown"),
            "network_type": "internal" if context.get("client_ip", "").startswith("192.168.") else "external"
        }

# Example ABAC policies
def create_example_policies() -> List[ABACPolicy]:
    """Create example ABAC policies."""

    policies = [
        # High-priority policy: Super admins can do anything
        ABACPolicy(
            id="super_admin_all",
            name="Super Admin Full Access",
            description="Super admins have access to everything",
            conditions=[
                {
                    "operator": "in",
                    "attribute": "user.roles",
                    "value": ["super_admin"]
                }
            ],
            effect="allow",
            priority=100
        ),

        # Time-based access policy
        ABACPolicy(
            id="business_hours_only",
            name="Business Hours Access",
            description="Certain actions only during business hours",
            conditions=[
                {
                    "operator": "in",
                    "attribute": "action.name",
                    "value": ["create", "update", "delete"]
                },
                {
                    "operator": "time_range",
                    "attribute": "environment.time",
                    "value": [9, 17]  # 9 AM to 5 PM
                }
            ],
            effect="allow",
            priority=50
        ),

        # Department-based access
        ABACPolicy(
            id="hr_employee_data",
            name="HR Employee Data Access",
            description="HR department can access employee data",
            conditions=[
                {
                    "operator": "equals",
                    "attribute": "user.department",
                    "value": "hr"
                },
                {
                    "operator": "equals",
                    "attribute": "resource.type",
                    "value": "employee"
                }
            ],
            effect="allow",
            priority=30
        ),

        # Resource ownership policy
        ABACPolicy(
            id="resource_owner_access",
            name="Resource Owner Access",
            description="Users can access their own resources",
            conditions=[
                {
                    "operator": "equals",
                    "attribute": "user.id",
                    "value": "{resource.owner}"  # Dynamic reference
                }
            ],
            effect="allow",
            priority=20
        ),

        # Location-based restriction
        ABACPolicy(
            id="sensitive_data_location",
            name="Sensitive Data Location Restriction",
            description="Sensitive data only accessible from internal network",
            conditions=[
                {
                    "operator": "equals",
                    "attribute": "resource.classification",
                    "value": "sensitive"
                },
                {
                    "operator": "not_equals",
                    "attribute": "environment.network.network_type",
                    "value": "internal"
                }
            ],
            effect="deny",
            priority=80  # High priority for security
        )
    ]

    return policies
```

### 2. ABAC Integration with FastAPI

```python
# src/core/abac_middleware.py
from fastapi import Depends, HTTPException, status, Request
from src.core.abac import ABACEngine
from src.core.auth import get_current_user
from src.core.models import CurrentUser

class ABACAuthorizer:
    """ABAC authorizer for FastAPI integration."""

    def __init__(self):
        self.engine = ABACEngine()
        # Load policies from configuration or database
        policies = create_example_policies()
        for policy in policies:
            self.engine.add_policy(policy)

    async def authorize(
        self,
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        request: Request
    ) -> bool:
        """Authorize request using ABAC."""

        context = {
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "path": str(request.url.path),
            "method": request.method
        }

        return await self.engine.evaluate(
            user, resource_type, resource_id, action, context
        )

# Global ABAC authorizer instance
abac_authorizer = ABACAuthorizer()

def get_abac_authorizer() -> ABACAuthorizer:
    return abac_authorizer

def require_abac_authorization(
    resource_type: str,
    action: str,
    resource_id_param: str = "resource_id"
):
    """Decorator for ABAC authorization."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies
            current_user = None
            request = None

            for key, value in kwargs.items():
                if isinstance(value, CurrentUser):
                    current_user = value
                elif isinstance(value, Request):
                    request = value

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Get resource ID
            resource_id = kwargs.get(resource_id_param, "")

            # Check ABAC authorization
            authorized = await abac_authorizer.authorize(
                current_user, resource_type, resource_id, action, request
            )

            if not authorized:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied by policy"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Dynamic Authorization

### 1. Policy Management API

```python
# src/api/policies.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.core.auth import get_current_user
from src.core.permissions import require_permission, Permission
from src.core.abac import ABACPolicy
from src.core.schemas import PolicyCreate, PolicyUpdate, PolicyResponse
from src.core.models import CurrentUser

router = APIRouter(prefix="/policies", tags=["authorization-policies"])

@router.get("/", response_model=List[PolicyResponse])
@require_permission(Permission.ADMIN_ACCESS)
async def list_policies(
    current_user: CurrentUser = Depends(get_current_user)
):
    """List all authorization policies."""
    policies = abac_authorizer.engine.policies
    return [PolicyResponse.from_policy(p) for p in policies]

@router.post("/", response_model=PolicyResponse)
@require_permission(Permission.ADMIN_ACCESS)
async def create_policy(
    policy_data: PolicyCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Create new authorization policy."""

    policy = ABACPolicy(
        id=policy_data.id,
        name=policy_data.name,
        description=policy_data.description,
        conditions=policy_data.conditions,
        effect=policy_data.effect,
        priority=policy_data.priority
    )

    abac_authorizer.engine.add_policy(policy)

    # Save to persistent storage (database/config)
    await save_policy_to_storage(policy)

    return PolicyResponse.from_policy(policy)

@router.put("/{policy_id}", response_model=PolicyResponse)
@require_permission(Permission.ADMIN_ACCESS)
async def update_policy(
    policy_id: str,
    policy_update: PolicyUpdate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Update authorization policy."""

    # Find existing policy
    existing_policy = None
    for policy in abac_authorizer.engine.policies:
        if policy.id == policy_id:
            existing_policy = policy
            break

    if not existing_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Update policy
    updated_policy = ABACPolicy(
        id=existing_policy.id,
        name=policy_update.name or existing_policy.name,
        description=policy_update.description or existing_policy.description,
        conditions=policy_update.conditions or existing_policy.conditions,
        effect=policy_update.effect or existing_policy.effect,
        priority=policy_update.priority or existing_policy.priority
    )

    # Remove old policy and add updated one
    abac_authorizer.engine.policies.remove(existing_policy)
    abac_authorizer.engine.add_policy(updated_policy)

    # Save to persistent storage
    await update_policy_in_storage(updated_policy)

    return PolicyResponse.from_policy(updated_policy)

@router.delete("/{policy_id}")
@require_permission(Permission.ADMIN_ACCESS)
async def delete_policy(
    policy_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Delete authorization policy."""

    # Find and remove policy
    for policy in abac_authorizer.engine.policies[:]:  # Create copy for iteration
        if policy.id == policy_id:
            abac_authorizer.engine.policies.remove(policy)
            await delete_policy_from_storage(policy_id)
            return {"message": "Policy deleted successfully"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Policy not found"
    )

@router.post("/test")
@require_permission(Permission.ADMIN_ACCESS)
async def test_authorization(
    test_request: AuthorizationTestRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Test authorization for given parameters."""

    # Create mock user for testing
    mock_user = CurrentUser(
        id=test_request.user_id,
        email="test@example.com",
        username="testuser",
        is_active=True,
        roles=test_request.user_roles,
        scopes=[]
    )

    # Test authorization
    result = await abac_authorizer.engine.evaluate(
        mock_user,
        test_request.resource_type,
        test_request.resource_id,
        test_request.action,
        test_request.context
    )

    return {
        "authorized": result,
        "user_id": test_request.user_id,
        "resource_type": test_request.resource_type,
        "resource_id": test_request.resource_id,
        "action": test_request.action,
        "context": test_request.context
    }
```

## Performance Optimization

### 1. Authorization Caching

```python
# src/core/auth_cache.py
import redis.asyncio as redis
import json
from typing import Optional
from datetime import timedelta
from src.core.config import settings

class AuthorizationCache:
    """Cache for authorization decisions."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_ttl = timedelta(minutes=15)
        self.cache_prefix = "auth:"

    def _make_cache_key(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> str:
        """Create cache key for authorization decision."""
        return f"{self.cache_prefix}{user_id}:{resource_type}:{resource_id}:{action}"

    async def get_authorization(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> Optional[bool]:
        """Get cached authorization decision."""
        cache_key = self._make_cache_key(user_id, resource_type, resource_id, action)

        cached_result = await self.redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        return None

    async def set_authorization(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        authorized: bool
    ) -> None:
        """Cache authorization decision."""
        cache_key = self._make_cache_key(user_id, resource_type, resource_id, action)

        await self.redis.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(authorized)
        )

    async def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cached decisions for a user."""
        pattern = f"{self.cache_prefix}{user_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def invalidate_resource_cache(self, resource_type: str, resource_id: str) -> None:
        """Invalidate all cached decisions for a resource."""
        pattern = f"{self.cache_prefix}*:{resource_type}:{resource_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

### 2. Optimized Authorization Flow

```python
# src/core/optimized_auth.py
from typing import Optional
from src.core.auth_cache import AuthorizationCache
from src.core.abac import ABACEngine
from src.core.models import CurrentUser

class OptimizedAuthorizer:
    """Optimized authorizer with caching and short-circuits."""

    def __init__(self, abac_engine: ABACEngine, cache: AuthorizationCache):
        self.abac_engine = abac_engine
        self.cache = cache

    async def authorize(
        self,
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        context: dict = None,
        use_cache: bool = True
    ) -> bool:
        """Optimized authorization with caching."""

        # Check cache first
        if use_cache:
            cached_result = await self.cache.get_authorization(
                user.id, resource_type, resource_id, action
            )
            if cached_result is not None:
                return cached_result

        # Short-circuit for super admin
        if "super_admin" in user.roles:
            if use_cache:
                await self.cache.set_authorization(
                    user.id, resource_type, resource_id, action, True
                )
            return True

        # Check basic RBAC first (faster than ABAC)
        permission = f"{resource_type}:{action}"
        if self.role_hierarchy.has_permission(user.roles, permission):
            if use_cache:
                await self.cache.set_authorization(
                    user.id, resource_type, resource_id, action, True
                )
            return True

        # Fall back to full ABAC evaluation
        result = await self.abac_engine.evaluate(
            user, resource_type, resource_id, action, context or {}
        )

        # Cache the result
        if use_cache:
            await self.cache.set_authorization(
                user.id, resource_type, resource_id, action, result
            )

        return result
```

## Audit and Compliance

### 1. Authorization Audit Trail

```python
# src/core/auth_audit.py
from datetime import datetime
from typing import Dict, Any, Optional
from src.core.models import CurrentUser
from src.clients.data_service import AuditDataClient

class AuthorizationAuditor:
    """Audit trail for authorization decisions."""

    def __init__(self, audit_client: AuditDataClient):
        self.audit_client = audit_client

    async def log_authorization_attempt(
        self,
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        authorized: bool,
        policy_matched: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> None:
        """Log authorization attempt for audit trail."""

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "authorization_attempt",
            "user_id": user.id,
            "user_email": user.email,
            "user_roles": user.roles,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "authorized": authorized,
            "policy_matched": policy_matched,
            "context": context or {},
            "ip_address": context.get("client_ip") if context else None,
            "user_agent": context.get("user_agent") if context else None
        }

        await self.audit_client.create_audit_record(audit_record)

    async def log_permission_change(
        self,
        admin_user: CurrentUser,
        target_user_id: str,
        old_permissions: list,
        new_permissions: list,
        reason: str
    ) -> None:
        """Log permission changes for compliance."""

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "permission_change",
            "admin_user_id": admin_user.id,
            "admin_email": admin_user.email,
            "target_user_id": target_user_id,
            "old_permissions": old_permissions,
            "new_permissions": new_permissions,
            "reason": reason
        }

        await self.audit_client.create_audit_record(audit_record)

    async def log_policy_change(
        self,
        admin_user: CurrentUser,
        policy_id: str,
        change_type: str,  # "created", "updated", "deleted"
        old_policy: Optional[Dict] = None,
        new_policy: Optional[Dict] = None
    ) -> None:
        """Log policy changes for compliance."""

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "policy_change",
            "admin_user_id": admin_user.id,
            "admin_email": admin_user.email,
            "policy_id": policy_id,
            "change_type": change_type,
            "old_policy": old_policy,
            "new_policy": new_policy
        }

        await self.audit_client.create_audit_record(audit_record)
```

## Testing Authorization

### 1. Authorization Test Utilities

```python
# tests/auth_test_utils.py
from typing import List, Dict, Any
from src.core.models import CurrentUser
from src.core.abac import ABACEngine, ABACPolicy

class AuthorizationTestHelper:
    """Helper class for testing authorization."""

    def create_test_user(
        self,
        user_id: str = "test-user",
        roles: List[str] = None,
        attributes: Dict[str, Any] = None
    ) -> CurrentUser:
        """Create test user with specified roles and attributes."""
        user = CurrentUser(
            id=user_id,
            email=f"{user_id}@example.com",
            username=user_id,
            is_active=True,
            roles=roles or ["user"],
            scopes=[]
        )

        # Add custom attributes
        if attributes:
            for key, value in attributes.items():
                setattr(user, key, value)

        return user

    def create_test_policy(
        self,
        policy_id: str,
        conditions: List[Dict[str, Any]],
        effect: str = "allow",
        priority: int = 0
    ) -> ABACPolicy:
        """Create test ABAC policy."""
        return ABACPolicy(
            id=policy_id,
            name=f"Test Policy {policy_id}",
            description=f"Test policy for {policy_id}",
            conditions=conditions,
            effect=effect,
            priority=priority
        )

    async def assert_authorized(
        self,
        authorizer: 'OptimizedAuthorizer',
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Assert that authorization succeeds."""
        result = await authorizer.authorize(
            user, resource_type, resource_id, action, context
        )
        assert result, f"Expected authorization to succeed for {user.id}:{resource_type}:{action}"

    async def assert_not_authorized(
        self,
        authorizer: 'OptimizedAuthorizer',
        user: CurrentUser,
        resource_type: str,
        resource_id: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Assert that authorization fails."""
        result = await authorizer.authorize(
            user, resource_type, resource_id, action, context
        )
        assert not result, f"Expected authorization to fail for {user.id}:{resource_type}:{action}"

# Test fixture
@pytest.fixture
def auth_test_helper():
    return AuthorizationTestHelper()
```

### 2. Authorization Test Examples

```python
# tests/test_authorization.py
import pytest
from src.core.abac import ABACEngine
from src.core.optimized_auth import OptimizedAuthorizer
from tests.auth_test_utils import AuthorizationTestHelper

class TestRBACAuthorization:
    """Test Role-Based Access Control."""

    async def test_admin_full_access(self, auth_test_helper: AuthorizationTestHelper):
        """Test that admin users have full access."""
        # Create admin user
        admin_user = auth_test_helper.create_test_user("admin", ["admin"])

        # Create authorizer
        engine = ABACEngine()
        authorizer = OptimizedAuthorizer(engine, None)

        # Test various actions
        await auth_test_helper.assert_authorized(
            authorizer, admin_user, "user", "any-user", "read"
        )
        await auth_test_helper.assert_authorized(
            authorizer, admin_user, "user", "any-user", "update"
        )
        await auth_test_helper.assert_authorized(
            authorizer, admin_user, "content", "any-content", "delete"
        )

    async def test_user_limited_access(self, auth_test_helper: AuthorizationTestHelper):
        """Test that regular users have limited access."""
        # Create regular user
        user = auth_test_helper.create_test_user("user", ["user"])

        # Create authorizer
        engine = ABACEngine()
        authorizer = OptimizedAuthorizer(engine, None)

        # Test read access (should work)
        await auth_test_helper.assert_authorized(
            authorizer, user, "content", "public-content", "read"
        )

        # Test admin action (should fail)
        await auth_test_helper.assert_not_authorized(
            authorizer, user, "user", "other-user", "delete"
        )

class TestABACAuthorization:
    """Test Attribute-Based Access Control."""

    async def test_time_based_access(self, auth_test_helper: AuthorizationTestHelper):
        """Test time-based access control."""
        # Create user
        user = auth_test_helper.create_test_user("user", ["user"])

        # Create time-based policy
        policy = auth_test_helper.create_test_policy(
            "business_hours",
            conditions=[
                {
                    "operator": "time_range",
                    "attribute": "environment.time",
                    "value": [9, 17]
                }
            ],
            effect="allow"
        )

        # Create engine with policy
        engine = ABACEngine()
        engine.add_policy(policy)
        authorizer = OptimizedAuthorizer(engine, None)

        # Mock business hours context
        business_hours_context = {"current_hour": 10}

        # Test during business hours
        await auth_test_helper.assert_authorized(
            authorizer, user, "document", "doc-1", "create", business_hours_context
        )

        # Mock after hours context
        after_hours_context = {"current_hour": 20}

        # Test after hours
        await auth_test_helper.assert_not_authorized(
            authorizer, user, "document", "doc-1", "create", after_hours_context
        )

    async def test_department_based_access(self, auth_test_helper: AuthorizationTestHelper):
        """Test department-based access control."""
        # Create HR user
        hr_user = auth_test_helper.create_test_user(
            "hr_user",
            ["user"],
            {"department": "hr"}
        )

        # Create non-HR user
        dev_user = auth_test_helper.create_test_user(
            "dev_user",
            ["user"],
            {"department": "development"}
        )

        # Create department-based policy
        policy = auth_test_helper.create_test_policy(
            "hr_access",
            conditions=[
                {
                    "operator": "equals",
                    "attribute": "user.department",
                    "value": "hr"
                },
                {
                    "operator": "equals",
                    "attribute": "resource.type",
                    "value": "employee"
                }
            ],
            effect="allow"
        )

        # Create engine with policy
        engine = ABACEngine()
        engine.add_policy(policy)
        authorizer = OptimizedAuthorizer(engine, None)

        # Test HR user access to employee data
        await auth_test_helper.assert_authorized(
            authorizer, hr_user, "employee", "emp-123", "read"
        )

        # Test non-HR user access to employee data
        await auth_test_helper.assert_not_authorized(
            authorizer, dev_user, "employee", "emp-123", "read"
        )

class TestAuthorizationPerformance:
    """Test authorization performance and caching."""

    async def test_authorization_caching(self, auth_test_helper: AuthorizationTestHelper):
        """Test that authorization results are properly cached."""
        # This test would require a real Redis instance or mock
        # Implementation depends on your testing setup
        pass

    async def test_authorization_performance(self, auth_test_helper: AuthorizationTestHelper):
        """Test authorization performance under load."""
        import time

        user = auth_test_helper.create_test_user("user", ["user"])
        engine = ABACEngine()
        authorizer = OptimizedAuthorizer(engine, None)

        # Measure authorization time
        start_time = time.time()

        for i in range(100):
            await authorizer.authorize(user, "content", f"content-{i}", "read")

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Assert reasonable performance (adjust threshold as needed)
        assert avg_time < 0.01, f"Authorization too slow: {avg_time}s per call"
```

## Related Documents

- `docs/atomic/security/authentication-guide.md` - Authentication implementation
- `docs/atomic/security/security-testing.md` - Security testing patterns
- `docs/atomic/services/fastapi/security-patterns.md` - FastAPI security basics
- `docs/atomic/integrations/redis/fastapi-integration.md` - Redis caching integration
- `docs/atomic/architecture/data-access-architecture.md` - Data service patterns

## Best Practices

### Implementation Checklist
- [ ] Implement hierarchical RBAC with clear role inheritance
- [ ] Use context-aware authorization for resource access
- [ ] Implement ABAC for complex business rules
- [ ] Cache authorization decisions for performance
- [ ] Audit all authorization attempts for compliance
- [ ] Test authorization logic thoroughly
- [ ] Use policy management APIs for dynamic updates
- [ ] Implement proper error handling and logging
- [ ] Follow principle of least privilege
- [ ] Regular review and update of authorization policies

### Security Considerations
- [ ] Default deny policy for all resources
- [ ] Secure policy storage and management
- [ ] Regular audit of permissions and roles
- [ ] Protection against privilege escalation
- [ ] Secure attribute collection and validation
- [ ] Rate limiting for authorization checks
- [ ] Monitoring for authorization bypasses
- [ ] Secure policy update mechanisms
- [ ] Separation of authorization and authentication
- [ ] Regular security testing and penetration testing