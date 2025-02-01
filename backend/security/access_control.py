from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.document import DocumentAccess, AccessLevel
from ..models.user import User

class DocumentAccessManager:
    def __init__(self):
        self.access_store = AccessStore()
        self.policy_validator = AccessPolicyValidator()
    
    async def apply_access_policy(
        self,
        document_id: str,
        policy: Dict[str, Any]
    ) -> DocumentAccess:
        """Apply access control policy to document"""
        # Validate policy
        await self.policy_validator.validate(policy)
        
        # Create access control record
        access_control = DocumentAccess(
            document_id=document_id,
            owner_id=policy['owner_id'],
            access_levels=policy['access_levels'],
            restrictions=policy.get('restrictions', {}),
            expiration=policy.get('expiration'),
            metadata={
                'created_at': datetime.utcnow(),
                'last_modified': datetime.utcnow(),
                'modified_by': policy['owner_id']
            }
        )
        
        # Store access control
        await self.access_store.store_access_control(access_control)
        
        return access_control
    
    async def check_access(
        self,
        user: User,
        document_id: str,
        required_level: AccessLevel
    ) -> bool:
        """Check if user has required access level"""
        try:
            # Get document access control
            access_control = await self.access_store.get_access_control(document_id)
            
            # Check user access level
            user_level = access_control.access_levels.get(user.id)
            if not user_level:
                return False
            
            # Check if access level is sufficient
            return self._is_access_sufficient(user_level, required_level)
            
        except Exception as e:
            await self.audit_logger.log_access_check(
                user_id=user.id,
                document_id=document_id,
                result='error',
                error=str(e)
            )
            return False
    
    def _is_access_sufficient(
        self,
        user_level: AccessLevel,
        required_level: AccessLevel
    ) -> bool:
        """Check if user's access level is sufficient"""
        access_hierarchy = {
            AccessLevel.OWNER: 4,
            AccessLevel.ADMIN: 3,
            AccessLevel.WRITE: 2,
            AccessLevel.READ: 1,
            AccessLevel.NONE: 0
        }
        return access_hierarchy[user_level] >= access_hierarchy[required_level] 