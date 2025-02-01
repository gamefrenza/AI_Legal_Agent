from typing import List, Dict, Any
from ..models.user import Role, Permission
from ..models.audit import AuditLog

class RoleManager:
    def __init__(self):
        self.role_store = RoleStore()
        self.audit_logger = AuditLogger()
    
    async def create_role(
        self,
        name: str,
        permissions: List[str],
        metadata: Dict[str, Any]
    ) -> Role:
        """Create new role with permissions"""
        # Validate role data
        await self._validate_role_data(name, permissions)
        
        # Create role
        role = Role(
            name=name,
            permissions=permissions,
            metadata=metadata
        )
        
        # Store role
        await self.role_store.store_role(role)
        
        # Log role creation
        await self.audit_logger.log_role_creation(role)
        
        return role
    
    async def assign_role(
        self,
        user_id: str,
        role_name: str,
        assigner_id: str
    ) -> None:
        """Assign role to user"""
        # Get role
        role = await self.role_store.get_role(role_name)
        if not role:
            raise ValueError(f"Role not found: {role_name}")
        
        # Assign role
        await self.role_store.assign_user_role(user_id, role.id)
        
        # Log role assignment
        await self.audit_logger.log_role_assignment(
            user_id=user_id,
            role_id=role.id,
            assigner_id=assigner_id
        )
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles assigned to user"""
        return await self.role_store.get_user_roles(user_id) 