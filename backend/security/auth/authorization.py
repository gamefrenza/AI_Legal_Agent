from typing import List, Set, Optional
from ..models.user import User, Role, Permission
from ..models.resource import Resource
from ..utils.cache import Cache

class AuthorizationManager:
    def __init__(self):
        self.permission_cache = Cache()
        self.role_manager = RoleManager()
    
    async def check_permission(
        self,
        user: User,
        resource: Resource,
        action: str
    ) -> bool:
        """Check if user has permission for action on resource"""
        try:
            # Get user permissions
            permissions = await self._get_user_permissions(user)
            
            # Check resource-specific permissions
            required_permission = f"{resource.type}:{action}"
            if required_permission not in permissions:
                return False
            
            # Check resource-level restrictions
            return await self._check_resource_restrictions(
                user,
                resource,
                action
            )
            
        except Exception as e:
            await self.auth_logger.log_permission_check(
                user_id=user.id,
                resource_id=resource.id,
                action=action,
                result=False,
                error=str(e)
            )
            return False
    
    async def _get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for user including role-based permissions"""
        # Check cache first
        cached_permissions = await self.permission_cache.get(f"user_perms:{user.id}")
        if cached_permissions:
            return cached_permissions
        
        # Collect permissions from all roles
        permissions = set()
        for role in user.roles:
            role_permissions = await self.role_manager.get_role_permissions(role)
            permissions.update(role_permissions)
        
        # Add direct user permissions
        permissions.update(user.direct_permissions)
        
        # Cache permissions
        await self.permission_cache.set(
            f"user_perms:{user.id}",
            permissions,
            ttl=300  # 5 minutes
        )
        
        return permissions 